# Licensing Design: one app, licensed through the Imagery License Server

Status: design (author, 2026-11-26). It replaced an earlier plan (Lite open source,
Professional a separate private build that swaps `Edition.incl`). Nothing is built yet; see BACKLOG.

## Decisions (author, 2026-11-26)

- **One application.** App Builder for FutureBasic (the built app: Studio for FB) is the same app for Lite and
  Professional. Professional features are in every copy, switched on by the licence.
- **Lite has a licence too.** Users register on the Imagery License Server, get a free Lite licence, and only
  then download the app.
- **Upgrade from inside the app.** A Licence menu shows the licence and leads to the Professional upgrade.
- **The source:**
  - App Builder's source becomes **private**: it is one licensed binary.
  - **LogicBank for FutureBasic** and the **SQL Generator** stay **public** (MIT), as separate modules in
    public repositories.
  - Generated apps belong to their users.
- **A licence is bound to the registered account** (email / company), not to a Mac: it works on any Mac the
  person uses.
- **Licences are signed** for both editions. The app checks the signature with a public key built into it,
  offline. A licence cannot be forged or edited.
- **Generated apps never check a licence.** Licences gate App Builder's features only. A generated app, with
  its copy of LogicBank for FutureBasic, runs anywhere.

## Pricing (author, 2026-11-26)

One price list for every Imagery application (the License Server's `docs/plans/CONCURRENT_USER_TIERS.md`). It is
introductory for the first year, and customers keep it as long as they renew without a break. Not yet public: the
marketing repository keeps unpublished prices out.

| Tier | App Builder: developer seats | Annual | Monthly (annual / 12 + 20%) |
|---|---|---:|---:|
| Starter | up to 5 | $299 | $29.90 |
| Team | up to 25 | $499 | $49.90 |
| Unlimited | no limit | $899 | $89.90 |
| Added seat (Starter only) | +1 each | $59 | $5.90 |

- **Lite stays free** on registration. **Professional is sold on the tiers,** counted as developer seats: a desktop app
  has no concurrent sign-ins.
- **The licence will carry `tier` and `seats`.** `Licence.incl` reads the payload as a dictionary, so the new claims
  need no change to verification; showing them in the Licence window is a small follow-up.
- **The free modules are the reason to subscribe.** The SQL Generator, LogicBank for FutureBasic and the Web Toolkit
  are free (MIT). With them you write your own rules and pages; App Builder automates both (`Free Modules Design.md`).
- **The web target** (feature bit 9, below) is in Professional.

## Seats: copies on the local network, and Macs activated online (author, 2026-11-26)

The author: "there may be a need for a [Bonjour] connection to search for other instances running on the same network
... with the same license if they're cheating". The answers to the questions that followed:

| Question | Decision |
|---|---|
| How copies find each other | **Bonjour (mDNS / DNS-SD)**, the way Macs find printers. No server, no setup. |
| More copies on the network than seats | The newest copy is **read-only until resolved**. It says "This licence is already in use on <Mac name>" and can open and read projects, but generates nothing until another copy closes or seats are added. |
| Copies on other networks | **Each Mac is activated online once.** Entering a licence registers the Mac with the License Server, which refuses more Macs than seats. After that, App Builder works offline. Moving to a new Mac frees a seat, from the Licence window or the account page. |
| Lite | **One person, any of their Macs, one copy at a time** on the same network. |

### On the local network (Bonjour)

- **What each copy announces:** a service `_appbuilderfb._tcp` (registered with `DNSServiceRegister`), with a TXT
  record holding:
  - `lic`: a fingerprint of the licence id, HMAC-SHA256 with a constant in the app, the first 16 hex characters. The
    licence itself never goes on the network.
  - `mac`: a random id this Mac keeps in the Keychain.
  - `seats`: the licence's seat count.
- **What each copy listens for** (`DNSServiceBrowse`, then `DNSServiceResolve` for the TXT record): the distinct
  `mac` values with the same `lic`, its own included. One person on one Mac with two copies open counts once.
- **When the count exceeds the seats,** the copy that joined last turns read-only. Each copy records when it started
  in its TXT record (`since`), so every copy agrees on who joined last. When another copy goes away, the read-only
  copy is told and works again; it does not need restarting.
- **In FutureBasic:** a C block with `<dns_sd.h>` (part of macOS, no library to add) and `DNSServiceSetDispatchQueue`
  on the main queue, the way the Web Toolkit's FastCGI server works. FB's toolbox headers have no Bonjour calls,
  so the C block declares the few it needs.
- **macOS asks permission once.** Since macOS 15, the first browse shows "allow App Builder to find devices on your
  local network". Info.plist needs `NSLocalNetworkUsageDescription` (why) and `NSBonjourServices`
  (`_appbuilderfb._tcp`).
  - If the person declines, the local check is off, and the online activation still holds the seats.
  - A firewall that drops multicast has the same effect.
- **What it does not do:** it is a deterrent, not a lock. It sees one network segment, and a determined person can
  block it. The online activation is what holds the seat count.

### Across networks (online activation)

- **On entering a licence,** App Builder sends the License Server the licence id and this Mac's id (the same random
  id), signed with nothing secret. The server answers yes, or "all N seats are in use", naming the Macs by the names
  their owners gave them.
- **Afterwards App Builder works offline.** It does not check in again unless the licence is entered again, renewed,
  or a seat is released.
- **"Release this Mac"** in the Licence window, or on the account page, frees a seat for a new Mac.
- **The server side** is the License Server's work: activation and release endpoints, and a list of Macs per licence
  (its backlog, with the concurrent-user tiers).

### Plan

1. **Here:** `Licence Seats.incl` (the Bonjour C block, the count, read-only mode); the Info.plist keys; read-only
   mode gating every generate command (with `LicenceGate`); a Mac test program (two copies on two Macs).
2. **Here:** activation and release in `Licence.incl` and the Licence window, against a stub until the License
   Server has the endpoints.
3. **The License Server:** the endpoints and the Macs list.

## Why signed licences, and which signature

The License Server's tokens today (`XXXX-XXXX-MMMM-XXXX-XXXX`) have two problems for App Builder:

- **They can be forged.** The checksum uses a published salt and a non-cryptographic hash.
- **The hash differs by platform.** It is C++'s `std::hash`, whose results differ between the server's
  library (libstdc++, Linux) and macOS.

So App Builder uses a **signed licence** instead:

- **The algorithm is ECDSA P-256 with SHA-256 (ES256).** macOS verifies it natively, and FB can call it:
  `SecKeyCreateWithData` and `SecKeyVerifySignature` with `kSecKeyAlgorithmECDSASignatureMessageX962SHA256`
  are in FutureBasic_Documentation's `Toolboxes/Headers/Security/SecKey.incl`.
- **No extra library is needed.** Ed25519 would need one; the Security framework does not offer it.
- **The server signs** with OpenSSL (C++). Only the server holds the private key.
- **The app checks** with the public key compiled into it.

### The licence

A licence is a short text in two parts, `<payload>.<signature>`, both base64url (the JWT idea, without the
library). The payload is JSON:

```json
{
  "lic": "L-2026-000417",                 // the licence's id on the License Server
  "product": "app_builder_fb",
  "account": "jane@example.com",          // the registered account (the "site")
  "name": "Jane Outerbridge",
  "edition": "lite",                      // lite | professional
  "features": 1,                          // the feature bits (below)
  "issued": "2026-11-26",
  "expires": null                         // Lite: none; Professional: the subscription's end
}
```

- **How it reaches the app:** the user pastes it, opens a `.fblicence` file the License Server sends, or clicks
  an `appbuilderfb://licence?...` link from the License Server's page (a URL scheme App Builder registers).
- **Where it is kept:** in the Keychain (`docs/design/Generator App Design.md`: secrets in the Keychain).
- **When it is checked:** at launch and whenever it is entered. The check is offline: the signature, the
  product, the expiry date.
- **On the network, later:** a periodic, optional check for a revoked licence. It never blocks offline work.

## Feature bits

App Builder becomes one more product on the License Server, `app_builder_fb`. Like Fleet Dispatcher, its
editions are bundles of feature bits. The bits are App Builder's; the server mirrors the table (as it mirrors
Fleet's `docs/LICENSING.md`).

| Bit | Feature | Edition |
|---:|---|---|
| 0 | Studio core: projects from SQLite, model, design, generation, rules, LogicBank for FutureBasic, scenarios, model diagram, sample databases | Lite |
| 1 | AI Assistant with the user's own key (Translate, Suggest Rules, Suggest Controls) | Lite |
| 2 | API Logic Server projects: Open ALS Project, a running server's model | Professional |
| 3 | The Professional runtime in generated apps (ALS client, sign-in, the rules preview) | Professional |
| 4 | Rules exchanged with ALS: `declare_logic.py` import and export, equivalence tests | Professional |
| 5 | Integration and scheduled rules (server events; e.g. the Flight Service filing simulation) | Professional |
| 6 | Authorization rules (row-level security, grants by role) | Professional |
| 7 | Rule governance: versions, sign-off, an audit trail | Professional |
| 8 | AI through the ALS project's `genai-logic`; team prompts and settings | Professional |
| 9 | The web target: App Builder builds the pages for the Web Toolkit (forms, lists, bindings, rules) from the model (author, 2026-11-26: "That's why it's incentive to buy the subscription") | Professional |
| 10–15 | reserved | |

- **Lite is `0x0003`.** **Professional is `0x01FF`** (bits 0-8); with the web target, `0x03FF`. `Licence.incl` already
  treats unknown bits as features it does not offer yet, so a licence carrying bit 9 works today.
- **Trials:** a trial is an Professional licence that expires, as the License Server's 30-day trials already work.
- **The split between editions:** `Editions Design.md` → *Rules: where the line is*; this table is that
  split, in bits.

## In the app

### The gate

- **What replaces `Edition.incl`:** `Licence.incl`. `Edition.incl` is no longer replaced by a different build.
  `Licence.incl` keeps the licence, verified once, and answers `fn LicenceAllows( _featureALSProjects )`.
- **Every Professional command asks it:** menus, buttons, the Open ALS Project view, and generating with the
  Professional runtime.
- **A command the licence does not allow is shown, not hidden.** It carries an "Professional" badge, and choosing
  it opens the Upgrade sheet: what Professional adds, and *Upgrade…*. People see what they could have.
- **Without a valid licence,** App Builder opens on the Licence window. Projects can be opened and read, but
  nothing is generated until a licence is entered.

### The Licence menu

In the App Builder menu, after *About*:

| Item | Does |
|---|---|
| **Licence…** | The licence: account, name, edition, features (each with a tick or "Professional"), licence id, issued, expires |
| **Enter Licence…** | Paste a licence, or open a `.fblicence` file; it is verified and saved to the Keychain |
| **Upgrade to Professional…** | Opens the License Server's upgrade page for this licence (its id and account filled in). After payment, the server sends the Professional licence (a link back into the app, or a file) |
| **Manage Licence Online…** | The account's page on the License Server: renewal, invoices, other Macs |
| **Remove Licence…** | Takes the licence off this Mac (the Keychain item) |

The About box shows the edition and the licensed account.

## Registration and download (on the License Server)

1. **An App Builder landing page** on the License Server (`/appbuilder`, like `/fleet` and `/studio`): what it is,
   Lite and Professional side by side, the samples.
2. **Register:** name, email, company (the existing order form: *Register, Review, Licence*). Lite is free: the
   server's rule `free_licence_only_for_free_product` already governs free licences.
3. **The Lite licence is issued and signed.** The page shows the download link, and the licence by email (the
   text, a `.fblicence` file, and the `appbuilderfb://` link).
4. **First launch:** App Builder asks for the licence; the link or the file fills it in.
5. **Upgrade:** the same order form with payment (Stripe / PayPal, as on the server; decided 2026-11-28: both, the
   buyer chooses, on the providers' own pages; the licence is issued when the provider confirms - the License Server's
   `docs/BACKLOG.md`, *Decided 2026-11-28*). The new Professional licence
   replaces the Lite one, for the same account.

## What changes where

**App Builder (this repository):**
- `Licence.incl` (verify, keep in the Keychain, the gate) and the Licence window, menu and Upgrade sheet.
- The URL scheme and the `.fblicence` document type.
- The public key compiled in.
- Every Professional command gated.

**Repository visibility (the author, on GitHub):**
- **This repository becomes private.** It holds App Builder's source, Professional included; `src/Professional`
  no longer needs a separate private repository.
- **New public repositories** for the modules that stay open: LogicBank for FutureBasic (`AI Assistant
  Design.md`) and the SQL Generator (`src/SQLGeneratorExample`).

**The Imagery License Server:**
- The product `app_builder_fb`, its feature table (`AppBuilderModules.h`, mirroring the table above), and its
  seed rows.
- **Signed licences (ES256)** for App Builder: a key pair, signing on issue, the private key kept on the server
  only. The same signing can later serve other products.
- The `/appbuilder` landing page, the free Lite licence on registration, the download.
- The upgrade page, and the licence delivered back to the app (email, file, `appbuilderfb://` link).

## Tests

- **Here (no Mac):** a reference in Python signs a licence with a test key and checks it, including a tampered
  payload, an expired licence, another product, and a bad signature. The FB `Licence.incl` lints with the
  headers.
- **On a Mac:** a test program verifies the same reference licences with the Security framework, in
  `src/MacTests/`.
- **The gate:** every Professional command, with a Lite licence and with an Professional one.
- **The License Server:** its own tests for signing and for the product's feature table (`ProductCatalogTest`).

## Plan

1. **Here:** the Python reference and test licences; `Licence.incl` (verify with `SecKey…`, Keychain); a Mac test
   program.
2. **Here:** the Licence window and menu, the Upgrade sheet, the gate on every Professional command, the URL scheme
   and document type.
3. **The License Server:** the product, signed licences, `/appbuilder`, registration to download, the upgrade.
4. **The author:** repository visibility; the public module repositories.
