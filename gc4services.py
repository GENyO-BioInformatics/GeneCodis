def restartGC4addons():
    cmd = 'python toProduction.py'
    launchCMD(cmd)
    cmd = 'sudo systemctl daemon-reload'
    launchCMD(cmd)

def checkIfRunning():
    PROCNAME = "genecode_yang_xml"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            print("GeneCodis is being used!")
            exit()

def checkLogs(status):
    # status = ['ERROR','PROCESSING','ENDED', ...]
    cmd = "grep -rn web/htmls/jobs/*/*.log -e 'status={}' | for log in $(cut -f1 -d':'); do tail $log; echo $log; done"
    cmd = cmd.format(status)
    launchCMD(cmd)

def launchCMD(cmd):
    print(cmd)
    os.system(cmd)

def replaceStrOfFile(file,target,replacement):
    wholetext = open(file,'r').read()
    wholetext = wholetext.replace(target,replacement)
    with open(file,'w') as fileHNDL:
        fileHNDL.write(wholetext)

import sys, os, psutil

if sys.argv[1] == '-f':
    print("FORCING ACTION SELECTED")
    i = 1
else:
    i = 0
    checkIfRunning()

if sys.argv[1+i] == 'maintenance':
    try:
        cmd = "sudo cp web/templates/maintenance.html /usr/share/nginx/html/index.html"
        os.system(cmd)
    except:
        cmd = "sudo cp web/templates/maintenance.html /var/www/html/index.html"
        os.system(cmd)
    replaceStrOfFile("web/templates/index_template.html","validateForm","raiseMaintenance")

service = sys.argv[1+i]
action = sys.argv[2+i]

services = ['nginx','gunicorn','all']
actions = ['status','start','stop','restart','enable','disable']

if service not in services or action not in actions:
    print('exit()',service,action)
    print(service not in services)
    exit()

if action == 'restart':
    actions = ['stop','start']
    restartGC4addons()
else:
    actions = [action]
if service == 'all':
    services = ['nginx','gunicorn']
else:
    services = [service]

baseCmd = 'sudo systemctl {} {}'
for action in actions:
    for service in services:
        cmd = baseCmd.format(action,service)
        launchCMD(cmd)

if action == 'status':
    try:
        checkLogs(sys.argv[3+i])
    except:
        print('just basic logs')



# grep -rn web/htmls/jobs/*/*.log -e 'status=PROCESSING' | for log in $(cut -f1 -d':'); do tail $log; echo $log; done
# grep -rn web/htmls/jobs/*/*.log -e 'status=PROCESSING' | for log in $(cut -f1 -d':'); do mydir=$(dirname $log); grep -o '9606'  $mydir'/params.json'; done | wc -l
# grep -rn web/htmls/jobs/* -e 'status=PROCESSING' | for log in $(cut -f1 -d':'); do tail $log; echo $log; done
# grep -rn web/htmls/jobs/* -e 'status=PROCESSING' | for log in $(cut -f1 -d':'); do echo $log; done;
# sshpass -p "password" scp -r genecodis@192.168.2.26:/home/genecodis/GeneCodis4.0/web/htmls/jobs/giGkmaunVi .
# sudo systemctl stop gc4flower
# sudo systemctl start gc4flower
