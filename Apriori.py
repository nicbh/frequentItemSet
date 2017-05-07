from tools import fn_timer
import json, itertools
from memory_profiler import profile


def relations(frequentItems, count, confidence):
    relation = []
    for itemlist in frequentItems:
        current = {}
        pruns = []
        pruns_less = len(itemlist)
        for items, ccc in itemlist.items():
            length = len(items)
            items_set = set(items)
            if length <= 1:
                continue
            for i in range(1, length):
                enum = itertools.combinations(items, i)
                for right in enum:
                    if i > pruns_less:
                        right_set = set(right)
                        for prun in pruns:
                            prun_set = set(prun)
                            if right_set & prun_set == prun_set:
                                right_set = None
                                break
                        if right_set == None:
                            continue
                    left = list(items_set.difference(set(right)))
                    left.sort()
                    left = tuple(left)

                    # conf = frequentItems[length - 1][items] / frequentItems[i - 1][left]
                    conf = count[items] / count[left]
                    if conf >= confidence:
                        current[(left, right)] = conf
                    else:
                        pruns.append(right)
                        right_length = len(right)
                        if right_length < pruns_less:
                            pruns_less = right_length
        if len(current) > 0:
            relation.append(current)
    return relation


# @profile
@fn_timer
def apriori(file, generator, support, confidence):
    number = 0
    frequentItems = []
    currentItems = {}
    itemsCount = {}
    for List in generator(file):
        if isinstance(List, dict):
            number = List['number']
            line_num = List['lines']
            support_count = line_num * support
            continue
        for item in List:
            item = (item,)
            if item in currentItems:
                currentItems[item] = currentItems[item] + 1
            else:
                currentItems[item] = 1
    while True:
        tmpitems = {}
        for (item, num) in currentItems.items():
            itemsCount[item] = num
            if num >= support_count:
                tmpitems[item] = num

        if len(tmpitems) == 0:
            break
        frequentItems.append(tmpitems)

        nextlist = []
        for (item1, num1) in tmpitems.items():
            lastitem1 = item1[-1]
            item11 = list(item1[0:-1])
            for (item2, num2) in tmpitems.items():
                lastitem2 = item2[-1]
                item22 = list(item2[0:-1])
                if item11 == item22 and lastitem1 < lastitem2:
                    nextlist.append(item11 + [lastitem1, lastitem2])
        if len(nextlist) == 0:
            break
        nextlist = tuple(nextlist)

        currentItems = {}
        file.seek(0)
        linenum = 0
        # t000 = 0
        # t111 = 0
        # t1 = time.time()
        items_length = len(nextlist[0])
        for List in generator(file):
            linenum += 1
            if isinstance(List, dict):
                continue
            List_length = len(List)
            List_set = set(List)
            # t01 = time.time()
            for items in nextlist:
                # t0 = time.time()
                if items_length > List_length:
                    continue
                exist = True

                for x in items:
                    if x not in List_set:
                        exist = False
                        break

                if not exist:
                    # t000 = t000 + time.time() - t0
                    continue
                items = tuple(items)
                if items in currentItems:
                    currentItems[items] = currentItems[items] + 1
                else:
                    currentItems[items] = 1
                    # t111 = t111 + time.time() - t01
                    # t2 = time.time() - t1
                    # print(t000)
                    # print(t111)
                    # print(t2)
                    # print()
    return frequentItems, itemsCount, relations(frequentItems, itemsCount, confidence)
