from argparse import ArgumentParser
from functools import partial
from semstr.convert import FROM_FORMAT
from ucca import layer1
from ucca.core import Passage
from ucca.evaluation import SummaryStatistics
from ucca.layer1 import EdgeTags

from compare_yields import Evaluator

PREDICATE_RELATIONS = {"root", "acl", "advcl", "ccomp", "csubj", "parataxis", "xcomp"}
LINK_RELATIONS = {"appos", "conj", "list"}


class LostSceneEvaluator(Evaluator):
    def get_yields(self, passage: Passage):
        for unit in passage.layer(layer1.LAYER_ID).all:
            if unit.ftag in (EdgeTags.Process, EdgeTags.State):
                yield self.get_terminals(unit), unit.ftag
            elif passage.extra.get("format") == "conllu":  # UD predicate
                ftag = tag = unit.incoming[0].tag if unit.incoming else None
                funit = unit
                while ftag in LINK_RELATIONS:
                    funit = funit.incoming[0].parent
                    ftag = funit.incoming[0].tag if funit.incoming else None
                if ftag in PREDICATE_RELATIONS or ftag is None:
                    heads = [e.child for e in unit if e.tag == "head"]
                    while heads:
                        unit = heads[0]
                        heads = [e.child for e in unit if e.tag == "head"]
                    yield self.get_terminals(unit), tag

    def is_excluded(self, terminal):
        return super().is_excluded(terminal) or terminal.parents[0].ftag == EdgeTags.Linker or \
               terminal.parents[0].ftag == EdgeTags.Center and terminal.parents[0].parents[0].ftag == EdgeTags.Linker

    def evaluate_tags(self, gtags, rtags):
        g, r = list(map(set, (gtags, rtags)))
        common = g & r
        only_r = r - common
        m = min((len(g), len(r)))
        stat = SummaryStatistics(m, len(g) - m, len(r) - m)
        return g, only_r, r, stat

    def converters(self):
        from_format = dict(FROM_FORMAT)
        from_format["conllu"] = partial(from_format["conllu"], enhanced=False)
        return from_format


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate verbs against main relations")
    LostSceneEvaluator.add_arguments(argparser)
    LostSceneEvaluator(**vars(argparser.parse_args())).run(**vars(argparser.parse_args()))
