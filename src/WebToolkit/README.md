# Web Toolkit for FutureBasic (working name)

Web applications written in FutureBasic. You write FB (the widgets, and the functions their events call) and
the toolkit serves the page to any browser. Each click goes to your FB code in the background (AJAX), only what
changed comes back, and the page never reloads. Your business logic runs in FB on the server: LogicBank for
FutureBasic's rules, the SQL Generator's queries, or your own code.

```
Browser --HTTPS--> nginx --FastCGI--> your FB app (Web Toolkit)
```

A page is a few lines of FB:

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

## Getting started

1. Copy `Template/` (a FutureBasic project) and write your page in its `Pages.incl`.
2. Build and run it.
3. Start nginx with the template's `nginx.conf`, and open the page in a browser.

`Template/README.md` has the details. For a complete app, see the
[Orders example](../WebToolkitExample/README.md): customers, orders and items, with business rules.

## Pages laid out in XIB files

You can also lay a page out visually: open `Layout Tool/Layout Tool.html` in Safari (or use Interface
Builder), save the layout as a `.webxib` file, add it to the project's resources, and load it with
`fn WebLoadLayout( session, @"page", @"MyLayout" )`.

## What's in this folder

| | |
|---|---|
| `Web Server.incl`, `Web Session.incl`, `Web Widgets.incl`, `Web Render.incl`, `Web Events.incl`, `Web Layout.incl` | the core: it knows nothing about your data model |
| `Web Binding.incl` | optional: binds forms and tables through LogicBank for FutureBasic |
| `Resources/web.js`, `Resources/web.css` | the browser's side |
| `Template/` | the app template |
| `Layout Tool/` | the layout tool |
| `User Guide.txt` | the user guide |

The full reference is `docs/features/WEB_TOOLKIT_FEATURE.md` in the App Builder repository.

It runs on macOS (FutureBasic builds Mac programs), with nginx (free) in front. MIT License; see `LICENSE`.
Copyright (c) 2026 Imagery Business Systems, LLC.
