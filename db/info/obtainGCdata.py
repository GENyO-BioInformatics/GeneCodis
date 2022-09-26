import pandas
genes = pandas.read_csv("../maintenance/raw_sql/gene_table.tsv",sep="\t")
synonyms = pandas.read_csv("../maintenance/raw_sql/synonyms_table.tsv",sep="\t")
mirnas = synonyms[synonyms.source=="mirbase"]
cpgs = pandas.read_csv("../maintenance/raw_sql/cpgs_table.tsv",sep="\t")
dorothea = pandas.read_csv("../maintenance/raw_sql/DoRothEA_table.tsv",sep="\t")
mirnas_target = pandas.read_csv("../maintenance/raw_sql/miRTarBase_table.tsv",sep="\t")
tax = pandas.read_csv("../maintenance/raw_sql/taxonomy_table.tsv",sep="\t")
outDir = {}

for tax_id in tax.taxonomy_id.tolist():
    orgGenes = genes[genes.organism == tax_id]
    orgSyn = synonyms[synonyms['id'].isin(orgGenes.id.tolist())]
    onlyGenes = list(set(orgSyn[orgSyn.source=="entrez"].id.tolist()))
    onlyMirnas = orgSyn[orgSyn.source=="mirbase"]
    onlyMirnas = orgGenes[orgGenes['id'].isin(onlyMirnas.id.tolist())]
    onlyMirnasTarget = list(set(mirnas_target[mirnas_target['id'].isin(onlyGenes)].id.tolist()))
    onlyCpgTarget = list(set(cpgs[cpgs['id'].isin(onlyGenes)].id.tolist()))
    onlyDorotheaTarget = list(set(dorothea[dorothea['id'].isin(onlyGenes)].id.tolist()))
    outDir[tax_id] = {'genes':len(onlyGenes), 'mirna_directed':len(onlyMirnas), 'mirna_indirected':len(onlyMirnasTarget),'cpgs':len(onlyCpgTarget),'tfs':len(onlyDorotheaTarget)}

import json
with open('geneUniverse.json', 'w', encoding='utf-8') as f:
    json.dump(outDir, f, ensure_ascii=False, indent=4)
