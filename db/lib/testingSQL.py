import psycopg2, pandas

def startPSQL():
    conn = psycopg2.connect("host='localhost' dbname='genecodisdb' user='genecodis' password='genecodissymdromedb'")
    cur = conn.cursor()
    return [conn, cur]

def closePSQL(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

def querySQL(cmd):
    conn, cur = startPSQL()
    dat = pandas.read_sql_query(cmd, conn)
    closePSQL(conn, cur)
    return dat

def getPSQLtables():
    conn, cur = startPSQL()
    cmd = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    cur.execute(cmd)
    records = list(sum(cur.fetchall(), ()))
    closePSQL(conn, cur)
    return records

def previewAllTables():
    gc4tables = getPSQLtables()
    for gc4table in gc4tables:
        print(SQLquerier(gc4table,columns="*",entries=2).head)


def SQLquerier(table,columns="*",distinct="",filter="",entries="",random=""):
    conn, cur = startPSQL()
    columns = [columns] if isinstance(columns, str) else columns
    columns = ",".join(columns)
    cmd = "SELECT{} {} FROM {}{}{}{};"
    if distinct != "":
        distinct = " DISTINCT"
    if random != "":
        random = " ORDER BY random()"
    if filter != "":
        filter = getfilterSTR(filter)
    if entries != "":
        entries = " LIMIT {}".format(entries)
    cmd = cmd.format(distinct,columns,table,filter,random,entries)
    print(cmd)
    DF = querySQL(cmd)
    closePSQL(conn, cur)
    return(DF)

def getfilterSTR(filters):
    filtersstr = []
    for filter in filters:
        filtervalue = filters[filter]['filtervalue']
        filtervalue = "','".join(filtervalue)
        regex = filters[filter]['regex']
        if regex:
            querymode = '~'
        else:
            querymode = 'IN'
        filtstr = "{} {} ('{}')".format(filter,querymode,filtervalue)
        filtersstr.append(filtstr)
    filtersstr = ' WHERE {}'.format(' AND '.join(filtersstr))
    return filtersstr

def keggTaxid2entrezTaxid(keggTaxid=['hsa']):
    df = SQLquerier('taxonomy',columns=['taxonomy_id'],filter={'kegg_id':{'regex':False,'filtervalue':keggTaxid}})
    return df.taxonomy_id[0]

def limit2organism(keggTaxid=['hsa']):
    entrezTaxid = keggTaxid2entrezTaxid(keggTaxid)
    entrezTaxid = ['-'+entrezTaxid+'-']
    df = SQLquerier('annotation',columns=['id','annotation_id'],filter={'id':{'regex':True,'filtervalue':entrezTaxid}})
    return df

def getAnnotidsSample(entries=1,annotationSourceList=[]):
    if len(annotationSourceList) == 0:
        annotations = SQLquerier('annotation',columns=['annotation_source'],distinct=True).annotation_source
    else:
        annotations = annotationSourceList
    annotids = []
    for annotation in annotations:
        filters = {'annotation_source':{'regex':False, 'filtervalue':[annotation]}}
        annotation_id = SQLquerier('annotation',columns=['annotation_id'],filter=filters,entries=entries,random=True)
        annotids.extend(annotation_id.annotation_id.tolist())
    return(annotids)

def annotids2GC4ids(annotids,entrezTaxid=['9606'],entries=50):
    entrezTaxid = ['-'+taxid+'-' for taxid in entrezTaxid]
    GC4ids = []
    for annotid in annotids:
        filters = {'annotation_id':{'regex':False, 'filtervalue':[annotid]},
                                    'id':{'regex':True,'filtervalue':entrezTaxid}}
        annotid_GC4ids = SQLquerier('annotation',columns=['id'],filter=filters,entries=entries)
        GC4ids.extend(annotid_GC4ids.id.tolist())
    return(GC4ids)

def GC4ids2Genes(GC4ids,entrezTaxid=['9606']):
    filters = {'id':{'regex':False, 'filtervalue':GC4ids},
                     'organism':{'regex':False,'filtervalue':entrezTaxid}}
    genes = SQLquerier('gene',columns=['symbol'],filter=filters)
    print(len(set(genes)))
    return(genes.symbol.tolist())

def GC4ids2ENSG(GC4ids,entrezTaxid=['9606']):
    filters = {'id':{'regex':False, 'filtervalue':GC4ids},
                     'source':{'regex':False,'filtervalue':['ensembl']}}
    genes = SQLquerier('synonyms',columns=['synonyms'],filter=filters)
    print(len(set(genes)))
    return(genes.synonyms.tolist())

def getGenesOfAnnots(annotids,entrezTaxid=['9606'],entries=''):
    GC4ids = annotids2GC4ids(annotids,entrezTaxid,entries)
    genes = GC4ids2Genes(GC4ids,entrezTaxid)
    return(genes)

def annotids2term(annotids):
    filters = {'annotation_id':{'regex':False, 'filtervalue':annotids}}
    term = SQLquerier('annotation_info',filter=filters)
    return(term)

def coannotids2term(annotids):
    ALLids = ','.join(annotids)
    ALLids = list(set(ALLids.split(',')))
    terms = annotids2term(ALLids)
    idTermDict = dict(zip(terms.annotation_id, terms.term))
    termsCol = []
    for ids in annotids:
        terms = []
        for id in ids.split(','):
            term = idTermDict[id] if id in idTermDict else ''
            terms.append(term)
        termsCol.append(';'.join(sorted(terms)))
    return termsCol

organism = '9606'
annotations = ['GO_BP','GO_CC','GO_MF']
inputype = 'genes'

"SELECT annotation_id FROM go_bp WHERE id ~ '-{}-' ORDER BY RANDOM() LIMIT 5;".format(organism)
