#!/usr/bin/env python3
"""The API Logic Server contract the FutureBasic Enterprise client relies on, checked against a
running server.

    python3 tools/als_contract.py http://localhost:5656 [user] [password]

Each check is one thing src/Runtime/ALS Client.incl (and App Data Enterprise) does or expects:
login and its token, JSON:API lists, paging by links.next, filters and sorting, create, update
with the optimistic-lock checksum, a stale checksum refused, a rule's message, delete, and the
three shapes an error comes in. error_message() is the reference for ALSErrorMessage.

Needs a server with security on and the credit-limit rules (docs/design/ALS Contract.md says how
to run one). Exits 2 when no server answers, so run_tests.sh can skip it.
"""
import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1].rstrip('/') if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else 'http://localhost:5656'
USER = sys.argv[2] if len(sys.argv) > 2 else 'admin'
PASSWORD = sys.argv[3] if len(sys.argv) > 3 else 'p'
JSONAPI = 'application/vnd.api+json'
results = []


def call(method, path, body=None, token=None, content_type=JSONAPI):
    """One request -> (status, parsed JSON or None). Bare JSON strings are parsed too (fragments)."""
    url = path if path.startswith('http') else BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', content_type)
    req.add_header('Accept', 'application/vnd.api+json, application/json')
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))   # a local server: no proxy
    try:
        with opener.open(req, timeout=20) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw) if raw else None
        except ValueError:
            return e.code, raw.decode(errors='replace')


def error_message(status, payload):
    """What the user should read - the reference for ALSErrorMessage:
       {"errors": [{"title": ...}]}  -> the title (a rule's message; detail may be a dictionary)
       {"msg": ...} / {"message": ...} -> that text (token problems)
       "text"                          -> the text itself (a bad login)"""
    if isinstance(payload, dict):
        errors = payload.get('errors')
        if errors:
            first = errors[0]
            title = first.get('title')
            if isinstance(title, str) and title:
                return title
            detail = first.get('detail')
            if isinstance(detail, str) and detail:
                return detail
        for key in ('message', 'msg'):
            if isinstance(payload.get(key), str):
                return payload[key]
    if isinstance(payload, str) and payload:
        return payload
    return f'HTTP {status}'


def needs_sign_in(status):
    """401 (no or expired token, wrong password) and 422 (a token that is not a token)."""
    return status in (401, 422)


def check(name, ok, info=''):
    results.append(ok)
    print(('PASS  ' if ok else 'FAIL  ') + name + (f'   ({info})' if info and not ok else ''))


def fetch_all(resource, token, limit=100, query=''):
    """A whole list, page by page, by offset until meta.total rows have arrived - what App Data
    Enterprise does. links.next is NOT reliable: ALS (17.05) leaves it out one page early (with
    830 rows and pages of 200, the page at offset 600 has no next, though offset 800 holds 30)."""
    rows, offset, pages, total = [], 0, 0, None
    while total is None or offset < total:
        status, payload = call('GET', f'/api/{resource}?page[limit]={limit}&page[offset]={offset}{query}', token=token)
        if status != 200:
            return None, pages
        rows += payload['data']
        pages += 1
        total = payload['meta']['total']
        if not payload['data']:
            break
        offset += limit
    return rows, pages


def main():
    try:
        status, _ = call('GET', '/api/Category')
    except (urllib.error.URLError, OSError):
        print(f'als_contract: no server at {BASE} - skipped')
        return 2

    # sign-in
    check('a resource without a token is refused (401)', status == 401, status)
    status, payload = call('POST', '/api/auth/login', {'username': USER, 'password': 'wrong'}, content_type='application/json')
    check('a wrong password: 401 and a readable message', status == 401 and error_message(status, payload) == 'Wrong username or password', (status, payload))
    status, payload = call('POST', '/api/auth/login', {'username': USER, 'password': PASSWORD}, content_type='application/json')
    token = payload.get('access_token') if isinstance(payload, dict) else None
    check('login: POST /api/auth/login {username, password} -> access_token', status == 200 and bool(token), status)
    if not token:
        return 1
    status, payload = call('GET', '/api/Category', token='nonsense')
    check('a token that is not one: 422, means sign in again', needs_sign_in(status) and status == 422, status)

    # lists
    status, payload = call('GET', '/api/Category', token=token)
    check('a list: data[] of {type, id (text), attributes}, meta.total', status == 200 and isinstance(payload['data'][0]['id'], str) and 'total' in payload['meta'], status)
    check('every record carries S_CheckSum (optimistic locking)', 'S_CheckSum' in payload['data'][0]['attributes'])
    status, payload = call('GET', '/api/Order?page[limit]=200&page[offset]=600', token=token)
    check('ALS leaves links.next out one page early (offset 600 of 830): page by meta.total instead', 'next' not in payload['links'] and payload['meta']['total'] == 830, payload['links'])
    rows, pages = fetch_all('Order', token, limit=200)
    check('paging by offset to meta.total: all 830 orders in 5 pages of 200', rows is not None and len(rows) == 830 and pages == 5, (len(rows or []), pages))
    status, payload = call('GET', '/api/Customer?filter[Country]=Germany&sort=CompanyName&page[limit]=100', token=token)
    names = [r['attributes']['CompanyName'] for r in payload['data']]
    check('filter[Country]=Germany and sort=CompanyName', status == 200 and len(names) == 11 and names == sorted(names), len(names))
    status, payload = call('GET', '/api/Customer/ALFKI', token=token)
    check('one record: GET /api/Customer/ALFKI', status == 200 and payload['data']['id'] == 'ALFKI', status)
    original = payload['data']['attributes']

    # writes
    status, payload = call('POST', '/api/Category', {'data': {'type': 'Category', 'attributes': {'CategoryName_ColumnName': 'FB contract', 'Description': 'als_contract.py'}}}, token=token)
    new_id = payload['data']['id'] if status == 201 else None
    check('create: 201 and the new record (its id, its S_CheckSum)', status == 201 and new_id and 'S_CheckSum' in payload['data']['attributes'], status)
    status, payload = call('PATCH', '/api/Customer/ALFKI', {'data': {'type': 'Customer', 'id': 'ALFKI', 'attributes': {'ContactName': original['ContactName'] + ' (edited)', 'S_CheckSum': original['S_CheckSum']}}}, token=token)
    answered = payload['data']['attributes'] if status == 200 else {}
    check('update with the S_CheckSum read: 200 and the new values', status == 200 and answered.get('ContactName') == original['ContactName'] + ' (edited)', status)
    reread = call('GET', '/api/Customer/ALFKI', token=token)[1]['data']['attributes']
    check('ALS answers an update with the OLD S_CheckSum: read the record again for the new one', answered.get('S_CheckSum') == original['S_CheckSum'] and reread['S_CheckSum'] != original['S_CheckSum'], (answered.get('S_CheckSum', '')[:8], reread['S_CheckSum'][:8]))
    # a second user still holds the original checksum: their save is refused
    status, payload = call('PATCH', '/api/Customer/ALFKI', {'data': {'type': 'Customer', 'id': 'ALFKI', 'attributes': {'ContactName': 'Someone else', 'S_CheckSum': original['S_CheckSum']}}}, token=token)
    msg = error_message(status, payload)
    check('update with a stale S_CheckSum: 400 "row altered by another user"', status == 400 and 'altered by another user' in msg, (status, msg))
    status, payload = call('PATCH', '/api/Customer/ALFKI', {'data': {'type': 'Customer', 'id': 'ALFKI', 'attributes': {'ContactName': original['ContactName'], 'S_CheckSum': reread['S_CheckSum']}}}, token=token)
    check('the record put back with the checksum read after the update', status == 200, status)
    status, payload = call('PATCH', '/api/Customer/ALFKI', {'data': {'type': 'Customer', 'id': 'ALFKI', 'attributes': {'CreditLimit': 1}}}, token=token)
    msg = error_message(status, payload)
    check('a rule refuses the update: 400, the message is errors[0].title (detail is a dictionary)', status == 400 and msg.startswith('balance (') and isinstance(payload['errors'][0]['detail'], dict), (status, msg))
    if new_id:
        status, payload = call('DELETE', f'/api/Category/{new_id}', token=token)
        check('delete: 204 and no body', status == 204 and payload is None, status)
        status, payload = call('GET', f'/api/Category/{new_id}', token=token)
        check('the deleted record is gone (404)', status == 404, status)

    failed = results.count(False)
    print(f'als_contract: {len(results)} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
