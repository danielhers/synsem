#!/usr/bin/env bash

pip install wheel
for d in semstr ucca; do
    until yes | pip uninstall $d |& grep -q Skipping; do :; done
    cd ../$d
    rm -fv dist/*
    python setup.py bdist_wheel
done
cd ../tupa
pip --no-cache-dir install -r requirements.txt -f ../semstr/dist -f ../ucca/dist
