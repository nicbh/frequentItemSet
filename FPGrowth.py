from tools import fn_timer
from Apriori import relations
import json, itertools
from memory_profiler import profile


@fn_timer
# @profile
def fpgrowth(file, generator, support, confidence):
    number = 0
    frequentItems = []
    itemsCount = {}

    first = file.readline().strip()
    first = json.loads(first)
    number = first['number']
    line_num = first['lines']
    support_count = line_num * support
    root, headerTable = create_fptree(generator, support_count, file=file)
    mine_fptree(root, headerTable, support_count, [], frequentItems, itemsCount)
    return frequentItems, [], []  # , itemsCount, relations(frequentItems, itemsCount, confidence)


def gen(paths):
    for path in paths:
        num = path[0]
        path = path[1:]
        if len(path) > 0:
            for i in range(0, num):
                yield path


def mine_fptree(root, headerTable, support_count, preFix, frequentItems, itemsCount):
    for item, linklist in headerTable.items():
        paths = []
        allnum = 0
        for link in linklist:
            num = link[2]
            allnum += num
            path = [num]
            link = link[3]
            while link[3] != None:
                path.append(link[0])
                link = link[3]
            paths.append(path)
            tmppath = path.copy()
            tmppath.append(item)
            # items = path.copy()
            # items.append(item)
            # items = items[1:]
            # items.sort()
            # items = tuple(items)
            # for i in range(1, len(items) + 1):
            #     for itemt in itertools.combinations(items, i):
            #         itemsCount[itemt] = max(num, itemsCount.get(itemt, 0))
        newFrequentItems = preFix.copy()
        newFrequentItems.append(item)
        newFrequentItems.sort()
        items = tuple(newFrequentItems)
        if len(frequentItems) < len(items):
            for i in range(0, len(items) - len(frequentItems)):
                frequentItems.append({})
        frequentItems[len(items) - 1][items] = allnum
        nroot, nheaderTable = create_fptree(gen, support_count, paths=paths)
        if nroot != None:
            mine_fptree(nroot, nheaderTable, support_count, newFrequentItems, frequentItems, itemsCount)


def create_fptree(genList, support_count, file=None, paths=None):
    currentItems = {}
    func = genList
    if file != None:
        genList = func(file)
    else:
        genList = func(paths)
    for List in genList:
        for item in List:
            if item in currentItems:
                currentItems[item] = currentItems[item] + 1
            else:
                currentItems[item] = 1

    items_set = set([x for x, y in currentItems.items() if y >= support_count])
    currentItems = {x: y for x, y in currentItems.items() if y >= support_count}
    if len(currentItems) == 0:
        return None, None
    headerTable = {x: [] for x in currentItems.keys()}
    root = [None, [], 0, None]  # str, son, count, parent
    if file != None:
        file.seek(0)
        first = file.readline()
        genList = func(file)
    else:
        genList = func(paths)
    for List in genList:
        List = sorted([x for x in List if x in items_set], key=lambda x: -currentItems[x])
        head = root
        while len(List) > 0:
            for chain in head[1]:
                if chain[0] == List[0]:
                    chain[2] = chain[2] + 1
                    List = List[1:]
                    head = chain
                    break
            else:
                now = head
                while len(List) > 0:
                    newChain = [List[0], [], 1, now]
                    headerTable[List[0]].append(newChain)
                    now[1].append(newChain)
                    List = List[1:]
                    now = newChain
    return root, headerTable
