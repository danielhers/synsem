#!/usr/bin/env bash

pip install -U semstr udapi
mkdir -p data/ucca-train-dev
cd data
[[ -d sentences ]] || git clone https://github.com/UniversalConceptualCognitiveAnnotation/UCCA_English-EWT --branch=v1.0-sentences sentences
[[ -d ud ]] || git clone https://github.com/UniversalConceptualCognitiveAnnotation/UCCA_English-EWT --branch=v1.0-ud ud
[[ -d UD_English-EWT ]] || git clone https://github.com/UniversalDependencies/UD_English-EWT --branch=r2.3
[[ -f split.sh ]] || wget https://raw.githubusercontent.com/UniversalConceptualCognitiveAnnotation/UCCA_English-EWT/master/scripts/split.sh
chmod +x split.sh
./split.sh
cp -L sentences/{train,dev}/* ucca-train-dev
python -m semstr.scripts.annotate ud/train -o ud-train-dev -c ud/train -a -l en || exit 1
python -m semstr.scripts.annotate ud/dev -o ud-train-dev -c ud/dev -a -l en || exit 1
python -m scripts.evaluate_standard ud-train-dev ucca-train-dev --errors --as-table --no-normalize --errors-file confusion_matrix.csv
