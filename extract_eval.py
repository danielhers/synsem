import os
import re
import sys
from glob import glob
from itertools import product, chain, groupby

import pandas as pd


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


def parts(f):
    basename = os.path.basename(re.match(r"(.*?)\.[a-z.]+", f).group(1))
    m = re.match(r"(.*-\d+)-(.*)", basename)
    dirname = os.path.basename(os.path.dirname(f))
    # noinspection PyTypeChecker
    return (bool(m),) + (m.groups() if m else (basename, "")) + (dirname, "unlabeled" not in f, f)


def read(t):
    df = pd.read_csv(t[-1])
    cs = COLUMNS.isin(list(df.columns))
    return (list(cs),) + t[:-1] + ((df[list(COLUMNS[cs])] * 100).round(1),)


def main():
    filenames = [parts(f) for p in sys.argv[1:] or ["out/eval/ucca/*.csv", "out/eval/ud/*.csv"] for f in glob(p) or [p]]
    tuples1 = sorted(read(t) for _, ts in groupby(sorted(filenames), key=lambda l: l[1:3]) for t in ts)
    for ref, tuples2 in groupby(tuples1, lambda t: [c for c, e in zip(COLUMNS, t[0]) if e][0].partition("_")[0]):
        print()
        print(ref)
        for (model, features), tuples3 in groupby(sorted(tuples2, key=lambda t: t[2:4]), key=lambda t: t[2:4]):
            model = model.replace("v1-sentences", "ucca")
            tuples3 = list(tuples3)
            df = tuples3[0][-1]
            for t in tuples3[1:]:
                df = df.combine_first(t[-1])
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


if __name__ == "__main__":
    main()
