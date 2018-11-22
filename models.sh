#set +x

declare -A DATA UCCA_MODEL UCCA_UD_MODEL UD_MODEL UDPIPE_MODEL UD_DATA
CORPORA=(ewt ewt-dev ewt-test wiki-dev wiki-test 20k 20k-fr-dev 20k-fr-test fr-gsd-dev fr-gsd-test 20k-de-dev 20k-de-test de-gsd-dev de-gsd-test)
PARSED=$PWD/parsed
run() {
  $* || echo $* >> failed.txt
}

DATA[ewt]=../converted-udpipe/UCCA_English-EWT
DATA[wiki-dev]=../shared-task/data/dev-xml/UCCA_English-Wiki
DATA[wiki-test]=../shared-task/data/test-xml-gold/UCCA_English-Wiki
DATA[20k]=../shared-task/data/test-xml-gold/UCCA_English-20K
DATA[20k-fr-dev]=../shared-task/data/dev-xml/UCCA_French-20K
DATA[20k-fr-test]=../shared-task/data/test-xml-gold/UCCA_French-20K
DATA[20k-de-dev]=../shared-task/data/dev-xml/UCCA_German-20K
DATA[20k-de-test]=../shared-task/data/test-xml-gold/UCCA_German-20K

UCCA_MODEL[ewt]=ucca-bilstm-20180917
UCCA_MODEL[ewt-dev]=ucca-bilstm-20180917
UCCA_MODEL[ewt-test]=ucca-bilstm-20180917
UCCA_MODEL[wiki-dev]=ucca-bilstm-20180917
UCCA_MODEL[wiki-test]=ucca-bilstm-20180917
UCCA_MODEL[20k]=ucca-bilstm-20180917
UCCA_MODEL[20k-fr-dev]=ucca-fr-bilstm-20180917
UCCA_MODEL[20k-fr-test]=ucca-fr-bilstm-20180917
UCCA_MODEL[fr-gsd-dev]=ucca-fr-bilstm-20180917
UCCA_MODEL[fr-gsd-test]=ucca-fr-bilstm-20180917
UCCA_MODEL[20k-de-dev]=ucca-de-bilstm-20180917
UCCA_MODEL[20k-de-test]=ucca-de-bilstm-20180917
UCCA_MODEL[de-gsd-dev]=ucca-de-bilstm-20180917
UCCA_MODEL[de-gsd-test]=ucca-de-bilstm-20180917

UCCA_UD_MODEL[ewt]=ucca-ud-bilstm-20180917
UCCA_UD_MODEL[ewt-dev]=ucca-ud-bilstm-20180917
UCCA_UD_MODEL[ewt-test]=ucca-ud-bilstm-20180917
UCCA_UD_MODEL[wiki-dev]=ucca-ud-bilstm-20180917
UCCA_UD_MODEL[wiki-test]=ucca-ud-bilstm-20180917
UCCA_UD_MODEL[20k]=ucca-ud-bilstm-20180917
UCCA_UD_MODEL[20k-fr-dev]=ucca-ud-fr-bilstm-20180917
UCCA_UD_MODEL[20k-fr-test]=ucca-ud-fr-bilstm-20180917
UCCA_UD_MODEL[fr-gsd-dev]=ucca-ud-fr-bilstm-20180917
UCCA_UD_MODEL[fr-gsd-test]=ucca-ud-fr-bilstm-20180917
UCCA_UD_MODEL[20k-de-dev]=ucca-ud-de-bilstm-20180917
UCCA_UD_MODEL[20k-de-test]=ucca-ud-de-bilstm-20180917
UCCA_UD_MODEL[de-gsd-dev]=ucca-ud-de-bilstm-20180917
UCCA_UD_MODEL[de-gsd-test]=ucca-ud-de-bilstm-20180917

UD_MODEL[ewt]=en_ewt-no-reviews-20181119
UD_MODEL[ewt-dev]=en_ewt-20181119
UD_MODEL[ewt-test]=en_ewt-20181119
UD_MODEL[wiki-dev]=en_ewt-20181119
UD_MODEL[wiki-test]=en_ewt-20181119
UD_MODEL[20k]=en_ewt-20181119
UD_MODEL[20k-fr-dev]=fr_gsd-20181119
UD_MODEL[20k-fr-test]=fr_gsd-20181119
UD_MODEL[fr-gsd-dev]=fr_gsd-20181119
UD_MODEL[fr-gsd-test]=fr_gsd-20181119
UD_MODEL[20k-de-dev]=de_gsd-20181119
UD_MODEL[20k-de-test]=de_gsd-20181119
UD_MODEL[de-gsd-dev]=de_gsd-20181119
UD_MODEL[de-gsd-test]=de_gsd-20181119

# Use this vim command to switch between commented-out and actual values:
# %s/\([a-z0-9._-]\+\)\(\s\+#\s\+\)\(.*\)/\3\2\1
UDPIPE_MODEL[ewt]=english-ewt-no-reviews-ud-2.3-181119.udpipe  # english-ewt-no-reviews-ud-2.2-181023.udpipe  # english-gum-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[ewt-dev]=english-ewt-ud-2.3-181119.udpipe  # english-ewt-no-reviews-ud-2.2-181023.udpipe  # english-gum-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[ewt-test]=english-ewt-ud-2.3-181119.udpipe  # english-ewt-no-reviews-ud-2.2-181023.udpipe  # english-gum-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[wiki-dev]=english-ewt-ud-2.3-181119.udpipe  # english-ewt-ud-2.2-conll18-180430.udpipe  # english-gum-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[wiki-test]=english-ewt-ud-2.3-181119.udpipe  # english-ewt-ud-2.2-conll18-180430.udpipe  # english-gum-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[20k]=english-ewt-ud-2.3-181119.udpipe  # english-ewt-ud-2.2-conll18-180430.udpipe  # english-gum-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[20k-fr-dev]=french-gsd-ud-2.3-181119.udpipe  # french-gsd-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[20k-fr-test]=french-gsd-ud-2.3-181119.udpipe  # french-gsd-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[fr-gsd-dev]=french-gsd-ud-2.3-181119.udpipe  # french-gsd-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[fr-gsd-test]=french-gsd-ud-2.3-181119.udpipe  # french-gsd-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[20k-de-dev]=german-gsd-ud-2.3-181119.udpipe  # german-gsd-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[20k-de-test]=german-gsd-ud-2.3-181119.udpipe  # german-gsd-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[de-gsd-dev]=german-gsd-ud-2.3-181119.udpipe  # german-gsd-ud-2.2-conll18-180430.udpipe
UDPIPE_MODEL[de-gsd-test]=german-gsd-ud-2.3-181119.udpipe  # german-gsd-ud-2.2-conll18-180430.udpipe

UD_DATA[ewt]=../UCCA_English-EWT/ud.conllu
UD_DATA[ewt-dev]=../udpipe/ud-2.3/en_ewt/en_ewt-ud-dev.conllu
UD_DATA[ewt-test]=../udpipe/ud-2.3/en_ewt/en_ewt-ud-test.conllu
UD_DATA[fr-gsd-dev]=../udpipe/ud-2.3/fr_gsd/fr_gsd-ud-dev.conllu
UD_DATA[fr-gsd-test]=../udpipe/ud-2.3/fr_gsd/fr_gsd-ud-test.conllu
UD_DATA[de-gsd-dev]=../udpipe/ud-2.3/de_gsd/de_gsd-ud-dev.conllu
UD_DATA[de-gsd-test]=../udpipe/ud-2.3/de_gsd/de_gsd-ud-test.conllu

