from io import BytesIO, StringIO
import io
from operator import itemgetter
from flask import Blueprint, session
#from celery.result import AsyncResult
#from .tasks import launchJobs
from flask import *
import flask.scaffold
flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func
from psycopg2 import sql
from flask_restful import *
from flask import Flask, request, render_template
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, ValidationError, pre_load, post_load
from pandas import DataFrame
from gc4app.visualizator import *
from gc4app.commonthings import *
from gc4app.gc4mailer import sendMSG
from db.lib.gc4DBHandler import *
from db.lib.testingSQL import *
from db.lib.gc4loghandler import *
from gc4app.argumentsControl import GeneCodisParamsSchema
from gc4app.apriori import aprioriStats
# import modin.pandas as pandas
import json, re, numpy, os, csv, jinja2, time
import logging, datetime, random, string, hashlib, secrets
from zipfile import ZipFile
from flask_mail import Mail, Message
import subprocess
from dotenv import load_dotenv
load_dotenv()

bp = Blueprint('blueprint',__name__)
@bp.route("/", methods=('GET',))
def go2home():
    homeULR = os.getenv('API_URL').replace(':5000','').replace('/gc4','')
    return redirect(homeULR, code=302)

@bp.route("/analysis", methods=('POST',))
def GC4analysis():
    try:
        paramsDict = request.json
        print("post parameters:",paramsDict)
        #check if gc4uid exists (web) or not (wrapper)
        if len(paramsDict['gc4uid'])==0:
            for a in paramsDict['annotations']:
                if isinstance(a,list):    
                    paramsDict['annotations'] = [item for sublist in paramsDict['annotations'] for item in sublist]
                    break
        #check coannotation value
        checkcoanot=GeneCodisParamsSchema().checkCoannot(paramsDict)
        if(checkcoanot==False):
            return(Response("error: coannotation value must be 'coannotation_yes' or 'coannotation_no'.",status=400))
        #check length annotations
        checklenannots=GeneCodisParamsSchema().checklenwithcoanot(paramsDict)
        if(checklenannots==False):
            return(Response("error: number of annotations with coannotation activated must be 2.",status=400))
        #check input type 
        checkvalidTypes=GeneCodisParamsSchema().checkValidType(paramsDict)
        if(checkvalidTypes==False):
            return(Response("error:input type not valid, input type must be 'genes','tfs','cpgs' or 'mirnas'.",status=400))
        #check available wallenius
        checkAvailableWalleniuss=GeneCodisParamsSchema().checkAvailableWallenius(paramsDict)
        if(checkAvailableWalleniuss==False):
            return(Response("error:input type not valid, you cannot use wallenius with genes/proteins",status=400))
        #check input org
        checkvalidOrg=GeneCodisParamsSchema().checkValidOrg(paramsDict)
        if(checkvalidOrg==False):
            return(Response("error:input organism not valid, check available organisms for GeneCodis.",status=400))
        else:
            if isinstance(paramsDict['organism'],str): 
                orgsnames=["Mus musculus","Danio rerio","Drosophila melanogaster","Rattus norvegicus","Sus scrofa","Bos taurus","Caenorhabditis elegans","Canis familiaris","Gallus gallus","Arabidopsis thaliana","Oryza sativa","Saccharomyces cerevisiae","Escherichia coli","Homo sapiens"]        
                orgscodes=[10090,7955,7227,10116,9823,9913,6239,9615,9031,3702,39947,559292,511145,9606]
                orgs=dict(zip(orgsnames,orgscodes))
                paramsDict['organism']=orgs[paramsDict['organism']]
        #check input annots
        checkvalidanots=GeneCodisParamsSchema().checkValidAnot(paramsDict)
        if(checkvalidanots==False):
            return(Response("error: input annotation not valid, check available annotations from GeneCodis.",status=400))
        #check input types compatibility
        checkInputTypes=GeneCodisParamsSchema().checkInputTypes(paramsDict)
        #check input annots compatibility
        checkAnnotsByInput=GeneCodisParamsSchema().checkAnnotsByInput(paramsDict)
        #check input orgs compatibility
        checkAnnotsByOrg=GeneCodisParamsSchema().checkAnnotsByOrg(paramsDict)
        if checkInputTypes==False or checkAnnotsByInput==False or checkAnnotsByOrg==False:
            return(Response("error: input type selected not compatible with organism selected, please check available input types in GeneCodis website.", status=400))
        #check input email
        checkEmail=GeneCodisParamsSchema().checkEmail(paramsDict)
        if checkEmail==False:
            return(Response("error: email not valid, please check spelling.",status=400))
        #check input stat
        checkstat=GeneCodisParamsSchema().checkStat(paramsDict)
        if checkstat==False:
            return(Response("error: enrichment statistics input not valid, input must be 'hypergeom' or 'wallenius'.",status=400))
        #check input scope
        checkscope=GeneCodisParamsSchema().checkScope(paramsDict)
        if checkscope==False:
            return(Response("error: universe scope input not valid, input must be 'whole' or 'annotated'.",status=400))
        #check input algorithm
        checkalg=GeneCodisParamsSchema().checkCoAlg(paramsDict)
        if checkalg==False:
            return(Response("error: coannotation algorithm input not valid, input must be 'fpmax' or 'fpgrowth'.",status=400))
        #check input support coannotation
        checksupcoan=GeneCodisParamsSchema().checkinputsupport(paramsDict)
        if checksupcoan==False:
            return(Response("error: minimal input support coannotation not valid, input must be interger or decimal number between 0 and 100.",status=400))
        # fix json format from wrappers
        if len(paramsDict['gc4uid'])==0:
            input=paramsDict['input']
            if len(input)>1:
                input1=input['input']
                input2=input['input2']
                for a in input1:
                    if isinstance(a,list):    
                        input1 = [item for sublist in input1 for item in sublist]
                        paramsDict['input']['input']=input1
                        break
                for a in input2:
                    if isinstance(a,list):    
                        input2 = [item for sublist in input2 for item in sublist]
                        paramsDict['input']['input2']=input2
                        break
                if len(paramsDict['input']['input2'])==0:
                    paramsDict['inputNames']['input1unique'] = paramsDict['inputNames'].pop('input')
                    del paramsDict['inputNames']['input2']
                    del paramsDict['input']['input2']
                elif len(paramsDict['input']['input2'])==0 and len(input['inputNames'])>1:
                    return(Response("error: you provided two names but only one input list",status=400))
                
        #check input length (1 or 2 inputs)
        checkvalidinputs=GeneCodisParamsSchema().checkManyInputs(paramsDict)
        if(checkvalidinputs==False):
            return(Response("error:number of inputs not valid, check input lists and input names (max 2).",status=400))
        #create gc4uid if doesnt exist
        if len(paramsDict['gc4uid'])==0:
            paramsDict['gc4uid']=createjob("programmatic")
        GC4params = GeneCodisParamsSchema().load(paramsDict,many=False)
        email = GC4params.email
        jobName = GC4params.jobName
        gc4uid = GC4params.gc4uid
        coannotation = True if GC4params.coannotation == "coannotation_yes" else False
        # organism = str(GC4params.organism)
        # annotations = GC4params.annotations
        # input = GC4params.input
        # inputNames = GC4params.inputNames
        # inputSupport = GC4params.inputSupport
        # universe = GC4params.universe
        # inputtype = GC4params.inputtype
        # stat = GC4params.stat
        # algorithm  = GC4params.algorithm
        # scope = GC4params.scope

        if checkExistence("gc4uid",gc4uid) == False:
            print("DONT EXIST gc4uid: "+gc4uid)
            return(Response("error", status=400))

        #logFile = os.path.join(jobDir,gc4uid)+".log"
        jobDir = os.path.join('web/htmls/jobs/',gc4uid)
        os.makedirs(jobDir,exist_ok=True)
        GC4paramsDict = GeneCodisParamsSchema().dump(GC4params)
        paramsJson = os.path.join('web/htmls/jobs/',gc4uid,'params.json')
        saveJson(GC4paramsDict,paramsJson)
        print("JSON format params:",paramsJson)
        GC4logger('Got analysis petition',gc4uid,'status=PROCESSING')
        startdate, startime = str(datetime.datetime.now()).split(' ')
        hash = createGC4hash(GC4paramsDict)
        # if checkExistence("hash",hash): # CACHE SYSTEM TODO !!
        #     report = recoverReport(gc4uid)
        addLog({'hash':hash,'startdate':startdate,'startime':startime},
                rowCondition={'gc4uid':gc4uid}) # SHOULD BE HERE OR AT THE END?
        GC4logger('Saved analysis parameters',gc4uid,'status=PROCESSING')

        #with current_app.app_context():
        #ORIGINAL VERSION
        #os.system("venv/bin/python relaunchJob.py {}".format(gc4uid)) # CAREFULL CTRL+C do not kill this
        
        #QEUEING VERSION FOR APOLO SERVER, WATCH OUT MEM-PER-CPU & CPUS-PER-TASK
        cmd = "/home/genecodis/GeneCodis4.0/venv/bin/python relaunchJob.py {}".format(gc4uid)
        toqeueCMD1 = '/usr/bin/sbatch --job-name={0} --output=/home/genecodis/GeneCodis4.0/web/htmls/jobs/{0}/SBATCH.log --mem-per-cpu=5000 --cpus-per-task=6 --wrap="{1}" &'.format(gc4uid,cmd)

        
        GC4logger('Your job is submitted to the jobs queue',gc4uid,'status=PROCESSING')
        writeReport("PENDING",gc4uid)
        #launch job
        os.system(toqeueCMD1)
        #check status of job
        output = subprocess.run(["/usr/bin/squeue -h -O State:. -n {}".format(gc4uid)], capture_output=True,text=True,check=True,shell=True)
        while(output.stdout=="PENDING\n"):
            output = subprocess.run(["/usr/bin/squeue -h -O State:. -n {}".format(gc4uid)], capture_output=True,text=True,check=True,shell=True)
            #if job started running tell the user
            if(output.stdout=="RUNNING\n"):
                GC4logger('Your job started running'.format(),gc4uid,'status=PROCESSING')
        #check if job exceeded memory limit
        while(output.stdout=="RUNNING\n"):
            output = subprocess.run(["/usr/bin/squeue -h -O State:. -n {}".format(gc4uid)], capture_output=True,text=True,check=True,shell=True)
            #wait for SBATCH.log creation
            while not os.path.exists(os.path.join(jobDir,"SBATCH.log")):
                time.sleep(1)
            #check memory limit message
            for line in open(os.path.join(jobDir,"SBATCH.log")).read().splitlines():
                if "Exceeded job memory limit" in line:
                    writeReport('EXCEEDED',gc4uid)
                    GC4logger("Exceeded job memory limit, please try with a lighter job",gc4uid,'status=ERROR')
                    return(Response("error", status=400))


        return(Response("OK, Analysis launched successfully, jobID:"+paramsDict['gc4uid'], status=200))

    except Exception as errorwhatever:
        print(errorwhatever)
        if email != '':
            try:
                sendMSG(email,gc4uid,jobName,current_app,status=False)
                GC4logger('SENT Error Email',gc4uid,'status=ERROR')
            except Exception as errorwhatever2:
                GC4logger('ERROR Sending Email',gc4uid,'status=ERROR')
                GC4logger(errorwhatever2,gc4uid,'status=ERROR')
        writeReport('FAILURE',gc4uid)
        GC4logger(errorwhatever,gc4uid,'status=ERROR')
        return(Response("error", status=400))

@bp.route("/createjob", methods=('GET',))
def createjob(prog="programmatic"):
    gc4uid = secrets.token_urlsafe(10)
    session['jamon'] = gc4uid
    while checkExistence('gc4uid',gc4uid):
        gc4uid = getGC4uid()
    jobDir = os.path.join('web/htmls/jobs/',gc4uid)
    os.makedirs(jobDir,exist_ok=True)
    print("NEW JOB CREATED")
    addLog({"gc4uid":gc4uid})
    GC4logger('Created job: '+gc4uid,gc4uid,'status=PROCESSING')
    if prog=="programmatic":
        return gc4uid
    else:
        return(Response(gc4uid, mimetype='text/plain'))

@bp.route('/session', methods=('GET',))
def session_view():
    session['jamon'] = 'detrevelez'
    print('In Session')
    print(session.get('jamon'))
    return Response(session.get('jamon'), mimetype='text/plain')

checkstatebp = Blueprint('checkstatebp',__name__)
@checkstatebp.route("/checkstate", methods=['GET'])
def checkstate():
    gc4uid = request.args.get('job')
    reportFile = os.path.join('web/htmls/jobs',gc4uid,"report.html")
    if os.path.isfile(reportFile) == False:
        state = {'state':"FAILURE"}
        return Response(state, mimetype='text/plain')
    with open(reportFile,'r') as reportHNDL:
        for line in reportHNDL:
            if "tile is-ancestor" in line or "fithtiary" in line:
                state = {'state':"SUCCESS"}
                break
            elif "notification is-warning" in line:
                state = {'state':"FAILURE"}
                break
            else:
                log =  "\n".join(open(os.path.join('web/htmls/jobs',gc4uid,"log")).read().splitlines()[:-1])
                state = {'state':"PENDING",'log':log}
                break
    print('checkstate:::: '+state['state'])
    return jsonify(state)

@bp.route("/analysisResults")
def recoverJob(isOld = False):
    gc4uid = request.args.get('job')
    reportFile = os.path.join('web/htmls/jobs',gc4uid,"report.html")
    report,params = recoverReport(gc4uid)
    warning = ''
    if 'fithtiary' in open(reportFile).readline():
        report = '<link rel="stylesheet" href="assets/css/flex_layout.css">'+report
        report = report.replace('initSlider','initSlider2')
        report = report.replace('openTab','openTab2')
        report = report.replace('updateVisualizations','updateVisualizations2')
        report += '''<script type="text/javascript">
                      openTabResults();
                      document.onload = document.querySelector('.tertiary > button').click();
                    </script>
             '''
    if 'notification is-warning' in report:
        warning = report
        report = ''
    html = render_template("index_template.html",params=params,warning=warning,report=report)
    return(html)

@bp.route("/database")
def downloadAnnot():
    annotation = request.args.get('annotation')
    nomenclature = request.args.get('nomenclature')
    organism = request.args.get('organism')
    df = getAnnot2ColDF(annotation,nomenclature,organism)
    resp = make_response(df.to_csv(sep='\t',index=False))
    fileName = "attachment; filename={}-{}taxId_GeneCodis4.tsv".format(annotation,organism)
    resp.headers["Content-Disposition"] = fileName
    resp.headers["Content-Type"] = "text/tsv"
    return (resp)

results = Blueprint('results',__name__)
@results.route("/results")
def getResults():
    job = request.args.get('job')
    annotation = request.args.get('annotation')
    download = request.args.get('download',False)
    sortby = request.args.get('sortby') 
    asc = request.args.get('asc')
    head = request.args.get('head')
    search = request.args.get('search')
    jsonified = request.args.get('jsonify')
    print("request arguments:",request)
    resultsPath = os.path.realpath(os.path.join('web/htmls/jobs',job))
    # chequear si estamos pulsando el boton de descargar todas las tablas o solo la actual
    if annotation == 'all':
        if jsonified is None:       
            enrichfiles = glob.glob(os.path.join(resultsPath, "*.tsv"))
            stream = BytesIO()
            with ZipFile(stream, 'w') as zf:
                for file in enrichfiles:
                    zf.write(file, os.path.basename(file))
            stream.seek(0)
            return send_file(
                stream,
                as_attachment=bool(all),
                download_name=job+'_enrichment_files.zip'
            )
        if jsonified == 'True' or 'true' or 't':
            enrichfiles = glob.glob(os.path.join(resultsPath, "*.tsv"))
            output=[]
            outputnames=[]
            for file in enrichfiles:
                outputnames.append(file[file.find('enrich-')+7:len(file)-4])
                df = pandas.read_csv(file,sep='\t')
                output.append(df.to_dict())
            dictionary = dict(zip(outputnames, output))
            return jsonify(dictionary)

    else:
        filename = 'enrich-'+annotation+'.tsv'
        fullName = os.path.join(resultsPath,filename)
        if os.path.isfile(fullName) == False:
            filename = 'enrich-'+annotation
        print(fullName)
        if sortby is None and head is None and search is None:
            if asc is not None:
                return(Response("error: sortBy parameter is empty.",status=400))
            else:
                return send_from_directory(resultsPath, filename,
                                    mimetype="Content-Type: text/tsv; charset=utf-8; Content-Disposition: filename={}".format(filename),
                                    as_attachment=bool(download))
        else:
            df = pandas.read_csv(fullName,sep='\t')
            if search is not None:
                df=df[df['description'].str.contains(search)]
            if sortby is None and asc is not None:
                return(Response("error: sortBy parameter is empty.",status=400))
            if sortby is not None:
                if sortby not in df.columns:
                    return(Response("error: incorrect sortby value.",status=400))
                if asc is None or asc=='False' or asc=='false' or asc=='F' or asc=='f':
                    if sortby=='description' or sortby=='annotation_id' or sortby=='genes':
                        df=df.sort_values(sortby,ascending=False,key=lambda col: col.str.lower())
                    else:
                        df=df.sort_values(sortby,ascending=False)
                elif asc=='True' or asc=='true' or asc=='T' or asc=='t':
                    if sortby=='description' or sortby=='annotation_id' or sortby=='genes':
                        df=df.sort_values(sortby,ascending=True,key=lambda col: col.str.lower())
                    else:
                        df=df.sort_values(sortby,ascending=True)
                else:
                    return(Response("error: incorrect asc value.",status=400))
            if head is not None:
                if head.isdigit()==False:
                    return(Response("error: incorrect head value.",status=400))
                df=df.iloc[:int(head)]
            output2=''
            output2=output2+'\t'.join(df.columns)+'\n'
            for i,row in df.iterrows():
                output2=output2+row[0]+'\t'+row[1]+'\t'+str(row[2])+'\t'+str(row[3])+'\t'+str(row[4])+'\t'+str(row[5])+'\t'+str(row[6])+'\t'+str(row[7])+'\t'+str(row[8])+'\t'+str(row[9])+'\t'+str(row[10])+'\n'
            return Response(output2,mimetype='text/plain')
            


@bp.route("/geneinfo")
def getgeneinfo():
    genes = request.args.get('genes')
    organism = request.args.get('org')
    geneInfo = getGeneInfo(genes,organism)
    return Response(geneInfo, mimetype='text/plain')

@bp.route("/mirnas")
def transformmirnas():
    mirnas = request.args.get('mirnas')
    action = request.args.get('action')
    target = request.args.get('target')
    mirnasinfo = transformiRNAs(mirnas,action,target)
    return Response(mirnasinfo, mimetype='text/plain')

@bp.route("/params")
def recoverparams():
    gc4uid = request.args.get('job')
    report,params = recoverReport(gc4uid)
    return params

qc = Blueprint('qc',__name__)
@qc.route("/qc")
def recoverqc():
    gc4uid = request.args.get('job')
    report,params = recoverReport(gc4uid)
    input=params['input']
    organism=params['organism']
    universe=params['universe']
    annotations=params['annotations']
    inputtype=params['inputtype']
    inputNames=params['inputNames']
    coannotation=params['coannotation']
    stat=params['stat']
    jobDir=os.path.join('web/htmls/jobs/',gc4uid)
    inputsDict = checkNgenerate(input,str(organism),universe,annotations,jobDir,inputtype,inputNames,coannotation,stat)
    outdic={}
    for key in inputsDict.keys():
        for engene in inputsDict[key]:
            dic2={}
            if engene=="engenes":
                for item in inputsDict[key][engene]:
                    newname=item[item.find("engene-")+7:len(item)]
                    dic2[newname]=(inputsDict[key][engene][item])
                outdic[key]=dic2
            if engene=="notInDB":
                outdic[key]["notInDB"]=inputsDict[key][engene]
    for k in list(outdic.keys()):
        if k=="input1unique":
            if len(inputNames)==2:
                outdic[inputNames['input']] = outdic.pop(k)
            else:
                outdic[inputNames['input1unique']] = outdic.pop(k)
        if k=="input2unique":
            outdic[inputNames['input2']] = outdic.pop(k)
    for k in list(outdic.keys()):
        for k2 in list(outdic[k].keys()):
            if 'coannot' in outdic[k][k2].keys():
                del (outdic[k][k2]['coannot'])
            if 'annotation' in outdic[k][k2].keys():
                del outdic[k][k2]['annotation']
            if 'mirnatargets' in outdic[k][k2].keys() and bool(outdic[k][k2]['mirnatargets'])==False:
                del outdic[k][k2]['mirnatargets']
    print("apiurl:",os.getenv('API_URL'))
    return jsonify(outdic)

@bp.route("/queryTerm")
def query():
    database = request.args.get('databases')
    if isinstance(database,str):
        database = database.split(',')
    term = request.args.get('term')
    sortby = request.args.get('sortby') 
    asc = request.args.get('asc')
    params=['term','databases','sortby','asc']
    for arg in request.args.keys():
        if arg not in params:    
            return(Response("error: parameter not found.",status=400))
    conn = open_connection()
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tablas=cur.fetchall()
    tablas=[item for sublist in tablas for item in sublist]
    tablas.remove("prec2maturesmirnas")
    tablas.remove("taxonomy")
    tablas.remove("annotation_info")
    tablas.remove("bias")
    tablas.remove("gene")
    tablas.remove("synonyms")
    tablas.remove("gc4log")
    tablas.remove("annotation")
    if database is not None:
        database2=[]
        for db in database:
            database2.append(db.lower())
        for db in database2:
            if db not in tablas:
                return(Response("error: database not found.",status=400))
    else:
        database2=tablas
    cur.execute("(SELECT distinct annotation_info.annotation_id from annotation_info where term like %s)",["%{}%".format(term.lower())])
    annotation_ids=cur.fetchall()
    annotation_ids=[item for sublist in annotation_ids for item in sublist]
    results=[]
    for annotation in annotation_ids:
        for tabla in database2:
            cur.execute(sql.SQL("SELECT distinct {table}.annotation_id,annotation_info.term,{table}.annotation_source FROM annotation_info,{table} where annotation_info.annotation_id={table}.annotation_id and annotation_info.annotation_id=%s").format(table=sql.Identifier(tabla)),[annotation])
            result=cur.fetchall()
            if(any(result)):
                results.append(result)
    results=[item for sublist in results for item in sublist]
    results=list(dict.fromkeys(results))
    columns = ['db_id', 'annotation','db']
    results = pandas.DataFrame(results, columns = columns)
    if sortby is None and asc is not None:
        return(Response("error: sortBy parameter is empty.",status=400))
    if sortby is not None:
        if sortby not in results.columns:
                    return(Response("error: incorrect sortby value.",status=400))
        if asc is None or asc=='False' or asc=='false' or asc=='F' or asc=='f':
            results=results.sort_values(sortby,ascending=False,key=lambda col: col.str.lower())
        elif asc=='True' or asc=='true' or asc=='T' or asc=='t':
            results=results.sort_values(sortby,ascending=True,key=lambda col: col.str.lower())
        else:
            return(Response("error: incorrect asc value.",status=400))
    output2=''
    output2=output2+'\t'.join(results.columns)+'\n'
    for i,row in results.iterrows():
        output2=output2+row[0]+'\t'+row[1]+'\t'+row[2]+'\n'
    cur.close()
    close_connection(conn)
    return Response(output2,mimetype='text/plain')

@bp.route("/queryGene")
def queryGene():
    org = request.args.get('orgs')
    if isinstance(org,str):
        org = org.split(',')
    genes = request.args.get('genes')
    database = request.args.get('databases')
    if isinstance(genes,str):
        genes = genes.split(',')
    if isinstance(database,str):
        database = database.split(',')
        database2=[]
        for db in database:
            database2.append(db.lower())
    params=['orgs','databases','sortby','asc','genes']
    for arg in request.args.keys():
        if arg not in params:    
            return(Response("error: parameter not found.",status=400))
    conn = open_connection()
    cur = conn.cursor()
    if genes is None:
        return(Response("error: genes parameter is empty.",status=400))
    ids=[]
    for gene in genes:
        cur.execute("SELECT gene.id from gene where gene.symbol=%s",[gene.upper()])
        result=cur.fetchall()
        ids.append(result)
    ids=[item for sublist in ids for item in sublist]
    ids=[item for sublist in ids for item in sublist]
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tablas=cur.fetchall()
    tablas=[item for sublist in tablas for item in sublist]
    tablas.remove("prec2maturesmirnas")
    tablas.remove("taxonomy")
    tablas.remove("annotation_info")
    tablas.remove("bias")
    tablas.remove("gene")
    tablas.remove("synonyms")
    tablas.remove("gc4log")
    tablas.remove("annotation")
    results=[]
    for tabla in tablas:
        for id in ids:
            cur.execute(sql.SQL("select distinct gene.id,{table}.annotation_id,gene.symbol,annotation_info.term,gene.tax_id,{table}.annotation_source from {table},gene,annotation_info where {table}.id=%s and gene.id={table}.id and {table}.annotation_id=annotation_info.annotation_id").format(table=sql.Identifier(tabla)),[id])
            result=cur.fetchall()
            if any(result):
                results.append(result)
    results=[item for sublist in results for item in sublist]
    columns = ['gene_id','db_id','gene_name', 'annotation','organism_id','db']
    results=list(dict.fromkeys(results))
    results = pandas.DataFrame(results, columns = columns)
    if database is not None:
        for db in database2:
            if db not in tablas:
                return(Response("error: incorrect database value.",status=400))
        results = results[results['db'].str.lower().isin(database2)]
    if org is not None:
        results = results[results['organism_id'].isin(org)]
    output2=''
    output2=output2+'\t'.join(results.columns)+'\n'
    for i,row in results.iterrows():
            output2=output2+row[0]+'\t'+row[1]+'\t'+row[2]+'\t'+row[3]+'\t'+row[4]+'\t'+row[5]+'\n'           
    cur.close()
    close_connection(conn)
    return Response(output2,mimetype='text/plain')

@bp.errorhandler(429)
def ratelimit_handler(e):
    return "You have exceeded the GeneCodis rate-limit, which is 10 requests per minute. If you think you may need a further access to GeneCodis please contact us at bioinfo@genyo.es"
