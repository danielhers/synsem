#!/usr/bin/env bash
#SBATCH --mem=10G
#SBATCH --time=0-3
#SBATCH --array=0-13

DIR=$PWD
. models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

for d in ${CORPORA[@]}; do
  echo $d
  rm -fv $PARSED/conllu/${UDPIPE_MODEL[$d]}/$d.conllu
  data=${DATA[$d]}
  if [[ -z "$data" ]]; then
    echo No UCCA data found for $d, using UD data instead as input
    data=${UD_DATA[$d]}
  fi
  if [[ -z "$data" ]]; then
    echo No UD input data found for $d
  else
    echo $data
    run python -m semstr.scripts.udpipe $data -u ../udpipe/models/${UDPIPE_MODEL[$d]} -o $PARSED/conllu/${UDPIPE_MODEL[$d]} -j $d.tmp $*
    run ../udpipe/udpipe-ud-2.3-181115/udpipe --tag --parse  ../udpipe/udpipe-ud-2.3-181115/${UDPIPE_MODEL[$d]} < $PARSED/conllu/${UDPIPE_MODEL[$d]}/$d.tmp.conllu > $PARSED/conllu/${UDPIPE_MODEL[$d]}/$d.conllu
    rm -f $PARSED/conllu/${UDPIPE_MODEL[$d]}/$d.tmp.conllu
  fi
done

