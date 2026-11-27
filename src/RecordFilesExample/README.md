# Record Files for FutureBasic: an example

Records of a fixed size in random-access files, the way FutureBasic always could (`begin record`, `open "R"`,
`record`, `read file`, `write file`), found by B-tree indexes in the manner of Btrieve, and timed against SQLite
on the same data.

## Run it

Open `RecordFilesExample.fbeproj` in FutureBasic, build and run. Choose a size and click **Run**. The files go
to `~/Library/Application Support/Record Files Example/`, and **Show the Files** opens the folder.

Each run builds every record, opens the files again, looks up 10,000 customers by number, reads the orders of
10,000 customers, reads every customer in name order, removes 1,000 items and adds as many (the freed slots are
reused, so the file does not grow), and checks every index. The table shows the time each step took in the
record files and in SQLite.

## The files

| File | What it is |
|---|---|
| `Record File.incl` | the module: record files, in FutureBasic |
| `Record Index.incl` | the module: B-tree index files (C inside the .incl, with FB declarations) |
| `Orders Records.incl` | Customer, Order and Item as records, with six indexes: what App Builder would generate |
| `Sample Data.incl` | the data, made by formula (the same for both engines) |
| `SQLite Comparison.incl` | the same work in SQLite (`-lsqlite3` is in Build Settings) |
| `Benchmark.incl` | the seven steps and the table of times |

The design and the file formats are in `docs/design/Record Files Design.md` in the repository.

MIT License; see `LICENSE`. Copyright (c) 2026 Imagery Business Systems, LLC.
