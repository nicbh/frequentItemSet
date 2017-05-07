from naiveMethod import naiveFrequentItemSet
from Apriori import apriori
from FPGrowth import fpgrowth
import os.path, json


def lineGenerate(file):
    for line in file:
        line = line.strip()
        List = json.loads(line)
        if isinstance(List, list):
            List = list(set(List))
        yield List


if __name__ == '__main__':
    support = 0.01
    confidence = 0.1
    file1 = 'dataset/GroceryStore'
    file2 = 'dataset/UNIX_usage'
    file3 = 'dataset/smallGS'
    file4 = 'dataset/smallUnix'
    rootdir = file1
    # rootdir = file2
    # rootdir = file3
    # rootdir = file4
    rootname = rootdir[rootdir.rfind('/') + 1:]
    cachename = 'tmp/' + rootname + '.json'
    hashset = set()
    if not os.path.exists(cachename):
        with open(cachename, 'w', encoding='utf-8') as f:
            List = []
            for parent, dirnames, filenames in os.walk(rootdir):
                for filename in filenames:  # 输出文件信息
                    if filename != '.DS_Store' and not filename.endswith('.txt'):
                        filename = os.path.join(parent, filename);
                        print("deal with file: " + filename)  # 输出文件路径信息
                        with open(filename, encoding='utf-8') as input:
                            if filename.endswith('.csv'):
                                for line in input:
                                    line = line.strip()
                                    lili = line.split('"')
                                    if not lili[1].isdigit():
                                        continue
                                    number = lili[1]
                                    item = lili[3][1:-1]
                                    itemlist = item.split(',')
                                    itemlist = [x.strip() for x in itemlist]
                                    for item in itemlist:
                                        hashset.add(item)
                                    List.append(itemlist)
                            elif 'sanitized_all' in filename:
                                tmplist = []
                                for line in input:
                                    line = line.strip()
                                    if 'SOF' in line:
                                        tmplist = []
                                        continue
                                    if 'EOF' in line:
                                        for item in tmplist:
                                            hashset.add(item)
                                        List.append(tmplist)
                                        continue
                                    if len(line) > 0:
                                        if line[0] == '-':
                                            tmplist[-1] += ' ' + line
                                        elif len(tmplist) > 0 and line[0] == '<' and line[-1] == '>' and line[
                                                                                                         1:-1].isdigit():
                                            tmplist[-1] += ' ' + line
                                        else:
                                            tmplist.append(line)
            f.write(json.dumps({'number': len(hashset), 'lines': len(List)}) + '\n')
            for item in List:
                f.write(json.dumps(item) + '\n')
    # func = naiveFrequentItemSet
    func = apriori
    # func = fpgrowth
    with open(cachename, encoding='utf-8') as file:
        freq, count, rel = func(file, lineGenerate, support, confidence)
        allfreq = {}
        for f in freq:
            allfreq.update(f)
        allfreq = sorted([(x, y) for x, y in allfreq.items()], key=lambda x: x[1], reverse=True)
        print(allfreq)
        allrel = {}
        for r in rel:
            allrel.update(r)
        allrel = sorted([(x, y) for x, y in allrel.items()], key=lambda x: x[1], reverse=True)
        print(allrel)
