# Host check for sliced gc.collect().
# Build the unix port with MICROPY_GC_INCREMENTAL, a tiny block budget,
# MICROPY_GC_SLICE_GAP_US=0, and MICROPY_GC_INCREMENTAL_VERIFY=1.
# A correct slice frees nothing on the first call, survives graph edits
# while the mark is open, and frees the garbage only after a full finish.

import gc


class Node:
    def __init__(self, i, nxt=None):
        self.i = i
        self.nxt = nxt
        self.bag = []


def build_chain(n):
    head = None
    for i in range(n):
        head = Node(i, head)
    return head


def walk(head):
    seen = 0
    node = head
    while node is not None:
        seen += node.i
        for item in node.bag:
            seen += item.i
        node = node.nxt
    return seen


def main():
    gc.collect(1)
    before = gc.mem_alloc()
    junk = [Node(i) for i in range(400)]
    grown = gc.mem_alloc()
    if grown <= before:
        raise SystemExit("setup did not allocate")
    del junk
    # A handful of slices must not finish a 400-node heap.
    for _ in range(4):
        gc.collect()
    mid = gc.mem_alloc()
    if mid < grown - 4096:
        raise SystemExit("early gc.collect calls freed the heap (%s -> %s)" % (grown, mid))
    # The same call, repeated, has to reach the sweep. A no-op would not.
    n = 0
    while gc.mem_alloc() > before + 4096:
        gc.collect()
        n += 1
        if n > 200000:
            raise SystemExit("gc.collect never reclaimed the dropped nodes")
    if n < 20:
        raise SystemExit("reclaim took only %s slices; expected a long slice sequence" % n)
    after = gc.mem_alloc()
    print("reclaim slices", n, "alloc", before, grown, mid, after)

    head = build_chain(300)
    hold = {}
    gc.collect()
    node = head
    step = 0
    while node is not None and step < 200:
        node.bag.append(Node(100000 + step))
        hold[step] = node.i
        if node.nxt is not None and node.nxt.nxt is not None:
            # Drop one link. The skipped node is only garbage if nothing else
            # kept it; the kept suffix must stay reachable.
            node.nxt = node.nxt.nxt
        node = node.nxt
        step += 1
    # Closures and a set, so those stores are in the open window too.
    cells = []

    def remember(value):
        box = value

        def inner():
            return box

        return inner

    for i in range(40):
        cells.append(remember((i, head)))
    uniq = set()
    for i in range(40):
        uniq.add(("k", i))
    gc.collect(1)
    if walk(head) <= 0:
        raise SystemExit("chain walk failed")
    for fn in cells:
        got = fn()
        if got[1] is not head:
            raise SystemExit("closure lost the chain")
    if ("k", 3) not in uniq:
        raise SystemExit("set lost an element")
    if hold[0] != head.i:
        raise SystemExit("dict lost a stored attribute")
    print("gc slice stress ok", after, mid, grown)


main()
