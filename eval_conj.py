from argparse import ArgumentParser
from functools import partial

from semstr.convert import FROM_FORMAT
from ucca import layer1
from ucca.evaluation import SummaryStatistics, get_yield
from ucca.ioutil import get_passages_with_progress_bar


FROM_FORMAT["conllu"] = partial(FROM_FORMAT["conllu"], dep=True)


def conj_spans(passage):
    for node in passage.layer(layer1.LAYER_ID).all:
        if node.tag:  # UCCA
            if node.tag == layer1.NodeTags.Foundational and node.connector:
                yield frozenset(map(get_yield, node.centers))
        elif any(e.tag.partition(":")[0] == "cc" for e in node):  # UD and there is a coordination
            yield frozenset([get_yield(node)] + [get_yield(e.child) for e in node if e.tag.partition(":")[0] == "conj"])


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
