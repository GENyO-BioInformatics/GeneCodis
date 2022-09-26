#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from lib.BuildGeneCodisDBLib import *

env_path = Path('../../') / '.env'
load_dotenv(dotenv_path=env_path)

print("Download Tables")

os.makedirs("log",exist_ok = True) # Create log directory

# Get datetime to name the log file as a date
dt = datetime.datetime.today()
logfile = "log/"+"".join(str(i) for i in [dt.year,dt.month,dt.day,dt.hour,dt.minute])+".log"  # Example of logfile: 2021924123.log

# First step is downloading needed files. We will use download_file function located in lib/BuildGeneCodisDBLib.py
# In order to download some files in parallel we will use multiprocessing python module

url_file = pandas.read_csv("data/url_file.tsv",sep="\t") # Read url file


# To use Pool() for multiprocessing we need to input the variables as list of lists [url,name,type,download]

urls = url_file.URL.tolist()
names = url_file.Dir.tolist()
types = url_file.Type.tolist()
downloads = url_file.Download.tolist()


input_data = [(urls[i],names[i],types[i],downloads[i]) for i in range(len(url_file.index))]

with Pool() as pool: #Run pool.starmap using download_file function. This will take a long time
    res_download = pool.starmap(download_file,input_data)

res_download = dict(ChainMap(*res_download))

# We try the downloading of files with Error. For example HPO usually fails

print("Try downloading fail files")

new_download = [download_file(urls[i],names[i],types[i],downloads[i]) for i in range(len(urls)) if res_download[names[i]] != "Correct"]
new_download = dict(ChainMap(*new_download))

for file in new_download:
    if new_download[file] == "Correct":
        res_download[file] = "Correct"


# In occassions gunziped files downloading is incorrect, so we check that the downloading was correct
# Use check_gs_files function. In this case we will not use Pool() because downloading in a loop is better

urls_gz = url_file.loc[url_file.Type == "application/gzip"]

urls = urls_gz.URL.tolist()
names = urls_gz.Dir.tolist()
types = urls_gz.Type.tolist()
downloads = urls_gz.Download.tolist()

print("Check gz files")

[check_gz_files(urls[i],names[i],types[i],downloads[i]) for i in range(len(urls_gz.index))]


# DoRothEA files are in rda format. To read them in python, we use pyreadr module
# We have dorothea datframes for human (9606) and mouse (10090)

tax_ids = ["9606","10090"]

print("Process DoRothEA")

[write_dorothea(tax_id) for tax_id in tax_ids]

# Ensembl gtfs need to be downloaded from ensembl FTP site. You can see that we downloaded some {taxonomy_id}_ensembl_directory with the information to download gtf files
# We need to know the tax ids of organism included in GeneCodis and the url where gtf are located
# For this reason we use data/taxonomy_information.tsv where all this info is located

taxonomy_data = pandas.read_csv("data/taxonomy_information.tsv",sep="\t")
tax_ids = taxonomy_data['taxonomy_id'].tolist()

# We will use again multiprocessing module. In this case, we apply ensembl_gtf function

print("Read ensembl sources and download gtf files")

input_data = [(tax_id,url_file.loc[url_file.Dir.isin(["data/"+str(tax_id)+"_ensembl_directory"])]["URL"].tolist()[0]) for tax_id in tax_ids if os.path.isfile("data/"+str(tax_id)+"_ensembl_directory")]

res_ensembl_gtf = []

for tax_id in tax_ids:
    print(tax_id)
    res_ensembl_gtf.append(ensembl_gtf(tax_id,url_file.loc[url_file.Dir.isin(["data/"+str(tax_id)+"_ensembl_directory"])]["URL"].tolist()[0]))

res_ensembl_gtf = dict(ChainMap(*res_ensembl_gtf))

# Panther database need to be downloaded too, we have downloaded panther_release file with all files availables, but we only need SequenceAssociationPathway file

print("Download Panther")

with open("data/panther_release","r") as f:
    panther_files = f.readlines()
panther_files = [x for x in panther_files if "SequenceAssociationPathway" in x]
panther_files = panther_files[0].rstrip().split(" ")[-1]

res_panther = download_file(os.path.join("ftp://ftp.pantherdb.org/pathway/current_release",panther_files),"data/pantherdb.tsv",'text/plain',"Normal")

# WikiPathways files also need to be downloaded by organism with function download_wikipathways

print("Download WikiPathways")

res_wikipathways = download_wikipathways(taxonomy_data)

# As well as kegg with function download_kegg

print("Download Kegg")

res_kegg = download_kegg(taxonomy_data)

# Gene info and gene2refseq files are too large to be read directly, so we divide it by tax id with generate_sub_files_gene_info function
# That will generate {tax_id}_gene_info.tsv and {tax_id}_gene2refseq.tsv files

print("Split gene info")

input_data = [(tax_id,"data/gene_info.gz") for tax_id in tax_ids]

with Pool() as pool:
    pool.starmap(generate_sub_files_gene_info, input_data)

print("Split gene2refseq")

input_data = [(tax_id,"data/gene2refseq.gz") for tax_id in tax_ids]

with Pool() as pool:
    pool.starmap(generate_sub_files_gene_info, input_data)


# Similarly, gaf file is also a large file to manage directly, so we split it by tax_id using generate_sub_files_gaf function
# That will generate {tax_id}.gaf files

print("Split goa gaz")

input_data = [(tax_id,'data/goa_uniprot_all.gaf.gz') for tax_id in tax_ids]

with Pool() as pool:
    pool.starmap(generate_sub_files_gaf, input_data)

# Finally, we process manifest file from EPIC with process_epic_manifest function

print("Read epic manifest")

process_epic_manifest()

resStatus = {**res_panther,**res_ensembl_gtf,**res_download,**res_wikipathways,**res_kegg}
resStatus = pandas.DataFrame(resStatus.items(), columns=['File', 'Status'])

print("Final Download")
print(resStatus)

if "Error download" in resStatus.Status.tolist() or "Unexpected file type" in resStatus.Status.tolist():
    resStatus.to_csv(logfile,sep="\t",index=False)
    send_email(os.getenv("MAIL_USERNAME"),os.getenv('MAIL_PASSWORD'),os.getenv("MAIL2_NAME"),'GC4 DB Update Error','Please find attached the file with the information of downloading',logfile)
