from argparse import ArgumentParser
from functools import partial
from operator import attrgetter

from semstr.convert import FROM_FORMAT
from typing import Set, Tuple, List
from ucca import layer0, layer1
from ucca.core import Node, Passage, Edge
from ucca.evaluation import SummaryStatistics
from ucca.ioutil import get_passages

FROM_FORMAT["conllu"] = partial(FROM_FORMAT["conllu"], dep=True, enhanced=False)


class Evaluator:
    def __init__(self, relations: Tuple[str] = None, errors: bool = False, **kwargs):
        del kwargs
        self.relations = relations
        self.errors = errors

    def get_terminals(self, unit: Node, visited: Set[Edge] = None, excluded_tags: Set[str] = None):
        if visited is None:
            visited = set()
        outgoing = {e for e in set(unit) - visited if not e.attrib.get("remote")
                    and (not excluded_tags or e.tag not in excluded_tags)}
        terminals = [t for e in outgoing for t in self.get_terminals(e.child, visited | outgoing)]
        if not unit.tag or unit.tag in (layer0.NodeTags.Word, layer0.NodeTags.Punct):
            terminals.append(unit)  # UD: all nodes; UCCA: only terminals
        return terminals

    def get_yields(self, passage: Passage):
        for unit in passage.layer(layer1.LAYER_ID).all:
            if self.relations is None:
                yield self.get_terminals(unit)
            else:
                for edge in unit:
                    if edge.tag in self.relations:
                        terminals = self.get_terminals(edge.child)
                        yield terminals

    def evaluate(self, guessed: Passage, ref: Passage):
        assert guessed.ID == ref.ID, "Inconsistent order of passages: %s != %s" % (guessed.ID, ref.ID)
        guessed_yields, ref_yields = [list(self.get_yields(p)) for p in (guessed, ref)]
        punct_positions = {t.position for p, yields in zip((guessed, ref), (guessed_yields, ref_yields))
                           for y in yields for t in y if t.punct}
        g, r = [set(filter(None, (frozenset(t.position for t in y) - punct_positions - {0} for y in yields)))
                for yields in (guessed_yields, ref_yields)]
        common = g & r
        only_g = g - common
        only_r = r - common
        stat = SummaryStatistics(len(common), len(only_g), len(only_r))
        if self.errors:
            if only_r:
                for y in sorted(only_r, key=min):
                    print("https://github.com/danielhers/UCCA_English-EWT/blob/v1-guidelines-images/%s.svg" % ref.ID,
                          ref.ID[:-3], " ".join(ref.by_id("0.%d" % i).text for i in sorted(y)), sep="\t")
        elif g or r:
            print(guessed.ID, "F1 = %.3f" % stat.f1, sep="\t")
            for yields in guessed_yields, ref_yields:
                texts = [" ".join(map(str, sorted(y, key=attrgetter("position")))) for y in yields]
                print(*texts, sep="\t")
            print()
        return stat

    def run(self, guessed: List[str], ref: List[str], **kwargs):
        del kwargs
        guessed, ref = [get_passages(f, converters=FROM_FORMAT) for f in (guessed, ref)]
        stats = SummaryStatistics.aggregate([self.evaluate(g, r)
                                             for g, r in zip(guessed, ref)])
        stats.print()

    @staticmethod
    def add_arguments(p):
        p.add_argument("guessed", help="File or directory for graphs to evaluate")
        p.add_argument("ref", help="File or directory for graphs to use as reference")
        p.add_argument("-e", "--errors", action="store_true", help="Print just false negatives, with image links")
        p.add_argument("-r", "--relations", nargs="+",
                       help="Dependency relation of dependent clause to use for extracting UD yields")


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate all yields of units in graphs from both sources")
    Evaluator.add_arguments(argparser)
    Evaluator(**vars(argparser.parse_args())).run(**vars(argparser.parse_args()))
