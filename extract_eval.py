import sys
from collections import namedtuple
from itertools import product, chain, groupby

import os
import pandas as pd
import re
from glob import glob
from operator import attrgetter


def split(s):
    # print(s)
    return s.split("\t")


UCCA_RELS = split("A	C	D	E	F	G	H	L	N	P	R	S	U")
ALL_UD_RELS = split("acl	advcl	advmod	amod	appos	aux	case	cc	ccomp	compound	conj	cop	csubj"
                    "	dep	det	discourse	expl	fixed	flat	goeswith	head	iobj	list	mark	nmod"
                    "	nsubj	nummod	obj	obl	orphan	parataxis	punct	root	vocative	xcomp")
UD_RELS = split("acl	advcl	advmod	amod	appos	aux	case	cc	ccomp	compound	conj	cop	det"
                "	expl	iobj	mark	nmod	nsubj	nummod	obj	obl	parataxis	xcomp")

COLUMNS = pd.Series(list(map("_".join, chain(
    product(["UCCA", "CoNLL-U"], ["primary", "remote"], ["unlabeled", "labeled"], ["precision", "recall", "f1"]),
    product(["UCCA", "CoNLL-U"], UCCA_RELS + UD_RELS, ["labeled"], ["f1"])))))

COUNTS_COLUMNS = pd.Series(list(map("_".join, product(
    ["UCCA", "CoNLL-U"], UCCA_RELS + UD_RELS, ["labeled"], ["ref", "guessed", "matches"]))))

REF_COUNTS_COLUMNS = pd.Series(list(map("_".join, product(
    ["UCCA", "CoNLL-U"], UCCA_RELS + UD_RELS, ["labeled"], ["ref"]))))

Corpus = namedtuple("Corpus", ("index", "name"))

CORPORA = {
    "ewt":         Corpus(0,  "English EWT sentences with UCCA annotation"),
    "ewt-dev":     Corpus(1,  "English EWT UD dev"),
    "ewt-test":    Corpus(2,  "English EWT UD test"),
    "wiki-dev":    Corpus(3,  "English Wiki dev"),
    "wiki-test":   Corpus(4,  "English Wiki test"),
    "20k":         Corpus(5,  "English 20K"),
    "20k-fr-dev":  Corpus(6,  "French 20K dev"),
    "20k-fr-test": Corpus(7,  "French 20K test"),
    "fr-gsd-dev":  Corpus(8,  "French GSD dev"),
    "fr-gsd-test": Corpus(9,  "French GSD test"),
    "20k-de-dev":  Corpus(10, "German 20K dev"),
    "20k-de-test": Corpus(11, "German 20K test"),
    "de-gsd-dev":  Corpus(12, "German GSD dev"),
    "de-gsd-test": Corpus(13, "German GSD test"),
}


class Data(namedtuple("Data", ("columns", "count_columns", "report", "scores", "counts"))):
    def column_names(self):
        return [c for c, e in zip(COLUMNS, self.columns) if e]

    def counts_column_names(self):
        return [c for c, e in zip(COUNTS_COLUMNS, self.count_columns) if e]

    def ref(self):  # UCCA/CoNLL-U, indicating the format of the reference
        try:
            column_name = (self.column_names() or self.counts_column_names())[0]
        except IndexError as e:
            raise ValueError("No relevant columns found in '%s'" % self.report.filename) from e
        try:
            return column_name.partition("_")[0]  # e.g. UCCA_primary_labeled_precision -> UCCA
        except IndexError as e:
            raise ValueError("Failed to parse column name '%s'" % column_name) from e


class Report(namedtuple("Report", ("is_ref", "model", "features", "ref", "labeled", "counts", "corpus", "filename"))):
    @staticmethod
    def create(f):
        basename = os.path.basename(re.match(r"(.*?)\.[a-z.]+", f).group(1))
        m = re.match(r"(.*-\d+)-(.*)", basename)
        path = f.split(os.sep)
        # noinspection PyTypeChecker
        fields = (bool(m),) + (basename, "") + \
                 (path[-2], "unlabeled" not in f, "counts" in f, CORPORA[path[-3]], f)
        return Report(*fields)

    def read(self):
        try:
            df = pd.read_csv(self.filename)
        except pd.errors.EmptyDataError as e:
            raise IOError("Failed reading '%s'" % self.filename) from e
        cs = COLUMNS.isin(list(df.columns))
        ccs = COUNTS_COLUMNS.isin(list(df.columns))
        return Data(columns=list(cs), count_columns=list(ccs), report=self,
                    scores=(df[list(COLUMNS[cs])] * 100).round(1), counts=df[list(COUNTS_COLUMNS[ccs])])


def eval_corpus(corpus, reports):
    key = attrgetter("model", "features")
    data = sorted(r.read() for _, rs in groupby(sorted(reports), key=key) for r in rs)
    print()
    columns = list(map(strip, sorted(set(c for d in data for c in d.column_names()[6:]))))
    print(*([corpus.name] + 14 * [""] + columns), sep="\t")
    for tup in groupby(sorted(data, key=Data.ref), key=Data.ref):
        eval_ref(*tup, columns=columns)


def eval_ref(ref, data, columns=None):
    print()
    key = attrgetter("report.model", "report.features")
    data = sorted(data, key=key)
    count_columns = [c for c in COUNTS_COLUMNS if ref in c]
    count_columns = dict(zip(map(strip, count_columns), count_columns))
    counts = combine(data, "counts").astype(int)
    counts["zero"] = 0
    ccs = [count_columns[c] for c in columns]
    ccs = [c if c in counts.columns.tolist() else "zero" for c in ccs]
    print(*([ref] + 14 * [""] + [counts[ccs].to_csv(header=False, index=False, sep="\t")]), sep="\t", end="")
    for tup in groupby(data, key=key):
        eval_model_features(*tup)


def eval_model_features(model_features, data):
    model, features = model_features
    model = model.replace("v1-sentences", "ucca")
    data = list(data)
    df = combine(data)
    if not df.eq(100).all().all():
        columns = df.columns.tolist()
        cs = [c for c in COLUMNS if c in columns]
        # rels = strip(cs)
        # expected = UCCA_RELS + UD_RELS
        # assert rels[-len(expected):] == expected, "Missing fine-grained columns in %s %s for relations: %s" % (
        #     model, features, ", ".join(r for r in expected if r not in rels) or rels)
        # noinspection PyTypeChecker
        print("", model, features,
              df[cs].to_csv(header=False, index=False, sep="\t").strip().replace("\n", "\n\t\t\t"), sep="\t")


def combine(data, attr="scores"):
    df = getattr(data[0], attr)
    for data in data[1:]:
        df = df.combine_first(getattr(data, attr))
    return df


def strip(c):
    for s in "UCCA_", "CoNLL-U_", "_labeled", "_f1", "_ref":
        c = c.replace(s, "")
    return c


def main():
    reports = [Report.create(f) for p in sys.argv[1:] or
               ["eval/*/ucca/*.csv", "eval/*/ud/*.csv"] for f in glob(p) or [p]]
    key = attrgetter("corpus")
    for tup in groupby(sorted(reports, key=key), key=key):
        eval_corpus(*tup)


if __name__ == "__main__":
    main()
