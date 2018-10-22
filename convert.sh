#!/usr/bin/env bash
#SBATCH --mem=10G
#SBATCH --time=0-3
#SBATCH --array=0-3

DIR=$PWD
. $DIR/models.sh
echo SLURM_ARRAY_TASK_ID=$SLURM_ARRAY_TASK_ID
[[ -n "$SLURM_ARRAY_TASK_ID" ]] && CORPORA=(${CORPORA[$SLURM_ARRAY_TASK_ID]})

for d in ${CORPORA[@]}; do
  for MODEL in ${UDPIPE_MODEL[$d]} ${UD_MODEL[$d]}; do  # Parsed UD to UCCA
    python -m semstr.convert $PARSED/conllu/$MODEL/$d.conllu -o $PARSED/xml/$MODEL/$d --extra-normalization --label-map=$DIR/../semstr/semstr/util/resources/ud_ucca_label_map.csv $*
  done
  if [[ -n "${UD_DATA[$d]}" ]]; then  # Convert gold UD to UCCA and gold UCCA to UD
    python -m semstr.convert ${UD_DATA[$d]} -o $PARSED/xml/ud/$d --extra-normalization --label-map=$DIR/../semstr/util/resources/ud_ucca_label_map.csv $*
    python -m semstr.convert ${DATA[$d]} -o $PARSED/conllu/ucca/$d --label-map=$DIR/../semstr/util/resources/ucca_ud_label_map.csv $*
    for MODEL in ${UCCA_UD_MODEL[$d]} ${UCCA_MODEL[$d]}; do  # Parsed UCCA to UD
      python -m semstr.convert $PARSED/xml/$MODEL/$d -o $PARSED/conllu/$MODEL/$d -f conllu --label-map=$DIR/../semstr/semstr/util/resources/ucca_ud_label_map.csv $*
    done
  fi
done

