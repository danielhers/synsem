grep -Phro '(?<=type=")[A-Z](?=")' v1-sentences-xml|sort|uniq -c| awk '{print $2,$1}' | jq -R . | jq -sr 'map(./" ")|transpose|map(join("\t"))[]'
