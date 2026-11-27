# Orders: a Web Toolkit for FutureBasic example

Customers, their orders and items on a web page, served by a FutureBasic program behind nginx. Every save goes
through LogicBank for FutureBasic's rules, in FB, on the server:

- an item's amount is quantity x price, less the order's discount;
- an order's total and item count;
- a customer's balance (unshipped orders), which may never go over the credit limit. Try it: the page shows you
  the rule's message.

Totals and balances update without a reload, and Ship Today takes an order off the balance. The Item form saves
itself when you switch tabs (the page lifecycle at work). Open the page in two browsers and they share the data.

## Run it

1. Build `WebToolkitExample.fbeproj` in FutureBasic and run it. Its window tells you it's serving.
2. Install nginx (`brew install nginx`), then in this folder: `nginx -c "$PWD/nginx.conf" -p "$PWD"`.
3. Open http://127.0.0.1:8088/.

The data is kept in memory (`Data Memory.incl`), so every start begins with the same three customers.

## How it's made

The page is laid out in three XIB files, `CustomerPanel.webxib`, `OrderPanel.webxib` and `ItemPanel.webxib`,
which you can edit with the layout tool (`../WebToolkit/Layout Tool/Layout Tool.html`) or Interface Builder.
`Pages.incl` binds them to the data, and `Rules.incl` holds the business rules.

It's built from the toolkit's app template; see the [Web Toolkit](../WebToolkit/README.md) for the toolkit
itself.

MIT License; see `LICENSE`. Copyright (c) 2026 Imagery Business Systems, LLC.
