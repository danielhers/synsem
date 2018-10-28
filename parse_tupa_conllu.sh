#!/usr/bin/env bash
#SBATCH --mem=10G
#SBATCH --time=0-3
#SBATCH --array=0-4

DIR=$PWD
. $DIR/models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

source activate tupa-ud-cortex
cd ../tupa-ud
for d in ${CORPORA[@]}; do
  tupa ${DATA[$d]} -m models/conll2018/${UD_MODEL[$d]} -o $PARSED/conllu/${UD_MODEL[$d]} -j $d -f conllu $*
done

