#!/usr/bin/env bash
#SBATCH --mem=1G
#SBATCH --time=0-1
#SBATCH --array=0-13

DIR=$PWD
. models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

for d in ${CORPORA[@]}; do
  OUT=$DIR/eval/$d
  mkdir -p $OUT/{,all/}{ucca,ud}

  # Evaluate on UD
  if [[ -z "${UD_DATA[$d]}" ]]; then
    echo No UD data for $d, skipping evaluation
  else
    REF=${UD_DATA[$d]}
    for MODEL in ${UCCA_UD_MODEL[$d]} ${UCCA_MODEL[$d]} ${UDPIPE_MODEL[$d]} ${UD_MODEL[$d]} ucca; do  # Evaluate w.r.t. gold UD
      GUESSED=$PARSED/conllu/$MODEL/$d
      [[ -d $GUESSED ]] || GUESSED=$GUESSED.conllu
      if [[ -e $GUESSED ]]; then
        echo $GUESSED $REF
        if [[ -n "${DATA[$d]}" ]]; then
          run python -m semstr.evaluate --no-enhanced --no-normalize $GUESSED $REF --unlabeled -s $OUT/ucca/$MODEL.unlabeled.ud.csv -c $OUT/ucca/$MODEL.unlabeled.ud.counts.csv -q --ref-yield-tags=${DATA[$d]} $*
          run python -m semstr.evaluate --no-enhanced --no-normalize $GUESSED $REF --constructions=categories -s $OUT/ucca/$MODEL.ud.csv -c $OUT/ucca/$MODEL.ud.counts.csv -o $OUT/all/ucca/$MODEL.ud.csv -q --ref-yield-tags=${DATA[$d]} $*
        fi
        run python -m semstr.evaluate --no-enhanced --no-normalize $GUESSED $REF --unlabeled -s $OUT/ud/$MODEL.unlabeled.csv -c $OUT/ud/$MODEL.unlabeled.counts.csv -q $*
        run python -m semstr.evaluate --no-enhanced --no-normalize $GUESSED $REF --constructions=categories -s $OUT/ud/$MODEL.ud.csv -c $OUT/ud/$MODEL.ud.counts.csv -o $OUT/all/ud/$MODEL.ud.csv -q $*
      else
        echo $GUESSED not found, cannot evaluate $MODEL
      fi
    done
  fi
done

