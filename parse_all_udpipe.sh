#!/usr/bin/env bash
#SBATCH --mem=10G
#SBATCH --time=0-3
#SBATCH --array=0-3

DIR=$PWD
. $DIR/models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

for d in ${CORPORA[@]}; do
  python -m semstr.scripts.udpipe ${DATA[$d]} -u ../udpipe/models/${UDPIPE_MODEL[$d]} -o $PARSED/conllu/${UDPIPE_MODEL[$d]} -j $d $*
done

