#set +x

declare -A DATA UCCA_MODEL UCCA_UD_MODEL UD_MODEL UDPIPE_MODEL UD_DATA
CORPORA=(ewt wiki-dev 20k 20k-fr-dev 20k-de-dev)
PARSED=$PWD/parsed

DATA[ewt]=../converted-udpipe/UCCA_English-EWT
DATA[wiki-dev]=../shared-task/data/dev-xml/UCCA_English-Wiki
DATA[20k]=../shared-task/data/test-xml-gold/UCCA_English-20K
DATA[20k-fr-dev]=../shared-task/data/dev-xml/UCCA_French-20K
DATA[20k-de-dev]=../shared-task/data/dev-xml/UCCA_German-20K

UCCA_MODEL[ewt]=ucca-bilstm-20180917
UCCA_MODEL[wiki-dev]=ucca-bilstm-20180917
UCCA_MODEL[20k]=ucca-bilstm-20180917
UCCA_MODEL[20k-fr-dev]=ucca-fr-bilstm-20180917
UCCA_MODEL[20k-de-dev]=ucca-de-bilstm-20180917

UCCA_UD_MODEL[ewt]=ucca-ud-bilstm-20180917
UCCA_UD_MODEL[wiki-dev]=ucca-ud-bilstm-20180917
UCCA_UD_MODEL[20k]=ucca-ud-bilstm-20180917
UCCA_UD_MODEL[20k-fr-dev]=ucca-ud-fr-bilstm-20180917
UCCA_UD_MODEL[20k-de-dev]=ucca-ud-de-bilstm-20180917

UD_MODEL[ewt]=en_ewt-20181023
UD_MODEL[wiki-dev]=en_ewt-20181023
UD_MODEL[20k]=en_ewt-20181023
UD_MODEL[20k-fr-dev]=fr_gsd-20181024
UD_MODEL[20k-de-dev]=de_gsd-20181024

UDPIPE_MODEL[ewt]=english-ewt-no-reviews-ud-2.2-181023.udpipe
UDPIPE_MODEL[wiki-dev]=english-ewt-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[20k]=english-ewt-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[20k-fr-dev]=french-gsd-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[20k-de-dev]=german-gsd-ud-2.2-conll18-180430.udpipe

UD_DATA[ewt]=../UCCA_English-EWT/ud.conllu
