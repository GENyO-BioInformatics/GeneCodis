#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
if 'db/maintenance' not in os.getcwd():
    os.chdir('db/maintenance')

from pathlib import Path  # Python 3.6+ only
from dotenv import load_dotenv
env_path = Path('../../') / '.env'
load_dotenv(dotenv_path=env_path)
from lib.BuildGeneCodisDBLib import *

sql_dir=os.fspath(Path('raw_sql').absolute())
tables = glob.glob(os.path.join(sql_dir,"*tsv"))
data_dir=os.fspath(Path('data').absolute())
conn = psycopg2.connect(host='localhost', dbname=os.getenv("DB_NAME"),
                         user=os.getenv("DB_USER"), password=os.getenv("DB_PSWD"))
cur = conn.cursor()

## With loading_data_sql we add tables to postgresql
for table in tables:
    loading_data_sql(table,conn,cur,dbname=os.getenv("DB_NAME"),user=os.getenv("DB_USER"),password=os.getenv("DB_PSWD"))

### CREATE JSONs to extract information
os.makedirs('info',exist_ok=True)
#Build json with information0
command = "SELECT taxonomy_id,output_name FROM taxonomy;"
res = launchQuery(command,"",getDF=True,dbname=os.getenv("DB_NAME"),user=os.getenv("DB_USER"), password=os.getenv("DB_PSWD"))
taxid2name = dict(zip(res.taxonomy_id,res.output_name))
json_file_web = {}
json_file_db = {}
annotations = set()
for taxid in taxid2name:
    command = "SELECT id FROM gene WHERE tax_id = %s"
    genes_by_taxid = len(launchQuery(command,(taxid,),getDF=True,dbname=os.getenv("DB_NAME"),user=os.getenv("DB_USER"), password=os.getenv("DB_PSWD"))['id'].tolist())
    outname = taxid2name[taxid]
    json_file_web[taxid] = {'number_of_genes':genes_by_taxid,"annotations":[],'name':outname}
    json_file_db[taxid] = {'number_of_genes':genes_by_taxid,"annotations":[],'name':outname}
    command="SELECT annotation.id,annotation_id,annotation_source FROM annotation INNER JOIN gene ON (annotation.id = gene.id) WHERE gene.tax_id = %s;"
    annotation_by_taxid = launchQuery(command,(taxid,),getDF=True,dbname=os.getenv("DB_NAME"),user=os.getenv("DB_USER"), password=os.getenv("DB_PSWD"))
    taxIDannotations = unique(annotation_by_taxid['annotation_source'].tolist())
    annotations.update(taxIDannotations)
    for annotation in taxIDannotations:
        subann = annotation_by_taxid[annotation_by_taxid['annotation_source']==annotation]
        sub_dict = {annotation:len(subann.index)}
        json_file_db[taxid]['annotations'].append(sub_dict)
        if (sub_dict[annotation]>100):
            if annotation not in ['cpgs']:
                json_file_web[taxid]['annotations'].append(sub_dict)

annotations.remove('cpgs')
annotation_json = 'info/info_annotation.json'
if os.path.exists(annotation_json):
    annotation_json = json.loads(open(annotation_json).read())
else:
    annotation_json = {}

for annotation in annotations:
    if annotation not in annotation_json:
        annotation_json[annotation] = {"fullname":"", "webname":""}

with open('info/data_in_db.json', 'w') as fp:
    json.dump(json_file_db, fp,sort_keys=True)

with open('info/data_in_web.json', 'w') as fp:
    json.dump(json_file_web, fp,sort_keys=True)

with open('info/info_annotation.json', 'w') as fp:
    json.dump(annotation_json, fp,sort_keys=True)

bias_file = pandas.read_csv("raw_sql/bias_table.tsv",sep="\t")
Synonyms_Table = pandas.read_csv('raw_sql/synonyms_table.tsv',sep="\t")
bias_file.index = bias_file.id
bias_file.loc[Synonyms_Table.id[Synonyms_Table.source == 'mirbase'],'mirnas'] = 1
bias_file.to_csv('raw_sql/bias_table.tsv',sep="\t",index=False)
#bias_file = pandas.read_csv("raw_sql/bias_table.tsv",sep="\t")
cmd = "../../venv/bin/python generateTableHTML.py"; print(cmd); os.system(cmd)

#### generate_mirnas_precompiled.py

print('Transforming gene-based to mirnas-based databases')
pandas.options.mode.chained_assignment = None

### This script transform gene-annotation to mirna-annotation based on the target genes

command = "SELECT annotation_id,id FROM miRTarBase"
mirna_input = launchQuery(command,args=())
universe_ann = pandas.DataFrame({'id':[],'annotation_id':[],"annotation_source":[]})
universe = list(set(list(mirna_input.annotation_id)))

input_data = [(mirna,mirna_input[mirna_input.annotation_id == mirna]['id'].tolist()) for mirna in universe]

with Pool() as pool:
    universe_ann = pandas.concat(pool.starmap(by_mirna,input_data)).dropna()

command = "SELECT * FROM tam_2;"
tam2 = launchQuery(command,args=())
command = "SELECT * FROM HMDD_v3;"
hmdd = launchQuery(command,args=())
command = "SELECT * FROM MNDR;"
mndr = launchQuery(command,args=())

universe_ann = pandas.concat([universe_ann,tam2,hmdd,mndr])

universe_ann.to_csv("raw_sql/mirna_to_annotation_table.tsv",sep="\t",index=False)

conn = psycopg2.connect(host='localhost', dbname=os.getenv("DB_NAME"),
                         user=os.getenv("DB_USER"), password=os.getenv("DB_PSWD"))
cur = conn.cursor()

loading_data_sql("raw_sql/mirna_to_annotation_table.tsv",conn,cur,dbname=os.getenv("DB_NAME"),user=os.getenv("DB_USER"),password=os.getenv("DB_PSWD"))
