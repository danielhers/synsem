#!/usr/bin/env bash
#SBATCH --mem=10G
#SBATCH --time=0-3
#SBATCH --array=0-13

DIR=$PWD
. models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

source activate tupa-dev-cortex
cd ../tupa-dev
for d in ${CORPORA[@]}; do
  echo $d
  data=${DATA[$d]}
  if [[ -z "$data" ]]; then
    echo No UCCA data found for $d, using UD data instead: ${UD_DATA[$d]}
    data=${UD_DATA[$d]}
  fi
  if [[ -z "$data" ]]; then
    echo No data found for $d
  else
    run tupa $data -m models/stripped/${UCCA_UD_MODEL[$d]} -o $PARSED/xml/${UCCA_UD_MODEL[$d]}/$d $*
  fi
done

