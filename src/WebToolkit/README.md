# Web Toolkit for FutureBasic (working name)

Web applications written in FutureBasic: you write FB - widgets, and the functions their events call - and the toolkit
serves the page to any browser. The page behaves as any modern page: each click goes to your FB code asynchronously
(AJAX), and only what changed comes back, with no reloads. The business logic runs in FB on the server:
LogicBank for FutureBasic's rules, the SQL Generator's queries, your own code.

```
Browser --HTTPS--> nginx --FastCGI--> your FB app (Web Toolkit)
```

```
void local fn GreetClicked( session as WebSessionRef, widgetId as CFStringRef, eventValue as CFStringRef )
fn WebSetMessage( session, @"greeting", fn StringWithFormat( @"Hello, %@", fn WebValue( session, @"visitorName" ) ), @"success" )
end fn

void local fn BuildPage( session as WebSessionRef )
fn WebField( session, @"page", @"visitorName", @"Your name", @"text", @"" )
fn WebButton( session, @"page", @"greet", @"Greet", @"primary" )
fn WebMessage( session, @"page", @"greeting", @"", @"info" )
fn WebOn( session, @"greet", @"clicked", @fn GreetClicked )
end fn
```

- **Start here:** copy `Template/` (an FB project), write your page in `Pages.incl`, build, start nginx with
  `Template/nginx.conf`.
- **The example:** `../WebToolkitExample/` (orders, with business rules).
- **Layouts:** lay a page out in a XIB with `Layout Tool/Layout Tool.html` (or Interface Builder), save it as
  `.webxib`, add it to Resources, and `fn WebLoadLayout( session, @"page", @"MyLayout" )`.
- **The reference:** `docs/features/WEB_TOOLKIT_FEATURE.md`.

Files: `Web Server.incl`, `Web Session.incl`, `Web Widgets.incl`, `Web Render.incl`, `Web Events.incl`, `Web Layout.incl` (the core,
which knows no data model), `Web Binding.incl` (optional: forms and tables through LogicBank for FutureBasic), and
`Resources/web.js`, `Resources/web.css`.

macOS (FutureBasic builds Mac programs); nginx (free) in front. MIT License - see LICENSE.
Copyright (c) 2026 Imagery Business Systems, LLC.
