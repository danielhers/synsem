#!/bin/bash

$(dirname $(which python))/udapy -s util.Filter delete_subtree='node.upos == "PUNCT"' $*
