from argparse import ArgumentParser
from functools import partial
from semstr.convert import FROM_FORMAT
from ucca import layer1
from ucca.core import Passage
from ucca.evaluation import SummaryStatistics
from ucca.layer1 import EdgeTags

from compare_yields import Evaluator


class SecondaryVerbEvaluator(Evaluator):
    def __init__(self, *args, **kwargs):
        kwargs["relations"] = (EdgeTags.Adverbial,)
        super().__init__(*args, **kwargs)

    def get_yields(self, passage: Passage):
        for unit in passage.layer(layer1.LAYER_ID).all:
            if unit.tag:
                for edge in unit:
                    if edge.tag in self.relations \
                            and not edge.attrib.get("remote") and not edge.child.attrib.get("implicit"):
                        yield self.get_terminals(edge.child), edge.tag
            else:
                if unit.token and unit.token.pos == "VERB":
                    for edge in unit:
                        if edge.tag not in {EdgeTags.Punctuation}:
                            yield [unit], edge.tag


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate verbs against main relations")
    SecondaryVerbEvaluator.add_arguments(argparser)
    SecondaryVerbEvaluator(**vars(argparser.parse_args())).run(**vars(argparser.parse_args()))
