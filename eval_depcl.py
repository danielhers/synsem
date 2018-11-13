from argparse import ArgumentParser
from functools import partial
from operator import attrgetter

from semstr.conversion.conllu import PUNCT_TAG
from semstr.convert import FROM_FORMAT
from ucca import layer0, layer1
from ucca.evaluation import SummaryStatistics
from ucca.ioutil import get_passages

FROM_FORMAT["conllu"] = partial(FROM_FORMAT["conllu"], dep=True, strip_suffixes=False)


def get_terminals(unit, visited=None):
    if visited is None:
        visited = set()
    outgoing = {e for e in set(unit) - visited if not e.attrib.get("remote")}
    terminals = [t for e in outgoing for t in get_terminals(e.child, visited | outgoing)]
    if not unit.tag or unit.tag in (layer0.NodeTags.Word, layer0.NodeTags.Punct):  # UD: all nodes; UCCA: only terminals
        terminals.append(unit)
    return terminals


def is_scene(node):
    return node.is_scene() and sum(len(t.text) for t in get_terminals(node.state or node.process)) > 2 \
        and len(node.get_terminals(punct=False)) > 1


def subordinate_clauses(passage):
    for unit in passage.layer(layer1.LAYER_ID).all:
        if unit.tag:  # UCCA
            if unit.tag == layer1.NodeTags.Foundational:
                yield from map(get_terminals, filter(layer1.FoundationalNode.is_scene, unit.elaborators))
        else:  # UD
            children = [e.child for e in unit if e.tag.partition(":")[0] in ("acl",)]
            if children:  # UD and there is a subordinate clause
                yield from map(get_terminals, children)


def evaluate(guessed, ref, errors=False):
    assert guessed.ID == ref.ID, "Inconsistent order of passages: %s != %s" % (guessed.ID, ref.ID)
    guessed_yields, ref_yields = [list(subordinate_clauses(p)) for p in (guessed, ref)]
    punct_positions = {t.position for yields in (guessed_yields, ref_yields) for y in yields for t in y
                       if t.tag in (layer0.NodeTags.Punct, PUNCT_TAG)}
    g, r = [set(frozenset(t.position for t in y) - punct_positions for y in yields)
            for yields in (guessed_yields, ref_yields)]
    common = g & r
    only_g = g - common
    only_r = r - common
    stat = SummaryStatistics(len(common), len(only_g), len(only_r))
    if errors:
        for y in sorted(only_r, key=min):
            print("https://github.com/danielhers/UCCA_English-EWT/blob/master-images/%s.svg" % ref.ID,
                  ref.ID[:-3], " ".join(ref.by_id("0.%d" % (i+1)).token.text for i in y), sep="\t")
    elif g or r:
        print(guessed.ID, "F1 = %.3f" % stat.f1, sep="\t")
        for yields in guessed_yields, ref_yields:
            clauses = [" ".join(map(str, sorted(y, key=attrgetter("position")))) for y in yields]
            print(*clauses, sep="\t")
        print()
    return stat


def main(args):
    guessed, ref = [get_passages(f, converters=FROM_FORMAT) for f in (args.guessed, args.ref)]
    stats = SummaryStatistics.aggregate([evaluate(g, r, errors=args.errors) for g, r in zip(guessed, ref)])
    stats.print()


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate yields of subordinate clauses or elaborator scenes")
    argparser.add_argument("guessed", help="File or directory for graphs to evaluate")
    argparser.add_argument("ref", help="File or directory for graphs to use as reference")
    argparser.add_argument("-e", "--errors", action="store_true", help="Print just false negatives, with image links")
    main(argparser.parse_args())
