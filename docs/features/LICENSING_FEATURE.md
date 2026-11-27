# Licensing: the licence in App Builder

Status: built here (2026-11-26); not yet built on a Mac. The License Server's side is not built. Design:
`docs/design/Licensing Design.md`.

## What it does

- **A licence is checked offline:** `src/AppBuilder/Licence.incl`.
  - A licence is `<payload>.<signature>`. The payload is base64url JSON. The signature is ECDSA P-256 / SHA-256
    (ANSI X9.62) of the payload's text.
  - App Builder checks it with the public key in `LICENCE_PUBLIC_KEY`, through the Security framework:
    `SecKeyCreateWithData`, `SecKeyVerifySignature`, `kSecKeyAlgorithmECDSASignatureMessageX962SHA256`.
  - It then checks the product (`app_builder_fb`) and the expiry date.
  - A licence is kept in the Keychain (service `App Builder for FutureBasic`, account `licence`).
  - `LicenceAllows( _licenceFeature… )` answers from the payload's feature bits:

    | Edition | Bits | Features |
    |---|---|---|
    | Lite | `0x0003` | core, AI |
    | Professional | `0x01FF` | Lite's, plus ALS projects, the Professional runtime, rules exchange, integration, authorization, governance, genai-logic |
- **The Licence window and menu:** `src/AppBuilder/Licence Window.incl`.
  - The App Builder menu, after About: Licence…, Enter Licence…, Upgrade to Professional…, Manage Licence Online…,
    Remove Licence….
  - The window shows the licence in words (who, the edition, until when, each feature ticked or "Professional"). It
    has a field to paste a licence, Get a Free Lite Licence, Upgrade, Manage Online, Remove and Close.
  - At launch, without a valid licence, the window opens.
- **The gates:** `fn LicenceGate( feature, what )`:
  - New Project from API Logic Server… (menu and the New Project view's button), Open API Logic Server Metadata…:
    ALS projects;
  - Import / Export Rules: rules exchange;
  - Generate App / XIBs / XIB / Binding (menu and toolbar): core, so nothing is generated without a licence.

  A locked command stays in its menu with "(Professional)" after its title. Choosing it explains, and offers the
  upgrade (or the Licence window, without a licence). `Edition.incl`'s `EditionProfessionalAvailable` is the licence's
  Professional runtime bit.
- **The License Server's pages:** `LICENCE_SERVER` + `/appbuilder`, `/appbuilder/upgrade?lic=…`, `/account`. The
  address (`https://license.imagery.com`, from the License Server's documents) is to confirm before release.

## The keys

`tools/licence_test_keys/TEST-ONLY-private.pem` is a TEST key, public in this repository. A licence signed with it
proves nothing. `LICENCE_PUBLIC_KEY` holds its public half until the License Server makes the production key pair; its
private key never leaves the server.

## Verification

- `tools/licence_reference.py --test` (in `run_tests.sh`) runs 10 cases:
  - valid Lite and Professional licences;
  - the last day, and the day after (expired);
  - edited, another licence's signature, another key, another product;
  - not a licence; pasted with spaces and new lines.
- `src/MacTests/Licence Verify Test.fb` is written by `--mac-test`. It carries `Licence.incl`'s verify part unchanged
  (`--mac-test-check`, in `run_tests.sh`) and the same 10 cases.
- **On a Mac (to do):** the test program says PASS for each case.
- **In the app (to do):**
  - no licence: the window opens at launch; Generate asks for a licence;
  - a Lite licence (`--issue lite`): ALS projects say Professional; Generate works;
  - an Professional licence: everything opens;
  - Remove, then relaunch;
  - the Keychain item is in Keychain Access.

## Not yet

- The `appbuilderfb://` URL scheme and the `.fblicence` document type (the licence arrives by link or file).
- The edition in the About box.
- The License Server: the product, signing, the pages (its own repository).

## Build fix (2026-11-27)

The author's first build of the Studio with the licence stopped at `include "Tlbx Security.incl"` (error 1234). That FB
header is dated 2026-05-05 and is not in the author's FutureBasic. `src/AppBuilder/Licence Security.incl` now declares the
calls `Licence.incl` uses, at its own top (first in a file of its own, `Licence Security.incl`; moved into `Licence.incl` the same day, because the editor, with the project already open, did not see the new file):
- the framework: `include library "Security"`;
- SecKey: `SecKeyCreateWithData`, `SecKeyVerifySignature` and the ES256 constants;
- SecItem: `SecItemCopyMatching`, `SecItemAdd`, `SecItemDelete` and the Keychain keys.

The Mac licence test carries the same declarations
(`tools/licence_reference.py --mac-test`).

