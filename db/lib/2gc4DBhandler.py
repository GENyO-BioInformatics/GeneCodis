from pathlib import Path
from datetime import datetime
import glob, sys, json, pandas, os, psycopg2, psycopg2.extras

def open_connection():
    conn = psycopg2.connect("host='localhost' dbname='genecodisdb' user='genecodis' password='genecodissymdromedb'")
    return conn

def close_connection(conn):
    conn.commit()
    conn.close()

def launchQuery(cmdTemplate,args,getDF=True):
    args = [tuple(arg) if isinstance(arg,list) else arg for arg in args]
    args = [tuple([arg,'']) if len(arg) == 1 else arg for arg in args]
    conn = open_connection()
    print(cmdTemplate)
    if getDF:
        df = pandas.read_sql_query(cmdTemplate,conn,params=args)
        close_connection(conn)
        return (df)
    cur = conn.cursor()
    cur.execute(cmdTemplate,args)
    cur.close()
    close_connection(conn)

def unique(list1):
    return list(set(list1))

params = {'organism': 559292, 'inputtype': 'genes', 'input': {'input': ['NRT1', 'IMD2', 'BIO2', 'BIO5', 'BIO3', 'BNA2', 'FLO5', 'MF(ALPHA)1', 'HOF1', 'BNA4', 'FLO9', 'SER3', 'RAF1', 'SUT1', 'SPR28', 'GAL2', 'SSP1', 'VHR2', 'SNZ1', 'YAL065C', 'CCP1', 'NYV1', 'CRR1', 'BAT2', 'VHT1', 'FLO1', '', 'BPL1', '', 'FAA2', 'LSP1', 'CWP1', 'CTA1', 'REP1', 'CHO1', 'IRC15', 'GEX2', '', 'GUT1', 'BNA5', 'CRD1', 'DIA3', 'TEC1', 'BNA1', 'PIL1', '', 'RCK1', 'ATO3', 'ATO2', 'GSY2', 'BIO4', 'MPC54', 'GSY1', 'IRC18', 'ITR1', '', 'PFU1', 'ANS1', 'SPS4', 'DTR1', 'CAT2', 'PES4', 'GLC3', 'YAP1801', 'ART10', 'OM45', 'NQM1', 'ADE1', '', 'IMA1', 'EIS1', 'HPC2', 'TNA1', 'ATP10', '', '', '', 'ADE2', 'TIR1', 'NTH2', 'SCW4', 'CST9', 'SHM2', 'MAN2', 'RFX1', 'FRE1', 'DPI8', 'YAK1', 'MHP1', 'MDG1', 'SPR3', 'THI73', 'PST2', 'SPI1', 'GPH1', '', 'SPO23', 'GID10', 'URA1', '', 'MIP6', 'MPC2', 'ADE5,7', 'PYK2', 'CAF120', 'PPZ2', 'THI5', 'UBP11', 'NCA2', '', 'URA4', 'UTH1', 'PRY1', 'SLM1', '', 'NDE2', '', 'AIM17', 'CDC15', '', 'RSF1', 'MTD1', 'AIM46', 'RTK1', 'MPC1', '', 'TSL1', 'PRR2', 'FAT3', 'REG2', '', 'ARC35', '', 'FUI1', 'INA17', 'PHO86', 'IGD1', 'FIT2', 'YRR1', 'GRX1', 'IML2', 'NGL3', 'STE3', 'EGO4', '', '', 'CTF19', 'PYC2', 'PCK1', 'PRM5', 'TOM71', 'HMS2', 'RRT5', 'KIN82', 'IMG1', 'TPS2', 'MEO1', 'TAT2', 'STE4', 'LYS1', 'TRX2', 'FMP23', 'PET123', 'NNK1', 'MAM1', 'ARE1', 'YCP4', 'GIP1', 'SUB1', 'PRE7', 'PNG1', 'TPP1', 'THO1', 'TDH1', 'TMA10', 'ZPS1', 'LEU4', 'OM14', 'SYF2', 'XYL2', 'LOH1', 'FUS2', 'VMA4', 'NPC2', 'BNA6', 'CMK1', 'ICY1', 'ADH3', 'BNS1', 'RSE1', 'FAR8', 'YET1', 'ADE13', 'YPF1', 'SNQ2', 'VPS36', 'DOG2', 'ENA5', 'CYB2', '', 'UGP1', 'GIP4', 'GYP6', 'LYS9', 'BDH1', 'PSO2', 'SUE1', 'NCA3', 'PMP3', 'GRX7', 'UBA1', 'AGP2', 'TPI1', 'MAG1', '', 'SPS1', '', 'GCV3', '', 'SMA1', 'TOS2', 'TDA1', 'ABZ1', 'SBA1', 'IMD3', 'AYR1', 'TPS1', '', 'SCM3', 'GPM2', 'GAS2', 'MRK1', 'SPO21', 'GAS4', 'EHT1', 'GLG1', 'DMA2', 'CDC55', 'URA3', 'CAT8', 'HSP12', 'AFG1', 'PCL5', 'MCO76', '', 'HPT1', 'WSC3', 'ATH1', 'UIP4', 'MSS11', 'SPO24', 'TFS1', 'PXA2', '', 'ECM4', 'HXK1', 'HFL1', 'ASH1', 'SPC25', '', 'NPL4', 'ECM15', '', 'ADE16', 'GPT2', 'ASR1', 'TRR2', 'RIB1', 'DCI1', 'LYS20', '', 'APN2', 'MPC3', 'AIM44', '', 'SKA1', 'TIP1', 'CEM1', 'ZTA1', 'PFY1', 'STB3', 'SDS24', 'VPS55', 'MTL1', 'CHZ1', 'SLZ1', 'BRE2', 'ILV3', 'HMX1', '', '', 'AZF1', 'BDH2', 'MSS4', 'FLP1', 'VHS1', 'ARP8', 'POX1', 'HSP150', '', 'MIP1', 'PEX32', 'ALT1', 'EST1', 'LAP3', '', 'RPN9', 'LPX1', 'RDN18-1', 'TPT1', 'MTC5', 'GLO4', 'TDA10', 'RPN4', 'COS111', 'SNX4', 'MSC3', 'OPI1', 'HUG1', 'APE3', 'NUM1', 'ECM34', 'MET6', 'GRX2', 'NDT80', '', 'PEX30', 'GYP7', 'UBX6', 'ARG4', 'CPS1', 'CAD1', 'ADE17', 'TIS11', 'PUP3', 'GCV1', '', 'ATF1', 'AHP1', '', 'SER1', 'REB1', '', 'PNC1', 'ADE8', 'HXT11', 'YAP1', 'TPC1', 'NNR2', 'ADH5', 'TMA108', 'SUC2', 'RPN10', 'MLS1', '', 'UGA2', '', 'DDI1', 'GLO1', '', 'PIG2', 'SOD1', 'PEX12', 'GPM1', 'RSC9', 'MRH1', 'CTR1', 'ATG34', 'DDR2', 'SEC20', 'GIS1', '', 'YIM1', 'SSH4', 'CMC4', '', '', 'RGI1', '', 'GCY1', 'MMS2', 'SNF3', 'PRM2', 'TSA1', 'PHM7', 'HOR7', 'AIM18', 'PEA2', 'PEX2', 'GOR1', 'GPD1', '', 'ADR1', '', 'GLG2', 'EMI2', 'PDS5', 'ADH7', 'TCB1', 'CDC48', 'RDL1', 'IRC21', '', 'MGM1', 'JSN1', 'DCS1', 'IME2', 'RET2', 'FMP45', 'SPO75', 'SLX1', 'PIS1', 'GLK1', '', 'CLN1', '', 'FLO11', 'RER1', 'DML1', 'LYP1', 'PRP28', 'GLC8', 'ARC18', 'MIC26', 'GCG1', 'RDN58-1', 'RDN25-1', 'GET2', 'PSD2', 'PEP4', '', 'TPK2', 'PEX14', 'COX26', 'PRM1', 'ARA1', '', 'SSP120', '', 'PNS1', 'TEP1', 'RHO5', 'ARF2', 'ADY2', '', 'MSC1', 'FOX2', 'MCK1', 'PRE6', 'LAM6', 'JEN1', 'LUG1', 'MEP1', 'MAD3', 'PRY3', 'SEM1', 'CKI1', 'EDE1', 'IQG1', 'SWI4', 'SAG1', 'SEO1', 'ENT2', 'MSY1', '', 'EMI1', 'QDR1', 'GUT2', 'PEX22', 'ERP3', 'ALD4', 'SPO1', 'TAT1', '', 'GRH1', 'IRC24', 'MAM3', 'NGR1', 'NCE102', 'SAS3', 'PTC1', 'RSC30', 'SNO2', 'ECM23', 'HXT2', 'CLB5', 'CSS2', '', 'SRF1', 'PEX18', 'INO1', 'ATG20', 'DIT1', '', '', 'PGK1', 'ADP1', 'ARA2', 'URH1', 'MSN4', 'FMP48', '', 'MNR2', 'FAR1', 'PCL9', 'ENO1', 'PEX4', '', 'IBA57', 'YPK1', 'PLB1', 'RIO1', 'TRK2', 'CIT1', '', '', 'COF1', 'AXL1', 'PET494', 'AIM2', '', '', 'RKI1', 'SDC25', 'PDX1', 'SGO1', 'PTC3', 'DOG1', 'MRPL39', '', 'SMC1', 'YRA1', 'PHO84', 'RTC2', '', 'UME6', 'IMA3']}, 'annotations': ['miRNA_Strong', 'GO_BP', 'KEGG'], 'test': ['hypergeometric'], 'pvalCorrection': 'fdr', 'inputSupport': 3, 'universe': [], 'email': '', 'jobName': 'input1', 'inputNames': {'input1unique': 'input1'}, 'gc4uid': 'yqTvCbX9Nc'}

input = params['input']
organism_id = str(params['organism'])
universe = params['universe']
annotations = params['annotations']
jobDir = jobDir = os.path.join('web/htmls/jobs/',params['gc4uid'])
flag_TFs = params['inputtype']
inputNames = params['inputNames']

##### UNIVERSE universe,invalidUniverse,type = check_universe(universe,organism_id)
def checkUniverse(universe,organism):
    print("Checking Universe")
    if universe == []: # I think We do not need this
        print("Use the whole universe for "+organism)
        command = "SELECT id FROM gene WHERE organism = %s;"
        args = (organism,)
        universe = launchQuery(command,args)['id'].tolist()
        invalidUniverse = []
        type="whole"
    else:
        print("Checking the customized universe")
        command = """SELECT synonyms.id,synonyms.synonyms FROM gene
                     INNER JOIN synonyms ON (gene.id = synonyms.id)
                     WHERE gene.organism = %s AND synonyms.synonyms IN %s;
                  """
        args = (organism,universe)
        gene_ids = launchQuery(command,args)
        invalidUniverse = [x for x in universe if x not in gene_ids['synonyms'].tolist()]
        universe = unique(gene_ids['id'].tolist())
        type = "custom"

#### checking_lists
def checkMiRNAs(input,organism):
    command = """SELECT annotation_id,miRNAs.id FROM miRNAs
                 INNER JOIN gene ON (gene.id = miRNAs.id)
                 WHERE annotation_id IN %s AND gene.organism = %s;
              """
    args = (input,organism)
    mirnas = launchQuery(command,args)
    return(mirnas)

def checkCPGs():


#### full_dict,synonyms_dict = checking_lists(input,flag_TFs,organism_id,inputNames)

for inputList in input:
    input[inputList]

    break






input


len(input)
if len(input)==2:
    input_lists, keys, extract = play_with_names(input,inputNames)
    for x in range(0,len(input)):
        input_list = extract[x]
        print("Checking "+input_list+" list")
        list_input = input_lists[x]
        key = keys[x]
        #final_input,invalidInput = which_input(input[input_list],list_input,flag_TFs,organism_id)

            args = (list_input,organism_id)
            mirnas_input = launchQuery(command,args)

            not_used = [x for x in list_input if x not in mirnas_input['annotation_id'].tolist()]
            mirnas_input = unique(mirnas_input['id'].tolist())

            print("Checking if there are any cpg in "+input_list+" list")
            command = "SELECT annotation_id,id FROM cpgs WHERE annotation_id IN %s;"
            args = (not_used,)
            cpgs_input = launchQuery(command,args)
            not_used = [x for x in not_used if x not in cpgs_input['annotation_id'].tolist()]
            cpgs_input = unique(cpgs_input['id'].tolist())

            print("Obtaining genes IDs from input")
            gene_ids,some_synonyms = check_synonyms(not_used,organism_id)
            not_used = [x for x in not_used if x not in gene_ids['synonyms'].tolist()]

            synonyms_dict = {'synonyms':{}}
            if len(some_synonyms.index)>0:
                for symbol in some_synonyms['symbol'].tolist():
                    synonyms_dict['synonyms'][symbol]=some_synonyms[some_synonyms['symbol']==symbol]["string_agg"].tolist()[0].split(",")
            if flag_TFs=="tfs":
                print("Checking if there are any TF in "+input_list+" list")
                command = "SELECT id,annotation_id FROM DoRothEA WHERE annotation_id IN %s;"
                args = (gene_ids['symbol'].tolist(),)
                tfs_input = launchQuery(command,args)
                not_tfs = gene_ids[~gene_ids['symbol'].isin(tfs_input['annotation_id'].tolist())]['synonyms'].tolist()
                not_used = not_used+not_tfs
                final_input = unique(mirnas_input+cpgs_input+tfs_input['id'].tolist())
            else:
                final_input = unique(mirnas_input+cpgs_input+gene_ids['id'].tolist())

            summary_input = []
            command = "SELECT * FROM synonyms WHERE{} synonyms IN %s;"
            print("ERROR! Synonyms")
            if len(final_input) > 0:
                command = command.format(" id IN %s AND")
                args = (final_input,list_input)
            else:
                command = command.format("")
                args = (list_input)
            gene_input = launchQuery(command,args)
            print("ERROR?")
            if (len(gene_input.index)==0):
                command = "SELECT * FROM gene WHERE id IN %s;"
                args = (final_input,)
                gene_input = launchQuery(command,args)
                summary_input = [{gene_input.iloc[x,0]:gene_input.iloc[x,1]} for x in range(len(gene_input.index))]
            else:
                gene_input = hierarchical_names(gene_input)
                summary_input = [{gene_input.iloc[x,0]:gene_input.iloc[x,2]} for x in range(len(gene_input.index))]


        full_dict[list_input]={'input':final_input,'invalidInput':invalidInput,'inputName':key+'_uniques'}
    gc4ids1 = redefine_dict(full_dict[input_lists[0]]['input'])
    gc4ids2 = redefine_dict(full_dict[input_lists[1]]['input'])
    common = gc4ids1.keys() & gc4ids2.keys()
    common = rebuild_dict(common,gc4ids1)
    gc4ids1invalid = full_dict[input_lists[0]]['invalidInput']
    gc4ids2invalid = full_dict[input_lists[1]]['invalidInput']
    common_invalid = list(set(gc4ids1invalid).intersection(gc4ids2invalid))
    full_dict['common'] = {'input':common,'invalidInput':common_invalid,'inputName':"_".join(keys)+'_commons'}
    for input_list in input_lists:
        full_dict[input_list]['input']=[x for x in full_dict[input_list]['input'] if x not in common]
        full_dict[input_list]['invalidInput']=[x for x in full_dict[input_list]['invalidInput'] if x not in common_invalid]
else:
    print("Checking input list")
    list_input = 'input1unique'
    key = inputNames['input1unique']
    final_input,invalidInput = which_input(input['input'],list_input,flag_TFs,organism_id)
    full_dict['input1unique']={'input':final_input,'invalidInput':invalidInput,'inputName':key}
full_list = []
for input_list in input:
    full_list.extend(input[input_list])
full_list = list(set(full_list))
synonyms_dict = check_synonyms_full_list(full_list,organism_id)
########

print("Checking Input Lists")
end_dict = {}
for input_list in full_dict:
    print("Processing "+input_list+" list")
    final_input = full_dict[input_list]['input']
    inputName = full_dict[input_list]['inputName']
    final_dict,notMapped = generate_engene(final_input,organism_id,universe,annotations,jobDir,inputName,type)
    if final_dict == "":
        end_dict[input_list] = {'name':inputName}
        continue
    final_dict = redistribute_dictionary(final_dict)
    final_dict = {'engenes':final_dict}
    final_dict['notInDB'] = {'invalidInput':full_dict[input_list]['invalidInput'],'notMapped':notMapped,'invalidUniverse':invalidUniverse}
    end_dict[input_list] = final_dict
end_dict['synonyms'] = synonyms_dict
return(end_dict)
