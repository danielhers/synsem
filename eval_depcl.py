from argparse import ArgumentParser
from functools import partial
from operator import attrgetter

from semstr.convert import FROM_FORMAT
from spacy.parts_of_speech import CCONJ, PUNCT
from ucca import layer0, layer1
from ucca.evaluation import SummaryStatistics
from ucca.ioutil import get_passages
from ucca.textutil import Attr

FROM_FORMAT["conllu"] = partial(FROM_FORMAT["conllu"], dep=True)


def get_terminals(unit, visited=None, conj=False):
    if visited is None:
        visited = set()
    outgoing = {e for e in set(unit) - visited if not e.attrib.get("remote")
                and e.tag not in ("punct", layer1.EdgeTags.Punctuation)
                and (conj or e.tag not in ("cc", "conj"))}
    return ([] if unit.tag and (unit.tag not in (layer0.NodeTags.Word, layer0.NodeTags.Punct)
                                or unit.tok[Attr.POS.value] == PUNCT) else [unit]) + \
        [t for e in outgoing for t in get_terminals(e.child, visited | outgoing, conj=True)]


def subordinate_clauses(passage):
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
                                if not terminals:
                                    break
                            elif edge.tag in (layer1.EdgeTags.Linker, layer1.EdgeTags.ParallelScene):
                                if edge.tag == layer1.EdgeTags.ParallelScene and terminals and \
                                        terminals[-1].position + 1 < edge.child.start_position:
                                    yield terminals
                                    terminals = []
                                terminals += get_terminals(edge.child)
                                continue
                            if terminals:
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
    guessed_yields, ref_yields = [list(subordinate_clauses(p)) for p in (guessed, ref)]
    g, r = [set(frozenset(t.position for t in y) for y in yields) for yields in (guessed_yields, ref_yields)]
    common = g & r
    only_g = g - common
    only_r = r - common
    if only_g or only_r:
        for i, yields in enumerate((guessed_yields, ref_yields), start=1):
            conj = [" ".join(map(str, sorted(y, key=attrgetter("position")))) for y in yields]
            print(guessed.ID, i, " | ".join(conj))
    return SummaryStatistics(len(common), len(only_g), len(only_r))


def main(args):
    guessed, ref = [get_passages(f, converters=FROM_FORMAT) for f in (args.guessed, args.ref)]
    stats = SummaryStatistics.aggregate([evaluate(g, r) for g, r in zip(guessed, ref)])
    stats.print()


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate yields of subordinate clauses or elaborator scenes")
    argparser.add_argument("guessed", help="File or directory for graphs to evaluate")
    argparser.add_argument("ref", help="File or directory for graphs to use as reference")
    main(argparser.parse_args())
