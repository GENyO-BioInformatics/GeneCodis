import json, hashlib, random, string, datetime, os,pandas
from numpy import row_stack
from pathlib import Path
from .gc4mailer import sendMSG

def saveJson(dictlike,jsonpath):
    with open(jsonpath,"w") as outjson:
        json.dump(dictlike,outjson)
    return(jsonpath)

def openJson(jsonFile):
    return(json.loads(open(jsonFile,"r").read()))

def mapper(tomap,mappings,keycolumns=False,writeTable=False,mappingFile="mymapping.tsv"):
    if not keycolumns:
        keycolumns = [0]*len(mappings)
    DFs = []
    for mapping in range(len(mappings)):
        mapName = os.path.basename(mappings[mapping])
        keycolumn = keycolumns[mapping]
        DF = pandas.read_csv(mappings[mapping],sep="\t",names=[mapName],index_col=keycolumn)
        DFs.append(DF)
    myMap = DFs[0].join(DFs[1:],how="inner")
    if writeTable:
        myMap.to_csv(mappingFile,sep="\t",header=False)
    return(myMap)

def save2File(outFile,str2write):
    with open(outFile,'w') as outFileHNDL:
        outFileHNDL.write(str2write)

def createGC4hash(dict2sort,skip=['email','inputNames','jobName','gc4uid']):
    str2hash = dict2strAlphanumSorted(dict2sort,skip)
    return(getHash(str2hash))

def dict2strAlphanumSorted(dict2sort,skip):
    sortedStr = ''
    for key in sorted(dict2sort):
        if key in skip:
            continue
        if isinstance(dict2sort[key], dict):
            value = dict2strAlphanumSorted(dict2sort[key],skip)
        elif isinstance(dict2sort[key], list):
            value = list2strAlphanumSorted(dict2sort[key])
        else:
             value = dict2sort[key]
        sortedStr += key+str(value)
    return(sortedStr)

def list2strAlphanumSorted(list2sort):
    return(''.join(sorted(list2sort)))

def getHash(str2hash):
    hash = hashlib.sha1()
    hash.update(str2hash.encode())
    return(hash.hexdigest())

def GC4logger(msg,gc4uid,status):
    logFile = os.path.join('web/htmls/jobs',gc4uid,"log")
    mytime = str(datetime.datetime.now()).split('.')[0]
    log = ''
    if os.path.isfile(logFile):
        log = open(logFile).read().splitlines()[:-1]
        log = "\n".join(log)+' OK\n'
    newlog = log+"{} GMT+1\t{}...\n{}\n".format(mytime,msg,status)
    with open(logFile,'w') as logger:
        logger.write(newlog)

def recoverReport(gc4uid):
    reportFile = os.path.join('web/htmls/jobs',gc4uid,'report.html')
    paramsFile = os.path.join('web/htmls/jobs',gc4uid,'params.json')
    reportExists = os.path.isfile(reportFile)
    paramsExists = os.path.isfile(paramsFile)
    if reportExists and paramsExists:
        report = open(reportFile).read()
        with open(paramsFile,'r') as paramsHNDL:
            params = json.load(paramsHNDL)
    elif reportExists:
        report = open(reportFile).read()
        params = None
    elif paramsExists:
        report = "<div class='notification is-warning'><p>\
        Your job is on our database but we cannot recover the results. \
        Please write to bioinfo@genyo.es, informing about this issue and \
        do not forget providing us the job url that your were introducing.\
        You can also relaunch the analysis again.</p></div>"
        with open(paramsFile,'r') as paramsHNDL:
            params = json.load(paramsHNDL)
    else:
        report = "<div class='notification is-warning'><p>\
        Sorry, that job does not exists. Please check \
        the job ticket is correct.</p></div>"
        params = None
    return(report,params)

def getJobticket(gc4uid):
    jobticket = """
      <p id="jobticket">
        Use this link,
        <a class="genyoLink" href="{0}/job={1}">{0}/job={1}</a>,
        to recover your job when it is finished and also to inform us
        in case of any issue.
      </p>
    """
    return(jobticket.format(os.getenv('API_URL'),gc4uid))

def invalidReport(gc4uid):
    print('Invalid Input')
    GC4logger('Invalid Input',gc4uid,'status=INVALIDINPUT')
    report = """<div class='notification is-warning'><p>It seems that you
    have provided an invalid input list. It could be also possible
    that the input does not match the selected organism or that we
    have no record of those in our database associated to the
    selected annotations. Sorry the inconveniences.
    Please go to the Help tab and check the allowed ids.</p></div>
    <script>window.onload = function(){
        raiseWarning('input', 'input', 'Invalid Input');
        raiseWarning('input2', 'input', 'Invalid Input');}
    </script>
    """
    return(report)
    #report = report.format(getJobticket(gc4uid))
    # outFile = os.path.join('web/htmls/jobs',gc4uid,"report.html")
    # save2File(outFile,report)

def pendingReport(gc4uid):
    statusreport = os.path.join('web/htmls/jobs',gc4uid,'log')
    statusreport = '\n'.join(open(statusreport).read().splitlines()[:-1])
    report = '''
      <div class="tile is-vertical" id="waiting">
      {}
    <figure class="image p-4">
      <img style="width:40%;height:auto;margin:auto;" src="assets/images/dnawaiting.gif">
    </figure>
    <pre id="statep">{}</pre>
    </div>
    <script>openTabResults();checkstate('{}');</script>'''
    return(report.format(getJobticket(gc4uid),statusreport,gc4uid))

def failureReport(gc4uid):
    report = "<div class='notification is-warning'><p>\
    Please send the job ticket, {}, to bioinfo@genyo.es, the server found an unexpected \
    error. We will solve it as soon as possible.\
    </p></div>".format(gc4uid)
    return(report.format(getJobticket(gc4uid)))

def failureReport2(gc4uid):
    report = "<div class='notification is-warning'><p>\
    Your job {} exceeded the memory limit, please try again with a lighter job. \
        \
    </p></div>".format(gc4uid)
    return(report.format(getJobticket(gc4uid)))

def writeReport(state,gc4uid):
    if state == "INVALID":
        report = invalidReport(gc4uid)
    elif state == "FAILURE":
        report = failureReport(gc4uid)
    elif state == "PENDING":
        report = pendingReport(gc4uid)
    elif state =="EXCEEDED":
        report = failureReport2(gc4uid)
    outFile = os.path.join('web/htmls/jobs',gc4uid,"report.html")
    save2File(outFile,report)


def logNsendError(errorwhatever,gc4uid,jobName,email):
    print(errorwhatever)
    if email != '':
        try:
            sendMSG(email,gc4uid,jobName,status=False)
            GC4logger('SENT Error Email',gc4uid,'status=ERROR')
        except Exception as errorwhatever2:
            GC4logger('ERROR Sending Email',gc4uid,'status=ERROR')
            GC4logger(errorwhatever2,gc4uid,'status=ERROR')
    GC4logger(errorwhatever,gc4uid,'status=ERROR')

def writeStats2(inputtype,inputList,stats,scope,ann,anAlgorithm,inputSuppt,engeneT,annT,statsT,totalT,typeOfAnalysis):
    data={'inputtype':[inputtype],'inputList':inputList,'stats':[stats],'scope':[scope],'anAlgorithm':[anAlgorithm],'inputSuppt':[inputSuppt],'engeneT':[engeneT],'annT':[annT],'statsT':[statsT],'totalT':[totalT]}    
    Path("./Optimization_tests").mkdir(parents=True, exist_ok=True)
    if(os.path.exists('./Optimization_tests/Example{0}_{1}_{2}.csv'.format(ann,typeOfAnalysis,inputtype))==False):
        df=pandas.DataFrame([data],columns=['inputtype','inputList','stats','scope','anAlgorithm','inputSuppt','engeneT','annT','statsT','totalT'])   
    else:
        df=pandas.read_csv('./Optimization_tests/Example{0}_{1}_{2}.csv'.format(ann,typeOfAnalysis,inputtype))
        df2=pandas.DataFrame([data],columns=['inputtype','inputList','stats','scope','anAlgorithm','inputSuppt','engeneT','annT','statsT','totalT'])
        df=pandas.concat([df,df2])
    
    df=df.explode((df.columns.values)[0])
    df=df.explode((df.columns.values)[2])
    df=df.explode((df.columns.values)[3])
    df=df.explode((df.columns.values)[4])
    df=df.explode((df.columns.values)[5])
    df=df.explode((df.columns.values)[6])
    df=df.explode((df.columns.values)[7])
    df=df.explode((df.columns.values)[8])
    df=df.explode((df.columns.values)[9])
    df.to_csv('./Optimization_tests/Example{0}_{1}_{2}.csv'.format(ann,typeOfAnalysis,inputtype),index=False)


def getInputList(inputsDict):
    #obtener la lista de datos introducida: genes, microRNAs,etc
    temp=inputsDict['input1unique']['engenes']
    return (temp[list(temp.keys())[0]]['annotated'])