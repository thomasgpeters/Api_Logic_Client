# Orders - a Web Toolkit for FutureBasic example

Customers, their orders and items on a web page, served by a FutureBasic program behind nginx. Every save goes through
LogicBank for FutureBasic's rules, in FB, on the server:

- an item's amount = quantity x price, less the order's discount;
- an order's total and item count;
- a customer's balance (unshipped orders) - never over the credit limit: try it, and the page shows the rule's message.

Totals and balances follow without a reload. Ship Today takes an order off the balance. The Item form saves itself when
you switch tabs (the page lifecycle). Open the page in two browsers: they share the data.

1. Build `WebToolkitExample.fbeproj` in FutureBasic and run it (its window says it is serving).
2. `brew install nginx`, then in this folder: `nginx -c "$PWD/nginx.conf" -p "$PWD"`.
3. Open http://127.0.0.1:8088/.

The page is laid out in three XIB files - `CustomerPanel.webxib`, `OrderPanel.webxib`, `ItemPanel.webxib` - which
the layout tool (`../WebToolkit/Layout Tool/Layout Tool.html`) or Interface Builder edits; `Pages.incl` binds them.

The data is in memory (`Data Memory.incl`), so every start begins with the same three customers.
Built from `../WebToolkit/Template/`; the toolkit: `../WebToolkit/README.md`. MIT License - see LICENSE.
