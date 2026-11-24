# Editions and Licensing

The Studio generates a business app in one of two editions. **Lite ships first**; Enterprise is
on the roadmap (author, 2026-11-24: "I want to get the free, SQLite edition out the door first,
then we can roadmap the paid edition for future").

| | Lite | Enterprise |
|---|---|---|
| Price | free | paid |
| Source | open source (this repository, public) | private repository, paid build only |
| Tiers | two: the app and its SQLite database | three: the app, an API Logic Server, the database |
| Data | `App Data Lite.incl`: the app opens the database itself (`Data Records.incl`) | `App Data Enterprise.incl`: JSON:API calls to the server (`ALS Client.incl`) |
| Business rules | in the app: LogicBank for FutureBasic, `Studio Rules.incl` + `Rules.incl` | on the server: LogicBank in ALS, `declare_logic.py` exported by the Studio |
| Sign-in | none (the database is on this Mac) | the header's Log In: the server's JWT login |
| Status | building now | roadmap |

API Logic Server is open source and the same for everyone, in either edition (author). What
Enterprise sells is the Studio's three-tier generation and its client runtime, not the server.

## One app, two data layers

Everything a user sees is the same in both editions: the shell, the pages, the XIBs, the
bindings, the model diagram. Only the data layer differs, behind one interface (the
application layer of `App Shell Design.md`, book §5.3: the infrastructure is replaced, the UI
survives):

```
App Pages.incl  ──  AppDataList / AppDataSave / AppDataRemove / AppDataLogin / AppDataKeyValues
                         │                                   answers in AppDataDone( op, entity, result, message )
          ┌──────────────┴───────────────┐
  App Data Lite.incl              App Data Enterprise.incl  (private)
  Data Records + Logic Engine      ALS Client (URLSession, asynchronous)
  SQLite on this Mac               API Logic Server → database
```

The interface answers through a handler rather than a return value because the server's replies
come back later (URLSession). Lite answers at once, through the same handler, so the pages need
no edition test.

## How the code is split

| Where | What |
|---|---|
| This repository (public) | the Studio; `src/Generator/Edition.incl`, the **Lite-only** edition hook; the runtime for Lite (`App Data Lite.incl`, the data runtime, the rules engine, the shell) |
| Private repository (to create) | its own `Edition.incl` (offers Enterprise when the licence allows, adds its runtime files and start-up), `App Data Enterprise.incl`, its sign-in window, the `declare_logic.py` export step, and the paid build's project file |

The paid build is the same Studio with one file replaced: its project lists the private
`Edition.incl` in place of this one. The hook's functions:

| Function | Lite (this repository) |
|---|---|
| `EditionEnterpriseAvailable` | `NO` |
| `EditionOfProject( projectDict )` | `Project.json` `"edition"`, Lite unless Enterprise is available |
| `EditionDescription( edition )` | the words the README and main program use |
| `EditionDataRuntimeFiles( edition )` | the data runtime, the rules engine, `App Data Lite.incl` |
| `EditionMainStart( edition, host, user )` | `DataOpen`, `DeclareStudioRules`, `DeclareRules`, `LogicActivate` |
| `EditionRulesInApp( edition )` | `YES` |
| `EditionRefusal( edition, hasDatabase )` | refuses an app for a model read from an API Logic Server: that app is Enterprise. Open the server's SQLite database instead for a Lite app |

The existing `ALS Client.incl`, `ALS Binding.incl` and `ALS App.incl` in `src/Runtime/` are no
longer copied into generated apps. They are the starting point of the Enterprise runtime and move
to the private repository when it exists. They are already public in this repository's history,
which is acceptable: they are a thin JSON:API client for an open-source server.

## Licensing (decision for later)

Decided (author, 2026-11-24): the Studio checks the licence **offline** (it never calls the
License Server, consistent with "no Imagery application is a dependency"), and the licence gates
**the Studio only**: apps already generated never stop working.

Still open: **how** the Studio knows a licence is real. What the License Server issues today
(`Imagery-License-Server` README, `TokenGenerator`):

- a key `XXXX-XXXX-MMMM-XXXX-XXXX`: site, product, module bitmask, random part, checksum;
- the checksum is C++ `std::hash` of the other parts plus a salt that is published in the README.

Two things stop the Studio from using it as it is. First, `std::hash` is not the same on Linux
and on a Mac (libstdc++ and libc++ differ), so FutureBasic cannot recompute it. Second, anyone
who reads the salt can make a valid key. There is also no product entry for the FB Studio yet;
the existing `imagery_logicbank_studio` product "is free and never checks a licence".

The choices, in plain terms:

| Option | How it works | Trade-off |
|---|---|---|
| **A. The key as it is, with a portable checksum** | The License Server computes the checksum with SHA-256 (the same on every machine) instead of `std::hash`. The Studio recomputes it. | A small change on the License Server. Anyone who reads the Studio's code or the README can still make a key: it keeps honest people honest. |
| **B. A signed licence file** | Besides the key, the License Server issues a small file (who, which product, Enterprise, expiry) and *signs* it with a private key that never leaves the server. The Studio holds only the matching public key: it can check a signature but cannot make one, so nobody can forge a licence without the server's private key. macOS checks such signatures natively (`SecKeyVerifySignature`, in FB's Security headers). | A new feature on the License Server (key pair, signing, a file to download). The strongest offline option. |
| **C. Online activation** | The Studio sends the key to the License Server, which says yes or no. | Simple to reason about; makes the License Server a run-time dependency, which the no-dependency rule forbids. |

A signature works like a notary's seal: anyone can check it, only the notary can make it.
Option A is enough for a first paid release if forgery is not a worry; B can follow without
changing what users do (they still enter the key; the file comes with it).

Whichever is chosen, the License Server needs a product for the FB Studio (proposal:
`imagery_logicbank_studio_fb`, bit 0 `enterprise`) and the Studio needs a "Licence…" entry in
Project Settings or Preferences. Both belong to the Enterprise work.

## Roadmap (Enterprise)

1. Choose the licence option (A, B or C above) — author.
2. Create the private repository; move the ALS runtime there.
3. `App Data Enterprise.incl`: list / save / remove / login over JSON:API, one request context
   per call (URLSession `userData`), answers on the main thread (`dispatchmain`).
4. Sign-in window; token kept for the session; the Keychain for a remembered password.
5. Generate App (Enterprise): export the project's rules to `declare_logic.py` for the server.
6. License Server: the FB Studio product and the chosen licence format.
7. The paid build: project file, release, distribution from the License Server.
