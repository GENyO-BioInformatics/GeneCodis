engenePath = '/home/eidrian/Desktop/GeneCodis4.0/web/htmls/jobs/ToN4ApSiKCBRGQ/engene-Homo_sapiens_example-CoAnnotationGO_BP_DoRothEA'
stat = 'wallenius'
gc4uid = 'ToN4ApSiKCBRGQ'
algorithm = 'fpgrowth'
inputSupport = 0.20

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpmax, fpgrowth
#import modin.pandas as pandas
#import swifter
import numpy, pandas, time, multiprocessing, psutil, statistics, itertools, json
from collections import Counter
from scipy.stats import nchypergeom_wallenius, hypergeom
from statsmodels.stats.multitest import multipletests
from pygam import LogisticGAM, s
from db.lib.gc4DBHandler import *
from gc4app.commonthings import *

def __init__(inputsDict,inputSupport,coannotation,organism,inputtype,stat,algorithm,gc4uid,scope):
    if coannotation:
        inputsDict = expandIfSingleAnnot(inputsDict)
    jobsDict = defineJobs(inputsDict,inputSupport,organism,inputtype,stat,algorithm,gc4uid,scope)

def defineJobs(inputsDict,inputSupport,organism,inputtype,stat,algorithm,gc4uid,scope):
    print("DEFINIG JOB")
    print(inputsDict)
    cmds = []
    inputs = list(inputsDict.keys())
    for input in inputs:
        if 'engenes' not in inputsDict[input]:
            continue
        engenes = inputsDict[input]['engenes']
        invalidInput = len(inputsDict[input]['notInDB']['invalidInput'])
        for engenePath in engenes:
            print("Reading "+engenePath)
            jobUnit = engenes[engenePath]
            annotation = 'CoAnnotation' if isinstance(jobUnit['annotation'],list) else jobUnit['annotation']
            engene = pandas.read_csv(engenePath.rstrip("___"),sep="\t",dtype=str)
            engene = engene.apply(pandas.to_numeric, errors='ignore')
            engene.annotation_id = engene.annotation_id.apply(lambda x: ','.join(set(x.split(','))))
            if scope == 'whole':
                universe = getUniverse(organism,inputtype,annotation) if isinstance(jobUnit["universe"],int) else len(jobUnit["universe"])
                input_size = len(jobUnit["annotated"])+len(jobUnit["noAnnotated"])+invalidInput
            else:
                universe =  len(engene.index)
                inputsDict[input]['engenes'][engenePath]['universe'] = universe
                input_size = sum(engene.genes != '0')
            if stat == 'wallenius':
                print("Gennerating getGAModds")
                GC4logger('Calculating the bias score for '+annotation,gc4uid,'status=PROCESSING')
                engene.dropna(inplace=True) # !! REMOVE annots/genes without bias info since shouldn't be in the universe
                engene['bias'] = engene['bias'].apply(float)
                universe =  len(engene.index)
                inputsDict[input]['engenes'][engenePath]['universe'] = universe
                geneWeight = getGAModds(engene.bias,(engene.genes != '0').astype(int))
                min(geneWeight)
                print("Done")
                engene['geneWeight'] = geneWeight
            outFile = engenePath.replace('engene','enrich')+'.tsv'
            if annotation == 'CoAnnotation':
                print("Discovering CoAnnotations")
                GC4logger('Discovering CoAnnotations',gc4uid,'status=PROCESSING')
                results, inputSupport = controlApriori(gc4uid,engene,algorithm,inputSupport)
                print("Preparing to Stats")
                GC4logger('Obtaining data for the stats for '+annotation,gc4uid,'status=PROCESSING')
                statsDF = getDFtoStats(engene,stat,universe,iscoannot=True,results=results)
                outFile = outFile.replace(jobUnit['annotation'][0]+'___','CoAnnotation')
            else:
                print("Preparing to Stats for "+annotation)
                GC4logger('Obtaining data for the stats for '+annotation,gc4uid,'status=PROCESSING')
                statsDF = getDFtoStats(engene,stat,universe)

            print("Applying Stats")
            GC4logger('Applying Stats for '+annotation,gc4uid,'status=PROCESSING')
            if stat == 'wallenius':
                if min(statsDF.annotsbias) < 0:
                    print('stat == wallenius: statsDF.annotsbias')
                    statsDF.annotsbias = statsDF.annotsbias + min(statsDF.annotsbias)
                    print('!!! ODDS BELOW 0 !!!')
                    GC4logger('WARNING: ODDS BELOW 0 for '+annotation,gc4uid,'status=PROCESSING')
            results = applyStat(statsDF,stat,universe,input_size)
            print("DONE- Adding terms")
            results = append_terms(results)
            results.sort_values(by=["pval_adj"],inplace=True)
            results.to_csv(outFile,sep="\t",index=False)
            inputsDict[input]['engenes'][engenePath]['results'] = outFile
    return([inputsDict,inputSupport])

def getUniverse(organism,inputtype,annotation):
    universe = json.loads(open('db/info/geneUniverse.json').read())
    if annotation in ['MNDR','HMDD_v3','TAM_2']:
        inputtype = "mirna_directed"
    else:
        inputtype = "genes"
    universe = universe[organism][inputtype]
    return(universe)

def expandIfSingleAnnot(inputsDict):
    for input in inputsDict:
        print(input)
        if list(inputsDict[input].keys())[0] == 'name' or len(inputsDict[input]['engenes']) > 1:
            print("NO EXPANDING")
            continue
        print("EXPANDING")
        if len(list(inputsDict[input]['engenes'].keys())) == 0:
            print("NOTHING TO EXPAND")
            continue
        engenePath = list(inputsDict[input]['engenes'].keys())[0]
        singleEngene = inputsDict[input]['engenes'][engenePath].copy()
        tmpEngenePath =  engenePath + "___"
        inputsDict[input]['engenes'][tmpEngenePath] = singleEngene
        coannotEngene  = inputsDict[input]['engenes'][tmpEngenePath]
        coannotEngene['coannot'] = True
        coannotEngene['annotation'] = [coannotEngene['annotation']]
    return(inputsDict)

def getGAModds(lens,DEs):
    x = numpy.array(lens)
    y = numpy.array(DEs)
    ww = numpy.argsort(x) # ww
    size = int(numpy.ceil(len(y) / 10))
    low = sum(y[ww][0:size])
    hi = sum(y[ww][(len(y) - size):len(y)])
    if hi <= low:
        reflectionFactor = 10^10
        x = reflectionFactor - x
        newX = x
    else:
        newX = x
        x = numpy.insert(x,0,0)
        y = numpy.insert(y,0,0)
    x = numpy.array([[x1] for x1 in x])
    y = numpy.array([[y1] for y1 in y])
    lams = numpy.exp(numpy.random.rand(100, 1))
    gam = LogisticGAM(s(0,n_splines=6,spline_order=3,constraints='monotonic_inc')).gridsearch(x,y,lam=lams,progress=False)
    probs = gam.predict_proba(newX)
    return(probs)

def prepare2mlext(engene):
    subEngene = engene.loc[engene.genes != "0",]
    uniqueannots = set()
    for row in range(len(subEngene)):
        annots = subEngene.iat[row,0]
        uniqueannots.update(annots.split(","))
    annots_idxDict = {k: v for v, k in enumerate(uniqueannots)}
    idx_annotsDict = {v: k for v, k in enumerate(uniqueannots)}
    transactions = []
    for row in range(len(subEngene)):
        annots = subEngene.iat[row,0]
        idxs = [annots_idxDict[annot] for annot in list(set(annots.split(",")))]
        transactions.append(tuple(idxs))
    MLEtransactions =  [list(transaction) for transaction in transactions]
    te = TransactionEncoder()
    te_ary = te.fit(MLEtransactions).transform(MLEtransactions)
    df = pandas.DataFrame(te_ary, columns=te.columns_)
    return(df,idx_annotsDict)

def back2annot(results,idx_annotsDict):
    itemsets_trans = []
    try:
        for itemset in list(results.itemsets):
            itemsets_trans.append(','.join(sorted([idx_annotsDict[idx] for idx in list(itemset)])))
    except:
        ''
    results.itemsets = itemsets_trans
    return(results)

def monitorProcess(gc4uid,maxmins,fun,args):
    start = time.time()
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=fun,args=(args)+(queue,))
    process.start()
    try:
        results = queue.get(timeout=maxmins*60)
        GC4logger('Co-annotations discovered',gc4uid,'status=PROCESSING')
    except:
        process.terminate()
        results = []
        GC4logger('Too much time elapsed. Refining co-annotations discovery',gc4uid,'status=PROCESSING')
    eta = time.time() - start
    print(eta)
    return(eta,results)

def launchMLxtend(fun,df,minSupport,queue):
    itemsets = fun(df, min_support=minSupport,use_colnames=True)
    queue.put(itemsets)

def controlApriori(gc4uid,engene,algorithm,inputSupport,maxmins = 5):
    print('controlApriori')
    input_size = sum(engene.genes != "0")
    df, idx_annotsDict = prepare2mlext(engene)
    results = []
    coannotfun = fpgrowth if algorithm == 'fpgrowth' else fpmax
    if input_size in [1,2,3]:
        inputSupport = 1
    elif input_size in range(4,30):
        inputSupport = 300 / input_size / 100
    else:
        inputSupport = max(inputSupport,0.1)
    minSupport = int(numpy.ceil(inputSupport * input_size))
    while isinstance(results,list):
        if minSupport > input_size:
            break
        GC4logger('Using {} as minimun number of elements per co-annotation'.format(minSupport),gc4uid,'status=PROCESSING')
        eta, results = monitorProcess(gc4uid,maxmins,launchMLxtend,(coannotfun,df,inputSupport))
        print("after monitorProcess")
        minSupport += 1
        inputSupport = minSupport / input_size
    results = back2annot(results,idx_annotsDict)
    return([results,inputSupport-1])

def getDFtoStats(engene,stat,universe,iscoannot=False,results=[]):
    engene.annotation_id = engene.annotation_id.apply(str)
    annots = set(','.join(engene.loc[engene.genes != "0",].annotation_id).split(','))

    if iscoannot:
        results.itemsets = results.itemsets.apply(str)
        coannots = results.itemsets.str.split(',').transform(set)
        allcoannoted = engene.annotation_id.str.split(',').transform(set)
        input_list = [(coannots[i],allcoannoted,engene,stat,universe) for i in range(len(coannots))]
        res = list(map(do_coannot,input_list))

    else:
        input_list = [(annot,engene,stat,universe) for annot in annots]
        res = list(map(append_genes_and_bias,input_list))
    statsDF = pandas.DataFrame(res)
    return statsDF

def applyStat(statsDF,stat,universe,input_size):
    #universe, annotGenes, input_size, geneWeight - annotInput
    print('applyStat')
    statsDF['genesincat'] = statsDF['genesincat'].apply(int)
    statsDF['genes_found'] = statsDF['genes_found'].apply(int)
    universe,input_size = int(universe),int(input_size)
    if stat == 'wallenius':
        statsDF['annotsbias'] = statsDF['annotsbias'].apply(float)
        print('walleniusing')
        pval = [wallenius(universe,input_size,statsDF.iloc[i,2],statsDF.iloc[i,1],statsDF.iloc[i,3]) for i in range(len(statsDF.index))]
    else:
        print('hypergeometring')
        pval = [hypergeometric(universe,input_size,statsDF.iloc[i,2],statsDF.iloc[i,1]) for i in range(len(statsDF.index))]
    print('done test!')
    statsDF.insert(3,'pval',pval)

    statsDF.pval[statsDF.pval == 0] = min(statsDF.pval[statsDF.pval > 0])/156 #ÑAAAAPAAAA
    print('ñaping')
    statsDF.insert(4,'pval_adj',multipletests(statsDF.pval,method='fdr_bh')[1])
    statsDF.sort_values(by=['pval_adj'],inplace=True)
    print('relativing')
    relative_enrichment = (statsDF.genes_found / input_size) / (statsDF.genesincat / universe)
    statsDF.insert(5,'relative_enrichment',relative_enrichment)
    statsDF.insert(3,'universe',universe)
    statsDF.insert(2,'input_size',input_size)
    return(statsDF)

def append_genes_and_bias(params):
    annot,engene,stat,universe = params
    genesincatidx  = pandas.Series(engene.annotation_id).str.count(annot).values.astype(bool)
    genesincat  = sum(genesincatidx)

    inputgenesincatidx = numpy.logical_and(genesincatidx,engene.genes.values != "0")
    strInputgenesincat = ', '.join(engene.genes[inputgenesincatidx])
    inputgenesincat = sum(inputgenesincatidx)

    oddsRatio = 0 # because we need to return it somehow thanks
    if stat == "wallenius":
        genesINcatMeanWeight = numpy.mean(engene.geneWeight[genesincatidx])
        genesOUTcatMeanWeight = numpy.mean(engene.geneWeight[~genesincatidx])
        oddsRatio = genesINcatMeanWeight/genesOUTcatMeanWeight
        oddsRatio = 1 if genesincat == universe else oddsRatio

    return ({'annotation_id':annot, 'genes_found':inputgenesincat, 'term_genes':genesincat, 'annotsbias':oddsRatio, 'genes':strInputgenesincat})

def do_coannot(params):
    coannot,allcoannoted,engene,stat,universe = params
    genesincatidx = numpy.array([coannot.issubset(x) for x in allcoannoted])
    genesincat = sum(genesincatidx)

    inputgenesincatidx = numpy.logical_and(genesincatidx,engene.genes.values != "0")
    strInputgenesincat = ', '.join(engene.genes[inputgenesincatidx])
    inputgenesincat = sum(inputgenesincatidx)

    oddsRatio = 0 # because we need to return it somehow thanks
    if stat == "wallenius":
        genesINcatMeanWeight = numpy.mean(engene.geneWeight[genesincatidx])
        genesOUTcatMeanWeight = numpy.mean(engene.geneWeight[~genesincatidx])
        oddsRatio = genesINcatMeanWeight/genesOUTcatMeanWeight
        oddsRatio = 1 if genesincat == universe else oddsRatio

    return ({'annotation_id':','.join(coannot), 'genes_found':inputgenesincat, 'term_genes':genesincat, 'annotsbias':oddsRatio, 'genes':strInputgenesincat})

def hypergeometric(popSize,inputSize,popAnnot,inputAnnot):
    """
    popSize = i.e. all the genes of a genome or system M
    popAnnot = i.e. all the genes of GO:XXXXXX n
    inputSize = i.e. the genes selected N
    inputAnnot = i.e. the genes selected of that GO:XXXXXX
    """
    pval = hypergeom(popSize,popAnnot,inputSize).sf(inputAnnot-1)
    return(pval)

def wallenius(popSize,inputSize,popAnnot,inputAnnot,annotsbias):
    pval = nchypergeom_wallenius(popSize,popAnnot,inputSize,annotsbias).sf(inputAnnot-1)
    return(pval)
