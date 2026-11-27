# Record Files for FutureBasic - design

Author's idea (2026-11-27): FutureBasic's `begin record` types, written to random-access files as legacy FB always
could, with index files beside them, in the manner of Btrieve - "an interesting exercise ... I would love to see
how it performs". If it proves stable, App Builder gets a developer choice: **generate record files with B-tree
indexes instead of SQLite** (author: "a developer selection to output Record databases with B-Tree indexes").

The example: `src/RecordFilesExample/` (Customer, Order, Item; timed against SQLite). Tests:
`tools/check_record_index.py`, `tools/check_record_files_example.py`; formats read independently by
`tools/record_files_reference.py` (also `--index` / `--records` to look inside a file made on a Mac).

## What is loaded into memory

Nothing beyond what is asked for. A record is found by its number with one seek and one read (record n starts at
n x the slot length); a key is found with three or four index pages (4 KB each) for millions of entries, most of
them from a page cache (512 pages per index, 2 MB). Opening the files reads their headers only.

## Record files (`Record File.incl`, FutureBasic)

`open "R", fileID, url, slotLength`, `record #fileID, n`, `read file` / `write file`. All fields little-endian.

| Slot | Bytes | Content |
|---|---|---|
| 0 | 32 | header: magic `FBRD` (1178751556), version 1, record size, slot length, first free slot, live count, closed cleanly (1 / 0), reserved |
| n >= 1 | 8 + record size | status (1 live, 2 free), next free slot, then the record's bytes |

- Append: the first free slot, else the end of the file. Delete: the slot goes on the free list (its bytes stay
  until it is reused). Records are at least 24 bytes (the header must fit in slot 0, and every slot write is whole).
- Text in a record: `Str63` / `Str255` fields (Pascal strings); `RecordSetText` / `RecordText` move a CFString in
  and out (UTF-8, cut on a character's edge). A `CFStringRef` field would store a pointer, not the text.
- **A stop in the middle.** The header says "not closed cleanly" while the file is open. Opened again after a stop,
  the live count and the free list are rebuilt from the slots' status words (`RecordFileWasRecovered`), and the
  entity's indexes are rebuilt from the record file. The record file is the truth; indexes can always be made again.
  What is not covered: a record whose 8 + n bytes were half written when the machine lost power (no journal; SQLite
  has one). A record checksum in the slot header is the next step if this becomes an App Builder option.

## Indexes (`Record Index.incl`, C)

C, between the markers "record index core", compiled and tested here exactly as written. Why C: FutureBasic cannot
be compiled here, and a B-tree's page splitting is where bugs hide; in C it runs against a sorted-list model on
thousands of random operations, and its files are read back by an independent reader.

- **Keys are segments** (as Btrieve): `RIKeyAddLong` (8 bytes, the sign flipped, big-endian: the bytes sort as the
  numbers), `RIKeyAddPascal` / `RIKeyAddString` (a fixed width of text, padded; caseless folds a-z). The segments'
  widths add up to the index's key length.
- **Equal keys are allowed:** every entry is the key followed by the record number (4 bytes, big-endian), so entries
  are unique and equal keys stay in record order. Seek Equal finds the first; Next walks them while
  `RICursorKeyEquals`.
- **Seeks:** First, Last, Equal, Greater or Equal, Greater, Less or Equal, Less; then Next / Previous along the
  leaves, which are chained both ways.
- **Pages** (4096 bytes; page 0 the header: magic `FBRI`, version, page size, key length, root, page count, entry
  count, height, closed cleanly). A node: leaf flag, count, next leaf, previous leaf, then entries (leaves:
  key + record) or child 0 then (separator, child) pairs (internal: child i + 1 holds entries >= separator i).
- **Writes** go straight to the file; the header is written on open ("open") and on close ("closed cleanly", with
  `fsync`). An index found "open" is not trusted: it is rebuilt from its record file.
- **Deletes** remove the entry; nodes are not merged (an emptied leaf stays in the chain until the index is
  rebuilt). Rebuilding an index is one scan of its record file.
- `RICheck`: the whole tree - order, ranges, depth, leaf links, counts.

## The App Builder option (when it is stable)

What the generator would write per entity, as the example's `Orders Records.incl` shows by hand:

- a `begin record` from the model: whole numbers as `long`, decimals as `double`, text as `Str63` / `Str255` by its
  size, dates as `long` yyyymmdd, booleans as `long`;
- the record file and an index on the key, one per relationship (the foreign key: "the orders of a customer") and
  one per lookup's display column (caseless text);
- Add / Find / First / Next / Remove functions, and the rebuild-on-open rule;
- `App Data Records.incl` beside `App Data Lite.incl`: the same app data interface (list / save / remove), so the
  pages do not change; LogicBank for FutureBasic's rules run the same way (its data layer is already separate,
  as `Data Memory.incl` shows).

Open before it is offered: record checksums; text wider than 255 bytes; changing a record's layout (a new column
means rewriting the file - the generator would write a converter); several processes at once (`open "R"` is
exclusive: one app at a time).
