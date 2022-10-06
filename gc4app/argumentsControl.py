from marshmallow import Schema,fields,ValidationError,pre_load,post_load
import re

class GeneCodisParams:
    def __init__(self,organism,annotations,input,inputtype,inputNames,
        universe,inputSupport,email,jobName,gc4uid,stat,algorithm,
        coannotation,inputmode,scope):
        self.organism = organism
        self.annotations = annotations
        self.inputSupport = inputSupport
        self.universe = universe
        self.email = email
        self.jobName = jobName
        self.input = input
        self.inputtype = inputtype
        self.inputNames = inputNames
        self.gc4uid = gc4uid
        self.coannotation = coannotation
        self.stat = stat
        self.algorithm  = algorithm
        self.inputmode = inputmode
        self.scope = scope

class GeneCodisParamsSchema(Schema):
    organism = fields.Integer(required=True)
    annotations = fields.List(fields.Str(),required=True)
    input = fields.Dict(keys=fields.Str(),values=fields.List(fields.Str()),required=True)
    inputtype = fields.Str(default='genes')
    inputNames = fields.Dict(keys=fields.Str(),values=fields.Str(),required=True)
    universe = fields.List(fields.Str())
    inputSupport = fields.Integer(default=10)
    email = fields.Str()
    jobName = fields.Str()
    gc4uid = fields.Str()
    stat = fields.Str()
    algorithm = fields.Str()
    coannotation = fields.Str(default='coannotation_yes')
    inputmode = fields.Str()
    scope = fields.Str()

    @pre_load
    def refineParams(self, in_data,**kwargs):
        print("Pre Load Params")
        print(in_data)
        return(in_data)

    @post_load
    def getParams(self, in_data,**kwargs):
        print("Post Load Params")
        print(in_data)
        return GeneCodisParams(**in_data)

    def checkValidType(self, in_data,**kwargs):
        checked=True
        inputtype=in_data['inputtype']
        types=['genes','tfs','cpgs','mirnas']
        if inputtype not in types:
            checked=False
        print("Valid input type:",checked)
        return(checked)
    
    def checkValidOrg(self,in_data,**kwargs):
        checked=True
        orgid=in_data['organism']  
        orgsnames=["Mus musculus","Danio rerio","Drosophila melanogaster","Rattus norvegicus","Sus scrofa","Bos taurus","Caenorhabditis elegans","Canis familiaris","Gallus gallus","Arabidopsis thaliana","Oryza sativa","Saccharomyces cerevisiae","Escherichia coli","Homo sapiens"]        
        orgscodes=[10090,7955,7227,10116,9823,9913,6239,9615,9031,3702,39947,559292,511145,9606]
        if isinstance(orgid,str):
            if orgid not in orgsnames:
                checked=False
        if isinstance(orgid,int):
            if orgid not in orgscodes:
                checked=False
        print("Valid org:",checked)
        return(checked)
    
    def checkValidAnot(self,in_data,**kwargs):
        checked=True
        annots=in_data['annotations']
        if len(annots)==0:
            checked=False
        annotsDB=['BioPlanet','GO_BP','GO_CC','GO_COVID','GO_MF','KEGG','MGI','Panther','Reactome','WikiPathways','DoRothEA','miRTarBase','HMDD_v3','MNDR','TAM_2','CTD','LINCS','PharmGKB','DisGeNET','HPO','OMIM']
        for myann in annots:
            if myann not in annotsDB:
                checked=False
        print("check valid annotations:",checked)
        return(checked)

    def checkInputTypes(self, in_data,**kwargs):
        checked=True
        inputtype=in_data['inputtype']
        orgid=in_data['organism']
        
        if orgid==10090 and inputtype=='cpgs':
            checked=False

        if orgid in [7955,7227,10116,9823]:
            if inputtype=='tfs' or inputtype=='cpgs':
                checked=False
        
        if orgid in [9913,6239,9615,9031,3702,39947,559292,227321,511145,237561]:
            if inputtype=='tfs' or inputtype=='cpgs' or inputtype=='mirnas':
                checked=False

        print("checkInputTypes:",checked)
        return(checked)

    def checkAnnotsByInput(self, in_data,**kwargs):
        checked=True
        inputtype=in_data['inputtype']
        orgid=in_data['organism']
        stat=in_data['stat']
        annots=in_data['annotations']
        anots=['MNDR','TAM_2','HMDD_v3']
        if inputtype=='genes' or inputtype=='tfs' or inputtype=='cpgs' or stat=='wallenius' :
            if any(ele in anots for ele in annots)==True:
                checked=False
            if inputtype=='tfs' and ('DoRothEA' in annots):
                checked=False
        if inputtype=='mirnas' :
            if 'miRTarBase' in annots:
                checked=False
            if stat=='wallenius' and any(ele in anots for ele in annots)==True:
                checked=False
        print("checkAnnotsByInput:",checked)
        return(checked)

    def checkAnnotsByOrg(self, in_data,**kwargs):
        checked=True
        inputtype=in_data['inputtype']
        orgid=in_data['organism']
        stat=in_data['stat']
        annots=in_data['annotations']
        if orgid==3702 and any(ele in ['BioPlanet','GO_COVID','MGI','Reactome','DoRothEA','miRTarBase','HMDD_v3','MNDR','TAM_2','CTD','LINCS','PharmGKB','DisGeNET','HPO','OMIM']for ele in annots):
            checked=False
        if orgid==6239 and any(ele in ['BioPlanet','GO_COVID','IMG','DoRothEA','miRTarBase','HMDD_v3','MNDR','TAM_2' ,'LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False
        if orgid==7227 and any(ele in ['BioPlanet','GO_COVID','MGI','DoRothEA','HMDD_v3','MNDR','TAM_2' ,'LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False
        if orgid==7955 and any(ele in ['BioPlanet','GO_COVID','DoRothEA' or'HMDD_v3','MNDR','TAM_2' ,'LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False
        if orgid==9031 and any(ele in ['BioPlanet','GO_COVID','MGI','DoRothEA','miRTarBase','HMDD_v3','MNDR','TAM_2','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False
        
        if orgid==9615 and any(ele in ['BioPlanet','GO_COVID','MGI','DoRothEA','miRTarBase','HMDD_v3','MNDR','TAM_2','CTD','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False

        if orgid==9823 and inputtype=='genes' and any(ele in ['BioPlanet','GO_COVID','MGI','Panther','WikiPathways','DoRothEA','miRTarBase','HMDD_v3','MNDR','TAM_2','CTD','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False
        if orgid==9823 and inputtype=='mirnas' and any(ele in ['BioPlanet','GO_BP','GO_CC','GO_COVID','GO_MF','KEGG','MGI','Panther','Reactome','WikiPathways','DoRothEA','miRTarBase','HMDD_v3','TAM_2','CTD','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False

        if orgid==9913 and any(ele in ['BioPlanet','GO_COVID','MGI','DoRothEA','miRTarBase','HMDD_v3','MNDR','TAM_2','CTD','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False

        if orgid==10090 and  inputtype=='genes' and any(ele in ['BioPlanet','GO_COVID','HMDD_v3','MNDR','TAM_2','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False
        if orgid==10090 and  inputtype=='tfs' and any(ele in ['BioPlanet','GO_COVID','DoRothEA','HMDD_v3','MNDR','TAM_2','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False
        if orgid==10090 and  inputtype=='mirnas' and any(ele in ['BioPlanet','GO_COVID','miRTarBase','TAM_2','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False

        if orgid==10116 and  inputtype=='genes' and any(ele in ['BioPlanet','GO_COVID','DoRothEA','HMDD_v3','MNDR','TAM_2','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False
        if orgid==10116 and  inputtype=='mirnas' and any(ele in ['BioPlanet','GO_COVID','DoRothEA','miRTarBase','HMDD_v3','TAM_2','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False

        if orgid==39947 and any(ele in ['BioPlanet','GO_COVID','MGI','Panther','Reactome','WikiPathways','DoRothEA','miRTarBase','HMDD_v3','TAM_2','CTD','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False
        if orgid==511145 and any(ele in ['BioPlanet','GO_COVID','MGI','Reactome','WikiPathways','DoRothEA','miRTarBase','HMDD_v3','TAM_2','CTD','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False
        if orgid==559292 and any(ele in ['BioPlanet','GO_COVID','MGI','DoRothEA','miRTarBase','HMDD_v3','TAM_2','CTD','LINCS','PharmGKB','DisGeNET','HPO','OMIM'] for ele in annots):
            checked=False
        
        print("checkAnnotsByOrg:",checked)
        return(checked)
    
    def checkEmail(self, in_data,**kwargs):
        checked=False
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if in_data['email']!='':
            if(re.fullmatch(regex, in_data['email'])):
                checked=True
        else:
            checked=True
        print("checkEmail:",checked)
        return(checked)
        
    def checkStat(self,in_data,**kwargs):
        checked=True
        stats=['hypergeom','wallenius']
        stat=in_data['stat']
        if stat not in stats:
            checked=False
        print("check valid stat:",checked)
        return(checked)

    def checkScope(self,in_data,**kwargs):
        checked=True
        scopes=['whole','annotated']
        scope=in_data['scope']
        if scope not in scopes:
            checked=False
        print("check valid scope:",checked)
        return(checked)

    def checkCoAlg(self,in_data,**kwargs):
        checked=True
        algs=['fpmax','fpgrowth']
        alg=in_data['algorithm']
        if alg not in algs:
            checked=False
        print("check valid coannotation algorithm:",checked)
        return(checked)

    def checkinputsupport(self,in_data,**kwargs):
        checked=True
        minimum=in_data['inputSupport']
        if isinstance(minimum,float)==False and isinstance(minimum,int)==False:
            checked=False
        else:
            if minimum<0 or minimum>100:
                checked=False
        print("check input support:",checked)
        return(checked)
    
    def checkManyInputs(self,in_data,**kwargs):
        checked=True
        inputs=len(in_data['input'])
        names=len(in_data['inputNames'])
        if inputs>2 or names>2:
            checked=False
        if inputs!=names:
            checked=False
        if inputs<1 or names<1:
            checked=False
        print("check valid number of inputs:",checked)
        return(checked)
    
    def checkCoannot(self,in_data,**kwargs):
        checked=True
        coanot=in_data['coannotation']
        if coanot not in ["yes","no"]:
            checked=False
        print("check valid coannotation value:",checked)
        return(checked)

    def checklenwithcoanot(self,in_data,**kwargs):
        checked=True
        coanot=in_data['coannotation']
        annots=in_data['annotations']
        if coanot=="yes" and len(annots)>2:
            checked=False
        print("check valid input annotations with coannotation:",checked)
        return(checked)




