import requests, json, os, pandas
import urllib3
import urllib
from io import StringIO

#urlBase="http://localhost:5000/"
#URL base for GeneCodis
urlBase='https://genecodis.genyo.es/gc4'

def launchAnalysis(organism,inputType,inputQuery,annotationsDBs,enrichmentStat="hypergeom",
universeScope="annotated",coannotation="no",coannotationAlgorithm="fpgrowth",minimalInputCoannotation=10,
secondInputQuery=[],inputName1="input1",inputName2="input2",customUniverse=[],email="",ReportName="input1"):
    
    params={
    "inputmode": "on",
    "organism":organism,
    "inputtype":inputType,
    "input":{"input":inputQuery,"input2":secondInputQuery},
    "annotations":annotationsDBs,
    "stat":enrichmentStat,
    "scope":universeScope,
    "coannotation":coannotation,
    "algorithm":coannotationAlgorithm,
    "inputSupport":minimalInputCoannotation,
    "inputNames":{"input": inputName1, "input2": inputName2},
    "universe":customUniverse,
    "email":email,
    "jobName":ReportName
    }

    print('Got analysis petition...')
    #Add GC4uid to job params
    params['gc4uid'] = ""
    #Define URL to request job analysis
    analysisURL = urlBase+'/analysis'
    #Make request to genecodis server
    myresp = requests.post(analysisURL,json=params,verify=False)
    try:
        myresp.raise_for_status()
    except requests.HTTPError as e:
        if myresp.text:
            raise requests.HTTPError(myresp.text)
        else:
           raise e
    params['gc4uid']=myresp.text[myresp.text.find(":")+1:len(myresp.text)]
     # check errors
    try: 
        if checkInvalidInput(params['gc4uid'])==True:
            raise ValueError("It seems that you have provided an invalid input list. It could be also possible that the input does not match the selected organism or that we have no record of those in our database associated to the selected annotations. Sorry the inconveniences. Please go to the Help tab and check the allowed ids.")
        if checkErrorStatus(params['gc4uid'])==True:
            raise ValueError("Please send the job ticket, ",params['gc4uid']," to bioinfo@genyo.es, the server found an unexpected error. We will solve it as soon as possible.")
        if checkRateLimit(params['gc4uid'])==True:
            raise ValueError("You have exceeded the GeneCodis rate-limit, which is 10 requests per minute. If you think you may need a further access to GeneCodis please contact us at bioinfo@genyo.es")
    except ValueError as e:
        raise e
    print('Performing the analyses for job:',params["gc4uid"],"...")
    #Get results from analysis
    return getResults(params['gc4uid'])  
def mirnasConversion(mirnas,target):
    try:
        mirnas=",".join(mirnas)
        if target not in ("precursor","mature"):
            raise ValueError("ERROR: target value must be 'precursor' or 'mature'.")
        mirnasURL=urlBase+'/mirnas?mirnas={}&target={}&action=replace'.format(mirnas,target)
        content = requests.get(mirnasURL, verify=False).text
    except ValueError as e:
        raise e
    return content

def getGeneAnnotPairs(annotation,organism,nomenclature):
    try:
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
            raise ValueError("Input error, organism not in GeneCodis database. Please check available databases.")
    
        if annotation not in ["BioPlanet","GO_BP","GO_CC","GO_MF","GO_COVID","KEGG","Panther","OMIM","PharmGKB","LINCS","CTD","DisGeNET","HPO","MGI","DoRothEA","miRTarBase","Reactome","TAM_2","MNDR"]:
            raise ValueError("Input error, annotation not in GeneCodis database. Please check available databases.")
        if nomenclature not in ["symbol","ensebl","entrez","uniot"]:
            raise ValueError("Input error, nomenclature must be 'symbol','ensebl','entrez' or 'uniprot'")

        anotpairlsURL=urlBase+'/database?annotation={}&organism={}&nomenclature={}'.format(annotation,organismCode,nomenclature)
        content = requests.get(anotpairlsURL, verify=False).text
        result = pandas.read_csv(StringIO(content),sep="\t")
        return result
    except ValueError as e:
        raise e
  
def checkInvalidInput(gc4uid):
    stateURL = urlBase+'/analysisResults?job={}'.format(gc4uid)
    state = requests.get(stateURL, verify=False).text
    try:
        if "invalid input list" not in state:
            return False
        else:
            return True
    except requests.exceptions as e:
        print("ERROR:",e)

def checkRateLimit(gc4uid):
    stateURL = urlBase+'/analysisResults?job={}'.format(gc4uid)
    state = requests.get(stateURL, verify=False).text
    try:
        if "rate-limit" not in state:
            return False
        else:
            return True
    except requests.exceptions as e:
        print("ERROR:",e)

def checkErrorStatus(gc4uid):
    stateURL = urlBase+'/analysisResults?job={}'.format(gc4uid)
    state = requests.get(stateURL, verify=False).text
    try:
        if "unexpected" not in state:
            return False
        else:
            return True
    except requests.exceptions as e:
        print("ERROR:",e)

def getResults(gc4uid):

    stateURL = urlBase+'/checkstate?job={}'.format(gc4uid)
    state = requests.get(stateURL, verify=False).text
    state = json.loads(state)
    while state['state']=="PENDING":
        state = requests.get(stateURL, verify=False).text
        state = json.loads(state)
    requestURL= urlBase+'/results?job={}'.format(gc4uid)+'&annotation=all&jsonify=t'
    results=dict()
    tempdic=dict()
    tempdic2=dict()
    #save jobid
    results['jobID']=gc4uid
    #get and save tables
    myresp=requests.get(requestURL,verify=False)
    content = myresp.json()
    for key in content.keys():
        tempDataF=pandas.DataFrame(content[key])
        tempdic[key]=tempDataF
    results['stats_tables']=tempdic
    #get and save quality controls
    qcURL=urlBase+'/qc?job={}'.format(gc4uid)
    myresp=requests.get(qcURL,verify=False)
    content = myresp.json()
    #for key in content.keys():
    #    tempDataF=pandas.DataFrame(content[key])
    #    tempdic2[key]=tempDataF
    #results['quality_controls']=tempdic2
    results['quality_controls']=content
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

result=launchAnalysis(organism="Homo sapiens",inputType="genes",inputQuery=["APOH", "APP", "COL3A1", "COL5A2", "CXCL6", "FGFR1", "FSTL1", "ITGAV", "JAG1", "JAG2", "KCNJ8", "LPL", "LRPAP1", "LUM", "MSX1", "NRP1", "OLR1", "PDGFA", "PF4", "PGLYRP1"],
annotationsDBs=["GO_BP", "GO_CC"],coannotation="yes",coannotationAlgorithm="fpmax",enrichmentStat="wallenius",
inputName1="input1",ReportName="API_Wrapper_example")
print(result)

#listmirnas=["hsa-mir-133a-1","hsa-miR-133a-3p","hsa-miR-133a-5p"]
#result=mirnasConversion(listmirnas,"mature")
#print(result)
#contenido=getResults("zqNYlq4g0D9s_w")

#result=getGeneAnnotPairs("GO_BP","Homo sapiens","symbol")
#print(result)
