declare -a DATA UCCA_MODEL UCCA_UD_MODEL UD_MODEL UDPIPE_MODEL
CORPORA=(wiki-dev 20k 20k-fr-dev 20k-de-dev)
PARSED=$PWD/../semstr/parsed

DATA[wiki-dev]=../shared-task/data/dev-xml/UCCA_English-Wiki
DATA[20k]=../shared-task/data/test-xml/UCCA_English-20K
DATA[20k-fr-dev]=../shared-task/data/dev-xml/UCCA_French-20K
DATA[20k-de-dev]=../shared-task/data/dev-xml/UCCA_German-20K

UCCA_MODEL[wiki-dev]=ucca-bilstm-20180917
UCCA_MODEL[20k]=ucca-bilstm-20180917
UCCA_MODEL[20k-fr-dev]=ucca-fr-bilstm-20180917
UCCA_MODEL[20k-de-dev]=ucca-de-bilstm-20180917

UCCA_UD_MODEL[wiki-dev]=ucca-ud-bilstm-20180917
UCCA_UD_MODEL[20k]=ucca-ud-bilstm-20180917
UCCA_UD_MODEL[20k-fr-dev]=ucca-ud-fr-bilstm-20180917
UCCA_UD_MODEL[20k-de-dev]=ucca-ud-de-bilstm-20180917

UD_MODEL[wiki-dev]=en_ewt-20180611
UD_MODEL[20k]=en_ewt-20180611
UD_MODEL[20k-fr-dev]=fr_gsd-20180614
UD_MODEL[20k-de-dev]=de_gsd-20180614

UDPIPE_MODEL[wiki-dev]=english-ewt-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[20k]=english-ewt-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[20k-fr-dev]=french-gsd-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[20k-de-dev]=german-gsd-ud-2.2-conll18-180430.udpipe

