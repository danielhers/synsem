import sys
from itertools import product, groupby

import pandas as pd
from glob import glob
from operator import attrgetter

from extract_eval import UCCA_RELS, UD_RELS, REF_COUNTS_COLUMNS, Data, Report, strip, combine

PRED_COUNTS_COLUMNS = pd.Series(list(map("_".join, product(
    ["UCCA", "CoNLL-U"], UCCA_RELS + UD_RELS, ["labeled"], ["guessed"]))))

MATCHES_COUNTS_COLUMNS = pd.Series(list(map("_".join, product(
    ["UCCA", "CoNLL-U"], UCCA_RELS + UD_RELS, ["labeled"], ["matches"]))))


def eval_corpus(corpus, reports):
    key = attrgetter("model", "features")
    data = sorted(r.read() for _, rs in groupby(sorted(reports), key=key) for r in rs)
    print(corpus.name)
    for tup in groupby(sorted(data, key=Data.ref), key=Data.ref):
        eval_ref(*tup)


def eval_ref(ref, data):
    key = attrgetter("report.model", "report.features")
    data = sorted(data, key=key)
    columns = list(map(strip, sorted(set(c for d in data for c in d.column_names()[6:]))))
    print(*(2 * [""] + columns), sep="\t")
    count_columns = [c for c in REF_COUNTS_COLUMNS if ref in c]
    count_columns = dict(zip(map(strip, count_columns), count_columns))
    counts = combine(data, "counts").astype(int)
    counts["zero"] = 0
    ccs = [count_columns[c] for c in columns]
    ccs = [c if c in counts.columns.tolist() else "zero" for c in ccs]
    print(*(["reference", ref] + [counts[ccs].to_csv(header=False, index=False, sep="\t")]), sep="\t", end="")
    for tup in groupby(data, key=key):
        eval_model_features(*tup)


def eval_model_features(model_features, data):
    model, features = model_features
    model = model.replace("v1-sentences", "ucca")
    data = list(data)
    df = combine(data, "counts").astype(int)
    columns = df.columns.tolist()
    for title, cs in ("predicted", PRED_COUNTS_COLUMNS), ("matched", MATCHES_COUNTS_COLUMNS):
        cs = [c for c in cs if c in columns]
        print(title, model + features,
              df[cs].to_csv(header=False, index=False, sep="\t").strip().replace("\n", "\n\t\t\t"), sep="\t")


def main():
    reports = [Report.create(f) for p in sys.argv[1:] or
               ["eval/*/ucca/*.csv", "eval/*/ud/*.csv"] for f in glob(p) or [p]]
    key = attrgetter("corpus")
    for tup in groupby(sorted(reports, key=key), key=key):
        eval_corpus(*tup)


if __name__ == "__main__":
    main()
