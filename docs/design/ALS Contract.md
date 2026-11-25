# The API Logic Server contract (Enterprise edition)

What the generated app's Enterprise data layer can rely on from API Logic Server, and what it
must do itself. Measured against a running server (API Logic Server / GenAI-Logic 17.05.44,
the Northwind sample with SQL security and a credit-limit rule) on 2026-11-25, and checked again
by `tools/als_contract.py` (18 checks) whenever a server is running.

The runtime's `src/Runtime/ALS Client.incl` follows it; `App Data Enterprise.incl` (next) builds on
that client with the same interface as the Lite edition (`App Data Lite.incl`), so the pages,
bindings and screens are the same in both editions.

## Sign-in

| | |
|---|---|
| Request | `POST /api/auth/login`, `Content-Type: application/json`, `{"username": "...", "password": "..."}` |
| Answer | `200 {"access_token": "<JWT>"}`; send `Authorization: Bearer <JWT>` with every request after |
| Lifetime | the sample's tokens last about 3.7 hours (`exp` in the JWT) |
| Wrong password | `401` and a bare JSON string: `"Wrong username or password"` |
| No token | `401` |
| Expired token | `401` |
| Something that is not a token | `422 {"msg": "Not enough segments"}` |

**The client:** 401 and 422 both mean *sign in again* (`ALSNeedsSignIn`). A bare JSON string
needs `NSJSONReadingFragmentsAllowed` to be read at all.

## Lists

`GET /api/<Resource>?page[limit]=<n>&page[offset]=<k>`, optionally
`&filter[<attribute>]=<value>`, `&sort=<attribute>` (`-attribute` descending),
`&fields[<Resource>]=a,b`.

```json
{ "data": [ { "type": "Customer", "id": "ALFKI",
              "attributes": { "CompanyName": "...", "S_CheckSum": "fd91..." },
              "relationships": { ... }, "links": { "self": "/api/Customer/ALFKI/" } } ],
  "meta":  { "count": 11, "limit": 100, "total": 11 },
  "links": { "self": "...", "next": "...", "last": "..." } }
```

- `id` is always text (`"1"`, `"ALFKI"`); the attributes hold the key columns too (`Id`).
- The default page is 250 rows here (it is a server setting); always ask for a page size.
- **`links.next` is not reliable**: with 830 orders and pages of 200, the page at offset 600 has
  no `next`, though offset 800 holds the last 30. **Page by offset until `meta.total` rows have
  arrived** (`ALSListPage`, `ALSResponseTotal`).

## Filters

Only the **JSON list form** filters reliably:
`filter=[{"name": "<attribute>", "op": "<op>", "val": <value>}, ...]` (URL-encoded).

| op | means | SQL Generator operator |
|---|---|---|
| `eq`, `ne` | = , != | `_isEqual`, `_isNotEqual` |
| `lt`, `le`, `gt`, `ge` | < , <= , > , >= | `_isLessThan` ... `_isGreaterThanOrEqual` |
| `like`, `ilike`, `notilike` | LIKE (case-sensitive), case-insensitive LIKE, NOT ILIKE | `_isLike`, (none), `_isNotLike` |
| `eq` / `ne` with `null` | IS NULL / IS NOT NULL | `_isNull`, `_isNotNull` |
| `in`, `notin` with a list | IN, NOT IN (several values: better than the SQL side's single `?`) | `_isIn`, `_isNotIn` |

- Several filters are joined with **AND** (ALS's `SAFRSBaseX._s_filter`; plain safrs would use OR).
- **No OR**: `{"or": [...]}` is refused (400). OR across values of one attribute is `in`.
- `is_null` / `is_` are not operators ("unknown operator").
- **`filter[attr][op]=val` is silently ignored** - it returns 0 rows, no error. Never write it.
  `filter[attr]=val` (equality only) works.
- Relationships: `include=<toone>` adds the parent to `included`; `/api/Customer/ALFKI/OrderList`
  lists a parent's children.

## Writes

| | Request | Answer |
|---|---|---|
| Create | `POST /api/<Resource>`, `{"data": {"type": "<Resource>", "attributes": {...}}}` | `201`, the new record (its `id`, generated keys, its `S_CheckSum`) |
| Update | `PATCH /api/<Resource>/<id>`, `{"data": {"type", "id", "attributes": {changed..., "S_CheckSum"}}}` | `200`, the record with the new values |
| Delete | `DELETE /api/<Resource>/<id>` | `204`, no body; a GET after it is `404` |

`Content-Type: application/vnd.api+json` for these.

## Multi-user: optimistic locking

Every record carries `S_CheckSum`. Sending it back with an update makes the save conditional:

- the checksum still matches -> saved;
- someone saved the record since it was read -> `400`, *"Sorry, row altered by another user -
  please note changes, cancel and retry"*;
- an update without `S_CheckSum` is saved unconditionally (last save wins) - the client always
  sends it.

**The update's answer still carries the old `S_CheckSum`** (the new values, the checksum they
replaced). Read the record again (`ALSGet`) before the next edit, or the next save is refused
as if another user had changed it.

## The business rules' answers

Rules run on the server (LogicBank, `logic/declare_logic.py`), for every client. A refused save:

```json
{"errors": [{"title": "balance (2102.0000000000) exceeds credit (1)",
             "detail": {"model": "Customer", "error_attributes": []}, "code": "2001"}]}
```

`400`; **the message is `errors[0].title`** - `detail` is a dictionary here, so a client that
prefers `detail` shows a dictionary instead of the rule's message (the runtime did, until this
contract was measured).

## Errors, all shapes

| Shape | When | What the user reads |
|---|---|---|
| `{"errors": [{"title": ..., "detail": ...}]}` | rules, stale checksum | `title` (`detail` only when it is text) |
| `{"msg": ...}` | token problems | `msg` |
| `"text"` | wrong password | the text |
| no body | network failure | the system's message (`ErrorLocalizedDescription`) |

## Running the test server

In a scratch folder (never in this repository):

```bash
python3 -m venv als-venv && . als-venv/bin/activate && pip install ApiLogicServer
ApiLogicServer create --project_name=nw --db_url=nw
ApiLogicServer add-auth --provider-type=sql --project-name=nw
```

Add the credit-limit rules as `nw/logic/logic_discovery/check_credit.py` (a constraint on
`Customer`, the sums, the formula and the copy, as in the Lite engine's acceptance scenarios), then:

```bash
cd nw && SECURITY_ENABLED=true python api_logic_server_run.py
```

```bash
python3 tools/als_contract.py http://localhost:5656 admin p
```

The sample's users: `admin`, `sa`, `u2`, `aneu`, `sam` (password `p`). `tools/run_tests.sh` runs the
contract checks when a server answers on `localhost:5656` and skips them otherwise.
