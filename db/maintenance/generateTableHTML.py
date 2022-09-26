#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas, re, requests

data_dir="data"

url_content = pandas.read_csv("data/url_file.tsv",sep="\t")
ensembl_directory = url_content[url_content.Dir.str.contains("ensembl_directory")].iloc[:,[0,4]]
url_content = url_content[~url_content.Dir.str.contains("ensembl_directory")].iloc[:,[0,4]]
ed = [text[0:(text.find("gtf/")+3)] for text in ensembl_directory.URL.tolist()]
add_rows = {'URL':[],'Source':[]}
eds = list(set(ed))

def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

for ed in eds:
    source = list(set(ensembl_directory[ensembl_directory.URL.str.contains(ed)]['Source'].tolist()))
    add_rows['Source'].extend(source)
    organisms = ensembl_directory[ensembl_directory.URL.str.contains(ed)]
    organisms = [text[findOccurrences(text, '/')[-2]+1:-1] for text in organisms.URL.tolist()]
    organisms = ", ".join(organisms)
    ed = ed + " (" + organisms + ")"
    add_rows['URL'].append(ed)

add_rows = pandas.DataFrame(add_rows)
url_content = pandas.concat([url_content,add_rows])
url_content = pandas.concat([url_content,pandas.DataFrame({"URL":["https://github.com/saezlab/dorothea/tree/master/data (mus_musculus, homo_sapiens)"],"Source":["DoRothEA"]})])

wiki_names = ", ".join(["Arabidopsis_thaliana","Bos_taurus","Caenorhabditis_elegans","Canis_familiaris","Danio_rerio","Drosophila_melanogaster","Gallus_gallus","Homo_sapiens","Mus_musculus","Oryza_sativa","Rattus_norvegicus","Saccharomyces_cerevisiae","Sus_scrofa"])
wiki_names = " (" + wiki_names + ")"
wiki_names = "http://data.wikipathways.org/current/gmt/" + wiki_names
url_content = pandas.concat([url_content,pandas.DataFrame({"URL":[wiki_names],"Source":["WikiPathways"]})])
url_content = pandas.concat([url_content,pandas.DataFrame({'URL':["http://current.geneontology.org/annotations/ (all organisms)"],"Source":["Gene Ontology"]})])
url_content = pandas.concat([url_content,pandas.DataFrame({'URL':["https://www.kegg.jp/kegg/rest/keggapi.html"],"Source":["KEGG"]})])
url_content = pandas.concat([url_content,pandas.DataFrame({"URL":["http://webdata.illumina.com.s3-website-us-east-1.amazonaws.com/downloads/productfiles/methylationEPIC/infinium-methylationepic-v-1-0-b5-manifest-file-csv.zip"],"Source":["Infinium MethylationEPIC"]})])
url_content = pandas.concat([url_content,pandas.DataFrame({"URL":["https://clue.io/touchstone"],"Source":["LINCS"]})])
url_content = pandas.concat([url_content,pandas.DataFrame({'URL':["https://ftp.ncbi.nih.gov/pub/taxonomy/taxdmp.zip"],"Source":["NCBI"]})])

sources = sorted(list(set(url_content.Source.tolist())))

table = ''
for source in sources:
    url_content_source = url_content[url_content.Source == source]
    subtable = '<p class="has-text-weight-bold">'+source+'</p>\n'
    for link in url_content_source.URL.tolist():
        subtable += '<p>'+link+'</p>\n'
    table += subtable

with open("table.html", 'w') as out_file:
    out_file.write(table)
