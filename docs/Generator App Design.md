# Generator App — Design

The generator itself (this repo's `Generator/` project; product name to be
decided) is a **macOS-only** FutureBasic app. The generated apps are described
in `App Shell Design.md`.

## Where things live

The app bundle is immutable: nothing is ever written inside `<App>.app`.

| What | Where | Notes |
|---|---|---|
| Runtime templates, XIB templates | inside the app bundle (`Contents/Resources`) | read-only, versioned with the app |
| Settings | `~/Library/Application Support/<App>/Settings.plist` | non-secret configuration (below) |
| Secrets | macOS **Keychain** (`Security/SecItem.incl`) | API keys, tokens, passwords — never in a file |
| Logs, caches | `~/Library/Application Support/<App>/Logs`, `Caches` | safe to delete |
| **Workspace** | a folder the user chooses (default `~/Documents/<App> Workspace`) | all projects the user works on |

Today the generator writes to `~/ApiLogicClient/<project>/`; that becomes the workspace.

### Workspace layout

```
<Workspace>/
├── <Project>/                 one generated app = one git repository
│   ├── <Project>.fb           generated (regenerated)
│   ├── Model.json, *.xib, …   generated (regenerated)
│   ├── <Entity> Hooks.incl    hand-edited, created only if missing
│   ├── Database/              the SQLite file (lite edition) and schema
│   └── .git/
└── …
```

## Settings (Application Support)

Non-secret values in `Settings.plist`; each secret is a Keychain item the
plist refers to by name.

| Group | Settings | Secret (Keychain) |
|---|---|---|
| Workspace | folder path, recent projects | — |
| Git | user name, email, default branch, remotes per project | — |
| GitHub | account, default owner/organization, visibility for new repos | personal access token |
| Generic Git | remote URL, auth method (HTTPS / SSH key path) | HTTPS password or token |
| ALS / APIs | server URL per project, login path | password / token |
| AI / LLMs | provider, endpoint, model name | API key |
| Email (notifications) | SMTP host, port, TLS, sender address | SMTP password |

New services follow the same pattern: one settings group, secrets in the Keychain.
A Settings window edits all groups; secrets are written to and read from the
Keychain only, never shown in full after entry.

## Git and GitHub

- **Git operations** run the system `git` (`/usr/bin/git`, from the Xcode command
  line tools) through `Task.incl` (NSTask) inside the project folder: init,
  status, add, commit, branch, fetch, pull, push. Output is captured and shown.
- **Generic Git**: any remote URL (HTTPS or SSH). HTTPS credentials come from the
  Keychain; SSH uses the user's existing keys.
- **GitHub**: the REST API over `URLSession` with the Keychain token — create a
  repository, list repositories, open a pull request. Pushing and pulling go
  through `git` like any other remote.
- Generating a project can optionally `git init` it and commit the generated
  files, so every regeneration is a reviewable diff.

## Open questions

- Product name (and therefore the Application Support folder and bundle id).
- Minimum macOS version.
- Whether the workspace can hold non-generated FB projects (e.g. Test_Xib_View).
