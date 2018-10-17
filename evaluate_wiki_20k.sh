#!/usr/bin/env bash
#SBATCH --mem=1G
#SBATCH --time=0-1
#SBATCH --array=0-3

DIR=$PWD
. $DIR/models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

for d in ${CORPORA[@]}; do
  OUT=$DIR/../semstr/out/eval/$d
  mkdir -p $OUT/{,all/}{ucca,ud}
  for MODEL in ${UCCA_UD_MODEL[$d]} ${UCCA_MODEL[$d]} ${UDPIPE_MODEL[$d]} ${UD_MODEL[$d]}; do
      GUESSED=$PARSED/xml/$MODEL/wiki-dev
      REF=${DATA[$d]}
      python -m semstr.evaluate $GUESSED $REF --unlabeled -s $OUT/ucca/$MODEL.unlabeled.csv -q
      python -m semstr.evaluate $GUESSED $REF --constructions=categories -s $OUT/ucca/$MODEL.csv -o $OUT/all/ucca/$MODEL.csv -q
      python -m semstr.evaluate $GUESSED $REF --constructions=categories -s $OUT/ud/$MODEL.csv -o $OUT/all/ud/$MODEL.csv -q --ref-yield-tags=$PARSED/conllu/${UDPIPE_MODEL[$d]}/$d
  done
done

