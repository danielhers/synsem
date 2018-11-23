#!/usr/bin/env bash
#SBATCH --mem=10G
#SBATCH --time=0-3
#SBATCH --array=0-13

DIR=$PWD
. models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

source activate tupa-ud-cortex
cd ../tupa-ud
for d in ${CORPORA[@]}; do
  echo $d
  rm -fv $PARSED/conllu/${UD_MODEL[$d]}/$d.conllu
  data=${UD_DATA[$d]}
  if [[ -z "$data" ]]; then
    echo No UD data found for $d, using UCCA data instead as input
    data=${DATA[$d]}
  fi
  if [[ -z "$data" ]]; then
    echo No UD input data found for $d
  else
    run tupa $data -m models/ud-2.3/${UD_MODEL[$d]} -o $PARSED/conllu/${UD_MODEL[$d]} -j $d -f conllu $*
  fi
done

