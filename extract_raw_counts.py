import sys
from itertools import product, groupby

import pandas as pd
from glob import glob
from operator import attrgetter

from extract_eval import UCCA_RELS, ALL_UD_RELS, REF_COUNTS_COLUMNS, Data, Report, strip, combine

PRED_COUNTS_COLUMNS = pd.Series(list(map("_".join, product(
    ["UCCA", "CoNLL-U"], UCCA_RELS + ALL_UD_RELS, ["labeled"], ["guessed"]))))

MATCHES_COUNTS_COLUMNS = pd.Series(list(map("_".join, product(
    ["UCCA", "CoNLL-U"], UCCA_RELS + ALL_UD_RELS, ["labeled"], ["matches"]))))


def eval_corpus(corpus, data, columns=None):
    print(corpus.name)
    for tup in groupby(sorted(filter(Data.ref, data), key=Data.ref), key=Data.ref):
        eval_ref(*tup, columns=columns)


def eval_ref(ref, data, columns=None):
    key = attrgetter("report.model", "report.features")
    data = sorted(data, key=key)
    if columns is None:
        columns = get_columns(data)
    else:
        print()
    count_columns = [c for c in REF_COUNTS_COLUMNS if ref in c]
    count_columns = dict(zip(map(strip, count_columns), count_columns))
    counts = combine(data, "counts").astype(int)
    counts["zero"] = 0
    ccs = [count_columns[c] for c in columns]
    ccs = [c if c in counts.columns.tolist() else "zero" for c in ccs]
    print(*(["reference", ref] + [counts[ccs].to_csv(header=False, index=False, sep="\t")]), sep="\t", end="")
    for tup in groupby(data, key=key):
        eval_model_features(*tup)


def get_columns(data):
    columns = sorted(set(strip(c) for d in data for c in d.column_names()[6:]))
    print(*(2 * [""] + columns), sep="\t")
    return columns


def eval_model_features(model_features, data):
    model, features = model_features
    model = model.replace("v1-sentences", "ucca")
    data = list(data)
    df = combine(data, "counts").astype(int)
    columns = df.columns.tolist()
    for row in (["guessed"], ["matches"], ["matches", "unlabeled"]):
        all_columns = pd.Series(list(map("_".join, product(
            ["UCCA", "CoNLL-U"], UCCA_RELS + ALL_UD_RELS, [row[1] if len(row) > 1 else "labeled"], [row[0]]))))
        cs = [c for c in all_columns if c in columns]
        print(row[-1], model + features,
              df[cs].to_csv(header=False, index=False, sep="\t").strip().replace("\n", "\n\t\t\t"), sep="\t")


def main():
    reports = [Report.create(f) for p in sys.argv[1:] or
               ["eval/*/ucca/*.csv", "eval/*/ud/*.csv"] for f in glob(p) or [p]]
    key = attrgetter("report.corpus")
    data = [r.read() for r in reports]
    columns = get_columns(data)
    for tup in groupby(sorted(data, key=key), key=key):
        eval_corpus(*tup, columns=columns)


if __name__ == "__main__":
    main()
