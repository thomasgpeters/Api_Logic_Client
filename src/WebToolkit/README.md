# Web Toolkit for FutureBasic (working name)

Web applications written in FutureBasic. You write FB (the widgets, and the functions their events call) and
the toolkit serves the page to any browser. The page behaves the way you'd expect a modern page to: each click
goes to your FB code in the background (AJAX), only what changed comes back, and nothing reloads. Your business
logic runs in FB on the server, whether that's LogicBank for FutureBasic's rules, the SQL Generator's queries
or your own code.

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

To start, copy `Template/` (an FB project), write your page in `Pages.incl`, build, and start nginx with
`Template/nginx.conf`. The example in `../WebToolkitExample/` keeps orders, with business rules.

You can also lay a page out in a XIB with `Layout Tool/Layout Tool.html` (or Interface Builder), save it as
`.webxib`, add it to Resources, and load it with `fn WebLoadLayout( session, @"page", @"MyLayout" )`. The full
reference is `docs/features/WEB_TOOLKIT_FEATURE.md`.

The core is `Web Server.incl`, `Web Session.incl`, `Web Widgets.incl`, `Web Render.incl`, `Web Events.incl` and
`Web Layout.incl`, and it knows nothing about your data model. `Web Binding.incl` is optional and binds forms
and tables through LogicBank for FutureBasic. The browser's side is `Resources/web.js` and `Resources/web.css`.

It runs on macOS (FutureBasic builds Mac programs), with nginx (free) in front. MIT License; see LICENSE.
Copyright (c) 2026 Imagery Business Systems, LLC.
