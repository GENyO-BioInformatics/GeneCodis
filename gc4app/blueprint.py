from io import BytesIO
from flask import Blueprint, session
#from celery.result import AsyncResult
#from .tasks import launchJobs
from flask import *
from flask_restful import *
from flask import Flask, request, render_template
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, ValidationError, pre_load, post_load
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
        print("parametros post:",paramsDict)
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
        os.system(toqeueCMD1)
        output = subprocess.run(["/usr/bin/squeue -h -O State:. -n {}".format(gc4uid)], capture_output=True,text=True,check=True,shell=True)
        while(output.stdout=="PENDING\n"):
            output = subprocess.run(["/usr/bin/squeue -h -O State:. -n {}".format(gc4uid)], capture_output=True,text=True,check=True,shell=True)
            if(output.stdout=="RUNNING\n"):
                GC4logger('Your job started running'.format(),gc4uid,'status=PROCESSING')

        return(Response("OK", status=200))

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
def createjob():
    gc4uid = secrets.token_urlsafe(10)
    session['jamon'] = gc4uid
    while checkExistence('gc4uid',gc4uid):
        gc4uid = getGC4uid()
    jobDir = os.path.join('web/htmls/jobs/',gc4uid)
    os.makedirs(jobDir,exist_ok=True)
    print("NEW JOB CREATED")
    addLog({"gc4uid":gc4uid})
    GC4logger('Created job: '+gc4uid,gc4uid,'status=PROCESSING')
    return(Response(gc4uid, mimetype='text/plain'))

@bp.route('/session', methods=('GET',))
def session_view():
    session['jamon'] = 'detrevelez'
    print('In Session')
    print(session.get('jamon'))
    return Response(session.get('jamon'), mimetype='text/plain')

@bp.route("/checkstate/job=<gc4uid>")
def checkstate(gc4uid):
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

@bp.route("/job=<gc4uid>")
def recoverJob(gc4uid,isOld = False):
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

@bp.route("/results")
def getResults():
    job = request.args.get('job')
    annotation = request.args.get('annotation')
    download = request.args.get('download',False)
    print("request arguments:",request)
    resultsPath = os.path.realpath(os.path.join('web/htmls/jobs',job))
    # chequear si estamos pulsando el boton de descargar todas las tablas o solo la actual
    if annotation == 'all':       
        enrichfiles = glob.glob(os.path.join(resultsPath, "*.tsv"))
        stream = BytesIO()
        with ZipFile(stream, 'w') as zf:
            for file in enrichfiles:
                zf.write(file, os.path.basename(file))
        stream.seek(0)
        return send_file(
            stream,
            as_attachment=bool(all),
            attachment_filename=job+'_enrichment_files.zip'
        )
    else:
        filename = 'enrich-'+annotation+'.tsv'
        fullName = os.path.join(resultsPath,filename)
        if os.path.isfile(fullName) == False:
            filename = 'enrich-'+annotation
        print(fullName)
        return send_from_directory(resultsPath, filename,
                                mimetype="Content-Type: text/tsv; charset=utf-8; Content-Disposition: filename={}".format(filename),
                                as_attachment=bool(download))


@bp.route("/geneinfo")
def getgeneinfo():
    genes = request.args.get('genes')
    organism = request.args.get('org')
    geneInfo = getGeneInfo(genes,organism)
    return Response(geneInfo, mimetype='text/plain')

@bp.route("/externalquery&org=<organism>&genes=<genes>", methods=('POST','GET'))
# localhost:5000/externalquery&org=9606&genes=1,2,3
def dumpquery(genes,organism):
    params = {"input": {"input": genes.split(',')}, "email": "", "coannotation": "coannotation_no", "inputSupport": '10', "jobName": "",
    "inputmode": "on", "scope": "annotated", "algorithm": "fpgrowth", "inputNames": {"input1unique": ""}, "universe": [],
    "inputtype": "mirnas", "organism": organism, "stat": "hypergeom", "annotations": []}

    cleanancescript = """<script>
        document.querySelector("#analysis").click();
        document.querySelector("#resultstab").style.display = 'none';
    </script>"""

    html = render_template("index_template.html",params=params,report=cleanancescript)
    return(html)

@bp.route("/mirnas")
def transformmirnas():
    mirnas = request.args.get('mirnas')
    action = request.args.get('action')
    target = request.args.get('target')
    mirnasinfo = transformiRNAs(mirnas,action,target)
    return Response(mirnasinfo, mimetype='text/plain')

@bp.route("/params/job=<gc4uid>")
def recoverparams(gc4uid):
    report,params = recoverReport(gc4uid)
    return params

@bp.route("/qc/job=<gc4uid>")
def recoverqc(gc4uid):
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
    return jsonify(inputsDict)