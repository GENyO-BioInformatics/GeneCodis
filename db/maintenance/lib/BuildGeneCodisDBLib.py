#!/usr/bin/python
# -*- coding: utf-8 -*-

from multiprocessing import Pool
import glob
import pandas
from pathlib import Path
import os,re
import requests
import urllib
import urllib.request
import numpy
import psycopg2
import psycopg2.extras
import datetime
import time
import zipfile
import json
from fdict import fdict, sfdict
import sys
import gzip
from zipfile import ZipFile
import networkx
import obonet

from gtfparse import read_gtf
import magic
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path
import subprocess
from dotenv import load_dotenv
from pathlib import Path  # Python 3.6+ only
import pyreadr
from collections import ChainMap
pandas.options.mode.chained_assignment = None

##################### Useful functions #################

def unique(list1):
    """Function to return the unique list of elements of a list"""
    unique_list=set(list1)
    unique_list=list(unique_list)
    return unique_list

def list_duplicates(seq):
    """ Function that returns the duplicated elements from a list"""
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set( x for x in seq if x in seen or seen_add(x) )
    # turn the set into a list (as requested)
    return list( seen_twice )

def read_zip_file(filepath,filename):
    """ Function to read zip files"""
    with zipfile.ZipFile(filepath) as z:
       with z.open(filename) as f:
          df = pandas.read_csv(f, sep="\t")
    return df


##################### Generate and Download Tables Functions #############################################

def send_email(email_sender,password,email_recipient,email_subject,email_message,attachment_location = ''):

    """ Function used to send email with the status of downloading files"""

    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = email_subject

    msg.attach(MIMEText(email_message, 'plain'))

    if attachment_location != '':
        filename = os.path.basename(attachment_location)
        attachment = open(attachment_location, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        "attachment; filename= %s" % filename)
        msg.attach(part)

    try:
        server = smtplib.SMTP("mail.genyo.es",587)
        server.ehlo()
        server.starttls()
        server.login(email_sender, password)
        text = msg.as_string()
        server.sendmail(email_sender, email_recipient, text)
        print('email sent')
        server.quit()
    except Exception as errorwhatever:
        print(errorwhatever)
        print("SMPT server connection error")
    return True

def check_file_MIME(type,pre_file,name):
    """ Function used to check if the downloaded file match with expected file format"""
    info = magic.from_file(pre_file,mime=True) #magic is used to get the MIME-type file
    info = 'application/gzip' if info == 'application/x-gzip' else info # This line change the MIME-type file for gzip because x-gzip fails
    if type == info: # If the expected MIME -file type matches with downaloaded MIME-file type the downloading is correct
        if os.path.isfile(name): # Remove file in case that it exists
            os.remove(name)
        os.rename(pre_file,name) # Rename pre_file as correct file name
        res = {name:"Correct"}
    else: # If MIME-types do not match, it is catch as an error
        res = {name:"Unexpected file type"}
    return res

def download_file(url,name,type,download):

    """ Function used to download files in two different ways.
    While download 'Normal' uses urllib.request.urlretrieve
    'Alt' download uses requests.get

    When we download a file, this is write as pre_file (v1)
    When we check that all is correct we rename the file to final file name"""

    filename, file_extension = os.path.splitext(name)
    pre_file = filename + "_v1" + file_extension # We create a pre file in order to do not overwrite the file previously downloaded. This is used to control errors in downloading process
    res = {}
    if download == "Normal":
        try: # We use try in order to catch exception in case the download fails
            urllib.request.urlretrieve(url,pre_file)
        except Exception as errorwhatever:
            res = {name:"Error download"}
    else:
        try: # We use try in order to catch exception in case the download fails
            r = requests.get(url)
            with open(pre_file, 'wb') as f:
                f.write(r.content)
        except Exception as errorwhatever:
            print(errorwhatever)
            res = {name:"Error download"}
    if len(res) == 0: # If there is not error in downloading
        res = check_file_MIME(type,pre_file,name) # Check MIME and change file name in case of success
    return res

def check_gz_files(url,name,type,download):
    """ Check that gz files can be read with zcat. If not, retry the downloading """
    error = True
    while error:
        res = subprocess.Popen(['gzip', '-v','-t', name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout,stderr = res.communicate()
        stdout = stdout.decode('ascii').rstrip().split("\t")[1].replace(" ","")
        if stdout == "OK":
            error = False
        else:
            download_file(url,name,type,download)

def write_dorothea(tax_id):
    """ Function that will read rdata downloaded from dorohea and transform it to dataframe"""
    result = pyreadr.read_r('data/'+str(tax_id)+'_dorothea.rda') # also works for Rds
    df1 = result[list(result.keys())[0]]
    df1 = df1.loc[df1.confidence.isin(["A","B","C"])]
    df1.to_csv("data/"+str(tax_id)+"_DoRothEA.tsv",sep="\t",index=None)

def process_gtf(n,tax_id,infoFile):
    """ Function used to read gtf file and return dataframe in tsv file"""
    fileName = list(infoFile)[0]
    status = infoFile[fileName]
    if status == "Correct":
        df = read_gtf(fileName) # This converts gtf to dataframe
        if "gene_name" in df.columns:
            df_genes = df[df["feature"] == "gene"].loc[:,["gene_id","gene_name","start","end"]]
        else:
            df_genes = df[df["feature"] == "gene"].loc[:,["gene_id","gene_id","start","end"]]
            df_genes.columns = ["gene_id","gene_name","start","end"]
        gtfFile = "data/"+str(tax_id) +"_"+str(n)+ "_gtf.tsv"
        df_genes.to_csv(gtfFile,sep="\t",index=None) # Write tsv file
    os.system("rm "+fileName) # Remove gtf file

def ensembl_gtf(tax_id,url):
    """ Function used to filter, download and read gtf files for each taxonomy identifier"""
    # Read {tax_id}_ensembl_directory file
    with open("data/"+str(tax_id)+"_ensembl_directory") as f:
        content = f.readlines()
        content_files = []
        for line in content:
            content_files.append(line.rstrip().split(" ")[-1])
    #Filter file keeping only .gtf and removing chromosome and abinitio files
    content_files = [x for x in content_files if "gtf" in x]
    content_files = [x for x in content_files if "chr." not in x]
    gtfFiles = [x for x in content_files if "abinitio" not in x]

    # Now, all gtf files are going to be downloaded and processed

    # First we prepare input data to use download_file function
    info = [download_file(url+gtfFile,"data/"+str(tax_id)+"_"+(url+gtfFile).split("/")[-1],"application/gzip","Normal") for gtfFile in gtfFiles]

    # Then we apply process_gtf file to read gtf as pandas dataframe and remove original gtf because it's not needed
    # In some ocassion there are more than one gtf file, so we name the files as {taxonomy_id}_n_gtf.tsv
    input_data = [process_gtf(n,tax_id,info[n]) for n in range(len(info))]

    info = dict(ChainMap(*info))
    return(info)

def generate_sub_files_gene_info(tax_id,filename):
    """ Function to separate gene info by tax id """
    out = os.path.basename(filename)
    out = out.split(".")[0]
    os.system('zcat '+filename+' | awk -F\''+str("\t")+'\' \'$1==\"'+str(tax_id)+'\" {print}\' >data/'+str(tax_id)+"_"+out+".tsv")
    content = os.popen('zcat '+filename+' | awk -F\''+str("\t")+'\' \'$1==\"#tax_id\" {print}\'').read()
    os.system('sed -i -e \'1i'+content+'\' data/'+str(tax_id)+"_"+out+".tsv")

def generate_sub_files_gaf(tax_id,name):
    """Function to generate gaf files for each tax id"""
    print('zgrep "\<taxon:'+str(tax_id)+'\>" '+name+'>data/'+str(tax_id)+'.gaf')
    os.system('zgrep "\<taxon:'+str(tax_id)+'\>" '+name+'>data/'+str(tax_id)+'.gaf')

def process_epic_manifest():
    """ Function to process epic manifest and obtain json with cpgs and genes"""
    with zipfile.ZipFile("data/meth.zip","r") as zip_ref:
        zip_ref.extractall("data/meth")
    file_loc = glob.glob("data/meth/*")[0]

    content = pandas.read_csv(file_loc,skiprows=7).iloc[:,[0,15]].dropna()

    meth_dictionary = content.set_index('IlmnID').to_dict()["UCSC_RefGene_Name"]

    meth_dictionary = {cpg:list(set(meth_dictionary[cpg].split(";"))) for cpg in meth_dictionary}

    with open('data/meth.json', 'w') as outfile:
        json.dump(meth_dictionary, outfile)

    os.system("rm -r data/meth")

def download_wikipathways(taxonomy_data):
    """ Function to download wikipathways files"""
    url = "http://data.wikipathways.org/current/gmt/"
    name = "wiki.html"
    r = requests.get(url)
    htmlSTR = str(r.content,'utf-8')
    gmtlink = re.compile("href='./(wikipathways-[0-9]+-gmt-[A-Z][a-z]+_[a-z]+.gmt)'")
    gmts = list(set(gmtlink.findall(htmlSTR)))
    gmtslinks = [url + x for x in gmts]
    organisms = [os.path.basename(gmtlink).split("-gmt-")[1].split(".gmt")[0].replace("_"," ") for gmtlink in gmtslinks]
    gmtslinks = {organisms[i]:gmtslinks[i] for i in range(len(organisms)) if organisms[i] in taxonomy_data.output_name.tolist()}
    gmtslinks = pandas.DataFrame(gmtslinks.items(), columns=['organism', 'url']).merge(taxonomy_data,left_on="organism",right_on="output_name").iloc[:,[2,1]]

    urls = gmtslinks.url.tolist()
    names = ["data/"+str(id)+".gmt" for id in gmtslinks.taxonomy_id.tolist()]

    input_data = [(urls[i],names[i],"text/plain","Alt") for i in range(len(urls))]

    with Pool() as pool: #Run pool.starmap using ensembl_gtf function. This will take a long time
        res_wiki = pool.starmap(download_file,input_data)
    res_wiki = dict(ChainMap(*res_wiki))
    return res_wiki

def download_kegg(taxonomy_data):
    """ Function to download kegg files """
    print("Downloading KEGG files")
    input_data = [(taxonomy_data.kegg_id.tolist()[i],taxonomy_data.taxonomy_id.tolist()[i]) for i in range(len(taxonomy_data.index))]
    with Pool() as pool: #Run pool.starmap using ensembl_gtf function. This will take a long time
        res_kegg = pool.starmap(download_single_kegg,input_data)
    res_kegg = dict(ChainMap(*res_kegg))
    return res_kegg

def download_single_kegg(kegg_id,tax_id):
    """ Function to download kegg files by tax_id """
    res1 = download_file(os.path.join('http://rest.kegg.jp/link',kegg_id,'pathway'),"data/"+str(tax_id)+"_kegg.tsv","text/plain","Normal")
    res2 = download_file(os.path.join('http://rest.kegg.jp/conv',kegg_id,'ncbi-geneid'),"data/"+str(tax_id)+"_kegg_ncbi.tsv","text/plain","Normal")
    res3 = download_file(os.path.join('http://rest.kegg.jp/list/pathway/',kegg_id),'data/'+str(tax_id)+'_kegg_pathways.tsv',"text/plain","Normal")
    res_kegg = {**res1,**res2,**res3}
    return res_kegg

def correct_tables(table,id):
    """ Function to remove duplicates"""
    table = table.reset_index(drop=True)
    duplicated = list_duplicates(table[id].tolist())
    for duplicated_sing in duplicated:
        indexes = [i for i, x in enumerate(table[id].tolist()) if x == duplicated_sing]
        table = table.drop(table.index[indexes[1]])
    return table

##################### Update GeneCodis Gene Tables #############################################

def read_manipulate_gene_info_by_tax(data_dir,tax_id,refseq2uniprot):
    """ Function to get all synonyms of entrez genes by tax_id: symbol, other_names,dbxRefs,uniprot,description and date"""
    sub_gene_info = pandas.read_csv(os.path.join(data_dir,str(tax_id)+"_gene_info.tsv"),sep="\t",low_memory=False).drop_duplicates()
    sub_refseq = pandas.read_csv(os.path.join(data_dir,str(tax_id)+"_gene2refseq.tsv"),sep="\t",low_memory=False).drop_duplicates()
    sub_gene_info['GeneID'] = [ str(x) for x in sub_gene_info['GeneID'].tolist() ]
    sub_gene_info['#tax_id'] = [ str(x) for x in sub_gene_info['#tax_id'].tolist() ]
    sub_refseq = sub_refseq[sub_refseq['protein_accession.version']!="-"]
    sub_refseq['GeneID'] = [ str(x) for x in sub_refseq['GeneID'].tolist() ]
    sub_refseq['#tax_id'] = [ str(x) for x in sub_refseq['#tax_id'].tolist() ]
    sub_refseq['protein_accession.version'] = [str(x.split(".")[0]) for x in sub_refseq['protein_accession.version'].tolist()]
    full_table = sub_refseq.merge(refseq2uniprot,left_on='protein_accession.version',right_on="#NCBI_protein_accession").iloc[:,[1,16,17]]
    full_table = sub_gene_info.merge(full_table,on="GeneID",how="left").fillna("").iloc[:,[0,1,2,4,5,8,14,17]].drop_duplicates()
    ensembl_table = pandas.read_csv(os.path.join(data_dir,"gene2ensembl.gz"),compression='gzip',sep="\t",low_memory=False).iloc[:,[0,1,2]].drop_duplicates()
    ensembl_table['GeneID'] = [ str(x) for x in ensembl_table['GeneID'].tolist() ]
    ensembl_table = ensembl_table[ensembl_table['GeneID'].isin(full_table['GeneID'].tolist())]
    full_table = full_table.merge(ensembl_table,on="GeneID",how="left").fillna("").iloc[:,[0,1,2,3,4,5,6,7,9]].drop_duplicates()
    full_table.columns = ['tax_id','entrez','symbol','other_names','dbxRefs','description','date','uniprot','ensembl']
    return(full_table)

def create_gene_table(full_table):
    """ Function to create Gene Table """
    symbols = full_table.iloc[:,[0,2,5]].drop_duplicates()
    symbols = symbols.iloc[:,[1,2,0]]
    return symbols

def check_genes_pool(symbol,rows,symbols):
    """ Function to process all possible synonyms by gene """

    # Check date
    entrez_values = unique(rows['entrez'].tolist())
    if (len(entrez_values)>1):
        last_date = sorted(rows['date'].tolist(),reverse=True)[0]
        description = rows[rows['date']==last_date]['description'].tolist()[0]
        rows['description'] = [description]*len(rows.index)

    # Check other names
    other_names = unique(rows['other_names'].tolist())
    other_names_total = []
    for other_name in other_names:
        if other_name != "-":
            other_name = other_name.split("|")
        else:
            other_name = ['']
        other_names_total.extend(other_name)

    other_names_total = [x for x in other_names_total if x != ""]
    other_names_total = [x for x in other_names_total if x not in symbols]

    # Check other databases
    dbxRefs = unique(rows['dbxRefs'].tolist())
    dbxRefs_total = []
    for row in dbxRefs:
        if row != "-":
            dbxRefs_row = row.split("|")
        else:
            dbxRefs_row = ['']
        dbxRefs_total.extend(dbxRefs_row)

    dbxRefs_total = [x for x in dbxRefs_total if x != ""]
    dbxRefs_total = unique(dbxRefs_total)

    description = unique(rows['description'].tolist())[0]

    uniprot = unique(rows['uniprot'].tolist())
    uniprot = [x for x in uniprot if x != ""]

    ensembl = unique(rows['ensembl'].tolist())
    ensembl = [x for x in ensembl if x != ""]

    #Load all info in a dictionary
    dictionary_gene = {'source':[],'synonyms':[],'description':[],'symbol':[]}

    dictionary_gene['source'].extend(['dbxRefs']*len(dbxRefs_total))
    dictionary_gene['synonyms'].extend(dbxRefs_total)

    dictionary_gene['source'].extend(["symbol"])
    dictionary_gene['synonyms'].extend([symbol])

    dictionary_gene['source'].extend(['other_name']*len(other_names_total))
    dictionary_gene['synonyms'].extend(other_names_total)

    dictionary_gene['source'].extend(['entrez']*len(entrez_values))
    dictionary_gene['synonyms'].extend(entrez_values)

    dictionary_gene['source'].extend(['uniprot']*len(uniprot))
    dictionary_gene['synonyms'].extend(uniprot)

    dictionary_gene['source'].extend(['ensembl']*len(ensembl))
    dictionary_gene["synonyms"].extend(ensembl)

    dictionary_gene['description'].extend([description]*len(dictionary_gene['source']))
    dictionary_gene['symbol'].extend([symbol]*len(dictionary_gene['source']))

    return(dictionary_gene)

def build_synonyms_table(syns_table):
    """ Function to build synonyms table """
    symbols = unique(syns_table['symbol'].tolist())
    input_data = [(symbol,syns_table.loc[syns_table.symbol.isin([symbol])],symbols) for symbol in symbols]

    with Pool() as pool:
        pool_out=pool.starmap(check_genes_pool, input_data)

    super_dict = {'symbol':[],'source':[],'synonyms':[]}
    for i in range(0,len(pool_out)):
        subdict = pool_out[i]
        super_dict['source'].extend(subdict['source'])
        super_dict['synonyms'].extend(subdict['synonyms'])
        super_dict['symbol'].extend(subdict['symbol'])
    super_df = pandas.DataFrame(super_dict).sort_values('symbol')
    super_df = super_df[super_df['synonyms']!=""].reset_index().iloc[:,[1,2,3]]
    idxs = []
    for i in range(0,len(super_df.index)):
        row = super_df.iloc[i,:]
        if row['synonyms'].isdigit() and row['source']=="other_name":
            idxs.append(i)

    syns_table = super_df.drop(idxs)
    syns_table = check_syns_names(syns_table)
    return syns_table

def check_syns_pool(syns_name,source):
    """Function to filter synonyms names"""
    patterns = ["Ensembl:","TAIR:","WormBase:","FLYBASE:","miRBase:","EnsemblRapid:"]
    syns_name_new = syns_name
    source_new = source
    for pattern in patterns:
        if pattern in syns_name:
            syns_name_new = syns_name.replace(pattern,"")
            source_new = pattern.replace(":","")
    if source == "dbxRefs" and ":" in syns_name_new:
        syns_name_new = "---"
    return source_new,syns_name_new

def check_syns_names(syns_table):
    """ Function to filter and label synonyms """
    with Pool() as pool:
        pool_out = pool.starmap(check_syns_pool, zip(syns_table['synonyms'].tolist(),syns_table['source'].tolist()))
    source = []
    syns_name = []
    for i in pool_out:
        source.append(i[0])
        syns_name.append(i[1])

    syns_table['synonyms'] = syns_name
    syns_table['source'] = source
    syns_table = syns_table.drop(syns_table[syns_table.source == "dbxRefs"].index)

    syns_table = syns_table.reset_index().iloc[:,[1,2,3]]

    duplicated_gene_synonyms = list_duplicates(syns_table['synonyms'].tolist())
    indexes = []
    for syn_name in duplicated_gene_synonyms:
        rows = syns_table[(syns_table['synonyms'] == syn_name) & (syns_table['source'] == "other_name")]
        if len(rows.index) > 1:
            for j,val in enumerate(rows.index):
                indexes.append(val)

    syns_table = syns_table.drop(indexes)
    syns_table = syns_table.drop_duplicates()

    syns_table = syns_table.reset_index().iloc[:,[1,2,3]]
    syns_table['source'].loc[(syns_table['source'] == "miRBase")] = "mirbase"
    syns_table['source'].loc[(syns_table['source'] == "FLYBASE")] = "ensembl"
    syns_table['source'].loc[(syns_table['source'] == "TAIR")] = "tair"
    syns_table['source'].loc[(syns_table['source'] == "WormBase")] = "wormbase"
    syns_table['source'].loc[(syns_table['source'] == "Ensembl")] = "ensembl"
    syns_table['source'].loc[(syns_table['source'] == "EnsemblRapid")] = "ensembl"
    syns_table = syns_table.drop_duplicates()
    return syns_table

def ensembl_checking(tax_id,syns_table,gene_table,data_dir):
    """ Function to add ensembl information, including gene length"""
    gtf_files = glob.glob(os.path.join(data_dir,tax_id+"*gtf.tsv"))
    gtfContent = pandas.DataFrame({"gene_id":[],"gene_name":[],"start":[],"end":[]})
    if len(gtf_files) > 0:
        for gtfFile in gtf_files:
            gtfFileDF = pandas.read_csv(gtfFile,sep="\t").dropna()
            gtfContent = pandas.concat([gtfContent,gtfFileDF]).drop_duplicates()
    mergeTable = gtfContent.merge(syns_table,left_on="gene_name",right_on="synonyms").iloc[:,[4,5,0,2,3]]
    length = mergeTable["end"] - mergeTable["start"]
    length = length.abs()
    mergeTable['length'] = length
    mergeTable = mergeTable.drop(columns=['start', 'end'])
    symbols = list(set(mergeTable.symbol))
    with Pool() as pool:
        pool_out=pool.starmap(calculate_length, zip(symbols,[mergeTable]*len(symbols)))
    mergeTable = pandas.concat(pool_out)
    synsGenes = gtfContent.merge(syns_table,left_on="gene_name",right_on="synonyms").iloc[:,[4,5,0]]
    synsGenes.columns = syns_table.columns
    synsGenes['source'] = "ensembl"
    syns_table = pandas.concat([syns_table,synsGenes])
    gene_table = gene_table[gene_table.symbol.isin(mergeTable.symbol)]
    syns_table = syns_table[syns_table.symbol.isin(mergeTable.symbol)]
    gene_table = gene_table.merge(mergeTable,on="symbol").iloc[:,[0,1,4,2]].drop_duplicates()
    syns_table = syns_table.drop_duplicates()
    result = {tax_id:{"syns_table":syns_table,"gene_table":gene_table}}
    return result

def Average(lst):
    return sum(lst) / len(lst)

def calculate_length(symbol,mergeTable):
    rowsMerge = mergeTable[mergeTable.symbol==symbol]
    if len(rowsMerge.index) > 1:
        average = Average(rowsMerge.length.tolist())
        insertRow = {"symbol":[symbol],"source":[rowsMerge.source.tolist()[0]],"length":[average]}
    else:
        insertRow = {"symbol":[symbol],"source":[rowsMerge.source.tolist()[0]],"length":[rowsMerge.length.tolist()[0]]}
    insertRow = pandas.DataFrame(insertRow)
    return(insertRow)

def update_miRNA_names(syns_table,data_dir,tax_id,taxonomy_information,gene_table,mirbaseDB):
    """ Function to include miRNA accession names as synonyms or as new genes """
    kegg = taxonomy_information[taxonomy_information['taxonomy_id'] == tax_id]['kegg_id'].tolist()[0]
    mirbaseDB = mirbaseDB[mirbaseDB.ID.str.contains(kegg)].reset_index().iloc[:,[1,2]]
    for i in range(len(mirbaseDB.index)):
        row = mirbaseDB.iloc[i,:]
        if row.ID in syns_table.synonyms.tolist():
            syns_table.loc[syns_table['synonyms'] == row.ID, ['source']] = "mirbase"
            symbol = syns_table[syns_table.synonyms == row.ID].symbol.tolist()[0]
            syns_append = pandas.DataFrame({"symbol":[symbol]*2,"source":["mirbase"]*2,"synonyms":[row.ID,row.Accession]}).drop_duplicates()
            syns_table = pandas.concat([syns_table,syns_append])
        else:
            if row.ID.replace(kegg+"-","") in syns_table.synonyms.tolist():
                syns_table.loc[syns_table['synonyms'] == row.ID.replace(kegg+"-",""), ['source']] = "mirbase"
                symbol = syns_table[syns_table.synonyms == row.ID.replace(kegg+"-","")].symbol.tolist()[0]
                syns_append = pandas.DataFrame({"symbol":[symbol]*2,"source":["mirbase"]*2,"synonyms":[row.ID,row.Accession]}).drop_duplicates()
                syns_table = pandas.concat([syns_table,syns_append])
            else:
                syns_append = pandas.DataFrame({"symbol":[row.ID]*2,"source":["mirbase"]*2,"synonyms":[row.ID,row.Accession]}).drop_duplicates()
                gene_append = pandas.DataFrame({'symbol':[row.ID],"description":[""],"length":[0],"tax_id":[tax_id]})
                gene_table = pandas.concat([gene_table,gene_append])
                syns_table = pandas.concat([syns_table,syns_append])

    syns_table = syns_table.drop_duplicates()
    result = {tax_id:{"syns_table":syns_table,"gene_table":gene_table}}
    return(result)

def check_gene_names(gene_table):
    """ Function to check gene names"""
    symbols = list(set(gene_table.symbol.tolist()))
    with Pool() as pool:
        pool_out=pool.starmap(remove_duplicated_genes, zip(symbols,[gene_table]*len(symbols)))
    gene_table = pandas.concat(pool_out)
    return gene_table

def remove_duplicated_genes(symbol,gene_table):
    """ Function to remove duplicates"""
    rowSymbol = gene_table[gene_table.symbol==symbol]
    rowSymbol = rowSymbol.iloc[[0],:]
    return rowSymbol

def define_GC4_internal_ids(gene_table,tax_id,syns_table):
    """ Function to add GC internal ids for each gene"""
    symbols = gene_table.symbol.tolist()
    internal_id = ["GC-"+str(tax_id)+"-"+str(x) for x in range(len(symbols))]
    gene_table['id']=internal_id
    gene_table = gene_table.iloc[:,[4,0,1,2,3]]
    syns_table = syns_table.merge(gene_table,on="symbol").iloc[:,[3,1,2]]
    result = {tax_id:{"syns_table":syns_table,"gene_table":gene_table}}
    return (result)

def merge_ensembl(Synonyms_Table,data_dir):
    """ Function to add and check ensembl id from NCBI"""
    ensembl_table = pandas.read_csv(os.path.join(data_dir,"gene2ensembl.gz"),compression='gzip',sep="\t",low_memory=False).iloc[:,[0,1,2]].drop_duplicates()
    ensembl_table['GeneID'] = [ str(x) for x in ensembl_table['GeneID'].tolist() ]
    ensembl_table = ensembl_table[ensembl_table['GeneID'].isin(Synonyms_Table['synonyms'].tolist())]
    genes = unique(ensembl_table['GeneID'].tolist())
    with Pool() as pool:
        pool_out = pool.starmap(ensembl_pool, zip(genes,[ensembl_table]*len(genes),[Synonyms_Table]*len(genes)))
    pool_out = pandas.concat(pool_out)
    Synonyms_Table = pandas.concat([Synonyms_Table,pool_out])
    Synonyms_Table = Synonyms_Table.drop_duplicates().reset_index().sort_values('id').iloc[:,[1,2,3]]
    return(Synonyms_Table)

def ensembl_pool(gene,ensembl_table,Synonyms_Table):
    """Function to get ensembl ids per gene"""
    gc_id = Synonyms_Table[Synonyms_Table['synonyms'] == gene]['id'].tolist()[0]
    ensembl_ids = ensembl_table[ensembl_table['GeneID'] == gene]['Ensembl_gene_identifier'].tolist()
    rows = []
    for ensembl_id in ensembl_ids:
        rows.append({'id':gc_id,'source':'ensembl','synonyms':ensembl_id})
    rows = pandas.DataFrame(rows)
    return(rows)

##################### Update GeneCodis Annotation #############################################

def build_lincs(data_dir,Gene_Table):
    """ Function to annotate genes with lincs database """
    print("\tStart Step 3.1. Annotate LINCS")
    human_gene = Gene_Table[Gene_Table['tax_id']==9606]
    lincs_db = pandas.read_csv(os.path.join(data_dir,"LINCS.tsv"),sep="\t").dropna()
    lincs_ann = lincs_db.iloc[:,[2,0]]
    lincs_ann.columns = ['annotation_id','term']
    lincs_ids = lincs_ann['annotation_id'].tolist()
    input_data = [(lincs_db.loc[lincs_db.ID.isin([id])].Target.tolist()[0],id,human_gene) for id in lincs_ids]
    with Pool() as pool:
        lincs = pandas.concat(pool.starmap(lincs_by_gene, input_data))

    lincs['annotation_source'] = 'LINCS'
    lincs = lincs.drop_duplicates()
    lincs_ann = lincs_ann.drop_duplicates()

    print("\tFinish Step 3.1.")
    return(lincs,lincs_ann)

def lincs_by_gene(targets,id,human_gene):
    """ Function to get all genes annotated by lincs annotation"""
    targets = [x for x in targets.split(", ")]
    human_gene = human_gene.loc[human_gene.symbol.isin(targets)].id.tolist()
    return(pandas.DataFrame({"id":human_gene,"annotation_id":[id]*len(human_gene)}))

def build_bioplanet(data_dir,Synonyms_Table):
    """ Function to annotate bioplanet database"""
    print("\tStart Step 3.2. Annotate BioPlanet")
    bioplanet_df = pandas.read_csv(os.path.join(data_dir,"bioplanet.csv"),low_memory=False).drop_duplicates()
    bioplanet_df.GENE_ID = [str(x) for x in bioplanet_df.GENE_ID.tolist()]
    bioplanet_table = Synonyms_Table.merge(bioplanet_df,left_on="synonyms",right_on="GENE_ID")
    bioplanet_table["annotation_source"] = "BioPlanet"
    bioplanet_table = bioplanet_table.iloc[:,[0,3,7]]
    bioplanet_table.columns = ["id","annotation_id","annotation_source"]
    bioplanet_ann = bioplanet_df.iloc[:,[0,1]].drop_duplicates()
    bioplanet_ann.columns = ["annotation_id","term"]
    print("\tFinish Step 3.2.")
    return bioplanet_table,bioplanet_ann

def build_disgenet(data_dir,Synonyms_Table):
    """ Function to annotate DisGeNET database"""
    print("\tStart Step 3.3. Annotate DisGeNET")
    disgenet_df = pandas.read_csv(os.path.join(data_dir,"disgenet.tsv.gz"),compression='gzip',sep="\t",low_memory=False).drop_duplicates()
    disgenet_df.geneId = [str(x) for x in disgenet_df.geneId.tolist()]
    disgenet_table = Synonyms_Table.merge(disgenet_df,left_on="synonyms",right_on="geneId")
    disgenet_table["annotation_source"] = "DisGeNET"
    disgenet_table = disgenet_table.iloc[:,[0,7,19]]
    disgenet_table.columns = ["id","annotation_id","annotation_source"]
    disgenet_ann = disgenet_df.iloc[:,[4,5]].drop_duplicates()
    disgenet_ann.columns = ["annotation_id","term"]
    print("\tFinish Step 3.3.")
    return disgenet_table,disgenet_ann

def read_gmtFile(gmtFile):
    """ Function to read properly gmt files"""
    #Open, read and split file
    with open(gmtFile,"r") as gmtFile:
        gmtFile = gmtFile.readlines()
    gmtFile = [x.rstrip().split("\t") for x in gmtFile]

    #Obtain Meta and Genes Information
    pathMeta = [x[0] for x in gmtFile]
    pathMeta = [x.split("%") for x in pathMeta]
    pathNames = [x[0].lstrip() for x in pathMeta]
    pathIDs = [x[2] for x in pathMeta]
    pathGenes = [x[2::] for x in gmtFile]

    #Build table
    annotation_dict = {'annotation_id':[], 'synonyms':[]}
    for i in range(len(pathIDs)):
        genes = pathGenes[i]
        id = [pathIDs[i]]*len(genes)
        annotation_dict['annotation_id'].extend(id)
        annotation_dict['synonyms'].extend(genes)

    annotation_info = {'annotation_id':pathIDs,'term':pathNames}
    return(annotation_dict,annotation_info)

def build_wikipathways(data_dir,Synonyms_Table):
    """ Function to annotate genes in WikiPathways"""
    print("\tStart Step 3.4. Annotate WikiPathways")
    gmts = glob.glob("data/*gmt")
    annotation_dict = {'annotation_id':[],'synonyms':[]}
    annotation_info = {'annotation_id':[],'term':[]}
    for gmt in gmts:
        ann_dict, ann_info = read_gmtFile(gmt)
        annotation_dict['annotation_id'].extend(ann_dict['annotation_id'])
        annotation_dict['synonyms'].extend(ann_dict['synonyms'])
        annotation_info['annotation_id'].extend(ann_info['annotation_id'])
        annotation_info['term'].extend(ann_info['term'])

    annotation_dict = pandas.DataFrame(annotation_dict)
    annotation_dict = annotation_dict.merge(Synonyms_Table,on="synonyms").iloc[:,[2,0]]
    annotation_dict['annotation_source'] = "WikiPathways"
    annotation_info = pandas.DataFrame(annotation_info)
    annotation_info = annotation_info[annotation_info['annotation_id'].isin(annotation_dict['annotation_id'].tolist())]
    annotation_dict = annotation_dict.drop_duplicates()
    annotation_info = annotation_info.drop_duplicates()
    print("\tEnd Step 3.4.")
    return(annotation_dict,annotation_info)

def build_reactome(data_dir,Synonyms_Table):
    """ Function to annotate Reactome pathways """
    print("\tStart Step 3.5. Annotate Reactome")
    reactome_table = pandas.read_csv(os.path.join(data_dir,"Reactome.txt"),sep="\t",header=None,low_memory=False).iloc[:,[0,1,3]]
    reactome_table.columns = ['synonyms',"annotation_id",'term']
    reactome_table = reactome_table.merge(Synonyms_Table,on="synonyms").iloc[:,[3,1,2]]
    reactome_ann = reactome_table.iloc[:,[1,2]].drop_duplicates()
    reactome_table = reactome_table.iloc[:,[0,1]]
    reactome_table['annotation_source']="Reactome"
    reactome_ann = reactome_ann.drop_duplicates()
    reactome_table = reactome_table.drop_duplicates()
    print("\tFinish Step 3.5.")
    return(reactome_table,reactome_ann)

def build_miRNA(data_dir,Synonyms_Table,prec2maturesmirnasHuman):
    """ Function to annotate three direct annotation of miRNAs: MNDR, TAM2 and HMDD"""
    print("\tStart Step 3.6. Annotate miRNA")
    mndr_table,mndr_ann = build_mndr(data_dir,Synonyms_Table)
    tam2_table,tam2_ann = build_tam2(data_dir,Synonyms_Table,prec2maturesmirnasHuman)
    hmdd_table,hmdd_ann = build_hmdd(data_dir,Synonyms_Table,prec2maturesmirnasHuman)
    mirna_table = pandas.concat([mndr_table,tam2_table,hmdd_table]).drop_duplicates()
    mirna_ann = pandas.concat([mndr_ann,tam2_ann,hmdd_ann]).drop_duplicates()
    print("\tFinish Step 3.6.")
    return(mirna_table,mirna_ann)

def build_mndr(data_dir,Synonyms_Table):
    """ Function to annotate MNDR """
    print("\t\tStart Step 3.6.1. Annotate MNDR database")
    with ZipFile(os.path.join(data_dir,"mndr.zip"), 'r') as zipObj:
        zipObj.extractall(data_dir)
    mndrDB = pandas.read_csv(os.path.join(data_dir,"miRNA-disease information/Experimental miRNA-disease information.txt"),sep="\t").iloc[:,[0,1,2,3,4,5,6,7,8]]
    mndrDB = mndrDB.merge(Synonyms_Table,left_on="ncRNA symbol",right_on="synonyms").iloc[:,[0,1,3,4,6,9,10,11]].dropna()
    mndrDB = mndrDB[mndrDB.source == "mirbase"]
    mndr_ann = mndrDB[mndrDB.source == "mirbase"].iloc[:,[4,3]].drop_duplicates()
    mndr_ann.columns = ['annotation_id',"term"]
    mndr_table = mndrDB.iloc[:,[5,4]].drop_duplicates()
    mndr_table["annotation_source"] = "MNDR"
    mndr_table.columns = ['id','annotation_id','annotation_source']
    print("\t\tFinish Step 3.6.1.")
    return(mndr_table,mndr_ann)

def build_tam2(data_dir,Synonyms_Table,prec2maturesmirnasHuman):
    """ Function to annotate TAM2"""
    print("\t\tStart Step 3.6.2. Annotate TAM 2.0 database")
    tam2DB = {"miRNA":[],"term":[]}
    ann_ids = []
    with open(os.path.join(data_dir,"tam2.txt"),"r") as tam2:
        for line in tam2:
            line = line.rstrip()
            line = line.split("\t")
            header = line[0]
            if header in ['Function']:
                term = line[1]
                mirnas = line[2::]
                for mirna in mirnas:
                    if mirna not in prec2maturesmirnasHuman:
                        continue
                    precAndMats = [mirna] + prec2maturesmirnasHuman[mirna]
                    tam2DB['miRNA'].extend(precAndMats)
                    tam2DB['term'].extend([term] * len(precAndMats))
                    ann_ids.append(term)
    ann_ids = list(set(ann_ids))
    tam2_ann = {"annotation_id":[],"term":[]}
    for i in range(len(ann_ids)):
        tam2_ann["annotation_id"].append("tam2_"+str(i))
        tam2_ann['term'].append(ann_ids[i])

    tam2_ann = pandas.DataFrame(tam2_ann)
    tam2DB = pandas.DataFrame(tam2DB)
    tam2_table = tam2DB.merge(Synonyms_Table,left_on = "miRNA", right_on = "synonyms").iloc[:,[2,1]]
    tam2_table['annotation_source'] = "TAM_2"
    tam2_table = tam2_table.merge(tam2_ann,on = "term").iloc[:,[0,3,2]]
    print("\t\tFinish Step 3.6.2.")
    return(tam2_table,tam2_ann)

def build_hmdd(data_dir,Synonyms_Table,prec2maturesmirnasHuman):
    """ Function to build HMDD """
    print("\t\tStart Step 3.6.3. Annotate HMDD v3 database")
    hmdd3DB = pandas.read_excel(os.path.join(data_dir,"hmdd3.xls"))#.iloc[:,[1,2]]
    hmdd3DB = dict(zip(hmdd3DB.mir.to_list(),hmdd3DB.disease.to_list()))
    hmdd3DBfull = {"miRNA":[],"term":[]}
    for mirna in hmdd3DB:
        if mirna not in prec2maturesmirnasHuman:
            continue
        precAndMats = [mirna] + prec2maturesmirnasHuman[mirna]
        hmdd3DBfull['miRNA'].extend(precAndMats)
        term = hmdd3DB[mirna]
        if "," in term:
            term = term.replace(" ","").split(",")
            term.reverse()
            term = " ".join(term)
        hmdd3DBfull['term'].extend([term] * len(precAndMats))
    hmdd3DB = pandas.DataFrame(hmdd3DBfull)
    #Synonyms_Table = pandas.read_csv("db/maintenance/raw_sql/synonyms_table.tsv",sep="\t")
    hmdd_table = hmdd3DB.merge(Synonyms_Table,left_on="miRNA",right_on="synonyms")
    hmdd_table['annotation_source'] = "HMDD_v3"
    hmdd_ann = {'annotation_id':[],'term':[]}
    i = 1
    for term in set(hmdd_table.term.to_list()):
        hmdd_ann['annotation_id'].append("hmdd3_"+str(i))
        hmdd_ann['term'].append(term)
        i += 1
    hmdd_ann = pandas.DataFrame(hmdd_ann)
    hmdd_table = hmdd_table.merge(hmdd_ann,left_on="term",right_on="term")
    hmdd_table = hmdd_table.loc[:,['id','annotation_id','annotation_source']]
    print("\t\tFinish Step 3.6.3.")
    return(hmdd_table,hmdd_ann)

def build_mirtarbase(data_dir,Synonyms_Table):
    """ Function to annotate miRTarBase"""
    print("\tStart Step 3.7. Annotate miRTarBase")
    read_target = pandas.read_excel(os.path.join(data_dir,"miRTarBase_SE_WR.xls")).iloc[:,[1,4]]
    read_target.columns = ['miRTarBase','synonyms']
    read_target['synonyms'] = [str(a) for a in read_target['synonyms'].tolist()]
    read_target =read_target.merge(Synonyms_Table, left_on='synonyms', right_on='synonyms').iloc[:,[2,0]]
    read_target =read_target.merge(Synonyms_Table, left_on='miRTarBase',right_on='synonyms').iloc[:,[0,2,1]]
    read_target.columns = ['id','annotation_id',"term"]
    read_target['annotation_source'] = 'miRTarBase'
    read_target = read_target.drop_duplicates()
    miRNA_ann = read_target.iloc[:,[1,2]].drop_duplicates()
    read_target = read_target.iloc[:,[0,1,3]]
    print("\tFinish Step 3.7.")
    return read_target,miRNA_ann

def build_methylation(data_dir,Gene_Table):
    """ Function to build methylation cpgs"""
    print("\tStart Step 3.8. Annotate CPGs")
    with open(data_dir+"/meth.json") as f:
        meth_info = json.load(f)

    df = pandas.DataFrame(list(meth_info.items()),columns = ['annotation_id','symbol'])
    subGene_Table = Gene_Table.loc[Gene_Table.tax_id.isin([9606])]
    input_data = [(cpg,meth_info[cpg]) for cpg in meth_info]
    with Pool() as pool:
        meth_info = pandas.concat(pool.starmap(by_cpg,input_data))
    meth_info = meth_info.merge(subGene_Table,on="symbol").iloc[:,[2,1]]
    meth_ann = meth_info
    meth_ann['term'] = meth_info['annotation_id'].tolist()
    meth_ann = meth_ann.iloc[:,[1,2]].drop_duplicates()
    meth_info['annotation_source'] = 'cpgs'
    meth_info = meth_info.iloc[:,[0,1,3]].drop_duplicates()
    print("\tFinish Step 3.8.")
    return(meth_info,meth_ann)

def by_cpg(cpg,genes):
    """ Function to build genes cpg subtables"""
    meth_info = pandas.DataFrame({"symbol":genes,"annotation_id":[cpg]*len(genes)})
    return meth_info

def build_dorothea(data_dir,Gene_Table):
    """ Function to annotate DoRothEA interactions"""
    print("\tStart Step 3.9. Annotate DoRothEA")
    dorothea_tables = glob.glob(os.path.join(data_dir,"*DoRothEA.tsv"))
    dorothea_table_tfs = pandas.DataFrame({'id':[],'annotation_id':[],'annotation_source':[]})
    dorothea_ann = pandas.DataFrame({'annotation_id':[],'term':[]})

    input_data = [(dorothea_table,Gene_Table[Gene_Table.tax_id == int(os.path.basename(dorothea_table).split("_")[0])]) for dorothea_table in dorothea_tables]
    with Pool() as pool:
        results = pool.starmap(by_dorothea,input_data)

    dorothea_table_tfs = pandas.concat([results[i][0] for i in range(len(results))]).drop_duplicates()
    dorothea_ann = pandas.concat([results[i][1] for i in range(len(results))]).drop_duplicates()
    print("\tFinish Step 3.9.")
    return(dorothea_table_tfs,dorothea_ann)

def by_dorothea(dorothea_table,org_genes):
    """ Function to process each dorothea table independently"""
    dorothea_tfs = pandas.read_csv(dorothea_table,sep="\t")
    dorothea_tfs = dorothea_tfs.merge(org_genes,left_on = "target",right_on="symbol").iloc[:,[4,0]].drop_duplicates()
    dorothea_tfs.columns = ["id",'annotation_id']
    dorothea_tfs['annotation_source'] = "DoRothEA"
    dorothea_ann_org = dorothea_tfs.merge(org_genes,left_on="annotation_id",right_on="symbol").iloc[:,[1,1]].drop_duplicates()
    dorothea_ann_org.columns = ["annotation_id",'term']
    res = [dorothea_tfs,dorothea_ann_org]
    return(res)

def build_MGI(data_dir,Synonyms_Table):
    """ Function to annotate MGI"""
    print("\tStart Step 3.10. Annotate MGI")
    with open(os.path.join(data_dir,"MGI_PhenoGenoMP.rpt")) as mgi:
        content = mgi.readlines()

    mgi = {'Mouse Marker Symbol':[],'Mammalian Phenotype ID':[]}
    for line in content:
        line_split = line.rstrip().split("\t")
        if len(line_split) == 6:
            if "|" in line_split[-1]:
                genes = line_split[-1].split("|")
                for gene in genes:
                    mgi['Mouse Marker Symbol'].append(gene)
                    mgi["Mammalian Phenotype ID"].append(line_split[3])
            else:
                mgi['Mouse Marker Symbol'].append(line_split[-1])
                mgi["Mammalian Phenotype ID"].append(line_split[3])

    mgi = pandas.DataFrame(mgi)
    homologenes = pandas.read_csv(os.path.join(data_dir,"HOM_AllOrganism.rpt"),sep="\t",low_memory=False).iloc[:,[0,2,4,5]]
    mouse_genes = homologenes[homologenes['Mouse MGI ID'].notna()]
    not_mouse_genes = homologenes[homologenes['Mouse MGI ID'].isna()]
    not_mouse_genes = not_mouse_genes[not_mouse_genes['DB Class Key'].isin(mouse_genes['DB Class Key'].tolist())]
    mouse_genes.set_index('DB Class Key',inplace=True)
    mouse_genes_dict = mouse_genes.to_dict()['Mouse MGI ID']
    not_mouse_genes['Mouse MGI ID'] = [mouse_genes_dict[homo] for homo in not_mouse_genes['DB Class Key']]
    homologenes = not_mouse_genes
    homologenes = homologenes.merge(mgi,left_on='Mouse MGI ID',right_on='Mouse Marker Symbol').iloc[:,[2,5]]
    homologenes["EntrezGene ID"] = [str(x) for x in homologenes["EntrezGene ID"]]
    homologenes = homologenes.merge(Synonyms_Table,left_on="EntrezGene ID",right_on="synonyms").iloc[:,[2,1]]
    ensembl_file = pandas.read_csv(os.path.join(data_dir,"MRK_ENSEMBL.rpt"),sep="\t",header=None).iloc[:,[0,5]]
    ensembl_file.columns = ['Mouse Marker Symbol','ensembl_id']
    mgi = ensembl_file.merge(mgi,on="Mouse Marker Symbol")
    mgi = mgi.merge(Synonyms_Table,left_on="ensembl_id",right_on="synonyms").iloc[:,[3,2]]
    mgi = pandas.concat([mgi,homologenes]).drop_duplicates()
    mgi['annotation_source'] = 'MGI'
    mgi.columns = ['id','annotation_id','annotation_source']
    mgi_info = pandas.read_csv(os.path.join(data_dir,"VOC_MammalianPhenotype.rpt"),sep="\t",header=None).iloc[:,[0,1]]
    mgi_info.columns = ['annotation_id','term']
    mgi_info = mgi_info[mgi_info['annotation_id'].isin(mgi['annotation_id'].tolist())].drop_duplicates()
    print("\tFinish Step 3.10.")
    return(mgi,mgi_info)

def build_CTD(data_dir,taxonomy_information,Synonyms_Table):
    """ Function to annotate CTD"""
    print("\tStart Step 3.11. Annotate CTD")
    CTD = pandas.read_csv(os.path.join(data_dir,"CTD.csv.gz"),header=None,compression='gzip',comment="#").iloc[:,[0,1,3,4,7]]
    CTD_ann = CTD.iloc[:,[1,0]].drop_duplicates()
    CTD_ann.columns = ['annotation_id','term']
    CTD.columns = ['ChemicalName','ChemicalID','GeneSymbol','GeneID','OrganismID']
    CTD = CTD.drop_duplicates().dropna()
    CTD['GeneID'] = [ str(x) for x in CTD['GeneID'].tolist() ]
    CTD['OrganismID'] = [ str(int(x)) for x in CTD['OrganismID'].tolist() ]
    CTD = CTD[CTD['OrganismID'].isin(taxonomy_information['taxonomy_id'].tolist())]
    CTD = CTD.merge(Synonyms_Table,left_on="GeneID",right_on="synonyms").iloc[:,[5,1]].drop_duplicates()
    CTD.columns = ['id','annotation_id']
    CTD['annotation_source'] = 'CTD'
    CTD_ann = CTD_ann[CTD_ann['annotation_id'].isin(CTD['annotation_id'].tolist())].drop_duplicates()
    print("\tFinish Step 3.11.")
    return CTD,CTD_ann

def build_pharmGKB(data_dir,Gene_Table):
    """ Function to annotate PharmGKB"""
    print("\tStart Step 3.12. Annotate pharmGKB")
    drugs = read_zip_file(os.path.join(data_dir,"drugs.zip"),"drugs.tsv")
    genes = read_zip_file(os.path.join(data_dir,"genes.zip"),"genes.tsv").iloc[:,[0,5]].drop_duplicates()
    relationships = read_zip_file(os.path.join(data_dir,"relationships.zip"),"relationships.tsv")
    relationships_1 = relationships[((relationships['Entity1_type']=='Chemical') & (relationships['Entity2_type']=='Gene'))].iloc[:,[0,1,2,3,4,5]]
    relationships_2 = relationships[((relationships['Entity1_type']=='Gene') & (relationships['Entity2_type']=='Chemical'))].iloc[:,[3,4,5,0,1,2]]
    relationships_2.columns = relationships_1.columns.tolist()
    relationships = pandas.concat([relationships_1,relationships_2]).drop_duplicates()
    pharmGKB_merge = relationships.merge(genes,left_on='Entity2_name',right_on='Symbol').iloc[:,[0,1,4]]
    pharminfo = pharmGKB_merge.iloc[:,[0,1]].drop_duplicates()
    pharminfo.columns = ['annotation_id','term']
    human_gene = Gene_Table[Gene_Table['tax_id']==9606]
    pharmGKB_merge = pharmGKB_merge.merge(human_gene,left_on='Entity2_name',right_on="symbol").iloc[:,[3,0]].drop_duplicates()
    pharmGKB_merge.columns = ['id','annotation_id']
    pharmGKB_merge['annotation_source'] = "PharmGKB"
    pharminfo = pharminfo[pharminfo['annotation_id'].isin(pharmGKB_merge['annotation_id'].tolist())].drop_duplicates()
    print("\tFinish Step 3.12.")
    return pharmGKB_merge,pharminfo

def build_panther(data_dir,Synonyms_Table):
    """ Function to annotate Panther"""
    print("\tStart Step 3.13. Annotate Panther")
    pantherdb = pandas.read_csv(os.path.join(data_dir,"pantherdb.tsv"),sep="\t",header=None).iloc[:,[0,1,4]].drop_duplicates()
    pantherdb.columns = ['annotation_id','term','gene_names']
    panther_info = pantherdb.iloc[:,[0,1]].drop_duplicates()
    panther_info.columns = ['annotation_id','term']
    pantherdb = matching_panther_names(pantherdb).drop_duplicates().iloc[:,[0,2]]
    pantherdb = pantherdb.merge(Synonyms_Table,left_on="gene_names",right_on="synonyms").iloc[:,[2,0]].drop_duplicates()
    pantherdb['annotation_source'] = "Panther"
    print("\tFinish Step 3.13.")
    return pantherdb,panther_info

def pool_panther_names(row):
    """ Split info by row"""
    genes = row.split("|")
    uniprot_name = [x.split("=")[1] for x in genes if "UniProtKB=" in x][0]
    return uniprot_name

def matching_panther_names(pantherdb):
    """ Match gene names"""
    with Pool() as pool:
        pool_out=list(pool.starmap(pool_panther_names, zip(pantherdb['gene_names'].tolist())))
    pantherdb['gene_names'] = pool_out
    return pantherdb

def build_hpo(data_dir,Synonyms_Table):
    """ Function to annotate HPO"""
    print("\tStart Step 3.14. Annotate HPO")
    hpo = pandas.read_csv(os.path.join(data_dir,"HPO.txt"),sep="\t",header=None,comment="#").iloc[:,[2,3,0]]
    hpo.columns = ['annotation_id','term','entrez']
    hpo_info = hpo.iloc[:,[0,1]].drop_duplicates()
    hpo = hpo.iloc[:,[0,2]]
    hpo.columns = ['annotation_id','synonyms']
    hpo['synonyms']=[str(x) for x in hpo['synonyms'].tolist()]
    hpo = hpo.merge(Synonyms_Table,on="synonyms").iloc[:,[2,0]].drop_duplicates()
    hpo['annotation_source']="HPO"
    print("\tFinish Step 3.14.")
    return hpo,hpo_info

def build_omim(data_dir,Synonyms_Table):
    """ Function to annotate OMIM"""
    print("\tStart Step 3.15. Annotate OMIM")
    mim2gene_medgen = pandas.read_csv("data/mim2gene_medgen",sep="\t",comment="#",header=None).iloc[:,[0,1,2,4]].dropna()
    mim2gene_medgen.columns = ["MIM number","GeneID",'phenotype',"MedGenCUI"]
    mim2gene_medgen = mim2gene_medgen[mim2gene_medgen['phenotype']=="phenotype"]
    mim2gene_medgen = mim2gene_medgen[mim2gene_medgen['GeneID']!="-"]

    names_ref = pandas.read_csv("data/MedGen_HPO_OMIM_Mapping.txt.gz",compression='gzip',sep="\t",low_memory=False,comment="#",header=None)
    names_ref.columns = ["ref"]
    ids = [x for x in names_ref['ref'].tolist() if x.split("|")[0] in mim2gene_medgen['MedGenCUI'].tolist()]
    names_ref = pandas.DataFrame({'id':[x.split("|")[0] for x in ids],'name':[x.split("|")[1] for x in ids]})

    merge_omim = names_ref.merge(mim2gene_medgen,left_on='id',right_on='MedGenCUI').iloc[:,[1,2,3]]
    merge_omim['GeneID'] = [str(x) for x in merge_omim['GeneID'].tolist()]

    merge_omim = merge_omim.merge(Synonyms_Table,left_on="GeneID",right_on="synonyms").iloc[:,[3,0,1]]
    merge_omim.columns = ['id','term','annotation_id']
    annotation_omim_info = merge_omim.iloc[:,[2,1]].drop_duplicates()
    merge_omim = merge_omim.iloc[:,[0,2]].drop_duplicates()
    merge_omim['annotation_source'] = "OMIM"
    print("\tFinish Step 3.15.")
    return merge_omim,annotation_omim_info

def build_kegg(taxonomy_information,Synonyms_Table):
    """ Function to annotate KEGG"""
    print("\tStart Step 3.16. Annotate KEGG")
    super_kegg_pathways = pandas.DataFrame({'annotation_id':[],'term':[]})
    super_kegg_genes = pandas.DataFrame({'id':[],'annotation_id':[],'annotation_source':[]})
    input_data = [(tax_id,Synonyms_Table) for tax_id in taxonomy_information.taxonomy_id.tolist()]
    with Pool() as pool:
        result = pool.starmap(by_tax_kegg,input_data)
    kegg_table = pandas.concat([result[i][1] for i in range(len(result))]).drop_duplicates()
    kegg_ann = pandas.concat([result[i][0] for i in range(len(result))]).drop_duplicates()
    print("\tFinish Step 3.16.")
    return kegg_table,kegg_ann

def by_tax_kegg(tax_id,Synonyms_Table):
    """ Function to read and process each kegg tax"""
    kegg_pathways = pandas.read_csv('data/'+str(tax_id)+'_kegg.tsv',sep="\t",header=None)
    kegg_pathways.columns = ['annotation_id','kegg_gene']
    kegg_genes = pandas.read_csv('data/'+str(tax_id)+'_kegg_ncbi.tsv',sep="\t",header=None)
    kegg_genes.columns = ['ncbi','kegg_gene']
    kegg_annotation = merge_kegg_annotation(kegg_genes,kegg_pathways,Synonyms_Table)
    kegg_pathways = pandas.read_csv('data/'+str(tax_id)+'_kegg_pathways.tsv',sep="\t",header=None)
    kegg_pathways.columns = ['annotation_id','term']
    kegg_pathways['annotation_id'] = [x.split(":")[1] for x in kegg_pathways['annotation_id']]
    kegg_pathways['term'] = [" - ".join(description.split(" - ")[:-1]) for description in kegg_pathways['term']]
    result = [kegg_pathways,kegg_annotation]
    return(result)

def merge_kegg_annotation(kegg_genes,kegg_pathways,Synonyms_Table):
    """ Function to match kegg annotation with genes"""
    merge_annotation = kegg_genes.merge(kegg_pathways,on="kegg_gene").iloc[:,[0,2]]
    merge_annotation.columns = ['synonyms','annotation_id']
    merge_annotation['synonyms'] = [w.replace('ncbi-geneid:', '') for w in merge_annotation['synonyms']]
    merge_annotation['annotation_id'] = [w.replace('path:', '') for w in merge_annotation['annotation_id']]
    merge_annotation = merge_annotation.merge(Synonyms_Table,on="synonyms").iloc[:,[2,1]]
    merge_annotation['annotation_source'] = 'KEGG'
    return merge_annotation

def build_go(Synonyms_Table,taxonomy_information,data_dir):
    """ Function to annotate GO"""
    print("\tStart Step 3.17. Annotate GO")
    geneOntology,go_ann,types_info = parsing_go(data_dir)
    go_entrez = build_go_from_ncbi_table(data_dir,Synonyms_Table)
    tax_ids = taxonomy_information['taxonomy_id'].tolist()
    print("\t\tStart Step 3.17.3. Annotate GO gaf")
    with Pool() as pool:
        pool_out=pool.starmap(build_go_from_gaf_files, zip([data_dir]*len(tax_ids),tax_ids,[Synonyms_Table]*len(tax_ids)))
    print("\t\tFinish Step 3.17.3.")
    pool_out = pandas.concat(pool_out)
    go = pandas.concat([go_entrez,pool_out]).drop_duplicates()
    #go = get_full_pathways_go(geneOntology,data_dir,go,types_info)
    print("\tFinish Step 3.17.")
    return go,go_ann

def parsing_go(data_dir):
    """ Function to parse go.obo"""
    print("\t\tStart Step 3.17.1. Parsing GO.obo")
    filename = os.path.join(data_dir,'go.obo')
    with open(filename) as f:
        lines = f.read().split("\n")
    #Remove end of filename and identify position
    typedef = [i for i,n in enumerate(lines) if n == "[Typedef]"][0]
    lines = lines[0:typedef]
    term_position = [i for i, n in enumerate(lines) if n == "[Term]"]
    names_position = [i for i, n in enumerate(lines) if n.startswith("name: ")]
    type_position = [i for i, n in enumerate(lines) if n.startswith("namespace: ")]
    parents_position = [i for i,n in enumerate(lines) if n.startswith("is_a: ")]
    i = list(range(len(term_position)))
    #Creating a dictionary to save the information
    with Pool() as pool:
        pool_out=pool.starmap(pool_obo, zip(i,[term_position]*len(i),[names_position]*len(i),[type_position]*len(i),[parents_position]*len(i),[lines]*len(i)))
    geneOntology = pandas.concat(pool_out)
    reps = {'biological_process': 'GO_BP', 'molecular_function': 'GO_MF', 'cellular_component':'GO_CC'}
    geneOntology['type'] = [reps.get(x,x) for x in geneOntology['type']]
    geneOntology = geneOntology[~geneOntology['term'].str.contains("obsolete")]
    go_ann = geneOntology.iloc[:,[0,2]].drop_duplicates()
    go_ann.columns = ['annotation_id',"term"]
    types_info = geneOntology.iloc[:,[0,1]].drop_duplicates()
    types_info.columns = ['annotation_id',"annotation_source"]
    print("\t\tFinish Step 3.17.1.")
    return geneOntology,go_ann,types_info

def pool_obo(i,term_position,names_position,type_position,parents_position,lines):
    """ Function to process each identity"""
    geneOntology = {'id':[],'type':[],'term':[],"parent":[]}
    values = [lines[term_position[i]+1], lines[names_position[i]], lines[type_position[i]]]
    values = [x.split(": ")[1::] for x in values]
    if i < len(term_position)-1:
        sub_parents = [x for x in parents_position if x > term_position[i] and x < term_position[i+1]]
    else:
        sub_parents = [x for x in parents_position if x > term_position[i]]
    parents = [lines[index] for index in sub_parents]
    parents = [x.split(" ! ")[0].split("is_a: ")[1] for x in parents]
    if len(parents)<1:
        geneOntology['id'].append(values[0][0])
        geneOntology['type'].append(values[2][0])
        geneOntology['term'].append(": ".join(values[1]))
        geneOntology['parent'].append(" ")
    else:
        geneOntology['id'].extend(values[0]*len(parents))
        geneOntology['type'].extend(values[2]*len(parents))
        geneOntology['term'].extend([": ".join(values[1])]*len(parents))
        geneOntology['parent'].extend(parents)
    geneOntology = pandas.DataFrame(geneOntology)
    return geneOntology

def build_go_from_ncbi_table(data_dir,Synonyms_Table):
    """ Function to obtain information from gene2go NCBI"""
    print("\t\tStart Step 3.17.2. Annotate GO from gene2go from NCBI")
    gene2go = pandas.read_csv(os.path.join(data_dir,"gene2go.gz"),compression='gzip',sep="\t")
    gene2go['GeneID'] = [ str(x) for x in gene2go['GeneID'].tolist() ]
    gene2go['#tax_id'] = [ str(x) for x in gene2go['#tax_id'].tolist() ]
    subGene2Go = gene2go[gene2go['GeneID'].isin(Synonyms_Table['synonyms'].tolist())].iloc[:,[1,2,7]]
    subGene2Go.columns = ['synonyms','annotation_id','annotation_source']
    result = subGene2Go.merge(Synonyms_Table, on='synonyms').iloc[:,[3,1,2]]
    reps = {'Process': 'GO_BP', 'Function': 'GO_MF', 'Component':'GO_CC'}
    result['annotation_source'] = [reps.get(x,x) for x in result['annotation_source']]
    print("\t\tFinish Step 3.17.2.")
    return result

def build_go_from_gaf_files(data_dir,tax_id,Synonyms_Table):
    """ Function to read each gaf file"""
    print("\t\t\tStart Step 3.17.3.1. Annotate GO from gaf of organism "+str(tax_id))
    go_gaf_file = os.path.join(data_dir,str(tax_id)+".gaf")
    go_gaf_table = pandas.read_csv(go_gaf_file,sep="\t",low_memory=False, comment = "!",header=None)
    go_gaf_table = go_gaf_table.iloc[:,[1,4,8]]
    go_gaf_table.columns = ['synonyms','annotation_id','annotation_source']
    reps = {'P': 'GO_BP', 'F': 'GO_MF', 'C':'GO_CC'}
    go_gaf_table['annotation_source'] = [reps.get(x,x) for x in go_gaf_table['annotation_source']]
    merge_annotation = go_gaf_table.merge(Synonyms_Table,on="synonyms").iloc[:,[3,1,2]]
    print("\t\t\tFinish Step 3.17.3.1.")
    return merge_annotation

def build_go_covid(Synonyms_Table,taxonomy_information,data_dir):
    """ Function to annotate GO covid"""
    print("\t\t\tStart Step 3.18. Annotate GO from gaf covid")
    go_gaf_file = os.path.join(data_dir,"covid.gaf")
    go_gaf_table = pandas.read_csv(go_gaf_file,sep="\t",low_memory=False, comment = "!",header=None)
    go_gaf_table = go_gaf_table.iloc[:,[1,4,8]]
    go_gaf_table.columns = ['synonyms','annotation_id','annotation_source']
    go_gaf_table['annotation_source'] = "GO_COVID"
    merge_annotation = go_gaf_table.merge(Synonyms_Table,on="synonyms").iloc[:,[3,1,2]].drop_duplicates()
    print("\t\t\tFinish Step 3.18.")
    return merge_annotation

##################### Update GeneCodis Bias #############################################

def create_bias_file(Gene_Table,meth_table,dorothea_table,miRTarBase_table,Synonyms_Table):
    """ Function to create bias file"""
    ids = Gene_Table.id.tolist()
    merge_file = Gene_Table.merge(meth_table,on="id",how="left").iloc[:,[0,3,5]]
    merge_file = merge_file.merge(dorothea_table,on="id",how="left").iloc[:,[0,1,2,3]]
    merge_file = merge_file.merge(miRTarBase_table,on="id",how="left").iloc[:,[0,1,2,3,4]]
    merge_file.columns = ["id","genes","cpgs","tfs","mirnas"]
    insert_list = [(id,merge_file) for id in ids]
    with Pool() as pool:
        bias_file = pandas.concat(pool.starmap(bias_by_gene, insert_list))
    bias_file.index = bias_file.id
    bias_file.loc[Synonyms_Table.id[Synonyms_Table.source == 'mirbase'],'mirnas'] = 1
    return bias_file

def bias_by_gene(id,merge_file):
    """ Function to get info from each gene"""
    gene_file = merge_file.loc[merge_file.id.isin([id])]
    length = gene_file.genes.tolist()[0]
    cpgs = len(set([cpg for cpg in gene_file.cpgs.tolist() if str(cpg) != "nan"]))
    tfs = len(set([tf for tf in gene_file.tfs.tolist() if str(tf) != "nan"]))
    mirnas = len(set([mirna for mirna in gene_file.mirnas.tolist() if str(mirna) != "nan"]))
    insertInfo = pandas.DataFrame({"id":[id],"genes":[length],"mirnas":[mirnas],"cpgs":[cpgs],"tfs":[tfs]})
    insertInfo = insertInfo.replace({0: None})
    return insertInfo

##################### Load GeneCodis Postgresql #############################################

def loading_data_sql(table,conn,cur,dbname,user,password):
    """ Function to add table to database"""
    data_name = os.path.basename(table).split("_table.tsv")[0]
    print("Insert data in "+data_name)
    table_content=pandas.read_csv(table,sep="\t",low_memory=False)
    cur.execute("drop table if exists "+data_name)
    command_to_create_table=[]
    with open(table,'r') as f:
        first_row = f.readline().rstrip().split("\t")
        for col in first_row:
            list_items = table_content[col].tolist()
            list_items = [str(x) for x in list_items]
            max_string = max(list_items, key=len)
            max_value = len(max_string)
            command = chunk_of_column(max_value,col)
            command_to_create_table.append(command)
        command_to_create_table = ",".join(command_to_create_table)
        command_to_create_table = "create table "+ data_name +" ("+command_to_create_table+")"
        cur.execute(command_to_create_table)
        cur.copy_from(f, data_name, sep='\t')
        conn.commit()
    if data_name == "gene":
        creatIndex('gene','id',dbname,user,password)
        creatIndex('gene','symbol',dbname,user,password)
        creatIndex('gene','tax_id',dbname,user,password)
    elif data_name == "bias":
        creatIndex('bias','id',dbname,user,password)
    elif data_name == "synonyms":
        creatIndex('synonyms','id',dbname,user,password)
        creatIndex('synonyms','synonyms',dbname,user,password)
    elif data_name == "annotation":
        creatIndex('annotation','id',dbname,user,password)
        creatIndex('annotation','annotation_source',dbname,user,password)
    elif data_name == "annotation_info":
        creatIndex('annotation_info','annotation_id',dbname,user,password)
    else:
        if table_content.columns.tolist() == ['id',"annotation_id","annotation_source"]:
            creatIndex(data_name,'annotation_id',dbname,user,password)

def chunk_of_column(max_value,col):
    """ Function to define which tables have primary keys"""
    primary_keys = {"gene":"id", #"table":"primary_key"
                    "taxonomy":"taxonomy_id",
                    "annotation_info":"id"}
    command = col + " VARCHAR(" + str(max_value) + ")"
    if col in primary_keys:
        primary_key = primary_keys[col]
        command = command + " PRIMARY KEY"
    return command

def creatIndex(table,column,dbname,user,password):
    """ Function to create index in tables """
    cmd = "CREATE INDEX  idx_{0}_{1} ON {0} ({1});"
    cmd = cmd.format(table,column)
    executeSQL(cmd,dbname,user,password)

def executeSQL(cmd,dbname,user,password):
    """ Function to execute SQL command"""
    conn, cur = startPSQL(dbname,user,password)
    cur.execute(cmd)
    closePSQL(conn, cur)

def startPSQL(dbname,user,password):
    """ Function to open Postgresql database"""
    conn = psycopg2.connect("host='localhost' dbname='"+dbname+"' user='"+user+"' password='"+password+"'")
    cur = conn.cursor()
    return [conn, cur]

def closePSQL(conn, cur):
    """ Function to close Postgresql"""
    conn.commit()
    cur.close()
    conn.close()

def launchQuery(cmdTemplate,args,getDF=True,dbname=os.getenv("DB_NAME"),user=os.getenv("DB_USER"), password=os.getenv("DB_PSWD")):
    """ Function to launch queries"""
    args = [tuple(arg) if isinstance(arg,list) else arg for arg in args]
    args = [tuple([arg,'x']) if len(arg) == 1 else arg for arg in args]
    conn = psycopg2.connect(host='localhost', dbname=dbname,
                             user=user, password=password)
    if getDF:
        df = pandas.read_sql_query(cmdTemplate,conn,params=args)
        conn.commit()
        conn.close()
        return (df)
    cur = conn.cursor()
    cur.execute(cmdTemplate,args)
    cur.close()
    conn.commit()
    conn.close()

##################### Generate mirnas precompiled #############################################

def by_mirna(mirna,targets):
    """ Get annotation for all target genes by mirna """
    targets.append(mirna)
    command = "SELECT annotation_id,annotation_source FROM annotation INNER JOIN gene ON (annotation.id = gene.id) WHERE annotation.id IN %s AND annotation_source != %s;"
    args = (targets,"miRTarBase")
    query_result = launchQuery(command,args)
    #query_result = query_result[query_result.annotation_source != "miRTarBase"]
    query_result['id'] = mirna
    query_result = query_result.iloc[:,[2,0,1]]
    return(query_result)
