#!/bin/bash

git clone https://github.com/UniversalConceptualCognitiveAnnotation/UCCA_English-Wiki -b master-sentences
cd UCCA_English-Wiki
python -m scripts.split_corpus -lq -t 4113 -d 514
cd ..

git clone https://github.com/UniversalDependencies/UD_English-EWT
cd UD_English-EWT
sed -i '/^# newdoc id = reviews/,$d' en_ewt-ud-*.conllu
cd ..

