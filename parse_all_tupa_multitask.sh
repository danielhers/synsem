#!/usr/bin/env bash
#SBATCH --mem=10G
#SBATCH --time=0-3
#SBATCH --array=1-8

DIR=$PWD
. $DIR/models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
for d in ${CORPORA[@]}; do
  tupa ${DATA[$d]} -m models/stripped/${UCCA_UD_MODEL[$d]} -o $PARSED/xml/${UCCA_UD_MODEL[$d]}/$d
done

