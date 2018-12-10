from argparse import ArgumentParser
from ucca import layer1
from ucca.core import Passage
from ucca.layer1 import EdgeTags

from compare_yields import Evaluator

PREDICATE_RELATIONS = ("root", "acl", "advcl", "ccomp", "csubj", "parataxis", "xcomp")
LINK_RELATIONS = ("appos", "conj", "list")

NON_CENTER = {EdgeTags.ParallelScene, EdgeTags.Participant, EdgeTags.Process, EdgeTags.State, EdgeTags.Adverbial,
              EdgeTags.Ground, EdgeTags.Elaborator, EdgeTags.Function, EdgeTags.Connector, EdgeTags.Relator,
              EdgeTags.Time, EdgeTags.Quantifier, EdgeTags.Linker}


class LostSceneEvaluator(Evaluator):
    def get_yields(self, passage: Passage):
        for unit in passage.layer(layer1.LAYER_ID).all:
            if unit.tag:  # UCCA main relations
                if unit.ftag in (EdgeTags.Process, EdgeTags.State):
                    yield self.get_terminals(unit.fparent), unit.ftag
            elif unit.incoming:  # UD predicate
                ftag = tag = unit.incoming[0].tag
                funit = unit
                while ftag in LINK_RELATIONS:
                    funit = funit.incoming[0].parent
                    ftag = funit.incoming[0].tag if funit.incoming else None
                if ftag in PREDICATE_RELATIONS:
                    yield self.get_terminals(unit), tag


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate verbs against main relations")
    LostSceneEvaluator.add_arguments(argparser)
    LostSceneEvaluator(**vars(argparser.parse_args())).run(**vars(argparser.parse_args()))
