import os, json
from datetime import date,datetime,timedelta
from dotenv import load_dotenv
load_dotenv()
from lib.gc4DBHandler import *

cmdTemplate = "SELECT * FROM gc4log;"
args = ''
loggc4 = launchQuery(cmdTemplate,args,getDF=True)
startdates = loggc4.startdate.to_list()

############ keep jobs of one month back, just in case cron fails ############
# oldestdate = date.today() - timedelta(days=30)
# actualdates = [startdate > oldestdate if startdate != None else True for startdate in startdates]
# actualjobids = loggc4.iloc[actualdates,].gc4uid.tolist()
# jobids2remove = set(loggc4.gc4uid) - set(actualjobids)
# cmdTemplate = "DELETE FROM gc4log WHERE gc4uid IN %s;"
# args = tuple([list(jobids2remove)],)
# loggc4 = launchQuery(cmdTemplate,args,getDF=False)
# actualjobsdirs = ['web/htmls/jobs/{}'.format(jobid) for jobid in actualjobids]
# alljobs = glob.glob('web/htmls/jobs/*')
# jobdirs2remove = set(alljobs) - set(actualjobsdirs)
# for jobid in jobdirs2remove: # NEW FOR APPART TO AVOID ERASE WITHOUT PARAMS SAVING
#     jobdir = os.path.join('web/htmls/jobs',jobid)
#     os.system('rm -rf {}'.format(os.path.abspath(jobdir)))
############################################################################vv

oldestdate = date.today() - timedelta(days=30)
olddates = [oldestdate > startdate if startdate != None else True for startdate in startdates]
jobids2remove = loggc4.iloc[olddates,].gc4uid.tolist()

if len(jobids2remove) > 0:
    alljson = []
    for jobid in jobids2remove:
        jobdir = os.path.join('../web/htmls/jobs',jobid)
        jsonFile = os.path.join(jobdir,'params.json')
        if os.path.isfile(jsonFile) == False:
            continue
        params = json.loads(open(jsonFile).read())
        idx = list(loggc4.gc4uid).index(jobid)
        if loggc4.endtime[idx] == None:
            elapsed = 'NA'
        else:
            mytime = datetime.combine(loggc4.enddate[idx],loggc4.endtime[idx]) - datetime.combine(loggc4.startdate[idx],loggc4.startime[idx])
            elapsed = mytime.total_seconds()
        params['elapsed'] = elapsed
        params['date'] = datetime.fromtimestamp(os.path.getmtime(jsonFile)).date()
        if 'coannotation' in params:
            params['coannotation'] = params['coannotation'].replace('coannotation_','')
        else:
            params['coannotation'] = 'yes'
        params['annotations'] = ', '.join(params['annotations'])
        if len(params['input']) == 2:
            params['input2'] = ', '.join(params['input']['input2'])
            params['inputName2'] =  params['inputNames']['input2']
            params['inputName'] = params['inputNames']['input']
        else:
            params['input2'] = ''
            params['inputName2'] = ''
            params['inputName'] = params['inputNames']['input1unique']
        params['input'] = ', '.join(params['input']['input'])
        params['universe'] = ', '.join(params['universe'])
        params.pop('inputNames', None)
        alljson.append(params)
    myDf = pandas.DataFrame(alljson)

    os.makedirs("/home/genecodis/GeneCodis4.0/db/stats/",exist_ok=True)
    statsFile = '/home/genecodis/GeneCodis4.0/db/stats/{}_GC4stats.tsv'.format(oldestdate.strftime("%m_%y"))
    mode, header  = 'w', True
    if os.path.isfile(statsFile):
        mode, header  = 'a', False

    myDf.to_csv(statsFile,sep="\t",index=False,mode=mode,header=header)

    cmdTemplate = "DELETE FROM gc4log WHERE gc4uid IN %s;"
    args = tuple([jobids2remove],)
    launchQuery(cmdTemplate,args,getDF=False)
    for jobid in jobids2remove: # NEW FOR APPART TO AVOID ERASE WITHOUT PARAMS SAVING
        jobdir = os.path.join('/home/genecodis/GeneCodis4.0/web/htmls/jobs',jobid)
        os.system('rm -rf {}'.format(os.path.abspath(jobdir)))
    print('Removed {} jobs'.format(len(jobids2remove)))
else:
    print('NO OLD JOBS, EXITING')

os.system('touch /home/genecodis/GeneCodis4.0/cronDone')

# os.chdir('/home/genecodis/GeneCodis4.0/db/maintenance')
# print('Beggining DB update!')
# updatesteps = ['generate_and_download_tables.py','updateGeneCodis.py','loadGeneCodistoPostgres.py']
# pythonpath = '/home/genecodis/GeneCodis4.0/venv/bin/python'
# try:
#     for step in updatesteps:
#         cmd = '{} {}'.format(pythonpath,step)
#         print(cmd)
#         os.system(cmd)
#     print('Updated DB!')
#     os.system('touch /home/genecodis/GeneCodis4.0/upDBdone')
# except Exception as excperror:
#     print(excperror)
#     os.system('touch /home/genecodis/GeneCodis4.0/upDBerror')
# # sudo nano /etc/crontab
# #0 1 * * * /home/genecodis/GeneCodis4.0/venv/bin/python /home/genecodis/GeneCodis4.0/db/cleanNupdate.py >> /home/genecodis/GeneCodis4.0/dbupdate.log 2>&1
