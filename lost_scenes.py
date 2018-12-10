from argparse import ArgumentParser
from functools import partial
from semstr.convert import FROM_FORMAT
from ucca import layer1
from ucca.core import Passage
from ucca.layer1 import EdgeTags

from compare_yields import Evaluator

PREDICATE_RELATIONS = {"root", "acl", "advcl", "ccomp", "csubj", "parataxis", "xcomp"}
LINK_RELATIONS = {"appos", "conj", "list"}

NON_CENTER = {EdgeTags.ParallelScene, EdgeTags.Participant, EdgeTags.Process, EdgeTags.State, EdgeTags.Adverbial,
              EdgeTags.Ground, EdgeTags.Elaborator, EdgeTags.Function, EdgeTags.Connector, EdgeTags.Relator,
              EdgeTags.Time, EdgeTags.Quantifier, EdgeTags.Linker}


class LostSceneEvaluator(Evaluator):
    def get_yields(self, passage: Passage):
        for unit in passage.layer(layer1.LAYER_ID).all:
            if unit.ftag in (EdgeTags.Process, EdgeTags.State):
                yield self.get_terminals(unit.fparent), unit.ftag
            elif passage.extra.get("format") == "conllu":  # UD predicate
                ftag = tag = unit.incoming[0].tag if unit.incoming else None
                funit = unit
                while ftag in LINK_RELATIONS:
                    funit = funit.incoming[0].parent
                    ftag = funit.incoming[0].tag if funit.incoming else None
                if ftag in PREDICATE_RELATIONS or ftag is None:
                    yield self.get_terminals(unit, excluded_tags=LINK_RELATIONS | {"cc"}), tag

    def is_excluded(self, terminal):
        return super().is_excluded(terminal) or terminal.parents[0].ftag == EdgeTags.Linker or \
               terminal.parents[0].ftag == EdgeTags.Center and terminal.parents[0].parents[0].ftag == EdgeTags.Linker

    def converters(self):
        from_format = dict(FROM_FORMAT)
        from_format["conllu"] = partial(from_format["conllu"], enhanced=False)
        return from_format


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate verbs against main relations")
    LostSceneEvaluator.add_arguments(argparser)
    LostSceneEvaluator(**vars(argparser.parse_args())).run(**vars(argparser.parse_args()))
