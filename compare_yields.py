from argparse import ArgumentParser
from functools import partial
from operator import attrgetter

from semstr.convert import FROM_FORMAT
from typing import Set, Tuple, List
from ucca import layer0, layer1
from ucca.core import Node, Passage, Edge
from ucca.evaluation import SummaryStatistics
from ucca.ioutil import get_passages

IMAGE_LINK_FORMAT = "https://github.com/danielhers/UCCA_English-EWT/blob/v1-guidelines-images/%s.svg"
UD_LINK_FORMAT = "https://github.com/danielhers/UCCA_English-EWT/blob/v1-guidelines-ud/%s.conllu"


class Evaluator:
    def __init__(self, relations: Tuple[str] = None, errors: bool = False, all_yields: bool = False, **kwargs):
        del kwargs
        self.relations = relations
        self.errors = errors
        self.all_yields = all_yields

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
            for edge in unit:
                if (self.relations is None or edge.tag in self.relations) and edge.tag != layer1.EdgeTags.Terminal \
                        and not edge.attrib.get("remote") and not edge.child.attrib.get("implicit"):
                    yield self.get_terminals(edge.child), edge.tag

    @staticmethod
    def join_tags(yields, punct_positions):
        ret = {}
        for y, t in yields:
            y = frozenset(t.position for t in y) - punct_positions - {0}
            if y:
                ret.setdefault(y, []).append(t)
        return ret

    @staticmethod
    def get_tags(tags, y):
        return "|".join(sorted(tags.get(y, ())))

    @staticmethod
    def to_text(p, y):
        return " ".join(p.by_id("0.%d" % i).text for i in sorted(y))

    def evaluate(self, guessed: Passage, ref: Passage):
        g, gtags, gyields, only_r, r, rtags, ryields, stat = self.evaluate_yields(guessed, ref)
        image_link = IMAGE_LINK_FORMAT % ref.ID
        ud_link = UD_LINK_FORMAT % ref.ID
        if self.all_yields:
            for y in sorted(g | r, key=min):
                print(image_link, ud_link, self.get_tags(gtags, y), self.get_tags(rtags, y), ref.ID[:-3],
                      self.to_text(ref, y), sep="\t")
        elif self.errors:
            if only_r:
                for y in sorted(only_r, key=min):
                    print(image_link, ud_link, ref.ID[:-3], self.to_text(ref, y), sep="\t")
        elif g or r:
            print(guessed.ID, "F1 = %.3f" % stat.f1, sep="\t")
            for yields in gyields, ryields:
                texts = [" ".join(map(str, sorted(y, key=attrgetter("position")))) for y, _ in yields]
                print(*texts, sep="\t")
            print()
        return stat

    def evaluate_yields(self, guessed, ref):
        assert guessed.ID == ref.ID, "Inconsistent order of passages: %s != %s" % (guessed.ID, ref.ID)
        gyields, ryields = [list(self.get_yields(p)) for p in (guessed, ref)]
        punct_positions = {t.position for yields in (gyields, ryields) for y, _ in yields for p in (guessed, ref)
                           for t in y if self.is_excluded(p.layer(layer0.LAYER_ID).by_position(t.position))}
        gtags, rtags = [self.join_tags(yields, punct_positions) for yields in (gyields, ryields)]
        g, r = list(map(set, (gtags, rtags)))
        common = g & r
        only_g = g - common
        only_r = r - common
        stat = SummaryStatistics(len(common), len(only_g), len(only_r))
        return g, gtags, gyields, only_r, r, rtags, ryields, stat

    def is_excluded(self, terminal):
        return terminal.punct

    def converters(self):
        from_format = dict(FROM_FORMAT)
        from_format["conllu"] = partial(from_format["conllu"], dep=True, enhanced=False)
        return from_format

    def run(self, guessed: List[str], ref: List[str], **kwargs):
        del kwargs
        guessed, ref = [get_passages(f, converters=self.converters()) for f in (guessed, ref)]
        stats = SummaryStatistics.aggregate([self.evaluate(g, r) for g, r in zip(guessed, ref)])
        stats.print()

    @staticmethod
    def add_arguments(p):
        p.add_argument("guessed", help="File or directory for graphs to evaluate")
        p.add_argument("ref", help="File or directory for graphs to use as reference")
        g = p.add_mutually_exclusive_group()
        g.add_argument("-e", "--errors", action="store_true", help="Print just false negatives, with image links")
        g.add_argument("-a", "--all-yields", action="store_true", help="Print all examples, with image links")
        p.add_argument("-r", "--relations", nargs="+",
                       help="Dependency relation of dependent clause to use for extracting UD yields")


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate all yields of units in graphs from both sources")
    Evaluator.add_arguments(argparser)
    Evaluator(**vars(argparser.parse_args())).run(**vars(argparser.parse_args()))
