from argparse import ArgumentParser
from ucca import layer1
from ucca.core import Passage

from compare_yields import Evaluator


class DependentClauseEvaluator(Evaluator):
    # def is_scene(self, node):
    #     return node.is_scene() and sum(len(t.text) for t in self.get_terminals(node.state or node.process)) > 2 \
    #         and len(node.get_terminals(punct=False)) > 1

    def get_yields(self, passage: Passage):
        for unit in passage.layer(layer1.LAYER_ID).all:
            if unit.tag:  # UCCA
                if unit.tag == layer1.NodeTags.Foundational:
                    yield from map(self.get_terminals,
                                   filter(layer1.FoundationalNode.is_scene,
                                          unit.participants if self.relations == ["xcomp"] else unit.elaborators))
            else:  # UD
                children = [e.child for e in unit if e.tag in self.relations]
                if children:  # UD and there is a subordinate clause
                    yield from map(self.get_terminals, children)


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate yields of subordinate clauses or elaborator scenes")
    DependentClauseEvaluator.add_arguments(argparser)
    DependentClauseEvaluator(**vars(argparser.parse_args())).run(**vars(argparser.parse_args()))
