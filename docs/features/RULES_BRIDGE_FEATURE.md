# Rules Bridge — declare_logic.py import / export, Rules.json, Studio Rules.incl

**Where:** `tools/rules_bridge.py` (bundled with the generator: `resources "../../tools"`),
`src/AppBuilder/Rules Bridge.incl` (runs it), *Model → Import Rules… / Export Rules…*, Generate App.

## How it works

The project's rules are kept in `<project>/Rules.json`:

```json
{ "version": 1, "rules": [
  { "id": "formula-OrderDetail-Amount", "kind": "formula", "entity": "OrderDetail", "attr": "Amount",
    "expression": "fn NumberWithDouble( ( fn LogicDouble( logicRow, @\"Quantity\" ) * fn LogicDouble( logicRow, @\"UnitPrice\" ) ) )",
    "dependsOn": ["Quantity", "UnitPrice"], "enabled": true,
    "source": "Rule.formula(derive=models.OrderDetail.Amount, as_expression=lambda row: row.Quantity * row.UnitPrice)" } ] }
```

Kinds: `formula` (expression), `constraint` (condition, message), `sum` / `count` (list,
childAttr, where), `copy` (role, parentAttr), `parentCheck` (role, message), `deleteAction`
(list, action, message), `rowEvent` / `commitEvent` (body). Each rule may carry `title`,
`enabled`, `note` (why it is off) and `source` (the Python it came from).

| Command | Does |
|---|---|
| `import <declare_logic.py>` | reads LogicBank rules with Python's `ast`; translates `lambda row:` into FB by the model's column types (`LogicDouble` / `LogicString`, `is None` → `LogicIsEmpty`, parent references, `and` / `or` / `not`, comparisons); finds child lists and parent roles from the model. Anything else (Python functions, conditional expressions, events) arrives **switched off** with its Python kept. Same ids replace, others are kept. |
| `check` | names against the model, dependencies, formula cycles; fills `dependsOn` |
| `generate` | `Studio Rules.incl` (CR line endings): one FB function per enabled rule and `DeclareStudioRules`; switched-off rules as comments |
| `export` | LogicBank rules: unchanged imports as they came, edited ones translated back from FB, the rest as comments |

The generator runs it with `/usr/bin/python3` (Xcode's command-line tools, which FB needs to
compile). Generate App writes `Studio Rules.incl` from `Rules.json`, or an empty
`DeclareStudioRules` when there is none; the generated main calls `DeclareStudioRules`, then the
developer's `DeclareRules`, then `LogicActivate`.

## Decisions
- Python owns import / export / generation: parsing Python belongs to Python, and the one
  implementation is fully tested here (`rules_bridge.py --test`, 23 checks).
- Untranslatable rules are kept, not guessed.

## Verify on a Mac
- [ ] *Import Rules…* on an ALS project's `logic/declare_logic.py`: the message counts; `Rules.json` written
- [ ] *Generate App*: `FBapp/Studio Rules.incl` lists the rules; the app builds; NSLog: `Logic: rules active`
- [ ] *Export Rules…*: a `declare_logic.py` ALS accepts
