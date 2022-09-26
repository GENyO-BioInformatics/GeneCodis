from marshmallow import Schema,fields,ValidationError,pre_load,post_load

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
