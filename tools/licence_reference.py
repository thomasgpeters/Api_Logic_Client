#!/usr/bin/env python3
"""App Builder's licences, worked out here: issue (sign) and verify, exactly as App Builder (Licence.incl) and the
Imagery License Server do. Design: docs/design/Licensing Design.md.

    python3 tools/licence_reference.py --test                    every case: valid, tampered, expired, other product ...
    python3 tools/licence_reference.py --issue lite jane@example.com "Jane Outerbridge" [--expires 2027-11-30]
    python3 tools/licence_reference.py --issue professional ...    a licence signed with the TEST key (for a Mac test)
    python3 tools/licence_reference.py --public-key              the TEST public key as App Builder embeds it
    python3 tools/licence_reference.py --mac-test                write src/MacTests/Licence Verify Test.fb
    python3 tools/licence_reference.py --mac-test-check          is that program up to date with Licence.incl?

A licence is "<payload>.<signature>":
    payload     base64url (no padding) of the licence's JSON (lic, product, account, name, edition, features, issued, expires)
    signature   base64url (no padding) of an ECDSA P-256 / SHA-256 signature (DER, ANSI X9.62) of the payload's
                base64url text - what macOS's SecKeyVerifySignature checks with
                kSecKeyAlgorithmECDSASignatureMessageX962SHA256
App Builder holds only the public key (65 bytes, 04 || X || Y, base64 in Licence.incl). The private key that signs real
licences lives on the License Server alone.

THE KEYS IN tools/licence_test_keys/ ARE FOR TESTS ONLY. They are public (in this repository): a licence signed with
them proves nothing. Before release, the License Server makes the production key pair and Licence.incl gets its public key.
"""
import base64
import json
import os
import sys
from datetime import date

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = os.path.join(HERE, 'licence_test_keys')
PRODUCT = 'app_builder_fb'

# the feature bits (Licensing Design.md); Licence.incl has the same table
FEATURES = [
    ('core', 'Studio core: projects from SQLite, generation, rules, LogicBank for FutureBasic'),
    ('ai', 'AI Assistant (your own key)'),
    ('als_projects', 'API Logic Server projects'),
    ('professional_runtime', 'Professional apps: the API Logic Server client'),
    ('rules_exchange', 'Rules exchanged with API Logic Server (declare_logic.py)'),
    ('integration', 'Integration and scheduled rules'),
    ('authorization', 'Authorization rules'),
    ('governance', 'Rule governance'),
    ('genai_logic', 'AI through API Logic Server (genai-logic)'),
]
LITE = 0x0003
PROFESSIONAL = 0x01FF


def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def unb64url(text):
    return base64.urlsafe_b64decode(text + '=' * (-len(text) % 4))


def test_keys():
    """the TEST key pair (made once, kept in tools/licence_test_keys/)"""
    os.makedirs(KEYS, exist_ok=True)
    private_path = os.path.join(KEYS, 'TEST-ONLY-private.pem')
    if not os.path.exists(private_path):
        key = ec.generate_private_key(ec.SECP256R1())
        with open(private_path, 'wb') as f:
            f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    with open(private_path, 'rb') as f:
        private = serialization.load_pem_private_key(f.read(), password=None)
    return private, private.public_key()


def public_key_base64(public):
    """65 bytes, 04 || X || Y (ANSI X9.63), base64: what SecKeyCreateWithData takes"""
    raw = public.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    return base64.b64encode(raw).decode('ascii')


def issue(private, lic, edition, account, name, issued, expires=None, features=None, product=PRODUCT):
    payload = {'lic': lic, 'product': product, 'account': account, 'name': name, 'edition': edition,
               'features': features if features is not None else (PROFESSIONAL if edition == 'professional' else LITE),
               'issued': issued, 'expires': expires}
    body = b64url(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    signature = private.sign(body.encode('ascii'), ec.ECDSA(hashes.SHA256()))
    return body + '.' + b64url(signature)


def verify(text, public, today):
    """(payload or None, the reason it is refused) - Licence.incl's LicenceVerify, step for step"""
    parts = (text or '').strip().split('.')
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None, 'This is not a licence: it should be two parts joined by a full stop.'
    try:
        body, signature = parts[0].encode('ascii'), unb64url(parts[1])
    except Exception:
        return None, 'This is not a licence: it contains characters a licence never has.'
    try:
        public.verify(signature, body, ec.ECDSA(hashes.SHA256()))
    except (InvalidSignature, ValueError):
        return None, 'The licence\'s signature does not match: it was changed, or it was not issued by Imagery.'
    try:
        payload = json.loads(unb64url(parts[0]))
    except Exception:
        return None, 'The licence could not be read.'
    if payload.get('product') != PRODUCT:
        return None, 'This licence is for another product.'
    if payload.get('expires') and str(payload['expires']) < today:
        return None, f'This licence expired on {payload["expires"]}.'
    return payload, None


def allows(payload, bit):
    return payload is not None and (int(payload.get('features', 0)) & (1 << bit)) != 0


def cases(private, public):
    """(name, licence text, today, expected: ok, expected words in the reason, features expected)"""
    other_private = ec.generate_private_key(ec.SECP256R1())
    lite = issue(private, 'L-TEST-0001', 'lite', 'jane@example.com', 'Jane Outerbridge', '2026-11-26')
    ent = issue(private, 'L-TEST-0002', 'professional', 'jane@example.com', 'Jane Outerbridge', '2026-11-26', '2027-11-30')
    body, sig = lite.split('.')
    tampered = json.loads(unb64url(body))
    tampered['features'] = PROFESSIONAL
    tampered_body = b64url(json.dumps(tampered, separators=(',', ':')).encode('utf-8'))
    return [
        ('a Lite licence: core and the AI assistant, nothing Professional', lite, '2026-11-26', True, '', LITE),
        ('a Professional licence until 2027-11-30', ent, '2026-11-26', True, '', PROFESSIONAL),
        ('the Professional licence the day it ends: still good', ent, '2027-11-30', True, '', PROFESSIONAL),
        ('the Professional licence the day after: expired', ent, '2027-12-01', False, 'expired', None),
        ('a Lite licence edited to Professional: the signature no longer matches', tampered_body + '.' + sig, '2026-11-26', False, 'signature', None),
        ('a licence with another licence\'s signature', body + '.' + ent.split('.')[1], '2026-11-26', False, 'signature', None),
        ('a licence signed with another key (not Imagery\'s)', issue(other_private, 'L-X', 'professional', 'x@example.com', 'X', '2026-11-26'), '2026-11-26', False, 'signature', None),
        ('a licence for another product', issue(private, 'L-TEST-0003', 'lite', 'jane@example.com', 'Jane', '2026-11-26', product='fleet_dispatcher'), '2026-11-26', False, 'another product', None),
        ('text that is not a licence', 'hello', '2026-11-26', False, 'not a licence', None),
        ('a licence pasted with spaces and a new line around it', '  ' + lite + '\n', '2026-11-26', True, '', LITE),
    ]


LICENCE_INCL = os.path.join(HERE, '..', 'src', 'AppBuilder', 'Licence.incl')
MAC_TEST = os.path.join(HERE, '..', 'src', 'MacTests', 'Licence Verify Test.fb')


def fb_string(text):
    return '@"' + text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def mac_test_source(private, public):
    """the Mac test: Licence.incl's verify part, unchanged, and every case - one FB program"""
    incl = open(LICENCE_INCL, newline='').read().replace('\r', '\n')
    def security_declarations():
        return incl[incl.index('include library'):incl.index('// --- end Security declarations ---')].rstrip().replace('\n', '\r')
    start = incl.index('// --- verify (shared')
    end = incl.index('// --- end verify ---') + len('// --- end verify ---')
    lines = ['/*',
             ' *   Licence Verify Test.fb - does App Builder\'s licence check work on this Mac?',
             ' *',
             ' *   Written by tools/licence_reference.py --mac-test: do not edit. Its verify part is src/AppBuilder/Licence.incl\'s,',
             ' *   unchanged (run_tests.sh checks); its cases are the reference\'s, signed with the TEST key. Open it in the',
             ' *   FutureBasic editor and run it: every case should say PASS in the NSLog window.',
             ' */',
             '',
             'include "NSLog.incl"',
             '// the Security declarations, as src/AppBuilder/Licence.incl has them (any FutureBasic, with or without its own',
             '// Tlbx Security.incl)',
             security_declarations(),
             '',
             incl[start:end].replace('\n', '\r'),
             '',
             '',
             'begin globals',
             'long gPassed, gFailed',
             'end globals',
             '',
             '',
             'void local fn LicenceCheckCase( caseName as CFStringRef, licenceText as CFStringRef, onDay as CFStringRef, expectValid as BOOL, words as CFStringRef, features as long )',
             'CFDictionaryRef payload = fn LicenceVerify( licenceText, onDay )',
             'BOOL            good',
             'if ( expectValid )',
             'good = ( payload != NULL )',
             'if ( good ) then good = ( fn LicenceFeaturesOf( payload ) == features )',
             'else',
             'good = ( payload == NULL )',
             'if ( good ) then good = fn StringContainsString( gLicenceVerifyProblem, words )',
             'end if',
             'if ( good )',
             'gPassed++',
             'NSLog( @"PASS  %@", caseName )',
             'else',
             'gFailed++',
             'NSLog( @"FAIL  %@   (%@)", caseName, gLicenceVerifyProblem )',
             'end if',
             'end fn',
             '',
             '']
    for name, text, today, ok, words, feats in cases(private, public):
        lines.append(f'fn LicenceCheckCase( {fb_string(name)}, {fb_string(text)}, @"{today}", {"YES" if ok else "NO"}, {fb_string(words)}, {feats or 0} )')
    lines += ['NSLog( @"licences: %ld passed, %ld failed", gPassed, gFailed )', '', 'HandleEvents', '']
    return '\r'.join(lines)


def main(argv):
    private, public = test_keys()
    if '--public-key' in argv:
        print(public_key_base64(public))
        return 0
    if '--issue' in argv:
        i = argv.index('--issue')
        edition, account, name = argv[i + 1], argv[i + 2], argv[i + 3]
        expires = argv[argv.index('--expires') + 1] if '--expires' in argv else None
        print(issue(private, 'L-TEST-' + edition.upper(), edition, account, name, date.today().isoformat(), expires))
        return 0
    if '--mac-test-check' in argv:
        current = open(MAC_TEST, newline='').read()
        program = mac_test_source(private, public)
        # the licences are signed afresh each time (ECDSA signatures differ), so compare all but the case lines
        strip = lambda text: [l for l in text.split('\r') if not l.startswith('fn LicenceCheckCase( @')]
        same = strip(current) == strip(program) and current.count('fn LicenceCheckCase( @') == program.count('fn LicenceCheckCase( @')
        print('the Mac test is up to date with Licence.incl' if same else 'the Mac test is out of date: run tools/licence_reference.py --mac-test')
        return 0 if same else 1
    if '--mac-test' in argv:
        with open(MAC_TEST, 'w', newline='') as f:
            f.write(mac_test_source(private, public))
        print('wrote', MAC_TEST)
        return 0
    failed = 0
    for name, text, today, ok, words, feats in cases(private, public):
        payload, reason = verify(text, public, today)
        good = (payload is not None) == ok and (ok or words in (reason or '')) and (not ok or int(payload['features']) == feats)
        if ok and good:
            good = allows(payload, 0) and allows(payload, 1) and (allows(payload, 2) == (feats == PROFESSIONAL))
        failed += 0 if good else 1
        print(f'{"PASS" if good else "FAIL"}  {name}' + ('' if good else f'   ({reason})'))
    print(f'licences: {len(cases(private, public))} cases, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
