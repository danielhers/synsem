#!/bin/bash

git clone https://github.com/UniversalConceptualCognitiveAnnotation/UCCA_English-Wiki -b master-sentences
cd UCCA_English-Wiki
python -m scripts.split_corpus -lq -t 4113 -d 514  # Split to train, dev and test
cd ..

git clone https://github.com/UniversalDependencies/UD_English-EWT
cd UD_English-EWT
sed -i '/^# newdoc id = reviews/,$d' en_ewt-ud-*.conllu  # Remove the reviews section
cd ..

