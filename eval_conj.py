from argparse import ArgumentParser
from spacy.parts_of_speech import CCONJ
from ucca import layer1
from ucca.core import Passage
from ucca.textutil import Attr

from compare_yields import Evaluator

COORDINATION_UD_TAGS = {"cc", "conj"}


class ConjunctEvaluator(Evaluator):
    def get_yields(self, passage: Passage):
        for unit in passage.layer(layer1.LAYER_ID).all:
            if unit.tag:  # UCCA
                if unit.tag == layer1.NodeTags.Foundational:
                    if unit.connector:  # nominal coordination
                        yield from map(self.get_terminals, unit.centers)
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
                                    terminals += self.get_terminals(edge.child)
                                    continue
                                if terminals:
                                    yield terminals
                                    terminals = []
                            if terminals:
                                yield terminals
            else:  # UD
                children = [e.child for e in unit if e.tag == "conj"]
                if children:  # UD and there is a coordination
                    yield from (self.get_terminals(c, excluded_tags=COORDINATION_UD_TAGS) for c in [unit] + children)


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate conjunct yields")
    ConjunctEvaluator.add_arguments(argparser)
    ConjunctEvaluator(**vars(argparser.parse_args())).run(**vars(argparser.parse_args()))
