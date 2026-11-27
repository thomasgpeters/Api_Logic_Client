# Page Designer Design: pages built from entities, linked by their relationships

Author, 2026-11-27: "we want to be able to create a page and drop an entity on that page that will ask us: do we want a
list or a scalar ... if there is another object already on the page then use the relationship to link the two, so that
it's similar to an invoice app for example: multiple object types on one page."

Today App Builder generates one page per entity: its List above its Form. The page designer lets the developer
compose pages from several entities, the way a real application is laid out: an Order with its customer and its lines
on one page, an Employee with the orders they took.

**Professional edition only** (author, 2026-11-27). The Lite edition keeps one page per entity (List with detail);
it ignores a project's `Pages.json`. In the Studio the Pages view is behind `LicenceGate`, as API Logic Server
projects are.

Status: phase 1 built (`tools/pages_reference.py`: the `Pages.json` format, the links, a page resolved); the rest
designed. The author accepted the proposals below (2026-11-27): the names Detail, List, List with detail; the
toolbar on the part with the focus; the same entity twice on a page later; the Web Toolkit to share `Pages.json` later.

## Words

- **Page**: a navigation-bar item of the generated app. It has a title, an icon and its parts, top to bottom.
- **Part**: one entity on a page, shown one of three ways:
  - **Detail** (the author's "scalar"): one record in a Form;
  - **List**: many records in a grid (with the tiles switch, as now);
  - **List with detail**: a List and, below it, the Form of the row chosen (today's page, as one part).
- **Link**: how a part's records follow another part on the page, from the model's relationships.
- **Driver**: the part whose current record the others follow. The record navigator moves the driver.

## The designer (Studio for FB)

A new view, **Pages**, beside Entity Definitions (toolbar and Project menu):

```
┌ Pages ─────────┐ ┌ Entities ──┐ ┌ Order Entry ─────────────────────────────────────────┐
│ Customers      │ │ Category   │ │ ┌ Order ─ Detail ─ driver ───────────────────────┐  │
│ Order Entry  ◀ │ │ Customer   │ │ │ the navigator moves it                         │  │
│ Products       │ │ Employee   │ │ └────────────────────────────────────────────────┘  │
│                │ │ Order      │ │ ┌ Customer ─ Detail ─ the Order's Customer ───────┐  │
│ [+] [-]        │ │ OrderDetail│ │ └────────────────────────────────────────────────┘  │
└────────────────┘ │ Product    │ │ ┌ OrderDetail ─ List ─ the Order's lines ─────────┐  │
                   └────────────┘ │ └────────────────────────────────────────────────┘  │
                                  └──────────────────────────────────────────────────────┘
```

- **Pages** list: add, remove, rename, reorder (drag); each page's icon (the SF Symbol picker the entities use).
- **Entities** palette: the model's entities; drag one onto the page.
- **The page**: its parts, top to bottom, drag to reorder; each part a card with its entity, its display
  (Detail / List / List with detail) and its link, all changeable after the drop.
- **On drop**, a small sheet asks the display: *List*, *Detail* or *List with detail*; and, when the page already has
  parts, the link it proposes (below), which the developer can change or set to *Not linked*.
- Saved in the project as `Pages.json`; the model diagram is unaffected.
- With no `Pages.json`, App Builder proposes today's pages: one per entity, List with detail. *Start from the
  model's pages* fills the designer with them, to edit.

## Links, from the relationships

`SQLite Model.incl` (and the ALS model) already gives each entity its relationships: `toone` on the child (its
foreign key: `fks`) and `tomany` on the parent (`parentKeys`). When entity B is dropped on a page holding A:

| The model says | The link proposed | At run time |
|---|---|---|
| B has a foreign key to A (B is A's child: OrderDetail -> Order) | B **follows** A: B's records are A's children | B shows the rows whose `fks` equal the current A's `parentKeys`; a new B gets them filled in |
| A has a foreign key to B (B is A's parent: Order -> Customer) | B **follows** A: B is A's parent | B (Detail) shows the parent of the current A |
| Several relationships (Order -> Employee twice: taken by, approved by) | the first, with a choice | the sheet lists them by name (`toone` / `tomany` names) |
| None directly, but through a part already linked | linked to that part instead | |
| None | *Not linked* | B has its own navigator-free list or detail |

The first part dropped is the page's **driver**: its record comes from the navigator (and the search). A part that
follows another changes when that part's current record changes, down the chain: Order -> its Customer, its lines;
a line chosen -> its Product.

The author's "parameter to set the current record in focus": a Detail part's record comes from one of
- the navigator (the driver),
- the part it follows (a parent, or the row chosen in a List of the same entity),
- *(later)* a fixed filter (a status, the signed-in user), or a value passed from another page (drill-in).

## Links between pages (drill-in)

Author, 2026-11-27: "we need to be able to drag and drop a relationship or an association between pages; first thing
that'll happen is it'll show you the relationship between the two pages based on relationships of the entities on
those pages."

- **In the designer:** drag a page in the Pages list onto another. A sheet lists the relationships between the two
  pages (`page_associations`): from each part of the first page to the second page's driver (the part that receives
  the record), the proposed one first, each in words - *"Customers -> Orders: the customer's orders"*, *"Order
  Entry (its order) -> Customers: the order's customer"*, *"Order Entry (its Customers part) -> Customers: the same
  customer"*. Choose one, give it a label (proposed: the other page's title, or the relationship's name for a
  parent), and it is saved as one of the first page's `links`. Nothing in common: the sheet says so and nothing is
  saved. A page can have several links; they are listed, and removed, on the page in the designer.
- **In the generated app:** the part a link starts from has a *Go to* button in its card's title row (several links:
  a menu), labelled with the link's label. It opens the other page for the part's current record: its driver shows
  that record's children (Customers -> Orders: VINET's orders, the navigator over them, "Order 1 of 1"), its parent
  (Orders -> Customers: the order's customer), or the same record. The crumb trail at the top shows where you came
  from (*Customers / VINET / Orders*) and goes back; the header's Back button too. The other page opened from its
  navigation-bar button shows all its records, as before.
- In `Pages.json`: `links: [ { page, fromPart, how, relationship, fks, parentKeys, label } ]` on the page they start
  from (the format in `tools/pages_reference.py`).

Tested (`tools/pages_reference.py`): Customers -> Orders (VINET: 10248), Orders -> Customers (10249: Toms
Spezialitäten), Order Entry -> Customers (from the order, and the same record from its Customers part), Order Entry
-> Products (the line chosen, and its Products part), Products -> Order Entry and Categories -> Orders (nothing in
common), Categories -> Products; the check reports a link to a missing page, to its own page, or along a
relationship that does not exist.

## The invoice, as an example

Page *Order Entry*: Order (Detail, driver) / Customer (Detail, follows Order as its parent, read-only) / OrderDetail
(List, follows Order as its children) / Product (Detail, follows the OrderDetail row chosen, read-only). The
navigator walks the orders; each order brings its customer and its lines; choosing a line shows its product. New on
OrderDetail adds a line to the current order (its OrderId filled in); the rules recompute the order's total.

## What the generated app needs

1. **The same entity on several pages.** A XIB part's controls have fixed tags, and tags must be unique in a window,
   so a part is generated per page: `<Page>_<Entity>Form.xib` with its own tag base, and the binding takes the base
   (`<Entity>RecordToForm( aRecord, tagBase )`) instead of fixed tag constants. This is the largest change: the XIB
   generator, the binding generator, Model Tags (one block per part) and App Pages.
2. **Parts stacked on a page**, each in its card, the heights shared (a Detail its natural height, Lists the rest).
3. **Linking at run time** (`App Pages.incl`, generated from `Pages.json`): when a part's current record changes, the
   parts that follow it are filled: children with `AppDataList` filtered by the foreign key (the data runtime's
   `DataChildren`), a parent with `DataParent`. In the Professional edition the same through ALS (`filter[...]`).
4. **The toolbar acts on the part with the focus** *(confirm)*: New, Save, Delete on the part last clicked;
   the navigator always on the driver.
5. **Save on a page of several parts** *(confirm)*: Save saves the part with the focus; a change left in another
   part is kept and its Save comes on when it gets the focus.

## Phases

1. **Done:** `Pages.json` and the link rules, with a Python reference (`tools/pages_reference.py`, the format in its
   header) tested on a Northwind fixture (`tools/fixtures/northwind.sql`: the classic schema and foreign keys, a few
   rows) and the three samples: the invoice page built from drops and resolved for an order; every relationship
   offered both ways.
2. The designer in Studio for FB (Cocoa drag and drop: the palette as a drag source, the page as a drop target;
   the sheet on drop; a page dragged onto another, the sheet of their relationships). The links between pages are in
   phase 1's reference already.
3. Parts with a tag base (XIB and binding generators); today's pages regenerated the same way, so nothing changes
   for a project without `Pages.json`.
4. The generated app: pages of parts, linking, the focus; the links between pages (Go to, the crumb trail, Back).
5. The invoice example on Northwind (Order Entry) as a test scenario; then the samples (Customs: an entry with its
   lines and its fees).

## Decided (author, 2026-11-27)

1. Display names: Detail, List, List with detail.
2. New, Save and Delete act on the part with the focus; the navigator on the driver.
3. The same entity twice on a page (an employee and their manager): later.
4. The Web Toolkit shares `Pages.json`: later.
5. Professional edition only.
