from datetime import datetime
import glob, sys, json, pandas, os, psycopg2, psycopg2.extras, re
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('../../') / '.env'
load_dotenv(dotenv_path=env_path)
pandas.options.mode.chained_assignment = None

def launchQuery(cmdTemplate,args,getDF=True):
    args = [tuple(arg) if isinstance(arg,list) else arg for arg in args]
    args = [tuple([arg,'x']) if len(arg) == 1 else arg for arg in args]
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

def open_connection():
    conn = psycopg2.connect(host='localhost', dbname=os.getenv("DB_NAME"),user=os.getenv("DB_USER"), password=os.getenv("DB_PSWD"))
    return conn

def close_connection(conn):
    conn.commit()
    conn.close()

def unique(list1):
    return list(set(list1))

def check_universe(universe,organism_id):
    print("Checking Universe")
    if universe == []:
        print("Use the whole universe for "+organism_id)
        command = "SELECT id FROM gene WHERE tax_id = %s;"
        args = (organism_id,)
        universe = launchQuery(command,args)['id'].tolist()
        not_used = []
        type="whole"
    else:
        print("Checking the customized universe")
        command = "SELECT synonyms.id,synonyms.synonyms FROM gene INNER JOIN synonyms ON (gene.id = synonyms.id) WHERE gene.tax_id = %s AND synonyms.synonyms IN %s;"
        args = (organism_id,universe)
        gene_ids = launchQuery(command,args)
        not_used = [x for x in universe if x not in gene_ids['synonyms'].tolist()]
        universe = unique(gene_ids['id'].tolist())
        type = "custom"
    return universe,not_used,type

def check_universe_mirnas(universe,organism_id):
    print("Checking Universe")
    if universe == []:
        print("Use the whole universe for "+organism_id)
        command = "SELECT id FROM gene WHERE tax_id = %s;"
        args = (organism_id,)
        universe = launchQuery(command,args)['id'].tolist()
        command = "SELECT DISTINCT id FROM synonyms WHERE source = %s AND id IN %s;"
        args = ("mirbase",universe)
        universe = launchQuery(command,args)['id'].tolist()
        not_used = []
        type="whole"
    else:
        print("Checking the customized universe")
        command = "SELECT synonyms.id,synonyms.synonyms FROM gene INNER JOIN synonyms ON (gene.id = synonyms.id) WHERE gene.tax_id = %s AND synonyms.synonyms IN %s;"
        args = (organism_id,universe)
        gene_ids = launchQuery(command,args)
        not_used = [x for x in universe if x not in gene_ids['synonyms'].tolist()]
        universe = unique(gene_ids['id'].tolist())
        type = "custom"
    return universe,not_used,type

def check_synonyms(not_used,organism_id):
    command = "SELECT gene.symbol,string_agg(synonyms.synonyms,',') FROM gene INNER JOIN synonyms ON (gene.id = synonyms.id) WHERE gene.tax_id = %s AND synonyms.synonyms IN %s GROUP BY gene.symbol;"
    args = (organism_id,not_used)
    gene_ids = launchQuery(command,args)
    some_synonyms = gene_ids[gene_ids['string_agg'].str.contains(',')]
    command = "SELECT gene.id,gene.symbol,synonyms.synonyms FROM gene INNER JOIN synonyms ON (gene.id = synonyms.id) WHERE gene.tax_id = %s AND synonyms.synonyms IN %s;"
    args = (organism_id,not_used)
    gene_ids = launchQuery(command,args).drop_duplicates()
    return gene_ids,some_synonyms

def hierarchical_names(final_input,list_input):
    hierc = {'symbol':0,'entrez':1,'ensembl':2,'tair':3,'wormbase':4,'uniprot':5,'other_name':6,'mirbase':7,"cpg":8}
    command = "SELECT * FROM synonyms WHERE id IN %s AND source = 'symbol';"
    args = (final_input,)
    gene_input = launchQuery(command,args)
    command = "SELECT * FROM synonyms WHERE{} synonyms IN %s;"
    command = command.format(" id IN %s AND")
    args = (final_input,list_input)
    gene_input_list = launchQuery(command,args)

    duplicated_list = list_duplicates(gene_input_list['id'].tolist())
    duplicated = gene_input_list[gene_input_list['id'].isin(duplicated_list)]
    gene_input_list = gene_input_list[~gene_input_list['id'].isin(duplicated_list)]
    for id in duplicated_list:
        row = duplicated[duplicated['id']==id]
        row['order'] = [hierc[source] for source in row['source'].tolist()]
        row = row.sort_values('order')
        row = {'id':[row['id'].tolist()[0]],'source':[row['source'].tolist()[0]],'synonyms':[row['synonyms'].tolist()[0]]}
        row = pandas.DataFrame(row)
        gene_input_list = pandas.concat([gene_input_list,row])

    gene_input = gene_input[~gene_input.id.isin(gene_input_list.id)]
    gene_input = pandas.concat([gene_input,gene_input_list])
    return gene_input

def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    seen_twice = set( x for x in seq if x in seen or seen_add(x) )
    return list( seen_twice )

def which_input(list_input,input_list,inputtype,organism_id):
    final_input = []
    not_used = list_input
    mirna_symbol_dict = {}

    if len(not_used) > 0:
        print("Checking if there are any cpg in "+input_list+" list")
        command = "SELECT annotation_id,id FROM cpgs WHERE annotation_id IN %s;"
        args = (not_used,)
        cpgs_input = launchQuery(command,args)
        not_used = [x for x in not_used if x not in cpgs_input['annotation_id'].tolist()]
        cpgs_input = unique(cpgs_input['id'].tolist())
        final_input.extend(cpgs_input)

    if len(not_used) > 0:
        print("Checking if there are any miRNA-gene in "+input_list+" list")
        command = "SELECT id,synonyms FROM synonyms WHERE source = 'mirbase' AND synonyms IN %s;"
        args = (not_used,)
        mirna_input = unique(launchQuery(command,args).id.tolist())
        if len(mirna_input) > 0:
            command = "SELECT id,symbol FROM gene WHERE id IN %s;"
            args = (mirna_input,)
            mirna_symbols = launchQuery(command,args).drop_duplicates()
            command = "SELECT annotation_id,id FROM miRTarBase WHERE annotation_id IN %s;"
            args = (mirna_input,)
            mirna_input = launchQuery(command,args)
            if len(mirna_input.index) > 0:
                command = "SELECT id,symbol FROM gene WHERE id IN %s;"
                args = (list(set(mirna_input.id.tolist())),)
                mirna_symbol = launchQuery(command,args)
                mirna_symbol = mirna_input.merge(mirna_symbol,on="id").drop_duplicates().iloc[:,[0,2]]
                if len(mirna_symbol.index) > 0:
                    for mirna in list(set(mirna_symbol.annotation_id.tolist())):
                        symbols = mirna_symbol[mirna_symbol.annotation_id == mirna]['symbol'].tolist()
                        mirna = mirna_symbols[mirna_symbols.id == mirna].symbol.tolist()[0]
                        mirna_symbol_dict[mirna] = symbols
            mirna_input = unique(mirna_input['id'].tolist())
            final_input.extend(mirna_input)

    if len(not_used) > 0:
        print("Obtaining genes IDs from input")
        gene_ids,some_synonyms = check_synonyms(not_used,organism_id)
        not_used = [x for x in not_used if x not in gene_ids['synonyms'].tolist()]
        synonyms_dict = {'synonyms':{}}
        if len(some_synonyms.index)>0:
            for symbol in some_synonyms['symbol'].tolist():
                synonyms_dict['synonyms'][symbol]=some_synonyms[some_synonyms['symbol']==symbol]["string_agg"].tolist()[0].split(",")
        if inputtype=="tfs":
            print("Checking if there are any TF in "+input_list+" list")
            command = "SELECT id,annotation_id FROM DoRothEA WHERE annotation_id IN %s;"
            args = (gene_ids['symbol'].tolist(),)
            tfs_input = launchQuery(command,args)
            not_tfs = gene_ids[~gene_ids['symbol'].isin(tfs_input['annotation_id'].tolist())]['synonyms'].tolist()
            not_used = not_used+not_tfs
            final_input.extend(unique(tfs_input['id'].tolist()))
        else:
            final_input.extend(unique(gene_ids['id'].tolist()))
    summary_input = []
    if len(final_input) == 0:
        return("","","")
    else:
        gene_input = hierarchical_names(final_input,list_input)
        summary_input = [{gene_input.iloc[x,0]:gene_input.iloc[x,2]} for x in range(len(gene_input.index))]
    return(summary_input,not_used,mirna_symbol_dict)

def checkNgenerate(input,organism_id,universe,annotations,jobDir,inputtype,inputNames,coannotation,stat):
    print(inputtype)
    # flag_mirnas = True if stat != 'wallenius' and inputtype == 'mirnas' else False
    if stat == 'hypergeom' and inputtype == 'mirnas':
        universe,invalidUniverse,type = check_universe_mirnas(universe,organism_id)
        print("Checking Input Lists")
        print([input,inputtype,organism_id,inputNames])
        full_dict,synonyms_dict = checking_lists(input,inputtype,organism_id,inputNames)
        if full_dict == "":
            return("")
        end_dict = {}
        for input_list in full_dict:
            print("Processing "+input_list+" list")
            final_input = full_dict[input_list]['input']
            inputName = full_dict[input_list]['inputName']
            mirna_target = full_dict[input_list]['mirnatargets']
            final_dict,notMapped = generate_engene_mirnas(final_input,organism_id,universe,annotations,jobDir,inputName,type,coannotation,mirna_target,inputtype)
            if final_dict == "":
                end_dict[input_list] = {'name':inputName}
                continue
            final_dict = redistribute_dictionary(final_dict)
            final_dict = {'engenes':final_dict}
            final_dict['notInDB'] = {'invalidInput':full_dict[input_list]['invalidInput'],'notMapped':notMapped,'invalidUniverse':invalidUniverse}
            mirnatargets = full_dict[input_list]['mirnatargets']
            for engene in final_dict['engenes']:
                annotated_list = final_dict["engenes"][engene]['annotated']
                mirnas = {}
                for mirna in mirnatargets:
                    target_genes = [x for x in mirnatargets[mirna] if x in annotated_list]
                    if len(target_genes) > 0:
                        mirnas[mirna] = target_genes
                final_dict['engenes'][engene]['mirnatargets'] = mirnas
            end_dict[input_list] = final_dict
        end_dict['synonyms'] = synonyms_dict
    else:
        universe,invalidUniverse,type = check_universe(universe,organism_id)
        print("Checking Input Lists")
        print([input,inputtype,organism_id,inputNames])
        full_dict,synonyms_dict = checking_lists(input,inputtype,organism_id,inputNames)
        if full_dict == "":
            return("")
        end_dict = {}
        for input_list in full_dict:
            print("Processing "+input_list+" list")
            final_input = full_dict[input_list]['input']
            inputName = full_dict[input_list]['inputName']
            final_dict,notMapped = generate_engene(final_input,organism_id,universe,annotations,jobDir,inputName,type,coannotation,inputtype,stat)
            if final_dict == "":
                end_dict[input_list] = {'name':inputName}
                continue
            final_dict = redistribute_dictionary(final_dict)
            final_dict = {'engenes':final_dict}
            final_dict['notInDB'] = {'invalidInput':full_dict[input_list]['invalidInput'],'notMapped':notMapped,'invalidUniverse':invalidUniverse}
            mirnatargets = full_dict[input_list]['mirnatargets']
            for engene in final_dict['engenes']:
                annotated_list = final_dict["engenes"][engene]['annotated']
                mirnas = {}
                for mirna in mirnatargets:
                    target_genes = [x for x in mirnatargets[mirna] if x in annotated_list]
                    if len(target_genes) > 0:
                        mirnas[mirna] = target_genes
                final_dict['engenes'][engene]['mirnatargets'] = mirnas
            end_dict[input_list] = final_dict
        end_dict['synonyms'] = synonyms_dict
    return(end_dict)

def generate_engene_mirnas(final_input,organism_id,universe,annotations,jobDir,inputName,type,coannotation,mirna_target,inputtype):
    mapping = {}
    for minidict in final_input:
        key = list(minidict.keys())[0]
        if key in universe: #if key is a mirna
            value = minidict[key] #synonyms
            if value in mirna_target: #if this mirna has targets
                targets = mirna_target[value]
                targets_id = []
                for target in targets:
                    target_id = [list(id.keys())[0] for id in final_input if list(id.values())[0] == target][0]
                    targets_id.append(target_id)
                targets = targets
            else:
                targets = []
            mapping[key] = targets

    for mirna in mapping:
        targets = mapping[mirna]

    final_dict = {}
    os.makedirs(jobDir,exist_ok=True)
    print("Created new job directory "+jobDir)
    inputName = re.sub("([!|\$|#|&|\"|\'|\(|\)|\||<|>|`|\\\|;|\s|\/]+)","", inputName)
    outSufix = os.path.join(jobDir,'engene-'+inputName+'-')
    notMapped = []

    if len(annotations) > 1:
        if coannotation == True:
            filename = outSufix + "CoAnnotation-" + '_'.join(annotations)
            noAnnotated,n_universe,annotatedGenes = get_annotation_universe_mirnas(universe,annotations,final_input,filename,organism_id)
            dictionary_annotation = saveDict(filename,annotations,noAnnotated,n_universe,annotatedGenes,coann=True)
            final_dict.update(dictionary_annotation)
        for annotation in annotations:
            filename = outSufix + annotation
            annotation = [annotation]
            noAnnotated,n_universe,annotatedGenes = get_annotation_universe_mirnas(universe,annotation,final_input,filename,organism_id)
            if len(annotatedGenes) == 0:
                notMapped.extend(annotation)
            else:
                dictionary_annotation = saveDict(filename,annotation,noAnnotated,n_universe,annotatedGenes,coann=False)
                final_dict.update(dictionary_annotation)
    else:
        filename = outSufix + annotations[0]
        annotation = annotations
        noAnnotated,n_universe,annotatedGenes = get_annotation_universe_mirnas(universe,annotation,final_input,filename,organism_id)
        if noAnnotated == "":
            return "",""
        if len(annotatedGenes) == 0:
            notMapped.extend(annotation)
        else:
            dictionary_annotation = saveDict(filename,annotation,noAnnotated,n_universe,annotatedGenes,coann=False)
            final_dict.update(dictionary_annotation)
    return final_dict,notMapped


def get_annotation_universe_mirnas(universe,annotation,final_input,filename,organism_id):

    command = "SELECT id,string_agg(annotation_id,',') FROM mirna_to_annotation WHERE id IN %s AND annotation_source IN %s GROUP BY id;"
    args = (universe,annotation)
    query_result = launchQuery(command,args)
    universe_ann = query_result.dropna()
    exchange_input = {'id':[],'synonyms':[]}
    for minidict in final_input:
        key = list(minidict.keys())[0]
        if key in universe:
            exchange_input['id'].append(key)
            exchange_input['synonyms'].append(minidict[key])
    print('exchange_input mirnas')
    print(exchange_input)
    genes_input = convert_genes(exchange_input)
    query_result = universe_ann.merge(genes_input,on="id",how="left").fillna("")
    query_result.columns = ["id","string_agg","symbol"]

    if len(query_result) == 0:
        print('get_annotation_universe len(query_result) == 0')
        return "","","" # Check if this works
    command = "SELECT id,symbol FROM gene WHERE id IN %s;"
    args = (universe,)
    universe_result = launchQuery(command,args)['symbol'].tolist()
    annotatedGenes = query_result[query_result['symbol']!=""]['symbol'].tolist()
    query_result.symbol[query_result.symbol == ''] = '0'
    if len(annotatedGenes) > 0:
        print("Writing engene file "+filename)
        write_engene_file_mirnas(filename,query_result)
    noAnnotated = [x for x in exchange_input['id'] if x not in query_result['id'].tolist()]
    noAnnotated = genes_input[genes_input['id'].isin(noAnnotated)]['synonyms'].tolist()
    return noAnnotated,universe_result,annotatedGenes

def play_with_names(input,inputNames):
    input_list = ['input1unique','input2unique']
    keys = [inputNames['input'],inputNames['input2']]
    extract = ['input','input2']
    return input_list, keys, extract

def redefine_dict(list_of_dictionaries):
    input_dictionary = {}
    for x in range(0,len(list_of_dictionaries)):
        for key in list_of_dictionaries[x]:
            input_dictionary[key] = list_of_dictionaries[x][key]
    return input_dictionary

def rebuild_dict(common,gc4ids1):
    common_list = []
    for key in common:
        insert_dict = {key:gc4ids1[key]}
        common_list.append(insert_dict)
    return common_list

def checking_lists(input,inputtype,organism_id,inputNames):
    full_dict = {}
    if len(input)==2:
        input_lists, keys, extract = play_with_names(input,inputNames)
        for x in range(0,len(input)):
            input_list = extract[x]
            list_input = input_lists[x]
            key = keys[x]
            final_input,invalidInput,mirna_symbol_dict = which_input(input[input_list],list_input,inputtype,organism_id)
            if final_input == "":
                return("","")
            full_dict[list_input]={'input':final_input,'invalidInput':invalidInput,'inputName':key+'_uniques',"mirnatargets":mirna_symbol_dict}

        mirnatargets1 = full_dict[input_lists[0]]['mirnatargets']
        mirnatargets2 = full_dict[input_lists[1]]['mirnatargets']
        common_keys = []
        for i in mirnatargets1.keys():
               for j in mirnatargets2.keys():
                            if i==j:
                                 common_keys.append(i)

        mirnatargetscommon = {key: mirnatargets1[key] for key in mirnatargets1 if key in common_keys}
        mirnatargets1 = {key: mirnatargets1[key] for key in mirnatargets1 if key not in common_keys}
        mirnatargets2 = {key: mirnatargets2[key] for key in mirnatargets2 if key not in common_keys}

        gc4ids1 = redefine_dict(full_dict[input_lists[0]]['input'])
        gc4ids2 = redefine_dict(full_dict[input_lists[1]]['input'])
        common = gc4ids1.keys() & gc4ids2.keys()
        common = rebuild_dict(common,gc4ids1)
        gc4ids1invalid = full_dict[input_lists[0]]['invalidInput']
        gc4ids2invalid = full_dict[input_lists[1]]['invalidInput']
        mirna_target1 = full_dict["input1unique"]['mirnatargets']
        mirna_target2 = full_dict["input2unique"]['mirnatargets']
        common_invalid = list(set(gc4ids1invalid).intersection(gc4ids2invalid))
        full_dict['common'] = {'input':common,'invalidInput':common_invalid,'inputName':"_".join(keys)+'_commons'}
        for input_list in input_lists:
            full_dict[input_list]['input']=[x for x in full_dict[input_list]['input'] if x not in common]
            full_dict[input_list]['invalidInput']=[x for x in full_dict[input_list]['invalidInput'] if x not in common_invalid]
        full_dict[input_lists[0]]['mirnatargets'] = mirnatargets1
        full_dict[input_lists[1]]['mirnatargets'] = mirnatargets2
        full_dict["common"]['mirnatargets'] = mirnatargetscommon
    else:
        print("Checking single input list")
        print(inputNames)
        list_input = 'input'
        key = inputNames['input1unique']
        final_input,invalidInput,mirna_symbol_dict = which_input(input['input'],list_input,inputtype,organism_id)
        if final_input == "":
            return("","")
        full_dict['input1unique']={'input':final_input,'invalidInput':invalidInput,'inputName':key,"mirnatargets":mirna_symbol_dict}
    full_list = []
    for input_list in input:
        full_list.extend(input[input_list])
    full_list = list(set(full_list))
    synonyms_dict = check_synonyms_full_list(full_list,organism_id)
    return full_dict,synonyms_dict

def check_synonyms_full_list(full_list,organism_id):
    gene_ids,some_synonyms = check_synonyms(full_list,organism_id)
    synonyms_dict = {}
    if len(some_synonyms.index)>0:
        for symbol in some_synonyms['symbol'].tolist():
            synonyms_dict[symbol]=some_synonyms[some_synonyms['symbol']==symbol]["string_agg"].tolist()[0].split(",")
    return synonyms_dict

def redistribute_dictionary(final_dict):
    for key in final_dict:
        final_dict[key]['universe'] = len(final_dict[key]['universe'])
    return final_dict

# def generate_engene(final_input,organism_id,universe,annotations,jobDir,inputName,type,coannotation,inputtype):
#     final_dict,notMapped = create_engene_files_gene_input(final_input,organism_id,universe,annotations,jobDir,inputName,type,coannotation,inputtype)
#     return final_dict,notMapped

def generate_engene(final_input,organism_id,universe,annotations,jobDir,inputName,type, coannotation,inputtype,stat):
    final_dict = {}
    os.makedirs(jobDir,exist_ok=True)
    print("Created new job directory "+jobDir)
    inputName = re.sub("([!|\$|#|&|\"|\'|\(|\)|\||<|>|`|\\\|;|\s|\/]+)","", inputName)
    outSufix = os.path.join(jobDir,'engene-'+inputName+'-')
    notMapped = []
    if len(annotations) > 1:
        if coannotation == True:
            filename = outSufix + "CoAnnotation-" + '_'.join(annotations)
            noAnnotated,n_universe,annotatedGenes = get_annotation_universe(annotations,organism_id,universe,final_input,filename,type,inputtype,stat)
            dictionary_annotation = saveDict(filename,annotations,noAnnotated,n_universe,annotatedGenes,coann=True)
            final_dict.update(dictionary_annotation)
        for annotation in annotations:
            filename = outSufix + annotation
            annotation = [annotation]
            noAnnotated,n_universe,annotatedGenes = get_annotation_universe(annotation,organism_id,universe,final_input,filename,type,inputtype,stat)
            if len(annotatedGenes) == 0:
                notMapped.extend(annotation)
            else:
                dictionary_annotation = saveDict(filename,annotation,noAnnotated,n_universe,annotatedGenes,coann=False)
                final_dict.update(dictionary_annotation)
    else:
        filename = outSufix + annotations[0]
        annotation = annotations
        noAnnotated,n_universe,annotatedGenes = get_annotation_universe(annotation,organism_id,universe,final_input,filename,type,inputtype,stat)
        if noAnnotated == "":
            return "",""
        if len(annotatedGenes) == 0:
            notMapped.extend(annotation)
        else:
            dictionary_annotation = saveDict(filename,annotation,noAnnotated,n_universe,annotatedGenes,coann=False)
            final_dict.update(dictionary_annotation)
    return final_dict,notMapped

def get_annotation_universe(annotation,organism_id,universe,final_input,filename,type,inputtype,stat):
    if len(final_input) == 0:
        return "","",""
    if type == "custom":
        # I think this makes no sense, why filter the universe by getting all
        # all the genes instead of just selecting all of the organism_id
        command = "SELECT annotation.id, string_agg(annotation_id,',') FROM annotation INNER JOIN gene ON (annotation.id = gene.id) WHERE gene.tax_id = %s AND annotation.annotation_source IN %s AND annotation.id IN %s GROUP BY annotation.id;"
        #command = "SELECT annotation.id, string_agg(annotation_id,','), bias.{} FROM annotation INNER JOIN bias ON (annotation.id = bias.id) INNER JOIN gene ON (annotation.id = gene.id) WHERE gene.tax_id = %s AND annotation.annotation_source IN %s AND annotation.id IN %s GROUP BY annotation.id, bias.id;".format(inputtype)
        args = (organism_id,annotation,universe)
    else:
        command = "SELECT annotation.id, string_agg(annotation_id,',') FROM annotation INNER JOIN gene ON (annotation.id = gene.id) WHERE gene.tax_id = %s AND annotation.annotation_source IN %s GROUP BY annotation.id;"
        #command = "SELECT annotation.id, string_agg(annotation_id,','), bias.{} FROM annotation INNER JOIN bias ON (annotation.id = bias.id) INNER JOIN gene ON (annotation.id = gene.id) WHERE gene.tax_id = %s AND annotation.annotation_source IN %s GROUP BY annotation.id, bias.id;".format(inputtype)
        args = (organism_id,annotation)
    query_result = launchQuery(command,args)
    exchange_input = {'id':[],'synonyms':[]}
    for gene in final_input:
        for key in gene:
            exchange_input['id'].append(key)
            exchange_input['synonyms'].append(gene[key])
    print('exchange_input genes')
    print(exchange_input)
    genes_input = convert_genes(exchange_input)
    query_result = query_result.merge(genes_input,on="id",how="left").fillna("")
    query_result.columns = ["id","string_agg","symbol"]
    if len(query_result) == 0:
        print('get_annotation_universe len(query_result) == 0')
        return "","",""
    biasDF = addBias(query_result.id.to_list(),inputtype) ## TOO SLOW - try to left the merge to SQL in above queries
    query_result = biasDF.merge(query_result,on="id",how="left").fillna("")
    command = "SELECT id,symbol FROM gene WHERE id IN %s;"
    args = (query_result['id'].tolist(),)
    universe_result = launchQuery(command,args)['symbol'].tolist()
    annotatedGenes = query_result[query_result['symbol']!=""]['symbol'].tolist()
    query_result.symbol[query_result.symbol == ''] = '0'
    if len(annotatedGenes) > 0:
        print("Writing engene file "+filename)
        write_engene_file(filename,query_result)
    noAnnotated = [x for x in exchange_input['id'] if x not in query_result['id'].tolist()]
    noAnnotated = genes_input[genes_input['id'].isin(noAnnotated)]['synonyms'].tolist()
    return noAnnotated,universe_result,annotatedGenes

def addBias(gc4ids,inputtype):
    command = "SELECT id,{} FROM bias WHERE id IN %s;".format(inputtype)
    args = (gc4ids,)
    biasDF = launchQuery(command,args)
    biasDF.columns.values[-1] = 'bias'
    return(biasDF)

def convert_genes(exchange_input):
    print(exchange_input)
    command = "SELECT synonyms,id FROM synonyms WHERE id IN %s AND synonyms IN %s;"
    args = (exchange_input['id'],exchange_input['synonyms'])
    query_result = launchQuery(command,args)
    return query_result

def write_engene_file_mirnas(filename,engene_format):
    engene_format = engene_format.drop(columns=['id'])
    str_agg = engene_format.string_agg.tolist()
    str_agg = [",".join(sorted(x.split(","))) for x in str_agg]
    engene_format.iloc[:,0] = str_agg
    engene_format = engene_format.drop_duplicates()
    engene_format.columns = ['annotation_id','genes','bias'][:len(engene_format.columns)]
    engene_format.to_csv(filename,sep="\t",header=True,index=False)

def write_engene_file(filename,engene_format):
    engene_format = engene_format.drop(columns=['id'])
    str_agg = engene_format.string_agg.tolist()
    str_agg = [",".join(sorted(x.split(","))) for x in str_agg]
    engene_format.iloc[:,1] = str_agg
    engene_format = engene_format.drop_duplicates()
    engene_format = engene_format.iloc[:,[1,2,0]]
    engene_format.columns = ['annotation_id','genes','bias'][:len(engene_format.columns)]
    engene_format.to_csv(filename,sep="\t",header=True,index=False)

def saveDict(filename,annotation,noAnnotated,universe_genes,selected_genes,coann):
    build_dict = {}
    if os.path.exists(filename):
        annotation = annotation[0] if len(annotation) == 1 else annotation
        build_dict = {filename:{'annotation':annotation,'noAnnotated':noAnnotated,'universe':universe_genes,"annotated":selected_genes,'coannot':coann}}
    return build_dict

def append_terms(fileStatistics):
    print('append_terms(fileStatistics)')
    print(fileStatistics)

    list_of_ids = fileStatistics.annotation_id.tolist()
    list_of_ids = list(map(str,list_of_ids))
    ALLids = ','.join(list_of_ids)
    ALLids = list(set(ALLids.split(',')))
    command = "SELECT * FROM annotation_info WHERE annotation_id IN %s;"
    args = (ALLids,)
    terms = launchQuery(command,args)
    idTermDict = dict(zip(terms.annotation_id, terms.term))
    termsCol = []
    for ids in list_of_ids:
        terms = []
        for id in ids.split(','):
            term = idTermDict[id] if id in idTermDict else ''
            terms.append(term)
        termsCol.append(', '.join(terms))
    fileStatistics.insert(0,'description',termsCol)
    print('ADDED TERMS')
    return fileStatistics

def getGeneInfo(genes,organism):
    if isinstance(genes,str):
        genes = genes.split(',')
    command = "SELECT gene.symbol, gene.description, synonyms.synonyms FROM gene INNER JOIN synonyms ON (gene.id = synonyms.id) WHERE gene.tax_id = %s AND synonyms.synonyms IN %s;"
    args = (organism,genes)
    genInfo = launchQuery(command,args)
    genInfo = genInfo.groupby(['symbol','description'],as_index=False).agg(', '.join)
    genInfo.columns = ['Official Symbol','Description','Synonyms']
    return(genInfo.to_csv(index=False, sep='\t'))

def transformiRNAs(mirnas,action,target):
    mirtype = ['precursor','mature']; mirtype.remove(target); mirtype = mirtype[0]
    if isinstance(mirnas,str):
        mirnas = mirnas.split(',')
    command = "SELECT id FROM synonyms WHERE synonyms IN %s;"
    args = (mirnas,)
    mirInfo = launchQuery(command,args)
    command = "SELECT id,synonyms FROM synonyms WHERE id IN %s;".format(mirtype)
    args = (mirInfo.id.to_list(),)
    mirInfoFull = launchQuery(command,args)
    command = "SELECT * FROM prec2maturesmirnas WHERE {} IN %s;".format(mirtype)
    args = (mirInfoFull.synonyms.to_list(),)
    precDF0 = launchQuery(command,args)
    command = "SELECT * FROM prec2maturesmirnas WHERE {} IN %s;".format(target)
    args = (mirInfoFull.synonyms.to_list(),)
    matDF0 = launchQuery(command,args)

    precDF = precDF0.merge(mirInfoFull,left_on='precursor', right_on='synonyms')
    precDF = precDF.merge(mirInfoFull[mirInfoFull.synonyms.isin(mirnas)],on='id')
    precDF['mirtype'] = 'precursor'
    if len(precDF) == 0:
        precDF = precDF0

    matDF = matDF0.merge(mirInfoFull,left_on='mature', right_on='synonyms')
    matDF = matDF.merge(mirInfoFull[mirInfoFull.synonyms.isin(mirnas)],on='id')
    matDF['mirtype'] = 'mature'
    if len(matDF) == 0:
        matDF = matDF0

    allinp = pandas.concat([precDF,matDF])

    if len(allinp.columns) == 2:
        if action == 'add':
            newinput = allinp[target].to_list() + mirnas
        if action == 'replace':
            newinput = allinp[target].to_list()

    else:
        finalDF = allinp[['id','mature','precursor','synonyms_y','mirtype']]
        finalDF.columns = ['id','mature','precursor','input','mirtype']

        finalDF.loc[finalDF.input.isin(finalDF['precursor']),'mirtype'] = 'precursor'
        finalDF.loc[finalDF.input.isin(finalDF['mature']),'mirtype'] = 'mature'
        nottobetransformed = finalDF[finalDF.mirtype == target].input.to_list()
        tobetransformed = finalDF[finalDF.mirtype == mirtype].input.to_list()
        transformed = finalDF[finalDF.mirtype == mirtype][target].to_list()
        transformed = list(set(transformed) - set(finalDF[finalDF.input.isin(nottobetransformed)][target].to_list()))

        if action == 'add':
            newinput = tobetransformed+nottobetransformed+transformed
        if action == 'replace':
            newinput = nottobetransformed+transformed

    newinput = '\n'.join(sorted(set(newinput))); newinput
    return(newinput)

def getAnnot2ColDF(annot,nomenclature,org):
    cmd = """SELECT synonyms,annotation_id FROM {0}
    INNER JOIN synonyms ON ({0}.id = synonyms.id)
    WHERE source = %s""".format(annot)
    args = (nomenclature,)
    if org != 'all':
        cmd += " AND {}.id ~ %s".format(annot)
        args += ("-"+org+"-",)
    cmd += ";"
    df = launchQuery(cmd,args)
    return(df)

#SELECT synonyms,annotation_id FROM go_bp INNER JOIN synonyms ON (go_bp.id = synonyms.id) WHERE source = 'symb';
