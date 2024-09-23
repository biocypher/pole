# VHP4Safety Compound Wiki

```
curl -H "Accept: text/csv" --data-urlencode query@compoundwiki/chemicals.rq -G https://compoundcloud.wikibase.cloud/query/sparql -o CompoundWiki.csv
curl -H "Accept: text/csv" --data-urlencode query@compoundwiki/webpages.rq -G https://compoundcloud.wikibase.cloud/query/sparql -o CompoundWiki_webpages.csv
curl -H "Accept: text/csv" --data-urlencode query@compoundwiki/edges.rq -G https://compoundcloud.wikibase.cloud/query/sparql -o CompoundWiki_edges.csv
```
