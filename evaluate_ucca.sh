#!/usr/bin/env bash
#SBATCH --mem=1G
#SBATCH --time=0-1
#SBATCH --array=0-13

# Evaluate against gold UCCA data

DIR=$PWD
. models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

for d in ${CORPORA[@]}; do
  OUT=$DIR/eval/$d
  UD_REF_YIELDS=$PARSED/conllu/${UDPIPE_MODEL[$d]}/$d.conllu
  [[ -n "${UD_DATA[$d]}" ]] && UD_REF_YIELDS=${UD_DATA[$d]}
  mkdir -p $OUT/{,all/}{ucca,ud}

  # Evaluate on UCCA
  REF=${DATA[$d]}
  if [[ -z "$REF" ]]; then
    echo No UCCA data for $d, skipping evaluation
  else
    for MODEL in ${UCCA_UD_MODEL[$d]} ${UCCA_MODEL[$d]} ${UDPIPE_MODEL[$d]} ${UD_MODEL[$d]} ud; do  # Evaluate on UCCA data
      GUESSED=$PARSED/xml/$MODEL/$d
      if [[ -d $GUESSED ]]; then
        echo $GUESSED $REF
        run python -m semstr.evaluate $GUESSED $REF --no-normalize --unlabeled --constructions=categories -s $OUT/ucca/$MODEL.unlabeled.csv -c $OUT/ucca/$MODEL.unlabeled.counts.csv -q $*
        run python -m semstr.evaluate $GUESSED $REF --no-normalize --unlabeled --constructions=categories -s $OUT/ud/$MODEL.unlabeled.csv -c $OUT/ud/$MODEL.unlabeled.counts.csv --ref-yield-tags=$UD_REF_YIELDS -q $*
        run python -m semstr.evaluate $GUESSED $REF --no-normalize --constructions=categories -s $OUT/ucca/$MODEL.csv -c $OUT/ucca/$MODEL.counts.csv -o $OUT/all/ucca/$MODEL.csv -q $*
        run python -m semstr.evaluate $GUESSED $REF --no-normalize --constructions=categories -s $OUT/ud/$MODEL.csv -c $OUT/ud/$MODEL.counts.csv -o $OUT/all/ud/$MODEL.csv --ref-yield-tags=$UD_REF_YIELDS -q $*
      else
        echo $GUESSED not found, cannot evaluate $MODEL
      fi
    done
  fi
done

