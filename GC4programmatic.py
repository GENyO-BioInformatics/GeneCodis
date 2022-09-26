from tabnanny import check
import requests, json, os, pandas
import urllib3
import urllib
from io import StringIO

def launchAnalysis(organism,inputType,inputQuery,annotationsDBs,enrichmentStat="hypergeom",
universeScope="annotated",coannotation="no",coannotationAlgorithm="fpgrowth",minimalInputCoannotation=10,
secondInputQuery=[],inputName1="input1",inputName2="input2",customUniverse=[],email="",ReportName="input1",outputType="dataframe"):
    
    if organism=="Homo sapiens":
        organismCode=9606
    elif organism=="Caenorhabditis elegans":
        organismCode=6239
    elif organism=="Canis familiaris":
        organismCode=9615
    elif organism=="Danio rerio":
        organismCode=7955
    elif organism=="Drosophila melanogaster":
        organismCode=7227
    elif organism=="Gallus gallus":
        organismCode=9031
    elif organism=="Bos taurus":
        organismCode=9913
    elif organism=="Mus musculus":
        organismCode=10090
    elif organism=="Rattus norvegicus":
        organismCode=10116
    elif organism=="Sus scrofa":
        organismCode=9823
    elif organism=="Arabidopsis thaliana":
        organismCode=3702
    elif organism=="Oryza sativa":
        organismCode=39947
    elif organism=="Saccharomyces cerevisiae":
        organismCode=559292
    elif organism=="Escherichia coli":
        organismCode=511145
    else:
        organismCode=9606

    if len(secondInputQuery)==0:
        input={'input': inputQuery}
        inputNames= {"input1unique": inputName1}
    else:
        input={'input': inputQuery,'input2':secondInputQuery}
        inputNames= {"input": inputName1, "input2": inputName2}

    if coannotation=="no":
        coannotation="coannotation_no"
    else:
        coannotation="coannotation_yes"
    
    params={
    "inputmode": "on",
    "organism":organismCode,
    "inputtype":inputType,
    "input":input,
    "annotations":annotationsDBs,
    "stat":enrichmentStat,
    "scope":universeScope,
    "coannotation":coannotation,
    "algorithm":coannotationAlgorithm,
    "inputSupport":minimalInputCoannotation,
    "inputNames":inputNames,
    "universe":customUniverse,
    "email":email,
    "jobName":ReportName
    }

    urlBase='https://genecodis.genyo.es/gc4'
    #Define URL to obtain gc4uid
    queryURL = os.path.join(urlBase,'createjob')
    print('Creating Job')
    #Add GC4uid to job params
    params['gc4uid'] = requests.get(queryURL,verify=False).text
    print('Job in progress: '+params['gc4uid'])
    #Define URL to request job analysis
    analysisURL = os.path.join(urlBase,'analysis')
    print("params",params)
    #Make request to genecodis server
    myresp = requests.post(analysisURL,json=params,verify=False)
    #Check if analysis has finished
    try:
        print('Checked DataBase\nGenerating Results...')
        while(checkState(params['gc4uid'])!="SUCCESS"):
            #print(checkState(params['gc4uid']))
            if(checkState(params['gc4uid'])=="SUCCESS"):
                break
    except requests.exceptions as e:
         print("ERROR:",e)
    #Get results from analysis
    return getResults(params,outputType)

def checkState(gc4uid,urlBase='https://genecodis.genyo.es/gc4'):
    #Function to check state of job, given the gc4uid
    #posible values: PENDING, SUCCESS or FAILURE
    
    stateURL = os.path.join(urlBase,'checkstate/job={}'.format(gc4uid))
    state = requests.get(stateURL, verify=False).text
    try:
        state = json.loads(state)
        return(state['state'])
        #if gc4uid doesnt exist print error
    except json.JSONDecodeError:
        print("server error, gc4uid not found")

def getResults(params,outputType):

    urlBase='https://genecodis.genyo.es/gc4'
    #Array to store links to the data
    urls=[]
    #Key with the name of each dataframe
    dicKeys=[]
    #Dictionary to store dataframes related to links
    results=dict()
    results['jobID']=params['gc4uid']
    #Check number of inputs
    #if one input, create links for each anotation
    if len(params['inputNames'])==1:
        for input in params['inputNames']:
            for annotation in params['annotations']:
                #Create links to the data and store them in the array
                endpoint="results?job={}&annotation={}"
                resultsStr = params['inputNames'][input]+"-"+annotation
                endpoint = endpoint.format(params['gc4uid'],resultsStr)
                downURL = os.path.join(urlBase,endpoint)
                print(downURL)
                dicKeys.append(resultsStr)
                urls.append(downURL)
            #if coannotation store link to the coannotated data
            if params['coannotation']=="coannotation_yes":
                endpoint="results?job={}&annotation={}"
                resultsStr = params['inputNames'][input]+"-CoAnnotation-"+params['annotations'][0]+"_"+params['annotations'][1]
                endpoint = endpoint.format(params['gc4uid'],resultsStr)                
                downURL = os.path.join(urlBase,endpoint)
                print(downURL)
                urls.append(downURL)
                dicKeys.append(resultsStr)
    #if two inputs, create links for each anotation, uniques and commons
    else:
        for input in params['inputNames']:
            for annotation in params['annotations']:
                endpoint="results?job={}&annotation={}"
                resultsStr = params['inputNames'][input]+"_uniques-"+annotation
                endpoint = endpoint.format(params['gc4uid'],resultsStr)
                downURL = os.path.join(urlBase,endpoint)
                #print(downURL)
                urls.append(downURL)
                dicKeys.append(resultsStr)
        for annotation in params['annotations']:
            endpoint="results?job={}&annotation={}"
            resultsStr = params['inputNames']['input']+"_"+params['inputNames']['input2']+"_commons-"+annotation
            endpoint = endpoint.format(params['gc4uid'],resultsStr)
            downURL = os.path.join(urlBase,endpoint)
            #print(downURL)
            urls.append(downURL)
            dicKeys.append(resultsStr)
        #if coannotation store link to the coannotated data
        if params['coannotation']=="coannotation_yes":
            #commons in coanotation
            endpoint="results?job={}&annotation={}"
            resultsStr = params['inputNames']['input']+"_"+params['inputNames']['input2']+"_commons-CoAnnotation-"+params['annotations'][0]+"_"+params['annotations'][1]
            endpoint = endpoint.format(params['gc4uid'],resultsStr)                
            downURL = os.path.join(urlBase,endpoint)
            #print(downURL)
            urls.append(downURL)
            dicKeys.append(resultsStr)
            #coanotation for input
            endpoint="results?job={}&annotation={}"
            resultsStr = params['inputNames']['input']+"_uniques-CoAnnotation-"+params['annotations'][0]+"_"+params['annotations'][1]
            endpoint = endpoint.format(params['gc4uid'],resultsStr)                
            downURL = os.path.join(urlBase,endpoint)
            #print(downURL)
            urls.append(downURL)
            dicKeys.append(resultsStr)
            #coanotation for input2
            endpoint="results?job={}&annotation={}"
            resultsStr = params['inputNames']['input2']+"_uniques-CoAnnotation-"+params['annotations'][0]+"_"+params['annotations'][1]
            endpoint = endpoint.format(params['gc4uid'],resultsStr)                
            downURL = os.path.join(urlBase,endpoint)
            #print(downURL)
            urls.append(downURL)
            dicKeys.append(resultsStr)    

    #For each url obtain the data and save it in the array as dataframes
    for url,name in zip(urls,dicKeys):
        myresp=requests.get(url,verify=False)
        try:
            if outputType=="dataframe":
                result = pandas.read_csv(StringIO(myresp.text),sep="\t")
            else:
                result= myresp.text
            results[name]=result
        except requests.exceptions as e:
            print("ERROR:",e)
    print("Analysis finished successfully, showing results")
    return results

params = {'organism': 9606, 
'inputtype': 'genes', 
'input': {'input': ['APOH', 'APP', 'COL3A1', 'COL5A2', 'CXCL6', 'FGFR1', 'FSTL1', 'ITGAV', 'JAG1', 'JAG2', 'KCNJ8', 'LPL', 'LRPAP1', 'LUM', 'MSX1', 'NRP1', 'OLR1', 'PDGFA', 'PF4', 'PGLYRP1', 'POSTN', 'PRG2', 'PTK2', 'S100A4', 'SERPINA5', 'SLCO2A1', 'SPP1', 'STC1', 'THBD', 'TIMP1', 'TNFRSF21', 'VAV2', 'VCAN', 'VEGFA', 'VTN']}, 
'annotations': ['GO_BP', 'GO_CC'], 
'stat': 'hypergeom', 
'scope': 'annotated', 
'coannotation': 'coannotation_yes', 
'inputmode': 'on', 
'universe': [], 
'email': '', 
'jobName': 'Homo_sapiens_example', 
'algorithm': 'fpgrowth', 
'inputSupport': 0, 
'inputNames': {'input1unique': 'Homo_sapiens_example'}}
params={"scope": "annotated", "coannotation": "coannotation_yes", "inputSupport": 10, "inputNames": {"input1unique": "Homo_sapiens_example"}, "universe": [], "email": "", "inputtype": "genes", "organism": 9606, "stat": "hypergeom", "inputmode": "on", "annotations": ["GO_BP", "GO_CC"], "jobName": "Homo_sapiens_example", "input": {"input": ["APOH", "APP", "COL3A1", "COL5A2", "CXCL6", "FGFR1", "FSTL1", "ITGAV", "JAG1", "JAG2", "KCNJ8", "LPL", "LRPAP1", "LUM", "MSX1", "NRP1", "OLR1", "PDGFA", "PF4", "PGLYRP1", "POSTN", "PRG2", "PTK2", "S100A4", "SERPINA5", "SLCO2A1", "SPP1", "STC1", "THBD", "TIMP1", "TNFRSF21", "VAV2", "VCAN", "VEGFA", "VTN"]}, "algorithm": "fpgrowth"}
params={"scope": "annotated", "coannotation": "coannotation_yes", "inputSupport": 0, "inputNames": {"input": "input1", "input2": "input2"}, "universe": [], "email": "", "inputtype": "genes", "organism": 9606, "stat": "hypergeom", "inputmode": "on", "annotations": ["GO_BP", "GO_CC"], "jobName": "Homo sapiens example", "input": {"input": ["LUM", "MSX1", "NRP1", "OLR1", "PDGFA", "PF4", "PGLYRP1", "POSTN", "PRG2", "PTK2", "S100A4", "SERPINA5", "SLCO2A1", "SPP1", "STC1", "THBD", "TIMP1", "TNFRSF21", "VAV2", "VCAN", "VEGFA", "VTN"], "input2": ["APOH", "APP", "COL3A1", "COL5A2", "CXCL6", "FGFR1", "FSTL1", "ITGAV", "JAG1", "JAG2", "KCNJ8", "LPL", "LRPAP1", "LUM", "MSX1", "NRP1", "OLR1", "PDGFA", "PF4"]}, "algorithm": "fpgrowth"}
params={"inputmode": "on", "annotations": ["KEGG", "Reactome"], "jobName": "Homo_sapiens_example", "email": "", "universe": [], "coannotation": "coannotation_yes", "inputtype": "tfs", "organism": 9606, "stat": "hypergeom", "scope": "annotated", "input": {"input": ["FOSL2", "NR3C1", "ARNTL", "SOX2", "SRF", "STAT6", "NFATC2", "ATF6"]}, "inputNames": {"input1unique": "Homo_sapiens_example"}, "algorithm": "fpgrowth", "inputSupport": 10}
params={"inputmode": "on", "annotations": ["GO_BP", "GO_CC"], "jobName": "Homo_sapiens_example", "email": "", "universe": [], "coannotation": "coannotation_yes", "inputtype": "cpgs", "organism": 9606, "stat": "hypergeom", "scope": "annotated", "input": {"input": ["cg12862002", "cg11807238", "cg08466770", "cg03996150", "cg11081441", "cg03269045", "cg07892276", "cg12560128", "cg20163324", "cg22833204", "cg06671069", "cg03320783", "cg08817962", "cg00474889", "cg02228675", "cg20724781", "cg15113090", "cg17990983", "cg22963452", "cg13155430", "cg25484698", "cg04640194", "cg09151598", "cg12652301", "cg06740354", "cg20161089", "cg07348311", "cg25800166", "cg09969248", "cg08596817", "cg12987761", "cg21052403", "cg17114584", "cg21730677", "cg09354037", "cg10311754", "cg24948564", "cg03538095", "cg27066543", "cg02988155", "cg24805898", "cg05338155", "cg00493400", "cg18766080", "cg23684711", "cg21135483", "cg21930140", "cg20729846", "cg19764540", "cg22281505"]}, "inputNames": {"input1unique": "Homo_sapiens_example"}, "algorithm": "fpgrowth", "inputSupport": 10}

urlencoded =urllib.parse.urlencode(params,doseq=True)
urllib3.disable_warnings()

result=launchAnalysis(organism="Homo sapiens",inputType="genes",inputQuery=["APOH", "APP", "COL3A1", "MSX1", "NRP1", "OLR1", "PDGFA", "PF4", "PGLYRP1"],
annotationsDBs=["GO_BP", "GO_CC"],outputType="dataframe",coannotation="yes",coannotationAlgorithm="fpmax",enrichmentStat="wallenius",
inputName1="input1",ReportName="API_Wrapper_example")
print(result)
#Output (dataframe,txt,csv,etc)
#Organism
#Input type
#input
#annotations
#stat
#universe scope
#coannotation
#coannotation algorithm
#input support for coannotation
#number of inputs
#input 2 (optional, if number of inputs==2)
#custom universe
#email
#job name