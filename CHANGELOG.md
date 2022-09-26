# Change Log

All changes to this project will be documented in this file

1. New updates on 2020-04-17

  1. Raw CDT table is a pre-downloaded file because website (http://ctdbase.org/reports/CTD_chem_gene_ixns.csv.gz) requires a hCAPTCHA. Updated on @raul branch (db/maintenance/data).

  2. Changed HPO download site. New link is http://compbio.charite.de/jenkins/job/hpo.annotations/lastSuccessfulBuild/artifact/util/annotation/genes_to_phenotype.txt. To include on the web. Updated on @raul branch (db/maintenance/data/url_file.tsv).

  3. Ensembl to gene file (ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2ensembl.gz) used to add ensembl information. Updated on @raul brach (db/maintenance/generate_and_download_tables.py).

  4. Both gene info and gene2refseq raw files were split by taxonomy id in order to be read faster. Updated on @raul branch (db/maintenance/generate_and_download_tables.py).

  5. Some changes in library and main scripts to consider these updates. Updated on @raul branch (db/maintenance/updateGeneCodis.py and db/maintenance/lib/BuildGeneCodisDBLib.py).

  6. GC4programmatic.R is now functional and adapted to new changes. Updated on @raul branch (GC4programmatic.R)

2. New updates on 2020-04-20

  1. GC4programmatic.py is changed. Final results are kept in a list of dataframes and downloading tables is an optional argument. Updated on @raul branch (GC4programmatic.py)
