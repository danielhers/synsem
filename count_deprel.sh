awk '{sub(/:.*|_/,"",$8);if($8)print $8}' ud/*.conllu | sort | uniq -c | awk '{print $2,$1}' | jq -R . | jq -sr 'map(./" ")|transpose|map(join("\t"))[]'
