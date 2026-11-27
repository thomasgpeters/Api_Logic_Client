#!/usr/bin/env python3
"""record_files_reference.py - Record Files for FutureBasic: the file formats, read independently of the FB code.

Two kinds of file (docs/design/Record Files Design.md):
  - a record file (Record File.incl, FutureBasic's own random-access file I/O): a 32-byte header in slot 0, then one
    fixed-size slot per record: status (1 live, 2 free), the next free slot, the record's bytes;
  - an index file (Record Index.incl, a B-tree in C): 4 KB pages; page 0 the header, then nodes.

This module encodes keys the way Record Index.incl does, reads both formats, and checks an index's tree with its
own walk (tools/check_record_index.py uses it to check the C code's files). From the command line it shows what is
in a file made on a Mac:

    python3 tools/record_files_reference.py --index "Customers by Name.index"
    python3 tools/record_files_reference.py --records Customers.records
"""
import struct
import sys

PAGE_SIZE = 4096
NODE_HEADER = 16
INDEX_MAGIC = 0x46425249          # "FBRI"
RECORDS_MAGIC = 0x46425244        # "FBRD"
RECORDS_HEADER = 32
SLOT_HEADER = 8
SLOT_LIVE, SLOT_FREE = 1, 2


# --- keys, as RIKeyAddLong / RIKeyAddBytes / RIKeyAddPascal build them ---
def key_long(value):
    """8 bytes: the sign flipped, big-endian - the bytes sort as the numbers do"""
    return ((value & 0xFFFFFFFFFFFFFFFF) ^ 0x8000000000000000).to_bytes(8, 'big')


def key_bytes(data, width, caseless=False):
    data = bytes(data[:width])
    if caseless:
        data = bytes(c - 32 if 97 <= c <= 122 else c for c in data)
    return data + bytes(width - len(data))


def key_text(text, width, caseless=False):
    """UTF-8, cut on a character's edge (as CFStringGetBytes with a byte limit does)"""
    out = b''
    for ch in text:
        b = ch.encode('utf-8')
        if len(out) + len(b) > width:
            break
        out += b
    return key_bytes(out, width, caseless)


def composite(key, record_number):
    return key + record_number.to_bytes(4, 'big')


# --- index files ---
def read_index_header(data):
    magic, version, page_size, key_length, root, pages, entries, height, clean = struct.unpack_from('<9I', data, 0)
    return {'magic': magic, 'version': version, 'pageSize': page_size, 'keyLength': key_length, 'root': root,
            'pages': pages, 'entries': entries, 'height': height, 'closedCleanly': clean}


def read_index(path):
    """the header, and every entry as (key bytes, record number), walked from the root (not the leaf chain)"""
    data = open(path, 'rb').read()
    header = read_index_header(data)
    problems = check_index_bytes(data, header)
    entries = []

    def walk(page_no):
        page = data[page_no * PAGE_SIZE:(page_no + 1) * PAGE_SIZE]
        count = struct.unpack_from('<I', page, 4)[0]
        c = header['keyLength'] + 4
        if page[0]:
            for i in range(count):
                e = page[NODE_HEADER + i * c:NODE_HEADER + (i + 1) * c]
                entries.append((e[:-4], int.from_bytes(e[-4:], 'big')))
            return
        for i in range(count + 1):
            walk(child(page, i, c))
    if not problems:
        walk(header['root'])
    return header, entries, problems


def child(page, i, c):
    if i == 0:
        return struct.unpack_from('<I', page, NODE_HEADER)[0]
    return struct.unpack_from('<I', page, NODE_HEADER + 4 + (i - 1) * (c + 4) + c)[0]


def check_index_bytes(data, header):
    """the tree's rules, checked with a walk of our own: [] when sound"""
    problems = []
    if header['magic'] != INDEX_MAGIC:
        return ['not an index file (magic)']
    if header['pageSize'] != PAGE_SIZE or len(data) % PAGE_SIZE:
        return ['the page size or the file length is wrong']
    k = header['keyLength']
    c = k + 4
    leaf_max = (PAGE_SIZE - NODE_HEADER) // c
    inner_max = (PAGE_SIZE - NODE_HEADER - 4) // (c + 4)
    pages = len(data) // PAGE_SIZE
    if header['pages'] > pages:
        problems.append(f"the header counts {header['pages']} pages, the file has {pages}")
    leaves = []
    seen = set()

    def node(page_no, depth, low, high):
        if problems:
            return
        if page_no == 0 or page_no >= pages or page_no in seen:
            problems.append(f'page {page_no}: outside the file, or reached twice')
            return
        seen.add(page_no)
        page = data[page_no * PAGE_SIZE:(page_no + 1) * PAGE_SIZE]
        count = struct.unpack_from('<I', page, 4)[0]
        if page[0]:
            if depth != header['height']:
                problems.append(f'page {page_no}: a leaf at depth {depth}, the height is {header["height"]}')
            if count > leaf_max:
                problems.append(f'page {page_no}: {count} entries, at most {leaf_max}')
                return
            items = [page[NODE_HEADER + i * c:NODE_HEADER + (i + 1) * c] for i in range(count)]
            for a, b in zip(items, items[1:]):
                if a >= b:
                    problems.append(f'page {page_no}: entries out of order')
            for e in items:
                if (low is not None and e < low) or (high is not None and e >= high):
                    problems.append(f'page {page_no}: an entry outside its range')
                if int.from_bytes(e[-4:], 'big') == 0:
                    problems.append(f'page {page_no}: an entry for record 0')
            leaves.append((page_no, struct.unpack_from('<I', page, 8)[0], struct.unpack_from('<I', page, 12)[0], count))
            return
        if count < 1 or count > inner_max:
            problems.append(f'page {page_no}: an internal node with {count} separators')
            return
        keys = [page[NODE_HEADER + 4 + i * (c + 4):NODE_HEADER + 4 + i * (c + 4) + c] for i in range(count)]
        for a, b in zip(keys, keys[1:]):
            if a >= b:
                problems.append(f'page {page_no}: separators out of order')
        for i in range(count + 1):
            node(child(page, i, c), depth + 1, keys[i - 1] if i > 0 else low, keys[i] if i < count else high)
    node(header['root'], 1, None, None)
    if problems:
        return problems
    # the leaf chain: in the walk's order, linked both ways
    for i, (no, nxt, prv, _) in enumerate(leaves):
        want_next = leaves[i + 1][0] if i + 1 < len(leaves) else 0
        want_prev = leaves[i - 1][0] if i > 0 else 0
        if nxt != want_next or prv != want_prev:
            problems.append(f'page {no}: leaf links next {nxt} / previous {prv}, expected {want_next} / {want_prev}')
    total = sum(n for *_, n in leaves)
    if total != header['entries']:
        problems.append(f"{total} entries in the leaves, {header['entries']} in the header")
    return problems


# --- record files (written by FutureBasic: little-endian UInt32 fields) ---
def read_records(path):
    data = open(path, 'rb').read()
    magic, version, record_size, slot_length, free_head, live, clean, _ = struct.unpack_from('<8I', data, 0)
    if magic != RECORDS_MAGIC:
        raise ValueError('not a record file (magic)')
    slots = []
    n = 1
    while n * slot_length < len(data):
        status, next_free = struct.unpack_from('<2I', data, n * slot_length)
        body = data[n * slot_length + SLOT_HEADER:n * slot_length + SLOT_HEADER + record_size]
        slots.append((n, status, next_free, body))
        n += 1
    header = {'version': version, 'recordSize': record_size, 'slotLength': slot_length, 'freeHead': free_head,
              'liveCount': live, 'closedCleanly': clean}
    return header, slots


def check_records(header, slots):
    """the free list reaches every free slot once; the live count matches"""
    problems = []
    live = sum(1 for _, s, _, _ in slots if s == SLOT_LIVE)
    if header['closedCleanly'] == 1 and live != header['liveCount']:
        problems.append(f"{live} live slots, the header says {header['liveCount']}")
    free = {n for n, s, _, _ in slots if s == SLOT_FREE}
    seen = set()
    n = header['freeHead']
    by_number = {n: nf for n, _, nf, _ in slots}
    while n:
        if n in seen or n not in free:
            problems.append(f'the free list reaches slot {n}, which is not free (or twice)')
            break
        seen.add(n)
        n = by_number[n]
    if header['closedCleanly'] == 1 and seen != free:
        problems.append(f'{len(free - seen)} free slots are not on the free list')
    return problems


def main(argv):
    if len(argv) == 3 and argv[1] == '--index':
        header, entries, problems = read_index(argv[2])
        print(header)
        print(f'{len(entries)} entries; first: {entries[:3]}')
        print('sound' if not problems else '\n'.join(problems))
        return 0 if not problems else 1
    if len(argv) == 3 and argv[1] == '--records':
        header, slots = read_records(argv[2])
        print(header)
        print(f'{len(slots)} slots, {sum(1 for _, s, _, _ in slots if s == SLOT_LIVE)} live')
        problems = check_records(header, slots)
        print('sound' if not problems else '\n'.join(problems))
        return 0 if not problems else 1
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
