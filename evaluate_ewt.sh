#!/usr/bin/env bash

. .virtualenv/bin/activate
python setup.py install >/dev/null || exit 1

DATA=../UCCA_English-EWT
OUT=out/eval
mkdir -p ${OUT}/{,all/}{ucca,ud}
TO_UD="-f conllu --label-map=semstr/util/resources/ucca_ud_label_map.csv"
TO_UCCA="--extra-normalization --label-map=semstr/util/resources/ud_ucca_label_map.csv"
REF_UD="--ref-yield-tags=${DATA}/ud"
REF_UCCA="--ref-yield-tags=${DATA}/v1-sentences"

# Gold UCCA to UD
CONVERTED=${DATA}/v1-sentences.converted.labeled
REF=${DATA}/ud
python semstr/convert.py ${DATA}/v1-sentences/* -o ${DATA}/v1-sentences.converted.labeled ${TO_UD}
python semstr/evaluate.py ${CONVERTED} ${REF} --unlabeled -s ${OUT}/ud/v1-sentences.converted.unlabeled.csv -q
python semstr/evaluate.py ${CONVERTED} ${REF} --constructions=categories -s ${OUT}/ucca/${CONVERTED##*/}.csv -o ${OUT}/all/ucca/${CONVERTED##*/}.csv -q ${REF_UCCA}
python semstr/evaluate.py ${CONVERTED} ${REF} --constructions=categories -s ${OUT}/ud/${CONVERTED##*/}.csv -o ${OUT}/all/ud/${CONVERTED##*/}.csv -q

for FEATURES in ud english-ewt-ud-2.2-conll18-180430; do
   for MODEL in ucca-bilstm-20180808- ucca-bilstm-nodep-20180611-; do
        # Parsed UCCA
        GUESSED=${DATA}/${MODEL}${FEATURES}
        REF=${DATA}/v1-sentences
        python semstr/evaluate.py ${GUESSED} ${REF} --unlabeled -s ${OUT}/ucca/${MODEL}${FEATURES}.unlabeled.csv -q
        python semstr/evaluate.py ${GUESSED} ${REF} --constructions=categories -s ${OUT}/ucca/${GUESSED##*/}.csv -o ${OUT}/all/ucca/${GUESSED##*/}.csv -q
        python semstr/evaluate.py ${GUESSED} ${REF} --constructions=categories -s ${OUT}/ud/${GUESSED##*/}.csv -o ${OUT}/all/ud/${GUESSED##*/}.csv -q ${REF_UD}
        # Parsed UCCA to UD
        CONVERTED=${GUESSED}.converted.labeled
        REF=${DATA}/ud
        python semstr/convert.py ${GUESSED}/* -o ${CONVERTED} ${TO_UD}
        python semstr/evaluate.py ${CONVERTED} ${REF} --unlabeled -s ${OUT}/ud/${MODEL}${FEATURES}.converted.unlabeled.csv -q
        python semstr/evaluate.py ${CONVERTED} ${REF} --constructions=categories -s ${OUT}/ucca/${CONVERTED##*/}.csv -o ${OUT}/all/ucca/${CONVERTED##*/}.csv -q ${REF_UCCA}
        python semstr/evaluate.py ${CONVERTED} ${REF} --constructions=categories -s ${OUT}/ud/${CONVERTED##*/}.csv -o ${OUT}/all/ud/${CONVERTED##*/}.csv -q
   done
   for MODEL in "" en_ewt-20180730-; do
        GUESSED=${DATA}/${MODEL}${FEATURES}
        REF=${DATA}/ud
        # Gold/parsed UD
        python semstr/evaluate.py ${GUESSED} ${DATA}/ud --unlabeled -s ${OUT}/ucca/${MODEL}${FEATURES}.unlabeled.csv -q
        python semstr/evaluate.py ${GUESSED} ${DATA}/ud --constructions=categories -s ${OUT}/ucca/${GUESSED##*/}.csv -o ${OUT}/all/ucca/${GUESSED##*/}.csv -q ${REF_UCCA}
        python semstr/evaluate.py ${GUESSED} ${DATA}/ud --constructions=categories -s ${OUT}/ud/${GUESSED##*/}.csv -o ${OUT}/all/ud/${GUESSED##*/}.csv -q
        # Gold/parsed UD to UCCA
        CONVERTED=${GUESSED}.converted.labeled
        REF=${DATA}/v1-sentences
        python semstr/convert.py ${GUESSED}/* -o ${DATA}/${MODEL}${FEATURES}.converted.labeled ${TO_UCCA}
        python semstr/evaluate.py ${CONVERTED} ${REF} --unlabeled -s ${OUT}/ucca/${MODEL}${FEATURES}.converted.unlabeled.csv -q
        python semstr/evaluate.py ${CONVERTED} ${REF} --constructions=categories -s ${OUT}/ucca/${CONVERTED##*/}.csv -o ${OUT}/all/ucca/${CONVERTED##*/}.csv -q
        python semstr/evaluate.py ${CONVERTED} ${REF} --constructions=categories -s ${OUT}/ud/${CONVERTED##*/}.csv -o ${OUT}/all/ud/${CONVERTED##*/}.csv -q ${REF_UD}
   done
done

python extract_eval.py ${OUT}/{ucca,ud}/*.csv
