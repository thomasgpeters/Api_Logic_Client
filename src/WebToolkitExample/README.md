# Orders: a Web Toolkit for FutureBasic example

Customers, their orders and items on a web page, served by a FutureBasic program behind nginx. Every save goes
through LogicBank for FutureBasic's rules, in FB, on the server:

- an item's amount = quantity x price, less the order's discount;
- an order's total and item count;
- a customer's balance (unshipped orders), which may never go over the credit limit. Try it, and the page shows
  you the rule's message.

Totals and balances follow along without a reload, and Ship Today takes an order off the balance. The Item form
saves itself when you switch tabs (that's the page lifecycle at work). If you open the page in two browsers,
they share the data.

1. Build `WebToolkitExample.fbeproj` in FutureBasic and run it (its window tells you it's serving).
2. `brew install nginx`, then in this folder: `nginx -c "$PWD/nginx.conf" -p "$PWD"`.
3. Open http://127.0.0.1:8088/.

The page is laid out in three XIB files, `CustomerPanel.webxib`, `OrderPanel.webxib` and `ItemPanel.webxib`,
which you can edit with the layout tool (`../WebToolkit/Layout Tool/Layout Tool.html`) or Interface Builder.
`Pages.incl` binds them.

The data is kept in memory (`Data Memory.incl`), so every start begins with the same three customers.
It's built from `../WebToolkit/Template/`, and the toolkit's own README is `../WebToolkit/README.md`.
MIT License; see LICENSE.
