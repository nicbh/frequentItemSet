from tools import fn_timer
import json, itertools
from memory_profiler import profile


def naiveRelations(frequentItems, count, confidence):
    relation = []
    for itemlist in frequentItems:
        current = {}
        for items, ccc in itemlist.items():
            length = len(items)
            items_set = set(items)
            if length <= 1:
                continue
            for i in range(1, length):
                enum = itertools.combinations(items, i)
                for right in enum:
                    left = list(items_set.difference(set(right)))
                    left.sort()
                    left = tuple(left)
                    conf = count[items] / count[left]
                    if conf >= confidence:
                        current[(left, right)] = conf
        if len(current) > 0:
            relation.append(current)
    return relation


@profile
@fn_timer
def naiveFrequentItemSet(file, generator, support, confidence):
    number = 0
    frequentItems = []
    Items = set()
    maxSet = 2
    itemsCount = {}
    for List in generator(file):
        if isinstance(List, dict):
            number = List['number']
            line_num = List['lines']
            support_count = line_num * support
            continue
        for item in List:
            Items.add(item)

    candidateItems = []
    for i in range(1, maxSet + 1):
        itemss = itertools.combinations(Items, i)
        candidateItems.append({x: i for x in itemss})
        frequentItems.append({})

    currentItems = {}
    file.seek(0)
    linenumber = 0
    for List in generator(file):
        linenumber += 1
        if isinstance(List, dict):
            continue
        List_length = len(List)
        List_set = set(List)
        for itemlist in candidateItems:
            for (items, items_length) in itemlist.items():
                if items_length > List_length:
                    continue

                exist = True
                for x in items:
                    if x not in List_set:
                        exist = False
                        break
                if not exist:
                    continue

                if items in currentItems:
                    currentItems[items] = currentItems[items] + 1
                else:
                    currentItems[items] = 1

    for (items, num) in currentItems.items():
        itemsCount[items] = num
        if num > support_count:
            frequentItems[len(items) - 1][items] = num

    return frequentItems, itemsCount, naiveRelations(frequentItems, itemsCount, confidence)
