# Web Toolkit for FutureBasic (working name): web applications written in FB, the way Wt does it in C++

Status: **a feasibility study** (author, 2026-11-26: "just a feasibility question at this point"); the question is
answered on a Mac by `src/MacTests/Web Server Test.fb`. Nothing beyond the test is planned until the author decides. Author, 2026-11-26: "create a web
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

## The plan

1. **Proof (now):** `src/MacTests/Web Server Test.fb`. A single-file program: the C server and an FB handler; a page
   with a counter button and a greeting field, updated without reloading. It answers whether FB can serve a page and
   take a click - and how it behaves (Safari and Chrome, several tabs, many clicks).
2. **The server:** `Web Server.incl`, with requests and responses as dictionaries, static files, cookies, limits, and
   its own tests.
3. **Widgets, sessions, events, rendering, `web.js`, themes:** the core, with an example app (the counter, a form, a
   table from SQLite through the SQL Generator).
4. **The module:** a README, a user guide, an example, MIT (author's call); the About Imagery window; a page on the site.
5. **Later:** templates, server push, charts and maps; App Builder generating web pages.

## Open questions (for the author)

- **The name:** "Web Toolkit for FutureBasic" is a working name.
- **Free and open (like the other two modules), or Imagery's own, licensed product?** Owning it outright is the
  point of replacing Wt; how it is shared is a separate choice.
- **The first real app to build with it:** something internal on the author's network, to drive the widget list.
