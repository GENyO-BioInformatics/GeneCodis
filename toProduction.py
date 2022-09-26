import os, json
from db.lib.gc4loghandler import *
from dotenv import load_dotenv
load_dotenv()

import sys
mode = sys.argv

def replaceStrOfFile(file,target,replacement):
    wholetext = open(file,'r').read()
    wholetext = wholetext.replace(target,replacement)
    with open(file,'w') as fileHNDL:
        fileHNDL.write(wholetext)

## Generate New HTMLs
cmd = "node ./web/source/generate_bulma.js"; print(cmd); os.system(cmd)

infoFile = 'db/maintenance/info/data_in_web.json'
with open(infoFile,'r') as datainwebHNDL:
    datainweb = json.load(datainwebHNDL)

validationdict = {}
for taxid in datainweb:
    validationdict[taxid] = [list(annot.keys())[0] for annot in datainweb[taxid]['annotations']]

#validationdict['9606'].remove("CTD") ## CTD blocked for humans PROBLEMS BINARY!

validation = json.dumps(validationdict)
validationFile = 'web/htmls/assets/js/organism_annotations.js'
with open(validationFile,'w') as validationHNDL:
    validationHNDL.write("var orgsAnnots = "+validation)

import time

## Pass repo web thingies to local server
mainHtml = 'web/htmls/indexBulma.html'
maintenanceHtml = 'web/htmls/maintenanceBulma.html'
templateFile = 'web/templates/index_template.html'
validatorTempFile = 'web/htmls/assets/js/validator_template.js'
validatorFile = 'web/htmls/assets/js/validator.js'
cmd = "cp {} {}".format(validatorTempFile,validatorFile); print(cmd); os.system(cmd)
cmd = "cp {} {}".format(mainHtml,templateFile); print(cmd); os.system(cmd)

API_URL = os.getenv("API_URL")
replaceStrOfFile(validatorFile,"API_URL",API_URL)
replaceStrOfFile(templateFile,'tab active','tab')
# replaceStrOfFile(templateFile,"id='resultstab' style='display:none;'","id='resultstab' class='is-active;'")
# replaceStrOfFile(templateFile,'<div id="analysis">','<div id="analysis" style="display:none;">')
replaceStrOfFile(templateFile,'<div class="hero-body">','<div class="hero-body">{{ warning|safe }}')
replaceStrOfFile(templateFile,'<div id="results" style="display:none;">','<div id="results" style="display:none;">\n{{ report|safe }}')
replaceStrOfFile(templateFile,"document.getElementsByName('organism')[0].value = '9606';","")
replaceStrOfFile(templateFile,"document.getElementById('genes').click();","")
replaceStrOfFile(templateFile,"document.getElementById('GO_BP').click();","recoverParams({{ params|safe }});")

createGC4logTable()

print('CACHEBOOSTING')
WEB_FOLDER = os.getenv("WEB_FOLDER")
cmd = 'sudo rm -rf {}/assets/*/*'.format(WEB_FOLDER); print(cmd); os.system(cmd)
cmd = 'sudo rm -rf web/htmls/assets/*/*[0-9].*'; print(cmd); os.system(cmd)
cacheboost = str(int(time.time()))
import glob
toBoost = glob.glob('web/htmls/assets/*/*.js') + glob.glob('web/htmls/assets/*/*.css')
for file in toBoost:
    print(file)
    filename, ext = os.path.splitext(file)
    newName = os.path.basename(filename)+cacheboost+ext
    replaceStrOfFile(mainHtml,os.path.basename(file),newName)
    replaceStrOfFile(maintenanceHtml,os.path.basename(file),newName)
    replaceStrOfFile(templateFile,os.path.basename(file),newName)
    #replaceStrOfFile(templateFile,os.path.basename(file),newName)
    outDir = '{}/assets/{}'.format(WEB_FOLDER,ext[1:])
    cmd = 'sudo mkdir -p {}'.format(outDir); print(cmd); os.system(cmd)
    cmd = 'sudo cp {} {}/{}'.format(file,outDir,newName); print(cmd); os.system(cmd)
    cmd = 'sudo cp {} {}'.format(file,file.replace('.',cacheboost+'.')); print(cmd); os.system(cmd)

# cmd = "sudo cp -r web/htmls/assets {}/.".format(WEB_FOLDER)
# print(cmd)
# os.system(cmd)
cmd = 'sudo cp -r web/htmls/assets/images {}/assets'.format(WEB_FOLDER); print(cmd); os.system(cmd)

if len(mode) > 1 and mode[1] == 'maintenance':
    cmd = "sudo cp web/htmls/maintenanceBulma.html {}/index.html".format(WEB_FOLDER); print(cmd); os.system(cmd)
else:
    cmd = "sudo cp web/htmls/indexBulma.html {}/index.html".format(WEB_FOLDER); print(cmd); os.system(cmd)
