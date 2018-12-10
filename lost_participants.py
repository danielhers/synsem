from itertools import groupby

from argparse import ArgumentParser
from functools import partial
from operator import itemgetter
from semstr.convert import FROM_FORMAT
from ucca import layer0
from ucca.core import Passage
from ucca.layer1 import EdgeTags

from compare_yields import Evaluator


class Scene:
    def __init__(self, yields):
        self.yields = yields

    def __repr__(self):
        return repr(self.yields)

    def __hash__(self):
        return 0

    def __eq__(self, other):
        return bool(frozenset(self.yields).intersection(other.yields))


class LostParticipantEvaluator(Evaluator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.relations = (EdgeTags.Participant, "nsubj", "obj", "iobj", "csubj", "ccomp", "xcomp", "obl")

    def get_yields(self, passage: Passage):
        yield from [(parent_id, self.get_terminals(unit), tag) for parent_id, unit_tags in
                    groupby(sorted(super().get_units(passage), key=self.parent_id), key=self.parent_id)
                    for unit, tag in unit_tags]

    @staticmethod
    def parent_id(unit_tag):
        unit, tag = unit_tag
        return unit.fparent.ID

    def evaluate_yields(self, guessed, ref):
        assert guessed.ID == ref.ID, "Inconsistent order of passages: %s != %s" % (guessed.ID, ref.ID)
        gyields, ryields = [list(self.get_yields(p)) for p in (guessed, ref)]
        punct_positions = {t.position for yields in (gyields, ryields) for _, y, _ in yields for p in (guessed, ref)
                           for t in y if self.is_excluded(p.layer(layer0.LAYER_ID).by_position(t.position))}
        gtags, rtags = [self.join_tags(yields, punct_positions) for yields in (gyields, ryields)]
        g, only_r, r, stat = self.evaluate_tags(gtags, rtags)
        gyields = [(y, t) for _, y, t in gyields]
        ryields = [(y, t) for _, y, t in ryields]
        return g, gtags, gyields, only_r, r, rtags, ryields, stat

    @staticmethod
    def join_tags(yields, punct_positions):
        ret = {}
        for parent_id, yield_tags in groupby(sorted(yields, key=itemgetter(0)), key=itemgetter(0)):
            ys = []
            ts = []
            for _, y, t in yield_tags:
                y = frozenset(t.position for t in y) - punct_positions - {0}
                if y:
                    ys.append(y)
                    ts.append(t)
            if ys:
                ret.setdefault(Scene(ys), []).extend(ts)
        return ret

    def converters(self):
        from_format = dict(FROM_FORMAT)
        from_format["conllu"] = partial(from_format["conllu"], enhanced=False)
        return from_format


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate verbs against main relations")
    LostParticipantEvaluator.add_arguments(argparser)
    LostParticipantEvaluator(**vars(argparser.parse_args())).run(**vars(argparser.parse_args()))
