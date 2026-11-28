# Draft post for the FutureBasic list

Plain text, no attachments: everything is on the web page the post links to (the list's storage fills up).
Written in the author's own style: short, direct, the point first. Not in the download (`tools/make_site.py` skips it).

---

**Subject:** Web apps in FutureBasic

Hi all,

I've been building web apps in FutureBasic. Not a web view in a Mac app: a real web app, served to
any browser, with the page written in FB and every click answered by FB code on the server.

A page is a few lines:

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

Click Greet and the message changes in place: the click goes to GreetClicked in the background and only
what changed comes back. The page never reloads.

How it runs: nginx (free) talks to the browsers, and passes each request to your FB app over FastCGI.
nginx handles HTTPS and the rest of the internet; your app just answers requests. It runs on a Mac.

In the download:
- the toolkit (a handful of .incl files) and an app template to copy;
- an example: customers, orders and items, where every save runs business rules in FB (totals,
  balances, a credit limit that refuses an order);
- a layout tool, so you can lay a page out visually (or in Interface Builder) instead of in code.

It's early, and the name is a working name. Tried on my Mac in Safari and Chrome. I'd like to hear what
you would build with it, and what widgets you'd want next.

Everything is here, no attachments: [link]

Free, MIT licence. Questions welcome.

[your name]
