from argparse import ArgumentParser
from ucca import layer1
from ucca.core import Passage

from compare_yields import Evaluator

COORDINATION_UD_TAGS = {"cc", "conj"}


class NestedConjunctEvaluator(Evaluator):
    def get_yields(self, passage: Passage):
        for unit in passage.layer(layer1.LAYER_ID).all:
            if unit.tag:  # UCCA
                if unit.tag == layer1.NodeTags.Foundational:
                    if unit.connector and unit.fparent and unit.fparent.connector:  # nominal coordination
                        yield from map(self.get_terminals, unit.centers)
            else:  # UD
                children = [e.child for e in unit if e.tag == "conj" and any(e1.tag == "conj" for e1 in unit.incoming)]
                if children:  # UD and there is a coordination
                    yield from (self.get_terminals(c, excluded_tags=COORDINATION_UD_TAGS) for c in [unit] + children)


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate conjunct yields")
    NestedConjunctEvaluator.add_arguments(argparser)
    NestedConjunctEvaluator(**vars(argparser.parse_args())).run(**vars(argparser.parse_args()))
