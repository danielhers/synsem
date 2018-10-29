from argparse import ArgumentParser
from functools import partial
from operator import attrgetter
from semstr.convert import FROM_FORMAT
from spacy.parts_of_speech import CCONJ
from ucca import layer0, layer1
from ucca.evaluation import SummaryStatistics
from ucca.ioutil import get_passages_with_progress_bar
from ucca.textutil import Attr

FROM_FORMAT["conllu"] = partial(FROM_FORMAT["conllu"], dep=True)


def get_terminals(unit, visited=None, conj=False):
    if visited is None:
        return sorted(get_terminals(unit, visited=set()), key=attrgetter("position"))
    outgoing = {e for e in set(unit) - visited if not e.attrib.get("remote")
                and e.tag not in ("punct", layer1.EdgeTags.Punctuation)
                and (conj or e.tag not in ("cc", "conj"))}
    return ([] if unit.tag and unit.tag != layer0.NodeTags.Word else [unit]) + \
        [t for e in outgoing for t in get_terminals(e.child, visited | outgoing, conj=True)]


def conjuncts(passage):
    for unit in passage.layer(layer1.LAYER_ID).all:
        if unit.tag:  # UCCA
            if unit.tag == layer1.NodeTags.Foundational:
                if unit.connector:  # nominal coordination
                    yield from map(get_terminals, unit.centers)
                else:  # predicate coordination, expressed as linkers + parallel scenes
                    ccs = {l.ID for l in unit.linkers if all(t.tok[Attr.POS.value] == CCONJ for t in l.get_terminals())}
                    if ccs:
                        terminals = []
                        for edge in unit:
                            if edge.child.ID in ccs:
                                if terminals:
                                    yield terminals
                                else:
                                    break
                                terminals = []
                            elif edge.tag in (layer1.EdgeTags.Linker, layer1.EdgeTags.ParallelScene):
                                terminals += get_terminals(edge.child)
                            elif terminals:
                                yield terminals
                                terminals = []
                        if terminals:
                            yield terminals
        else:  # UD
            children = [e.child for e in unit if e.tag == "conj"]
            if children:  # UD and there is a coordination
                yield get_terminals(unit)
                yield from map(get_terminals, children)


def evaluate(guessed, ref):
    assert guessed.ID == ref.ID, "Inconsistent order of passages: %s != %s" % (guessed.ID, ref.ID)
    guessed_yields, ref_yields = [list(conjuncts(p)) for p in (guessed, ref)]
    g, r = [set(frozenset(t.position for t in y) for y in yields) for yields in (guessed_yields, ref_yields)]
    common = g & r
    only_g = g - common
    only_r = r - common
    if only_g or only_r:
        for yields in guessed_yields, ref_yields:
            conj = [" ".join(str(t) for t in y) for y in yields]
            print(" | ".join(conj))
    return SummaryStatistics(len(common), len(only_g), len(only_r))


def main(args):
    guessed, ref = [get_passages_with_progress_bar(f, converters=FROM_FORMAT) for f in (args.guessed, args.ref)]
    stats = SummaryStatistics.aggregate([evaluate(g, r) for g, r in zip(guessed, ref)])
    stats.print()


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate conjunct yields")
    argparser.add_argument("guessed", help="File or directory for graphs to evaluate")
    argparser.add_argument("ref", help="File or directory for graphs to use as reference")
    main(argparser.parse_args())
