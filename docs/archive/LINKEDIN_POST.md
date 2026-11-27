# LinkedIn post — App Builder for FutureBasic

Attach `DOC_ONE_PAGER.pdf`, or a screenshot of the one-pager's masthead and big picture.

---

**Introducing App Builder for FutureBasic**

Point it at a database. Get a native Mac app in FutureBasic, with its screens, its data access and its business rules written for you, in code you can read and keep.

The Studio reads a data model (a SQLite database, or an API Logic Server project) and generates a complete FutureBasic project:

🖥 A List and a Form for every entity, as XIBs you can open in Xcode
🎨 A common look: navigation bar, your logo and tag-line, light and dark mode
🗄 A data runtime with a parameterized query builder and real transactions
⚙️ LogicBank for FutureBasic, a rules engine built into every app

The rules are the heart of it. Declare once that an order's total is the sum of its lines, that a customer's balance is the sum of unshipped orders, and that the balance can't exceed the credit limit. From then on, adding one order line updates the order, then the customer, then checks the limit, all in one transaction. If the check fails, nothing is saved, and the message says why.

The Studio also draws the model as an interactive entity-relationship diagram, with the rules marked where they act.

Everything generated is plain, commented FutureBasic. The files you write yourself are never overwritten, so the app stays yours.

It's in active development, and the first builds on the Mac are under way. If you write FutureBasic, I'd like to hear what you'd want from it.

#FutureBasic #macOS #MacDev #LowCode #BusinessRules #SQLite #APILogicServer #ImageryBusinessSystems
