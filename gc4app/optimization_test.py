
#### Hypergeometric single annotations ####

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpmax, fpgrowth
import numpy, pandas, time, multiprocessing, math, psutil, statistics, itertools, json
from collections import Counter
from scipy.stats import nchypergeom_wallenius, hypergeom
from statsmodels.stats.multitest import multipletests
from pygam import LogisticGAM, s

def getGAModds(lens,DEs):
    #lens,DEs = bias.bias,(bias.genes != '0').astype(int)
    x = numpy.array(lens)
    y = numpy.array(DEs)
    ww = numpy.argsort(x) # ww
    size = math.ceil(len(y) / 10)
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
    gam = LogisticGAM(s(0,n_splines=6,spline_order=3)).gridsearch(x,y,lam=lams,progress=False)
    odds = gam.predict_proba(newX)
    #odds = probs / (1 - probs)
    return(odds)

def append_genes_and_bias(params):
    annot,genesidx,subEngene,stat,biasuniverse,genes_found,term_genes,alpha = params
    idx = [i for i in range(len(genesidx)) if annot in genesidx[i]]
    genes = ','.join(subEngene.iloc[idx,:].genes)
    if stat == "wallenius":
        annotedbias = numpy.mean(subEngene.iloc[idx,:].odds)
        annotbias = annotedbias * (biasuniverse - genes_found) / (alpha - genes_found * annotedbias)
        annotbias = 1 if term_genes == genes_found else annotbias
        res = [genes,annotbias]
    else:
        res = [genes]
    return(res)

def do_coannot(params):
    coannot,allcoannoted,inputcoannoted,subEngene,stat,biasuniverse,alpha = params
    term = ','.join(coannot)
    term_genes = sum([coannot.issubset(x) for x in allcoannoted])
    annoted = [coannot.issubset(x) for x in inputcoannoted]
    genes = ','.join(subEngene.genes[annoted])
    genes_found = sum(annoted)
    res = [{term:genes_found},{term:term_genes}]

    if stat == 'wallenius':
        annotedbias = numpy.mean(subEngene.odds[annoted])
        annotbias = annotedbias * (biasuniverse - genes_found) / (alpha - genes_found * annotedbias)
        annotbias = 1 if term_genes == genes_found else annotbias
        res.extend([genes,annotbias])
    else:
        res.append(genes)
    return(res)

def hypergeometric(popSize,inputSize,popAnnot,inputAnnot):
    """
    popSize = i.e. all the genes of a genome or system M
    popAnnot = i.e. all the genes of GO:XXXXXX n
    inputSize = i.e. the genes selected N
    inputAnnot = i.e. the genes selected of that GO:XXXXXX x
    """
    pval = hypergeom(popSize,popAnnot,inputSize).pmf(inputAnnot)
    return(pval)

def wallenius(popSize,inputSize,popAnnot,inputAnnot,odds):
    pval = nchypergeom_wallenius(popSize,popAnnot,inputSize,odds).pmf(inputAnnot)
    return(pval)

def getStatsDF(engene,stat,iscoannot=False,results=[]):
    biasuniverse = len(engene.index)
    subEngene = engene.loc[engene.genes != "0",]
    alpha = 0
    if stat == 'wallenius':
        alpha = sum(engene.odds)
    if iscoannot:
        allcoannoted = engene.annotation_id.str.split(',').transform(set)
        coannots = results.itemsets.str.split(',').transform(set)
        inputcoannoted = subEngene.annotation_id.str.split(',').transform(set)
        input_list = [(coannots[i],allcoannoted,inputcoannoted,subEngene,stat,biasuniverse,alpha) for i in range(len(coannots))]
        res = list(map(do_coannot,input_list))
        genes = [res[i][2] for i in range(len(res))]
        genes_found = [res[i][0] for i in range(len(res))]
        genes_found = dict(pair for d in genes_found for pair in d.items())
        term_genes = [res[i][1] for i in range(len(res))]
        term_genes = dict(pair for d in term_genes for pair in d.items())
        statsDF = pandas.DataFrame.from_dict(genes_found,orient='index',columns=['genes_found'])
        statsDF['term_genes'] = pandas.Series(term_genes)
        if stat == 'wallenius':
            annotsbias = [res[i][3] for i in range(len(res))]
            statsDF['annotsbias'] = pandas.Series(annotsbias) if isinstance(annotsbias, dict) else annotsbias
    else:
        allannoted = ','.join(engene.annotation_id.to_list()).split(',')
        inputannoted = ','.join(subEngene.annotation_id.to_list()).split(',')
        term_genes = Counter(allannoted)
        genes_found = Counter(inputannoted)
        genesidx = [subEngene.iloc[i,0].split(",") for i in range(len(subEngene.index))]
        input_list = [(annot,genesidx,subEngene,stat,biasuniverse,genes_found[annot],term_genes[annot],alpha) for annot in genes_found]
        res = list(map(append_genes_and_bias,input_list))
        genes = [res[i][0] for i in range(len(res))]
        statsDF = pandas.DataFrame.from_dict(genes_found,orient='index',columns=['genes_found'])
        statsDF['term_genes'] = pandas.Series(term_genes)
        if stat == 'wallenius':
            annotsbias = [res[i][1] for i in range(len(res))]
            statsDF['annotsbias'] = pandas.Series(annotsbias) if isinstance(annotsbias, dict) else annotsbias
    statsDF['genes'] = pandas.Series(genes) if isinstance(genes, dict) else genes
    statsDF = statsDF.reset_index()
    statsDF.columns.values[0] = 'annotation_id'
    return(statsDF)

def applyStat(statsDF,stat,universe,input_size):
    #universe, annotGenes, input_size, odds - annotInput
    print('applyStat')

    if stat == 'wallenius':
        pval = [wallenius(universe,input_size,statsDF.iloc[i,2],statsDF.iloc[i,1],statsDF.iloc[i,3]) for i in range(len(statsDF.index))]
    else:
        pval = [hypergeometric(universe,input_size,statsDF.iloc[i,2],statsDF.iloc[i,1]) for i in range(len(statsDF.index))]

    statsDF.insert(3,'pval',pval)
    statsDF.pval[statsDF.pval == 0] = min(statsDF.pval[statsDF.pval > 0])/156 #ÑAAAAPAAAA
    statsDF.insert(4,'pval_adj',multipletests(statsDF.pval,method='fdr_bh')[1])
    statsDF.sort_values(by=['pval_adj'],inplace=True)
    relative_enrichment = (statsDF.genes_found / input_size) / (statsDF.term_genes / universe)
    statsDF.insert(3,'relative_enrichment',relative_enrichment)
    statsDF.insert(3,'universe',universe)
    statsDF.insert(2,'input_size',input_size)
    return(statsDF)



# results = applyStat(statsDF,stat,universe,input_size)



##### Coannotation ####

engenePath = '/home/usuario/Desktop/Raul_BackUp/github/GeneCodis4.0/db/examples/job_single_list/engene-Example_1-CoAnnotation'
print("Reading "+engenePath)
annotation = ["CTD","KEGG"]
engene = pandas.read_csv(engenePath.rstrip("___"),sep="\t",dtype=str)
stat = "wallenius"
results = []
iscoannot = True
universe = 20000
input_size = 35
algorithm = "fpmax"
inputSupport = 15

if stat == 'wallenius':
    print("Applying wallenius")
    engene.dropna(inplace=True) # !! REMOVE annots/genes without bias info since shouldn't be in the universe
    engene.bias = [float(x) for x in engene.bias]
    odds = getGAModds(engene.bias,(engene.genes != '0').astype(int))
    print("Done")
    engene['odds'] = odds

def controlApriori(engene,algorithm,inputSupport,maxmins = 6):
    print('controlApriori')
    input_size = sum(engene.genes != "0")
    df, idx_annotsDict = prepare2mlext(engene)
    results = []
    myfun = fpgrowth if algorithm == 'fpgrowth' else fpmax
    while isinstance(results,list):
        if inputSupport > input_size:
            return({'itemsets':[]})
        minSupport = inputSupport / input_size # WHAT WOULD HAPPEN IF minSupport = 1 <-  inputSupport == input_size
        eta, results = monitorProcess(maxmins,launchMLxtend,(myfun,df,minSupport))
        inputSupport += 1
    results = back2annot(results,idx_annotsDict)
    return([results,inputSupport-1])


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
    print(results)
    itemsets_trans = []
    try:
        for itemset in list(results.itemsets):
            itemsets_trans.append(','.join(sorted([idx_annotsDict[idx] for idx in list(itemset)])))
    except:
        ''
    results.itemsets = itemsets_trans
    return(results)

def monitorProcess(maxmins,fun,args):
    start = time.time()
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=fun,args=(args)+(queue,))
    process.start()
    try:
        results = queue.get(timeout=maxmins*60)
        print("DONE!!! results:")
    except:
        process.terminate()
        results = []
        print("TOO LONG!!!")
    eta = time.time() - start
    print(eta)
    return(eta,results)

def launchMLxtend(fun,df,minSupport,queue):
    itemsets = fun(df, min_support=minSupport,use_colnames=True)
    queue.put(itemsets)

if isinstance(annotation,list):
    print("Discovering CoAnnotations")
    results, inputSupport = controlApriori(engene,algorithm,inputSupport)

print("Preparing to Stats")
statsDF = getStatsDF(engene,stat,iscoannot,results)
results = applyStat(statsDF,stat,universe,input_size)
