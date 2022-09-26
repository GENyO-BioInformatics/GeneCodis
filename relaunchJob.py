from flask import Blueprint
from flask import *
from flask_restful import *
from flask import Flask, request, render_template
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, ValidationError, pre_load, post_load
from gc4app.visualizator import *
from gc4app.commonthings import *
from db.lib.gc4DBHandler import *
from db.lib.testingSQL import *
#from flask_mail import Mail, Message
from gc4app.gc4mailer import sendMSG
from db.lib.gc4loghandler import *
from gc4app.argumentsControl import GeneCodisParamsSchema
from gc4app.apriori import aprioriStats
import json, re, numpy, os, csv, jinja2, time
import logging, datetime, random, string, hashlib, sys
sys.setrecursionlimit(500)

#from flask_mail import Mail, Message
from flask import current_app
#import os
from dotenv import load_dotenv
load_dotenv()

from gc4app import factory
from flask_mail import Mail, Message

app = factory.create_app()
mail=Mail(app)

startdate = datetime.datetime.now()
enddate = datetime.datetime.now()
eta = enddate - startdate

jobid = sys.argv[1]
paramsJson = 'web/htmls/jobs/{}/params.json'.format(jobid)

try:
    paramsDict = json.loads(open(paramsJson).read())
    print('-----paramsDict-----')
    print(paramsDict)
    GC4params = GeneCodisParamsSchema().load(paramsDict,many=False)
    organism = str(GC4params.organism)
    annotations = GC4params.annotations
    input = GC4params.input
    inputNames = GC4params.inputNames
    inputSupport = GC4params.inputSupport
    universe = GC4params.universe
    email = GC4params.email
    inputtype = GC4params.inputtype
    jobName = GC4params.jobName
    gc4uid = GC4params.gc4uid
    stat = GC4params.stat
    algorithm  = GC4params.algorithm
    scope = GC4params.scope
    coannotation = True if GC4params.coannotation == "coannotation_yes" else False

    jobDir = os.path.join('web/htmls/jobs/',gc4uid)
    os.makedirs(jobDir,exist_ok=True)

    t0 = datetime.datetime.now()
    startdate, startime = str(t0).split(' ')
    addLog({'startdate':startdate,'startime':startime},
            rowCondition={'gc4uid':gc4uid}) # SHOULD BE HERE OR AT THE END?

    GC4logger('Querying the database',gc4uid,'status=PROCESSING')
    writeReport("PENDING",gc4uid)

    inputsDict = checkNgenerate(input,organism,universe,annotations,jobDir,inputtype,inputNames,coannotation,stat)
    print('-----inputsDict-----')
    print(inputsDict)
    if inputsDict == "":
        GC4logger('Error: Invalid Input',gc4uid,'status=INVALIDINPUT')
        writeReport("INVALID",gc4uid)
        print("ERROR EXITING")
        exit()

    GC4logger('Annotations obtained',gc4uid,'status=PROCESSING')
    synonyms = inputsDict['synonyms']
    inputsDict.pop('synonyms', None)
    engenesCheck = [bool(inputsDict[inputs]['engenes']) if 'engenes' in inputsDict[inputs] else True for inputs in inputsDict]

    if any(engenesCheck) == False:
        GC4logger('Error: Invalid Input',gc4uid,'status=INVALIDINPUT')
        writeReport("INVALID",gc4uid)
        print("ERROR EXITING engenesCheck")
        exit()

    print('Generating Jobs')
    GC4logger('Performing the analyses',gc4uid,'status=PROCESSING')
    jobsInfo = aprioriStats(inputsDict,inputSupport,coannotation,organism,inputtype,stat,algorithm,gc4uid,scope)
    jobsDict,inputSupport = jobsInfo.jobsDict
    paramsDict['inputSupport'] = inputSupport
    print('-----jobsDict-----')
    print(jobsDict)
    saveJson(paramsDict,paramsJson)

    outDir = os.path.join('web/htmls/jobs/',gc4uid)
    GC4logger('Generating report',gc4uid,'status=PROCESSING')
    GeneCodisResultsReporter(jobsDict,synonyms,organism,outDir)
    print('Report done')
    GC4logger('Analysis finished',gc4uid,'status=PROCESSING')
    t1 = datetime.datetime.now()
    enddate, endtime = str(t1).split(' ')
    addLog({'enddate':enddate,'endtime':endtime},
            rowCondition={'gc4uid':gc4uid})
    GC4logger('Showing results...',gc4uid,'status=PROCESSING')
    eta = str(t1 - t0)
    GC4logger('Elapsed time: '+eta,gc4uid,'status=ENDED')
    print('FINISHED')

    with app.app_context():
        if email != '':
            GC4logger('Sending Email',gc4uid,'status=PROCESSING')
            sendMSG(email,gc4uid,jobName,current_app)
            GC4logger('Giving Response',gc4uid,'status=ENDED')

except Exception as errorwhatever:
    #logNsendError(errorwhatever,gc4uid,jobName,email)
    print(errorwhatever)
    if email != '':
        try:
            sendMSG(email,gc4uid,jobName,app,status=False)
            GC4logger('SENT Error Email',gc4uid,'status=ERROR')
        except Exception as errorwhatever2:
            GC4logger('ERROR Sending Email',gc4uid,'status=ERROR')
            GC4logger(errorwhatever2,gc4uid,'status=ERROR')
    writeReport('FAILURE',gc4uid)
    GC4logger(errorwhatever,gc4uid,'status=ERROR')
