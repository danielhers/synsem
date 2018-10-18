import sys
from collections import namedtuple
from itertools import product, chain, groupby

import os
import pandas as pd
import re
from glob import glob
from operator import attrgetter


def split(s):
    print(s)
    return s.split("\t")


UCCA_RELS = split("A	C	D	E	F	G	H	L	N	P	R	S	U")
UD_RELS = split("acl	advcl	advmod	amod	appos	aux	case	cc	ccomp	compound	conj	cop	"
                "det	discourse	expl	fixed	flat	iobj	mark	"
                "nmod	nsubj	nummod	obj	obl	parataxis	punct	root	xcomp")

COLUMNS = pd.Series(list(map("_".join, chain(
    product(["UCCA", "CoNLL-U"], ["primary", "remote"], ["unlabeled", "labeled"], ["precision", "recall", "f1"]),
    product(["UCCA", "CoNLL-U"], UCCA_RELS + UD_RELS, ["labeled"], ["f1"])))))


class Data(namedtuple("Data", ("columns", "report", "scores"))):
    def column_names(self):
        return [c for c, e in zip(COLUMNS, self.columns) if e]

    def ref(self):
        return self.column_names()[0].partition("_")[0]  # e.g. UCCA_primary_labeled_precision -> UCCA


class Report(namedtuple("Report", ("is_ref", "model", "features", "ref", "labeled", "corpus", "filename"))):
    @staticmethod
    def create(f):
        basename = os.path.basename(re.match(r"(.*?)\.[a-z.]+", f).group(1))
        m = re.match(r"(.*-\d+)-(.*)", basename)
        path = f.split(os.sep)
        # noinspection PyTypeChecker
        fields = (bool(m),) + (m.groups() if m else (basename, "")) + (path[-2], "unlabeled" not in f, path[-3], f)
        return Report(*fields)

    def read(self):
        try:
            df = pd.read_csv(self.filename)
        except pd.errors.EmptyDataError as e:
            raise IOError("Failed reading '%s'" % self.filename) from e
        cs = COLUMNS.isin(list(df.columns))
        return Data(list(cs), self, (df[list(COLUMNS[cs])] * 100).round(1))


def eval_corpus(corpus, reports):
    key = attrgetter("model", "features")
    data = sorted(r.read() for _, rs in groupby(sorted(reports), key=key) for r in rs)
    print()
    print(corpus, data[0].column_names())
    for tup in groupby(data, key=Data.ref):
        eval_ref(*tup)


def eval_ref(ref, data):
    print()
    print(ref)
    key = attrgetter("report.model", "report.features")
    for tup in groupby(sorted(data, key=key), key=key):
        eval_model_features(*tup)


def eval_model_features(model_features, data):
    model, features = model_features
    model = model.replace("v1-sentences", "ucca")
    data = list(data)
    df = data[0].scores
    for data in data[1:]:
        df = df.combine_first(data.scores)
    if not df.eq(100).all().all():
        columns = df.columns.tolist()
        cs = [c for c in COLUMNS if c in columns]
        rels = [c.replace("UCCA_", "").replace("CoNLL-U_", "").replace("_labeled_f1", "") for c in cs]
        expected = UCCA_RELS + UD_RELS
        assert rels[-len(expected):] == expected, "Missing fine-grained columns in %s %s for relations: %s" % (
            model, features, ", ".join(r for r in expected if r not in rels) or rels)
        # noinspection PyTypeChecker
        print("", model, features,
              df[cs].to_csv(header=False, index=False, sep="\t").strip().replace("\n", "\n\t\t\t"), sep="\t")


def main():
    reports = [Report.create(f) for p in sys.argv[1:] or
               ["out/eval/*/ucca/*.csv", "out/eval/*/ud/*.csv"] for f in glob(p) or [p]]
    key = attrgetter("corpus")
    for tup in groupby(sorted(reports, key=key), key=key):
        eval_corpus(*tup)


if __name__ == "__main__":
    main()
