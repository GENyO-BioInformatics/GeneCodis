#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
if 'db/maintenance' not in os.getcwd():
    os.chdir('db/maintenance')

from lib.BuildGeneCodisDBLib import *

data_dir = os.fspath(Path('data').absolute())
#### Step 1. Reading taxonomy information ####
print("Start Step 1 Reading taxonomy information table")
taxonomy_information=pandas.read_csv(os.path.join(data_dir,"taxonomy_information.tsv"),sep="\t")
taxonomy_information['taxonomy_id'] = [str(x) for x in taxonomy_information['taxonomy_id'].tolist()]
print("Finish Step 1")
print("\n")
print("\n")
#### Step 2. Build Genes and Synonyms Tables
print("Start Step 2. Build gene tables")
tax_ids = taxonomy_information['taxonomy_id'].tolist()

# We use refseq2uniprot in order to get association between refseq and uniprot identifier
print("\tStart Step 2.1. Reading refseq2uniprot file")
refseq2uniprot = pandas.read_csv(os.path.join(data_dir,"refseq2uniprot.gz"),compression='gzip',sep="\t",low_memory=False).drop_duplicates()
print("\tFinish Step 2.1")
print("\n")


## Step 2.2.
print("\tStart Step 2.2. Create genes, mirnas and synonyms tables")

print("\t\tStart Step 2.2.0. Parse mirbase and create prec2maturesmirnasHuman")

## Step 2.2.1. Get table precursor to mature, needed to add matures to TAM and HMDD, and the converter tool.

# We obtain all date located in miRBase database to add miRNA names
with ZipFile(os.path.join(data_dir,"mirna.xls.zip"), 'r') as zipObj:
    zipObj.extractall(data_dir)

mirbaseDBraw = pandas.read_excel(os.path.join(data_dir,"miRNA.xls"))
mirbaseDBraw = mirbaseDBraw.loc[mirbaseDBraw.ID.str.startswith(tuple(taxonomy_information.kegg_id.to_list())),]
precursor = mirbaseDBraw.iloc[:,[0,1]].dropna()
#We obtain mature forms for each miRNA
mature_1 = mirbaseDBraw.iloc[:,[4,5]].dropna()
mature_2 = mirbaseDBraw.iloc[:,[7,8]].dropna()
mature_1.columns = mature_2.columns = precursor.columns.tolist()

# Finally we have miRNA name and Accession code
mirbaseDB = pandas.concat([precursor,mature_1,mature_2]).reset_index().iloc[:,[1,2]].drop_duplicates()

## Creation of precursors -> matures table
mirbaseDBraw.index = mirbaseDBraw.ID
precursor = mirbaseDBraw.iloc[:,[1]].ID.to_list()
matures = mirbaseDBraw.iloc[:,[5,8]].values.tolist()
precursor2matures = dict(zip(precursor,matures))
precursor2maturesDF = pandas.DataFrame.from_dict(precursor2matures,orient='index')
precursor2maturesDF.columns = ['mature','mature']
precursor2maturesDF = pandas.concat([precursor2maturesDF.iloc[:,[0]], precursor2maturesDF.iloc[:,[1]]])
precursor2maturesDF['precursor'] = precursor2maturesDF.index
precursor2maturesDF = precursor2maturesDF.dropna()
precursor2maturesDF.reset_index(drop=True,inplace=True)
precursor2maturesDF.to_csv('raw_sql/prec2maturesmirnas_table.tsv',sep="\t",index=False) # db/maintenance/

prec2maturesmirnasHuman = mirbaseDBraw.loc[mirbaseDBraw.ID.str.startswith('hsa-'),]
precursor = prec2maturesmirnasHuman.iloc[:,[1]].ID.to_list()
matures = prec2maturesmirnasHuman.iloc[:,[5,8]].values.tolist()
prec2maturesmirnasHuman = dict(zip(precursor,matures))

## Step 2.2.1. Get synonym aliases. We use read_manipulate_gene_info_by_tax function to obtain all possible synonym names
print("\t\tStart Step 2.2.1. Get synonyms aliases by gene")
input_data = [(data_dir,tax_id,refseq2uniprot) for tax_id in tax_ids]

with Pool() as pool:
    syns_tables_v1 = pool.starmap(read_manipulate_gene_info_by_tax, input_data)

print("\t\tFinal Step 2.2.1.")

## Step 2.2.2. Create Gene Table: symbol, description, tax_id
print("\t\tStart Step 2.2.2. Create gene tables")
input_data = [syns_tables_v1[i] for i in range(len(syns_tables_v1))]

with Pool() as pool:
    gene_tables_v1 = pool.starmap(create_gene_table, zip(input_data))

print("\t\tFinal Step 2.2.2.")

## Step 2.2.3. Create Synonyms Table: symbol, description, tax_id
print("\t\tStart Step 2.2.3. Create synonyms tables")

syns_tables_v2 = [build_synonyms_table(syns_tables_v1[i]) for i in range(len(syns_tables_v1))]
print("\t\tFinal Step 2.2.3.")

## Step 2.2.4. Add ensembl information from GTF files and calculate gene length
print("\t\tStart Step 2.2.4. Add ensembl information")

results = dict(ChainMap(*[ensembl_checking(tax_ids[i],syns_tables_v2[i],gene_tables_v1[i],data_dir) for i in range(len(tax_ids))]))

syns_tables_v3 = [results[tax_id]["syns_table"] for tax_id in tax_ids]
gene_tables_v2 = [results[tax_id]["gene_table"] for tax_id in tax_ids]

print("\t\tFinal Step 2.2.4.")

## Step 2.2.5. Add miRNA names
print("\t\tStart Step 2.2.5. Add miRNA names")
input_data = [(syns_tables_v3[i],data_dir,tax_ids[i],taxonomy_information,gene_tables_v2[i],mirbaseDB) for i in range(len(tax_ids))]
with Pool() as pool:
    results = pool.starmap(update_miRNA_names, input_data)

results = dict(ChainMap(*results))

syns_tables_v4 = [results[tax_id]["syns_table"] for tax_id in tax_ids]
gene_tables_v3 = [results[tax_id]["gene_table"] for tax_id in tax_ids]

print("\t\tFinal Step 2.2.5.")

## Step 2.2.6. Check gene names
print("\t\tStart Step 2.2.6. Check gene names")
gene_tables_v4 = [check_gene_names(gene_tables_v3[i]) for i in range(len(gene_tables_v3))]
print("\t\tFinal Step 2.2.6.")


## Step 2.2.7. Define internal ids
print("\t\tStart Step 2.2.7. Define internal GC ids")

input_data = [(gene_tables_v4[i],tax_ids[i],syns_tables_v4[i]) for i in range(len(tax_ids))]

with Pool() as pool:
    results = pool.starmap(define_GC4_internal_ids, input_data)

results = dict(ChainMap(*results))

print("\t\tFinal Step 2.2.7.")

Synonyms_Table = pandas.concat([results[tax_id]["syns_table"] for tax_id in tax_ids])
Gene_Table = pandas.concat([results[tax_id]["gene_table"] for tax_id in tax_ids])

print("\t\tStart Step 2.2.8. Add ensembl names from NCBI")
Synonyms_Table = merge_ensembl(Synonyms_Table,data_dir)
print("\t\tFinal Step 2.2.8.")
print("\tFinal Step 2.2.")

## We write gene and synonyms tables in raw_sql dir. That is used in order to avoid run all the steps 1 and 2 each time that
## we would like recodifing this section

os.makedirs('raw_sql', exist_ok=True)
sql_dir = os.fspath(Path('raw_sql').absolute())
Synonyms_Table.to_csv(os.path.join(sql_dir,'synonyms_table.tsv'),sep="\t",index=False)
Gene_Table.to_csv(os.path.join(sql_dir,'gene_table.tsv'),sep="\t",index=False)

Gene_Table = pandas.read_csv("raw_sql/gene_table.tsv",sep="\t")
Synonyms_Table = pandas.read_csv("raw_sql/synonyms_table.tsv",sep="\t")

print("Final Step 2.")

print("Start Step 3. Annotate gene tables")

## Now, we are going to annotate genes with all annotations included in GeneCodis.
## All functions returns two different dataframes
## {annotation}_table is the association between gene and annotation_id
## {annotation}_ann is the association between annotation_id and description term

#LINCS
lincs_table,lincs_ann = build_lincs(data_dir,Gene_Table)

#Bioplanet
bioplanet_table,bioplanet_ann = build_bioplanet(data_dir,Synonyms_Table)

#DisGenet
disgenet_table,disgenet_ann = build_disgenet(data_dir,Synonyms_Table)

#WikiPathways
wikipathways_table,wikipathways_ann = build_wikipathways(data_dir,Synonyms_Table)

#Reactome
reactome_table,reactome_ann = build_reactome(data_dir,Synonyms_Table)

#miRNA direct annotations
miRNA_table,miRNA_ann = build_miRNA(data_dir,Synonyms_Table,prec2maturesmirnasHuman)

#miRTarBase
miRTarBase_table, miRTarBase_ann = build_mirtarbase(data_dir,Synonyms_Table)

#Methylation probes
meth_table,meth_ann = build_methylation(data_dir,Gene_Table)

#DoRothEA
dorothea_table,dorothea_ann = build_dorothea(data_dir,Gene_Table)

#MGI
mgi_table,mgi_ann=build_MGI(data_dir,Synonyms_Table)

#CTD
CTD_table,CTD_ann=build_CTD(data_dir,taxonomy_information,Synonyms_Table)

#PharmGKB
pharmGKB_table,pharmGKB_ann=build_pharmGKB(data_dir,Gene_Table)

#Panther_Pathways
panther_table,panther_ann=build_panther(data_dir,Synonyms_Table)

#HPO
hpo_table,hpo_ann=build_hpo(data_dir,Synonyms_Table)

#OMIM
omim_table,omim_ann=build_omim(data_dir,Synonyms_Table)

#KEGG
kegg_table,kegg_ann = build_kegg(taxonomy_information,Synonyms_Table)

#GO
go_table,go_ann = build_go(Synonyms_Table,taxonomy_information,data_dir)

go_covid = build_go_covid(Synonyms_Table,taxonomy_information,data_dir)

print("Finish Step 3.")

#Prepare Tables
print("Start Step 4. Merging Annotation Info tables")
Annotation_Info = pandas.concat([disgenet_ann,bioplanet_ann,miRTarBase_ann,go_ann,kegg_ann,reactome_ann,wikipathways_ann,omim_ann,lincs_ann,hpo_ann,panther_ann,pharmGKB_ann,CTD_ann,mgi_ann,dorothea_ann,meth_ann,miRNA_ann])
Annotation_Table = pandas.concat([disgenet_table,bioplanet_table,miRTarBase_table,go_table,go_covid,kegg_table,omim_table,reactome_table,wikipathways_table,lincs_table,hpo_table,panther_table,pharmGKB_table,CTD_table,mgi_table,dorothea_table,meth_table,miRNA_table])
'GC-9606-8267' in lincs_table.annotation_id

print("Finish Step 4.")

Annotation_Info = Annotation_Info.drop_duplicates()
Annotation_Info = correct_tables(Annotation_Info,'annotation_id')
taxonomy_information['date']=str(datetime.datetime.now())
print("Start Step 5. Write tables in tsv files")
os.makedirs('raw_sql', exist_ok=True)
sql_dir = os.fspath(Path('raw_sql').absolute())
Synonyms_Table.to_csv(os.path.join(sql_dir,'synonyms_table.tsv'),sep="\t",index=False)
Gene_Table.to_csv(os.path.join(sql_dir,'gene_table.tsv'),sep="\t",index=False)
taxonomy_information.to_csv(os.path.join(sql_dir,'taxonomy_table.tsv'),sep="\t",index=False)

Annotation_Info = Annotation_Info[Annotation_Info.term != ""]
Annotation_Table = Annotation_Table[Annotation_Table.annotation_id.isin(Annotation_Info.annotation_id)]

Annotation_Info.to_csv(os.path.join(sql_dir,'annotation_info_table.tsv'),sep="\t",index=False)
Annotation_Table.to_csv(os.path.join(sql_dir,'annotation_table.tsv'),sep="\t",index=False)

annotations = unique(Annotation_Table['annotation_source'].tolist())
for annotation in annotations:
    subannotation = Annotation_Table[Annotation_Table['annotation_source']==annotation]
    subannotation.to_csv(os.path.join(sql_dir,annotation+'_table.tsv'),sep="\t",index=False)

print("Finish Step 5.")

print("Start Step 6. Create Bias File")

bias_file = create_bias_file(Gene_Table,meth_table,dorothea_table,miRTarBase_table,Synonyms_Table)
bias_file.to_csv(os.path.join(sql_dir,'bias_table.tsv'),sep="\t",index=False)

print("Finish Step 6.")

print("TABLES DONE!")
