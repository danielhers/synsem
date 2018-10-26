from argparse import ArgumentParser

from semstr.convert import FROM_FORMAT
from ucca import layer1
from ucca.evaluation import SummaryStatistics
from ucca.ioutil import get_passages_with_progress_bar


def conj_spans(passage):
    for node in passage.layer(layer1.LAYER_ID).all:
        if node.tag == layer1.NodeTags.Foundational and node.connector:
            yield tuple(sorted(tuple(sorted(t.position for t in c.get_terminals(punct=False))) for c in node.centers))


def count(guessed, ref):
    guessed = set(guessed)
    ref = set(ref)
    common = guessed & ref
    return SummaryStatistics(len(common), len(guessed) - len(common), len(ref) - len(common))


def main(args):
    guessed, ref = [map(conj_spans, get_passages_with_progress_bar(f, converters=FROM_FORMAT))
                    for f in (args.guessed, args.ref)]
    stats = SummaryStatistics.aggregate([count(g, r) for g, r in zip(guessed, ref)])
    stats.print()


if __name__ == "__main__":
    argparser = ArgumentParser(description="Evaluate conjunct spans")
    argparser.add_argument("guessed", help="File or directory for graphs to evaluate")
    argparser.add_argument("ref", help="File or directory for graphs to use as reference")
    main(argparser.parse_args())
