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
- **Association**: a named, directed link between two parts of a page, or from a part to another page, riding on a
  relationship of the model, with its cardinality (below). A part's *follows* and a page's *links* are associations.
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
| A join table between them (EmployeeTerritories: Employees and Territories; Order Details: Orders and Products) | after every direct one: B **through** the join table | B shows the rows joined to the current A |
| None | *Not linked* | B has its own navigator-free list or detail |

The first part dropped is the page's **driver**: its record comes from the navigator (and the search). A part that
follows another changes when that part's current record changes, down the chain: Order -> its Customer, its lines;
a line chosen -> its Product.

The author's "parameter to set the current record in focus": a Detail part's record comes from one of
- the navigator (the driver),
- the part it follows (a parent, or the row chosen in a List of the same entity),
- *(later)* a fixed filter (a status, the signed-in user), or a value passed from another page (drill-in).

## Associations: named, directed, with a cardinality

Author, 2026-11-27: "a proper association object within the system that understands the relationship and the direction
of the relationship, so one to many, many to many, one-to-one", with a name.

| Cardinality | From the current record of the source, the target shows | Comes from |
|---|---|---|
| one to many (1 : n) | its children (a customer's orders) | the target holds the foreign key |
| many to one (n : 1) | its parent (an order's customer) | the source holds the foreign key |
| one to one (1 : 1) | the same record; or the child whose foreign key is its whole primary key | the same entity, or such a key |
| many to many (n : n) | the rows joined to it (an employee's territories; the orders that include a product) | a join table: two foreign keys that are, together, its primary key |

Every association has a **name**, proposed and the developer's to change: *Customers to Orders*, *Orders to Shippers
(ShipVia)* when the foreign key plays a role, *Employees to Territories (through EmployeeTerritories)*, *Orders, the
same record*. Its **direction** is from the part or page it starts at to the one that receives the record. In
`Pages.json` an association is `{ name, how, cardinality, relationship, fks, parentKeys, through }`, plus `part` (on a
part: the part it follows) or `fromPart` and `page` (on a page: the link to another page).

## Links between pages (drill-in)

Author, 2026-11-27: "we need to be able to drag and drop a relationship or an association between pages; first thing
that'll happen is it'll show you the relationship between the two pages based on relationships of the entities on
those pages."

- **In the designer:** drag a page in the Pages list onto another. A sheet lists the relationships between the two
  pages (`page_associations`): from each part of the first page to the second page's driver (the part that receives
  the record), the proposed one first, each in words - *"Customers -> Orders: the customer's orders"*, *"Order
  Entry (its order) -> Customers: the order's customer"*, *"Order Entry (its Customers part) -> Customers: the same
  customer"*. Choose one, name it (the proposed name, the developer's to change), and it is saved as one of the
  first page's `links`, an association with its cardinality. Nothing in common: the sheet says so and nothing is
  saved. A page can have several links; they are listed, and removed, on the page in the designer.
- **In the generated app:** the part a link starts from has a *Go to* button in its card's title row (several links:
  a menu), labelled with the association's name. It opens the other page for the part's current record: its driver shows
  that record's children (Customers -> Orders: VINET's orders, the navigator over them, "Order 1 of 1"), its parent
  (Orders -> Customers: the order's customer), or the same record. The crumb trail at the top shows where you came
  from (*Customers / VINET / Orders*) and goes back; the header's Back button too. The other page opened from its
  navigation-bar button shows all its records, as before.
- In `Pages.json`: `links: [ { name, page, fromPart, how, cardinality, relationship, fks, parentKeys, through } ]` on the
  page they start from (the format in `tools/pages_reference.py`).

Tested (`tools/pages_reference.py`): Customers -> Orders (VINET: 10248), Orders -> Customers (10249: Toms
Spezialitäten), Order Entry -> Customers (from the order, and the same record from its Customers part), Order Entry
-> Products (the line chosen, and its Products part), Products -> Order Entry and Categories -> Orders (nothing in
common), Categories -> Products; the check reports a link to a missing page, to its own page, or along a
relationship that does not exist.

## The page flow diagram

Author, 2026-11-27: "the developer should be able to select Show Page Flow Diagram and they should see the
application's logical flow between the pages": page names, relationships, associations.

- **Model > Show Page Flow Diagram** (beside Show Model Diagram; Professional): writes `<project>/Page Flow.svg` from
  `Pages.json` and opens it, as the model diagram opens.
- **What it shows:** each page a card (its title, then its parts: entity, display, and what each follows with its
  cardinality: *Customers Detail · n : 1 from Orders*); an arrow for each link between pages, from the part it starts
  at to the page it opens, labelled with the association's name and cardinality. Pages in columns by how far they
  are from the first page along the links; a link back to an earlier page runs in its own lane under the cards. Light
  and dark mode follow the viewer.
- The example (Northwind: Customers, Orders, the invoice page, Products): `Page Flow Example.svg`, drawn by
  `python3 tools/pages_reference.py --flow-example`; any project's by `--flow <project>/Pages.json`. The reference
  is `page_flow_svg`; the Studio's is its FB port (an SVG is text: FB writes it as the ERD generator writes its page).

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
   offered both ways; associations with their names and cardinalities, many to many through join tables; links
   between pages; the page flow diagram.
2. The designer in Studio for FB (Cocoa drag and drop: the palette as a drag source, the page as a drop target;
   the sheet on drop; a page dragged onto another, the sheet of their associations; Show Page Flow Diagram). The
   associations, the links between pages and the diagram are in phase 1's reference already.
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
6. Associations are first-class: named, directed, one to many / many to one / one to one / many to many.
7. Show Page Flow Diagram: an SVG of the pages and the associations between them.
