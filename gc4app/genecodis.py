import os, json

class GeneCodisBinaryLauncher:
    def __init__(self,inputsDict,inputSupport,gc4uid,coannotation,organism,inputtype):
        binaryPath  = "./genecodis3_essentials/genecode_yang_xml"
        minsupport4random = min(3,inputSupport)
        jobsParams = [inputSupport,binaryPath,minsupport4random]
        if coannotation:
            inputsDict = self.expandIfSingleAnnot(inputsDict)
        self.jobsDict, allJobs = self.defineJobs(inputsDict,jobsParams,organism,inputtype)
        print('Launching Jobs')
        print("\n".join(allJobs))
        commandsFile = 'web/htmls/jobs/{}/commands.sh'.format(gc4uid)
        with open(commandsFile,'w') as commandsFileHNDL:
            commandsFileHNDL.write("\n".join(allJobs))
        self.jobs = allJobs
        # self.launchJobs(allJobs)
        # print('Jobs La2unched!')

    def expandIfSingleAnnot(self,inputsDict):
        for input in inputsDict:
            print(input)
            if list(inputsDict[input].keys())[0] == 'name' or len(inputsDict[input]['engenes']) > 1:
                print("NO EXPANDING")
                continue
            print("EXPANDING")
            if len(list(inputsDict[input]['engenes'].keys())) == 0:
                print("NOTHING TO EXPAND")
                continue
            engenePath = list(inputsDict[input]['engenes'].keys())[0]
            singleEngene = inputsDict[input]['engenes'][engenePath].copy()
            tmpEngenePath =  engenePath + "_"
            inputsDict[input]['engenes'][tmpEngenePath] = singleEngene
            coannotEngene  = inputsDict[input]['engenes'][tmpEngenePath]
            coannotEngene['coannot'] = True
            coannotEngene['annotation'] = [coannotEngene['annotation']]
        return(inputsDict)

    def defineJobs(self,inputsDict,jobsParams,organism,inputtype):
        print("DEFINIG JOB")
        print(inputsDict)
        cmds = []
        inputs = list(inputsDict.keys())
        for input in inputs:
            if 'engenes' not in inputsDict[input]:
                continue
            inputNumber = len(inputsDict[input]['notInDB']['invalidInput'])
            engenes = inputsDict[input]['engenes']
            for engenePath in engenes:
                jobUnit = engenes[engenePath]
                cmd, jobUnit = self.defineJob(jobUnit,engenePath,organism,inputtype,inputNumber,*jobsParams)
                inputsDict[input]['engenes'][engenePath] = jobUnit
                cmds.append(cmd)
        return(inputsDict, cmds)

    def defineJob(self,jobUnit,engenePath,organism,inputtype,inputNumber,inputSupport,binaryPath,minsupport4random,test=0,pvalCorrection=-1):
        # argsMap = {"hypergeometric":0,"chiSquare":1,"fdr":-1,
        # "permutations":1000,"none":0}
        engenePath = engenePath.rstrip("_")
        cmdStr = "{} {} {} -a{} -i{} -r{} -R{} -t{} -s{} -o {}"
        outFile = engenePath.replace("engene","enrich")
        annotation = jobUnit['annotation']
        print('!!!! organism,inputtype,annotation')
        print([organism,inputtype,annotation])
        universeNumber = self.getUniverse(organism,inputtype,annotation)
        print('!!!! universeNumber')
        print(universeNumber)
        #universeNumber = universeNumber if isinstance(universeNumber,int) else len(universeNumber)
        inputNumber += len(jobUnit["annotated"]+jobUnit["noAnnotated"])
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

    def getUniverse(self,organism,inputtype,annotation):
        universe = json.loads(open('db/info/geneUniverse.json').read())
        if annotation in ['MNDR','HMDD_v3','TAM_2']:
            inputtype = "mirna_directed"
        else:
            inputtype = "genes"
        universeNumber = universe[organism][inputtype]
        return(universeNumber)
