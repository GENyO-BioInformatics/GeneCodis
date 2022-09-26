In this repository you can find all information and data needed to download all required data and process them to build the database in SQL. You will find some directories and scripts to generate perfectly the Database

## Main Functionality

The script [updateGC4db.sh](updateGC4db.sh) is all you need to generate the database.

```console
user@user:~$ /site/of/genecodis/db/maintenance/updateGC4db.sh
```

Included in this script are 4 steps that have been explained now:

### 1. Download Intermediary Files

Firstly, to generate GeneCodis database we will need some essential files as annotation tables, genes information or taxonomy classification.The script used to download all this information is [generate_and_download_tables.py](generate_and_download_tables.py). If you want to know what are the URL that are downloaded you can check this [file](data/url_file.tsv).

WARNING: Do not worry if this step takes a long time

### 2. Built

GeneCodis 4.0 has been developed to manage some different types of annotation in a few organisms. Associations between genes and annotation terms has been carried out in SQL language with a open source object-relational database system called [PostgreSQL](https://www.postgresql.org/).

Creating tables to load in SQL is the first step. The script [updateGeneCodis.py](updateGeneCodis.py) that uses functions from [BuildGeneCodisDBLib.py](lib/BuildGeneCodisDBLib.py) has been developed to join all the information from annotations, genes and organisms in a few tables.

Until now, we have annotated genes for [Gene Ontology](http://geneontology.org/), [KEGG Pathway](https://www.genome.jp/kegg/pathway.html), [Panther DB](http://pantherdb.org/), [OMIM](https://www.omim.org/), [miTarBase](https://mirtarbase.cuhk.edu.cn/~miRTarBase/miRTarBase_2022/php/index.php), [DoRothEA](https://github.com/saezlab/dorothea/tree/master/data/TFregulons/consensus/Robjects_VIPERformat/normal), [Mouse Genomic Informatics](http://www.informatics.jax.org/), [Comparative Toxicogenomics Database](http://ctdbase.org/), [PharmGKB](https://www.pharmgkb.org/), [Human Phenotype Ontology](https://hpo.jax.org/app/), [BioPlanet](https://tripod.nih.gov/bioplanet/), [Reactome](https://reactome.org/), [DisGeNET](https://www.disgenet.org/), [LINCS project](https://clue.io/lincs), [HMDD3](https://www.cuilab.cn/hmdd), [TAM2](http://www.lirmed.com/tam2/) and [MNDR](https://www.rna-society.org/mndr/)

The created tables are gene, synonyms, taxonomy_information, annotation, annotation_info and one table by annotation source. These tables will be located in raw_sql folder.

WARNING: Do not worry if this step takes a long time

### 3 Pre Compiled miRNA associations

Because of obtain the associations between target genes and annotation from a set of miRNA is a long and computationally expensive process, we decided to pre-compiled that in order to avoid do the same queries for each job launched. This process is executed from [generate_mirnas_precompiled.py](generate_mirnas_precompiled.py) and creates a table in raw_sql named mirna_to_annotation_table.

### 4 Load in PostgreSQL

Finally, tables are introduced in PostgreSQL using the script [loadGeneCodistoPostgres.py](loadGeneCodistoPostgres.py) that takes also functions from [BuildGeneCodisDBLib.py](lib/BuildGeneCodisDBLib.py).
