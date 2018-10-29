from argparse import ArgumentParser
from functools import partial
from operator import attrgetter
from semstr.convert import FROM_FORMAT
from ucca import layer0, layer1
from ucca.evaluation import SummaryStatistics
from ucca.ioutil import get_passages_with_progress_bar

FROM_FORMAT["conllu"] = partial(FROM_FORMAT["conllu"], dep=True)


def get_terminals(unit, visited=None):
    if visited is None:
        return sorted(get_terminals(unit, visited=set()), key=attrgetter("position"))
    outgoing = {e for e in set(unit) - visited if not e.attrib.get("remote")}
    return ([] if unit.tag and unit.tag != layer0.NodeTags.Word else [unit]) + \
        [t for e in outgoing for t in get_terminals(e.child, visited | outgoing)]


def get_yield(unit):
    return frozenset(t.position for t in get_terminals(unit))


def conjuncts(passage):
    for node in passage.layer(layer1.LAYER_ID).all:
        if node.tag:  # UCCA
            if node.tag == layer1.NodeTags.Foundational and node.connector:
                yield node.centers
        else:  # UD
            children = [e.child for e in node if e.tag.partition(":")[0] == "conj"]
            if children:  # UD and there is a coordination
                print(node.get_terminals())
                yield [node] + children


def yields(nodes):
    # nodes = list(nodes)
    # for ns in nodes:
    #     conjs = " | ".join(" ".join(str(t) for t in get_terminals(n)) for n in ns)
    #     print(conjs)
    return set(frozenset(map(get_yield, ns)) for ns in nodes)


def count(guessed, ref):
    (p1, g), (p2, r) = (guessed, ref)
    assert p1.ID == p2.ID, "Inconsistent order of passages: %s != %s" % (p1.ID, p2.ID)
    common = g & r
    return SummaryStatistics(len(common), len(g) - len(common), len(r) - len(common))


def main(args):
    guessed, ref = [((p, yields(conjuncts(p))) for p in get_passages_with_progress_bar(f, converters=FROM_FORMAT))
                    for f in (args.guessed, args.ref)]
    stats = SummaryStatistics.aggregate([count(g, r) for g, r in zip(guessed, ref)])
    stats.print()


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate conjunct spans")
    argparser.add_argument("guessed", help="File or directory for graphs to evaluate")
    argparser.add_argument("ref", help="File or directory for graphs to use as reference")
    main(argparser.parse_args())
