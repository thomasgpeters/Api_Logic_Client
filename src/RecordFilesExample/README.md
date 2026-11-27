# Record Files for FutureBasic - example

Records of a fixed size in random-access files, the way FutureBasic always could (`begin record`, `open "R"`,
`record`, `read file`, `write file`), found by B-tree indexes in the manner of Btrieve - and timed against SQLite on
the same data.

Open `RecordFilesExample.fbeproj` in FutureBasic, build and run, choose a size, **Run**. The files go to
`~/Library/Application Support/Record Files Example/`; **Show the Files** opens the folder.

| File | What it is |
|---|---|
| `Record File.incl` | the module: record files (FutureBasic) |
| `Record Index.incl` | the module: B-tree index files (C inside the .incl, with FB declarations) |
| `Orders Records.incl` | Customer, Order and Item as records, with six indexes - what App Builder would generate |
| `Sample Data.incl` | the data, made by formula (the same for both engines) |
| `SQLite Comparison.incl` | the same work in SQLite (`-lsqlite3` is in Build Settings) |
| `Benchmark.incl` | the seven steps and the table of times |

The run: build every record; open again; 10,000 customers by number; the orders of 10,000 customers; every customer
in name order; 1,000 items removed and as many added (the freed slots are reused: the file does not grow); every
index checked.

Design and file formats: `docs/design/Record Files Design.md` in the repository. MIT License, see `LICENSE`.
