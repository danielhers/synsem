#!/usr/bin/env bash

. .virtualenv/bin/activate
python setup.py install >/dev/null || exit 1

DATA=../UCCA_English-Wiki/sentences/dev
PARSED=parsed
OUT=out/eval/wiki-dev
mkdir -p ${OUT}/{,all/}{ucca,ud}

python semstr/convert.py ${PARSED}/conllu/udpipe/wiki-dev.conllu -o ${PARSED}/xml/udpipe/wiki-dev --extra-normalization --label-map=semstr/util/resources/ud_ucca_label_map.csv
#python semstr/convert.py ${PARSED}/conllu/udpipe/wiki-dev.enhanced.conllu -o ${PARSED}/xml/udpipe.enhanced/wiki-dev --extra-normalization --label-map=semstr/util/resources/ud_ucca_label_map.csv

#for MODEL in udpipe.enhanced; do
for MODEL in ucca-bilstm-20180917 udpipe; do
    GUESSED=${PARSED}/xml/${MODEL}/wiki-dev
    REF=${DATA}
    python semstr/evaluate.py ${GUESSED} ${REF} --unlabeled -s ${OUT}/ucca/${MODEL}.unlabeled.csv -q
    python semstr/evaluate.py ${GUESSED} ${REF} --constructions=categories -s ${OUT}/ucca/${MODEL}.csv -o ${OUT}/all/ucca/${MODEL}.csv -q
    python semstr/evaluate.py ${GUESSED} ${REF} --constructions=categories -s ${OUT}/ud/${MODEL}.csv -o ${OUT}/all/ud/${MODEL}.csv -q --ref-yield-tags=${PARSED}/conllu/udpipe/wiki-dev
done

python extract_eval.py ${OUT}/{ucca,ud}/*.csv
