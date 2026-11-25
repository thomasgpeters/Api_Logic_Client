# Open ALS Project: a project from the model API Logic Server generated

The author (2026-11-25): the model is API Logic Server's, never FutureBasic's. The Lite edition
points at the SQLite file; the Enterprise edition points at the **ALS project** and reads the model
ALS generated there. The model file sits in the same place for any database: `database/models.py`.

## What the developer sees

*Project > New Project from API Logic Server…* (⇧⌘N), or **API Logic Server Project…** on the New
Project page, opens the **API Logic Server Project** page. Point at the ALS project one of four ways:

| | |
|---|---|
| type or paste | a folder, a model file, or a GitHub address, then **Read** |
| **Folder…** | the ALS project's folder (a clone of its repository); its `database/` or `ui/` folder works too |
| **Model File…** | `database/models.py` (or `ui/app/app_model.yaml`, `ui/admin/admin.yaml`) |
| drop | the folder or the file onto the drop zone |

The page shows what the model holds - *"17 resources, 56 relationships: Category, Customer, …"* -
and where it came from, suggests the project's name (the folder's or the repository's), and asks
for the **API Server** the generated app talks to (`http://localhost:5656` by default). **Create**
keeps a copy of the model in the project and opens it: the entity list, definitions, design, XIBs
and bindings work exactly as for a SQLite project. **From a Running Server…** is the older route
(the server's `/metadata`, which has no relationships).

GitHub addresses (a **public** repository; no sign-in, no GitHub API):

    https://github.com/<owner>/<repo>                       main, else master; the project at the top
    https://github.com/<owner>/<repo>/tree/<branch>/<sub>   a branch, and the project in a subfolder
    https://github.com/<owner>/<repo>/blob/<branch>/database/models.py
    https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>

The files are read over plain HTTPS from `raw.githubusercontent.com`.

## Where

| | |
|---|---|
| `src/Generator/ALSProjectView.xib` | the page: name, ALS project field, Read, Folder…, Model File…, the drop zone's box and label, summary, API Server, From a Running Server…, Cancel, Create |
| `src/Generator/Open ALS Project.incl` | the page's actions; `ALSProjectSetUp` makes the drop zone |
| `src/Generator/ALS Project.incl` | finding the model (folder, file, GitHub), keeping the copy, `ALSProjectStudioModel` |
| `src/Generator/ALS Model.incl` | parsing it (`ALSModelFromModelsPy`, `ALSModelFromYAML`, `ALSModelFromText`); moved here from `src/Enterprise/` - the Studio reads it |
| `src/Generator/Project Actions.incl` | `LoadALSModel` (the project's copy -> the Studio model); `LoadModelFile` opens `.py` / `.yaml` with it |
| `tools/als_project_reference.py` | the reference, function for function, and its test |

## Decisions

- **Order of the model files**: `database/models.py` (every project; the only one from ALS 17.04 on),
  else `ui/app/app_model.yaml` (17.3 and earlier), else `ui/admin/admin.yaml`. `admin.yaml`, when it
  is there, adds the column that names a record (`user_key`) for lookups. models.py first: on the
  public `ApiLogicServer/demo` repository its 26 relationships include all 11 of `admin.yaml`'s.
- **Told apart by contents**, not names (`Base):` means SQLAlchemy classes): a dropped or downloaded
  file works whatever it is called. Older projects write `class X(SAFRSBaseX, Base):`; both read.
- **A copy in the project**: `<project>/ALS Model/models.py` (or `app_model.yaml` / `admin.yaml`), and
  `admin.yaml` beside it. The project's `source` is the copy, so it opens again without the original
  or the network. `Project.json` keeps `alsSource` (where it came from) and `edition: enterprise`.
- **The drop zone is a subclassed view made in code** (author: FB's translator writes the subclass;
  only its own classes exist): `subclass view` laid over the XIB's box, `ViewRegisterForDraggedFileTypes`,
  the drop as `_viewPerformDragOperation` with `DialogEventArray` (FBExamples, DragDrop View).
- **The Studio model** (`ALSProjectStudioModel`) has SQLite Model.incl's shape: `pk` in key order,
  `keyKind` identity for one INTEGER key (the server assigns it; the Form shows it, never asks),
  else assigned; relationships with the parent's keys; a `lookup` on every single-column key to a
  parent (a composite key such as Order -> Location has none). Resource names, not table names
  (Category is stored in `CategoryTableNameTest`; the table is kept as `table`).
- GitHub is read while the developer waits (one small file, a few requests at most); a private
  repository (a Keychain token) and *Refresh Model* are backlog.
- **Generate App**: an ALS project is an Enterprise app (three-tier). In this open build
  (`Edition.incl`: Lite only) the model can be browsed, designed and its XIBs and bindings generated;
  Generate App explains that the app is the Enterprise edition.

## Verify

- Here: `tools/als_project_reference.py --test <ALS projects> [--github]` - GitHub addresses; each
  project's folder, `database/` folder and `models.py` find the same model; admin.yaml kept; the
  suggested name; the Studio model (keys in order, relationships' key columns exist, parentKeys,
  lookups whose display column exists; Northwind: Employee's two lookups to Department, none for
  Order -> Location, Customer shown by `CompanyName`, keyKind, Category's table). With `--github`:
  `ApiLogicServer/basic_demo` and `ApiLogicServer/demo` read over raw.githubusercontent.com; a
  repository without a model refused. 25 checks. In `run_tests.sh` (projects: `ALS_PROJECTS`;
  network: `ALS_GITHUB=1`).
- On a Mac: ⇧⌘N; drop an ALS project folder (`ApiLogicServer create --project_name=nw --db_url=nw-`)
  on the drop zone -> *17 resources …*; Create -> the entity list; Employee's definitions show
  WorksForDepartmentId and OnLoanDepartmentId as Dropdowns. Also paste
  `https://github.com/ApiLogicServer/basic_demo` and Read. Close and reopen the project from Recent
  Projects: it opens from `<project>/ALS Model/models.py`.
