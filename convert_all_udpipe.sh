#!/usr/bin/env bash
#SBATCH --mem=10G
#SBATCH --time=0-3

DIR=$PWD
. $DIR/models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

for d in ${CORPORA[@]}; do
  python -m semstr.convert $PARSED/conllu/${UDPIPE_MODEL[$d]}/$d.conllu -o $PARSED/xml/${UDPIPE_MODEL[$d]}/$d --extra-normalization --label-map=../semstr/semstr/util/resources/ud_ucca_label_map.csv
done

