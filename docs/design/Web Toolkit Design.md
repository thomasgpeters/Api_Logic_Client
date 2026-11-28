# Web Toolkit for FutureBasic (working name): web applications written in FB, the way Wt does it in C++

Status: **the module is built** (author, 2026-11-26: "Create the widget library for all of the HTML controls, including
the event handlers..."): `src/WebToolkit/` (the core, optional binding, `web.js`, themes), an app template and the Orders
example - lint-clean and tested here, not yet compiled on a Mac. How it works, every call, and the tests:
`docs/features/WEB_TOOLKIT_FEATURE.md`. It began as a feasibility study (`src/MacTests/Web Server Test.fb`,
`FastCGI Test.fb`). Author, 2026-11-26: "create a web
system, a web interface, a website application with FutureBASIC ... similar to Wt and C++". A new module, from scratch:
nothing like it exists for FutureBasic (no web-server example or HTTP library in FutureBasic_Documentation's 578
examples or its headers).

## The purpose: replace Wt, and its licence

The author (2026-11-26): "I'm not trying to bridge to Wt. I'm trying to replace Wt and make a standalone web server
that supports FutureBASIC in the logic side of the web, so we can eliminate the licence."
- **Not a bridge:** no Wt code, library, or process anywhere. Wt is open source under the GPL, or sold under a commercial
  licence; Imagery's web applications would no longer need either.
- **Standalone:** our own HTTP server, sessions, widgets and browser script, written in FB (with a little C for the
  sockets), and nothing else to install. HTTPS too, eventually, through Apple's Network framework (part of macOS, no
  licence), so even nginx or Apache in front becomes optional.
- **Clean-room, as LogicBank for FutureBasic was:** Wt is described below only to explain the idea - how a developer
  writes an app with it. None of its code or its documentation's text is used. Imagery owns everything in the module
  and licenses it as it chooses.
- **The business logic in FB:** the rules (LogicBank for FutureBasic), the queries (the SQL Generator) and the event
  handlers are FB code on the server; the browser only shows the page and sends the clicks.

## The pattern: FastCGI, with a FutureBasic app behind it (author, 2026-11-26)

```
Browser --HTTPS--> nginx (or Apache) --FastCGI--> the FB app (long-running, on a Mac)
                   TLS, HTTP parsing, static        requests in -> widgets -> HTML (or JSON) out;
                   files, limits, compression       the business logic in FB (LogicBank, the SQL Generator)
```

- **nginx does the risky parts:** TLS, HTTP parsing, slow or hostile clients, size limits, static files (CSS, `web.js`,
  pictures), compression. It is free (BSD licence).
- **The FB app answers requests:** method, path, query, cookies and body in; HTML built by the widgets (or JSON for
  event updates) out. It runs in the background (no window), kept running by `launchd`.
- **FastCGI is an open, published protocol:** binary records over a local socket - a few hundred lines of FB (and C) to
  read and write them. No licence.
- **Scale:** nginx can balance several copies of the FB app; sessions then live in SQLite so any copy serves any user.
- **Cocoa:**
  - Foundation (strings, dictionaries, JSON, dates, regular expressions, URLs) is used throughout.
  - AppKit's controls cannot draw themselves as HTML, so the web widgets are our own. Their calls read like FB's Cocoa
    statements (`fn WebButton( page, @"add", @"Add One" )`), so they feel familiar to FB programmers.
- **The proof:** `src/MacTests/Web Server Test.fb` answers HTTP itself, which proves the core (an FB socket server
  answering from FB code). The FastCGI version replaces only that connection layer: nginx in front, FastCGI records
  instead of HTTP text.

## The idea

In Wt, a developer writes only C++: a tree of widgets (`WText`, `WPushButton`, `WLineEdit`, `WTable`), with signals
connected to C++ functions. Wt's server turns the tree into HTML, sends a little JavaScript, and from then on carries
each click to the server and each change back to the page. The developer never writes HTML or JavaScript, and the page
updates without reloading.

The same for FutureBasic: the developer writes FB only - widgets, the functions their events call, property changes -
and the module serves it to any browser.

## What FB already gives us

- **Sockets and dispatch.** BSD sockets in C, through `BeginCFunction` ... `EndC` (C compiled as it is, declared to FB with
  `toolbox fn`). Grand Central Dispatch (`Tlbx Dispatch.incl`) waits for connections and data without blocking. Apple's
  Network framework and `Tlbx CFSocket.incl` are alternatives.
- **Calling FB from C.** An `@fn` pointer called with a C cast: how LogicBank for FutureBasic calls rules. The server
  calls the app's FB handler the same way.
- **One thread.** Everything runs on the main queue - the socket events too - so FB code is never entered from two
  threads (FB, like AppKit, expects the main thread).
- **The rest is FB's daily work:** dictionaries, strings, JSON (`JSONSerialization`), and our own modules for data (the
  SQL Generator) and rules (LogicBank for FutureBasic).

## Architecture

```
 Browser                                         FB process (a Mac)
 -------                                         ------------------
 GET /            ------------------------->     Web Server (C: sockets, HTTP/1.1, GCD on the main queue)
                  <-------------------------       -> Web Session: the cookie's session, or a new one
   the page (HTML + web.js + theme CSS)            -> its Web App: the widget tree, built by the developer's FB
 click            -- POST /event ---------->     Web Events: the widget's event -> the FB function connected to it
   { session, widget, event, value }               (the function changes properties, adds or removes widgets)
                  <-- { updates } -----------     Web Render: the changes since the last reply, as a list of updates
 web.js applies the updates (no reload)
```

| Wt (C++) | Web Toolkit for FutureBasic | File (proposal) |
|---|---|---|
| `WServer`, the HTTP connector | the server: listen, parse requests, answer; static files; sessions by cookie | `Web Server.incl` (FB + C) |
| `WApplication` per session | a session: its id, its widget tree, its own data; ended after an idle time | `Web Session.incl` |
| `WWidget` and its kinds | a widget: a dictionary (kind, id, properties, children); kinds: text, button, line edit, text area, check box, combo box, table, container, image, link, and later a chart and a map | `Web Widgets.incl` |
| signals and slots | `fn WebOn( widgetId, @"clicked", @fn MyClick )`: the event calls the function with the session and the value | `Web Events.incl` |
| incremental rendering | each property change is recorded; the reply to an event carries only what changed | `Web Render.incl` |
| Wt's JavaScript | `web.js`, a small file: sends events, applies updates, keeps the session; no framework needed | `web.js` (resource) |
| themes (Bootstrap) | CSS themes - base, light, dark, colourful - switched by a class on the page; a widget carries only a role (primary, danger), never a colour | `themes/*.css` (resources) |
| `WTemplate` | an HTML template with named places for widgets, for pages a designer lays out | later |
| server push (WebSockets) | at first, replies to events only; later, a WebSocket or long poll for updates the server starts (a timer, another user) | later |

### A page in FB (what the developer writes)

```
void local fn CountClicked( session as WebSessionRef, value as CFStringRef )
long n = fn WebLong( session, @"count", @"value" ) + 1
fn WebSetText( session, @"count", fn StringWithFormat( @"%ld", n ) )
end fn

void local fn BuildPage( session as WebSessionRef )
fn WebText( session, @"title", @"Counter", @"heading" )
fn WebText( session, @"count", @"0", @"" )
fn WebButton( session, @"add", @"Add one", @"primary" )
fn WebOn( session, @"add", @"clicked", @fn CountClicked )
end fn

fn WebServe( 8080, @fn BuildPage )
```

### Requests

- **`GET /`:** the page, with the session's widgets rendered in place. A new session sets its cookie.
- **`GET /web.js`, `/themes/<name>.css`, `/files/...`:** static resources, from the app bundle.
- **`POST /event`:** `{ "widget": "add", "event": "clicked", "value": "" }` is answered by
  `{ "updates": [ { "id": "count", "text": "1" } ] }`. Other update kinds: set a property, add a widget (its HTML) after
  another, remove one, show a message.
- **A JSON API** for the app's own endpoints, if wanted: the same handler.

### Security, from the start

- **Every text is escaped** when it is rendered (HTML entities). Nothing a user types is ever inserted as HTML.
- **Sessions:** a random id (128 bits, `SecRandomCopyBytes`) in an `HttpOnly`, `SameSite=Strict` cookie. Each event must
  carry the session's id as well (against cross-site requests).
- **Limits:** bounded request size and header count; time-outs for slow clients; sessions end when idle.
- **HTTPS:** at first the FB server listens on 127.0.0.1 and a reverse proxy (nginx, Apache or Caddy: free, no licence
  fee) on the public address handles HTTPS with Let's Encrypt certificates. Later the server serves HTTPS itself through
  Apple's Network framework (`nw_listener` with TLS parameters), and the proxy becomes optional: standalone.
- **Logging** is gated on `isLoggingOn` (FB Coding Rules 27).

## Where it runs, and how far it goes

- **A Mac.** FB builds macOS programs, so the server is a Mac (a Mac mini on the author's network fits). As in Wt,
  one process serves every session.
- **Small and medium internal apps,** a few hundred users at most: forms, lists, approvals, dashboards. Not a public
  site with heavy traffic.
- **A Mac and the web from one model.** App Builder could later generate a web front end from the same model and
  rules, beside the Mac app: the same entities, the same LogicBank for FutureBasic rules, the same SQL Generator
  queries - another view on the same domain (the DDD book's layer rule: the UI is replaceable).

## Hosting a Web Toolkit app (author, 2026-11-28: "the new path forward for my apps")

The author's direction after the Mac tests passed (2026-11-28: the Web Server Test, the FastCGI Test, the Orders
example): web apps in FB, served to anyone, hosted on macOS. What is in place and what a first public app still needs,
in the order that unblocks it. Backlog: *Web Toolkit - hosting*.

**In place (the toolkit, 2026-11-26):** every text escaped (proved on the Mac: `<b>Bob</b>` shown as typed); a 128-bit
random session id in an `HttpOnly; SameSite=Strict` cookie, `Secure` when nginx passes `HTTPS=on`; a token every event must carry; a 1 MB request limit and
bounded parameters; idle sessions ended after two hours; nginx in front (TLS, slow clients, static files); the app on
127.0.0.1 only; a LaunchAgent plist in the template (`com.example.webapp.plist`).

1. **The Mac.** FB builds macOS programs, so the host is a Mac:
   - a Mac mini on the author's network (cheapest; the router forwards 443, or a tunnel such as Cloudflare Tunnel
     reaches it with no open port and no fixed address);
   - or a rented Mac in a data centre (MacStadium, AWS EC2 Mac) when the app must not depend on the office.
   Either way: automatic login off, FileVault on, the firewall on, only 80 and 443 reachable (nginx), updates applied.
2. **HTTPS.** nginx with a Let's Encrypt certificate (`certbot`, renewed on a schedule); HTTP redirected to HTTPS; HSTS (the session
   cookie turns `Secure` by itself: the template's `nginx.conf` passes `HTTPS`). The template's `nginx.conf` gets a commented HTTPS server
   block, ready to fill in.
3. **Unattended.** The app as a LaunchDaemon (starts at boot with nobody logged in, restarted when it stops), not the
   template's LaunchAgent (needs a login); nginx as a `brew services` daemon; logs written to files and rotated;
   a health URL (`/health`) for a monitor to call. The app must run with no window: the server window becomes optional.
4. **Sign-in.** Users and passwords (salted, slow hashes: PBKDF2 through CommonCrypto), a sign-in page, the session
   tied to the user, sign-out, and a new session id at sign-in (against session fixation). Roles later, checked on the
   server for every event. Rate limits on sign-in in nginx (`limit_req`).
5. **Hardening.** Response headers from nginx: `Content-Security-Policy` (scripts only from the site: `web.js`),
   `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors 'none'`; limits per address (`limit_req`,
   `limit_conn`); a security review of the toolkit for public use (escaping, the token, the session store, the
   FastCGI parser - the C fuzzed here) before the first public app.
6. **Data.** SQLite behind the rules (`Data Records.incl`, as generated desktop apps), not the example's memory store;
   one writer (the app); backups on a schedule (`sqlite3 .backup` to another disk, kept for a set time) and a restore
   that has been tried.
7. **Deploying a new version.** Build on the development Mac, copy the app, restart the daemon (`launchctl kickstart
   -k`); sessions are in memory, so visitors sign in again - acceptable at first, sessions in SQLite later.
8. **Scale, honestly.** One FB process answers requests one at a time on the main thread: comfortable for small and
   medium apps (a few hundred users, forms and lists). More: several copies behind nginx with sessions in SQLite (the
   backlog has it). A public site with heavy traffic is not the target.

## The plan

1. **Proof (done):** `src/MacTests/Web Server Test.fb`. A single-file program: the C server and an FB handler; a page
   with a counter button and a greeting field, updated without reloading. It answers whether FB can serve a page and
   take a click - and how it behaves (Safari and Chrome, several tabs, many clicks).
2. **The server:** `Web Server.incl`, with requests and responses as dictionaries, static files, cookies, limits, and
   its own tests.
3. **Widgets, sessions, events, rendering, `web.js`, themes (built, 2026-11-26):** the core, with an example app (the counter, a form, a
   table from SQLite through the SQL Generator).
4. **The module:** a README, a user guide, an example, MIT (author's call); the About Imagery window; a page on the site.
5. **Later:** templates, server push, charts and maps; App Builder generating web pages.

## Decisions (author, 2026-11-26, while the module was built)

- **AJAX:** every widget is asynchronous; events go to FB with `fetch`, and the answers change the page in place.
- **A page lifecycle** (shown, hidden, visible, leaving, ended), so work is saved back to FB and the database, and the
  page behaves as people expect: unsaved changes are guarded, and auto-saving forms save themselves.
- **An app template** for the FB side: the events in and out of FastCGI, so an app is one file, `Pages.incl`.
- **Dynamic, tied to no data model:** the core knows no entity; binding to a model is an optional module. App Builder
  will offer two targets, **Desktop app** and **Web app**, both compiled by FutureBasic: one model, one set of rules,
  two event models (FB's own `on dialog`, and FastCGI events).
- **XIB files as page templates, and a layout tool** (built): one layout, made in Interface Builder or the layout tool,
  serves both targets (`WEB_TOOLKIT_FEATURE.md` -> XIB layouts and the layout tool).

## Open questions (for the author)

- **The name:** "Web Toolkit for FutureBasic" is a working name.
- ~~Free and open, or licensed?~~ **Decided (author, 2026-11-26): free, MIT, the third free module.** App Builder
  automating the pages is what is sold (`Free Modules Design.md`, `Licensing Design.md` -> Pricing).
- **The first real app to build with it:** something internal on the author's network, to drive the widget list.
