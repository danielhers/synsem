#!/usr/bin/env bash
#SBATCH --mem=1G
#SBATCH --time=0-1
#SBATCH --array=0-7

DIR=$PWD
. $DIR/models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

for d in ${CORPORA[@]}; do
  OUT=$DIR/eval/$d
  UD_REF_YIELDS=$PARSED/conllu/${UDPIPE_MODEL[$d]}/$d.conllu
  mkdir -p $OUT/{,all/}{ucca,ud}

  if [[ -n "${UD_DATA[$d]}" ]]; then
    REF=${UD_DATA[$d]}
    UD_REF_YIELDS=$REF
    for MODEL in ${UCCA_UD_MODEL[$d]} ${UCCA_MODEL[$d]} ${UDPIPE_MODEL[$d]} ${UD_MODEL[$d]} ucca; do  # Evaluate w.r.t. gold UD
      GUESSED=$PARSED/conllu/$MODEL/$d.conllu
      [[ -d $GUESSED ]] || GUESSED=$GUESSED.conllu
      if [[ -e $GUESSED ]]; then
        echo $GUESSED $REF
        python -m semstr.evaluate $GUESSED $REF --unlabeled -s $OUT/ud/$MODEL.unlabeled.csv -q $*
        python -m semstr.evaluate $GUESSED $REF --constructions=categories -s $OUT/ucca/$MODEL.ud.csv -c $OUT/ucca/$MODEL.ud.counts.csv -o $OUT/all/ucca/$MODEL.ud.csv -q --ref-yield-tags=${DATA[$d]} $*
        python -m semstr.evaluate $GUESSED $REF --constructions=categories -s $OUT/ud/$MODEL.ud.csv -c $OUT/ud/$MODEL.ud.counts.csv -o $OUT/all/ud/$MODEL.ud.csv -q $*
      else
        echo $GUESSED not found, cannot evaluate $MODEL
      fi
    done
  fi

  REF=${DATA[$d]}
  for MODEL in ${UCCA_UD_MODEL[$d]} ${UCCA_MODEL[$d]} ${UDPIPE_MODEL[$d]} ${UD_MODEL[$d]} ud; do  # Evaluate on UCCA data
    GUESSED=$PARSED/xml/$MODEL/$d
    if [[ -d $GUESSED ]]; then
      echo $GUESSED $REF
      python -m semstr.evaluate $GUESSED $REF --unlabeled -s $OUT/ucca/$MODEL.unlabeled.csv -q $*
      python -m semstr.evaluate $GUESSED $REF --constructions=categories -s $OUT/ucca/$MODEL.csv -c $OUT/ucca/$MODEL.counts.csv -o $OUT/all/ucca/$MODEL.csv -q $*
      python -m semstr.evaluate $GUESSED $REF --constructions=categories -s $OUT/ud/$MODEL.csv -c $OUT/ud/$MODEL.counts.csv -o $OUT/all/ud/$MODEL.csv --ref-yield-tags=$UD_REF_YIELDS -q $*
    else
      echo $GUESSED not found, cannot evaluate $MODEL
    fi
  done
done

