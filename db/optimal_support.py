from lib.gc4DBHandler import *
import random, time

def automatic_organism():
    cmd = "SELECT taxonomy_id FROM taxonomy;"
    conn = open_connection()
    df = pandas.read_sql_query(cmd,conn)
    close_connection(conn)
    org = random.choice(df['taxonomy_id'].tolist())
    return org

def automatic_list_of_genes(organism_id,k):
    cmd = "SELECT symbol FROM gene WHERE gene.organism = %s;"
    conn = open_connection()
    df = pandas.read_sql_query(cmd,conn,params=[organism_id])
    sampling = random.choices(df['symbol'].tolist(), k=k)
    report = {"org":organism_id,"genes":sampling,"n":k}
    return report

def generate_automatic_engene(i,input,universe,jobDir,annotations,inputNames,flag_TFs,organism_id):
    tic = time.clock()
    out_dictionary = checkNgenerate(input,organism_id,universe,annotations,jobDir,flag_TFs,inputNames)
    toc = time.clock()
    time_generate_engene = toc - tic
    out_dictionary = out_dictionary['input1unique']
    return out_dictionary,time_generate_engene


def expandIfSingleAnnot(inputsDict):
    if len(inputsDict['engenes']) == 1:
        engenePath = list(inputsDict['engenes'].keys())[0]
        tmpEngenePath =  engenePath + "_"
        singleEngene = inputsDict['engenes'][engenePath].copy()
        inputsDict['engenes'][tmpEngenePath] = singleEngene
        inputsDict['engenes'][tmpEngenePath]['coannot'] = True
    return(inputsDict)

def defineJobs(inputsDict,jobsParams):
    cmds = []
    inputs = list(inputsDict.keys())
    engenes = inputsDict['engenes']
    for engenePath in engenes:
        jobUnit = engenes[engenePath]
        cmd, jobUnit = defineJob(jobUnit,engenePath,*jobsParams)
        inputsDict['engenes'][engenePath] = jobUnit
        cmds.append(cmd)
    return(inputsDict, cmds)

def defineJob(jobUnit,engenePath,inputSupport,binaryPath,minsupport4random,test,pvalCorrection):
    engenePath = engenePath.rstrip("_")
    cmdStr = "{} {} {} -a{} -i{} -r{} -R{} -t{} -s{} -o {}"
    outFile = engenePath.replace("engene","enrich")
    universeNumber = jobUnit["universe"]
    universeNumber = universeNumber if isinstance(universeNumber,int) else len(universeNumber)
    inputNumber = len(jobUnit["annotated"])
    minsupport = 1
    algorithm = 2
    if jobUnit["coannot"] == True:
        outFile = engenePath.replace("engene","enrich")
        outFile = outFile.split("-")
        outFile[-1] = "CoAnnotation"
        outFile = "-".join(outFile)
        algorithm = 1
        minsupport = inputSupport
    cmd = cmdStr.format(binaryPath,engenePath,minsupport,algorithm,minsupport4random,universeNumber,inputNumber,test,pvalCorrection,outFile)
    jobUnit['cmd'] = cmd
    jobUnit['results'] = outFile
    return(cmd,jobUnit)

def launch_binary(inputsDict,support):
    binaryPath  = "/media/raul/TOSHIBA_EXT/GeneCodis4.0/genecodis3_essentials/genecode_yang_xml"
    jobsParams = [support,binaryPath,support,0,-1]
    inputsDict = expandIfSingleAnnot(inputsDict)
    inputsDict,cmds = defineJobs(inputsDict,jobsParams)
    tic = time.clock()
    for cmd in cmds:
        os.system(cmd)
    toc = time.clock()
    time_binary = toc - tic
    return time_binary



set_genes = list(range(10,1010,10))
min_support = list(range(3,50,2))
summary_results = {'k':[],'time_engene':[],'time_binary':[],"annotations":[],"support":[]}
set = 10
for set in set_genes:
    for sup in min_support:
        if sup < set:
            for i in range(1,20):
                organism_id = "9606"
                report = automatic_list_of_genes(organism_id,set)
                universe = []
                annotations = ["CTD"]
                jobDir = 'tests/CTD'
                input = {'input':['STAT1','IRF3','STAT2']}
                inputNames = {'input1unique':str(set)+"_"+str(i)+"_support-"+str(sup)}
                flag_TFs="genes"
                inputsDict,time_generate_engene = generate_automatic_engene(i,input,universe,jobDir,annotations,inputNames,flag_TFs,organism_id)
                time_binary = launch_binary(inputsDict,sup)
                summary_results['k'].append(set)
                summary_results['time_engene'].append(time_generate_engene)
                summary_results['time_binary'].append(time_binary)
                summary_results['annotations'].append(",".join(annotations))
                summary_results['support'].append(support)
