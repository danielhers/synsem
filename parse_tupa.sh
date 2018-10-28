#!/usr/bin/env bash
#SBATCH --mem=10G
#SBATCH --time=0-3
#SBATCH --array=0-4

DIR=$PWD
. $DIR/models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

source activate tupa-dev-cortex
cd ../tupa-dev
for d in ${CORPORA[@]}; do
  tupa ${DATA[$d]} -m models/${UCCA_MODEL[$d]} -o $PARSED/xml/${UCCA_MODEL[$d]}/$d $*
done

