from collections import Counter

from argparse import ArgumentParser
from ucca.core import Passage

from compare_yields import Evaluator


class AverageLengthCalculator(Evaluator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counts = {}

    def evaluate(self, guessed: Passage, ref: Passage):
        g, gtags, gyields, only_r, r, rtags, ryields, stat = self.evaluate_yields(guessed, ref)
        for tags in gtags, rtags:
            for y, ts in tags.items():
                for t in ts:
                    self.counts.setdefault(t, Counter())[len(y)] += 1
        return stat

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)
        for t, hist in sorted(self.counts.items()):
            print(t, *[hist[i] for i in range(1, 1 + len(hist))], sep="\t")
        print()
        print(*sorted(self.counts), sep="\t")
        print(*["%.1f" % (sum(i * hist[i] for i in range(1, 1 + len(hist))) / sum(hist.values()))
                for _, hist in sorted(self.counts.items())], sep="\t")


if __name__ == "__main__":
    argparser = ArgumentParser(description="Calculate average length per category")
    AverageLengthCalculator.add_arguments(argparser)
    AverageLengthCalculator(**vars(argparser.parse_args())).run(**vars(argparser.parse_args()))
