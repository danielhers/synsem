#!/usr/bin/env bash

cd ../tupa-dev
./activate.sh
pip install wheel
for d in semstr ucca; do
    until yes | pip uninstall $d |& grep -q Skipping; do :; done
    cd ../$d
    rm -f dist/*
    python setup.py bdist_wheel
done
cd ../tupa-dev
pip --no-cache-dir install -r requirements.txt -f ../semstr/dist -f ../ucca/dist
