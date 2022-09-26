library(httr)
library(jsonlite)
library(RCurl)
httr::set_config(config(ssl_verifypeer = 0L))

#URL base for GeneCodis
urlBase = "https://genecodis.genyo.es/gc4/"
#Message to show with invalid commons comparison
invalidCommons = "The input provided is not associated to the selected annotations or in case of comparative analysis there are not uniques or commons genes in the resulting list."

#function to validate email
isValidEmail <- function(x) {
  grepl("\\<[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\>", as.character(x), ignore.case=TRUE)
}

#function to create a gc4uid
createJob <- function(){
  #define URL to create gc4uid
  createjobURL = paste0(urlBase,"createjob")
  #make request to GeneCodis
  request = GET(createjobURL)
  #check if error ocurrs and stop execution
  warn_for_status(request)
  stop_for_status(request)
  #get content of request
  print(paste0("Created job:",content(request)))
  return(content(request))
}

#function to check the job status: PENDING, FAILURE, SUCCESS
checkState <- function(gc4uid){
  #define URL to check state
  stateURL = paste0(urlBase,"checkstate/job=",gc4uid)
  #print(paste0("Checking state with URL=",stateURL))
  #make request to GeneCodis
  request = GET(stateURL)
  #check if error happens and stop execution
  warn_for_status(request)
  stop_for_status(request)
  #get content of request
  request_content=content(request,"parsed")
  #check if request is giving correct job
  if(typeof(request_content)!="list"){
    stop("Server error, gc4uid not found")
  }else{
    #return state of job
    return(request_content$state)  
  }
}

#function to check if the input is not valid
checkInvalidInput <- function(gc4uid){
  #define URL to check status
  stateURL = paste0(urlBase,"job=",gc4uid)
  #make request to GeneCodis
  request = GET(stateURL)
  #check if error happens and stop execution
  warn_for_status(request)
  stop_for_status(request)
  #get content of request
  request_content=content(request,"text")
  #check if input is invalid
  presence=FALSE
  if(length(grep("invalid input list",request_content))>0){
    presence=TRUE
  }
  return(presence)
}

#function to check if unexpected error happened
checkErrorStatus <- function(gc4uid){
  #define URL to check serror
  stateURL = paste0(urlBase,"job=",gc4uid)
  #make request to GeneCodis
  request = GET(stateURL)
  #check if error happens and stop execution
  warn_for_status(request)
  stop_for_status(request)
  #get content of request
  request_content=content(request,"text")
  #check if unexpected error happened
  presence=FALSE
  if(length(grep("unexpected",request_content))>0){
    presence=TRUE
  }
  return(presence)
}

#function to launch analysis
launchAnalysis <- function(organism,inputType,inputQuery,annotationsDBs,enrichmentStat="hypergeom",
                           universeScope="annotated",inputCoannotation="no",coannotationAlgorithm="fpgrowth",minimalInputCoannotation=10,
                           secondInputQuery=list(),inputName1="input1",inputName2="input2",customUniverse=list(),inputEmail="",ReportName="input1",
                           outputType="dataframe"){
  #check organism code
  if(organism=="Homo sapiens"){
    organismCode=9606
  }else if(organism=="Caenorhabditis elegans"){
    organismCode=6239
  }else if(organism=="Canis familiaris"){
    organismCode=9615 
  }else if(organism=="Danio rerio"){
    organismCode=7955
  }else if(organism=="Drosophila melanogaster"){
    organismCode=7227
  }else if(organism=="Gallus gallus"){
    organismCode=9031
  }else if(organism=="Bos taurus"){
    organismCode=9913
  }else if(organism=="Mus musculus"){
    organismCode=10090
  }else if(organism=="Rattus norvegicus"){
    organismCode=10116
  }else if(organism=="Sus scrofa"){
    organismCode=9823
  }else if(organism=="Arabidopsis thaliana"){
    organismCode=3702
  }else if(organism=="Oryza sativa"){
    organismCode=39947
  }else if(organism=="Saccharomyces cerevisiae"){
    organismCode=559292
  }else if(organism=="Escherichia coli"){
    organismCode=511145
  }else{
    stop("Input error, organism not found.")
  }
  
  #check output type
  outputTypes=c("dataframe","text")
  if((outputType %in% outputTypes)==FALSE){
    stop("Input error, output type must be 'dataframe' or 'text'.")
  }
  #check input type
  inputTypes=c("genes","tfs","cpgs","mirnas")
  if((inputType %in% inputTypes)==FALSE){
    stop("Input error, input type value must be 'genes','tfs','cpgs' or 'mirnas'.")
  }
  #check enrichment stat
  enrichmentStats=c("hypergeom","wallenius")
  if((enrichmentStat %in% enrichmentStats)==FALSE){
    stop("Input error, enrichment stat method must be 'hypergeom' or 'wallenius'.")
  }
  #check scope
  scopes=c("annotated","whole")
  if((universeScope %in% scopes)==FALSE){
    stop("Input error, universe scope value must be 'annotated' or 'whole.")
  }
  #check coannotation algorithm
  coanalgs=c("fpgrowth","fpmax")
  if((coannotationAlgorithm %in% coanalgs)==FALSE){
    stop("Input error, coannotation algorithm must be 'fpgrowth' or 'fpmax'.")
  }
  #check minimalInputCoannotation
  if(typeof(minimalInputCoannotation)!="double"){
    stop("Input error, minimal input coannotation value must be of type double.")
  }else{
    #check decimal part of minimalInputCoannotation
    if(length(unlist(lapply(strsplit(as.character(minimalInputCoannotation), ''), function(x) which(x == '.'))))!=0){
      decimalPart=nchar(minimalInputCoannotation)-unlist(lapply(strsplit(as.character(minimalInputCoannotation), ''), function(x) which(x == '.')))
      if(decimalPart>1){
        stop("Input error, decimal part of minimal input coannotation value must be at most 1.")
      }
    }
  }
  
  #check if the input query has length 1
  if(length(inputQuery)==1){
    inputQuery=list(inputQuery,"")
    inputQuery[[-1]]<-NULL
  }
  
  #check if the annotationsDBs has length 1
  if(length(annotationsDBs)==1){
    annotationsDBs=list(annotationsDBs,"")
    annotationsDBs[[-1]]<-NULL
  }
  
  #check input universe
  if(length(customUniverse)==1){
    customUniverse=list(customUniverse,"")
    customUniverse[[-1]]<-NULL
  }
  
  #check number of inputs
  #only one input 
  if (length(secondInputQuery)==0){
    #raise error if there is name for second list but not the list
    if(inputName2!="input2"){
      stop("Input error, second input list not provided.")
    }else{
      inputToQuerty=list(input=(inputQuery))
      inputNames=list(input1unique=inputName1)
    }
  }else{
    #two inputs
    #check if the second input query has length 1
    if(length(secondInputQuery)==1){
      secondInputQuery=list(secondInputQuery,"")
      secondInputQuery[[-1]]<-NULL
    }
    inputToQuerty=list(input=(inputQuery),input2=(secondInputQuery))
    inputNames=list(input=inputName1, input2=inputName2)
  }
  
  #check if coannotation
  if (inputCoannotation=="no"){
    coannotation="coannotation_no"
  }else if (inputCoannotation=="yes"){
    coannotation="coannotation_yes"
  }else{
    stop("Input error, coannotation value must be 'yes' or 'no'.")
  }
  
  #check email
  if(!isValidEmail(inputEmail)&&inputEmail!=""){
    stop("Input error, the email entered is not valid.")
  }
  
  
  #create list of params
  # params <- list(inputmode = unbox("on"),
  #                email = unbox(inputEmail),
  #                inputSupport = unbox(minimalInputCoannotation),
  #                input = inputToQuerty,
  #                jobName= unbox(ReportName),
  #                annotations = (annotationsDBs),
  #                stat = unbox(enrichmentStat),
  #                scope = unbox(universeScope),
  #                algorithm = unbox(coannotationAlgorithm),
  #                inputNames = inputNames,
  #                inputtype = unbox(inputType),
  #                organism = unbox(organismCode),
  #                universe = list(),
  #                gc4uid = unbox(createJob()),
  #                coannotation = unbox(coannotation))
  params <- list(inputmode = "on",
                 email = inputEmail,
                 inputSupport = minimalInputCoannotation,
                 input = inputToQuerty,
                 jobName= ReportName,
                 annotations = annotationsDBs,
                 stat = enrichmentStat,
                 scope = universeScope,
                 algorithm = coannotationAlgorithm,
                 inputNames = inputNames,
                 inputtype = inputType,
                 organism = organismCode,
                 universe = customUniverse,
                 gc4uid = createJob(),
                 coannotation = coannotation)
  #convert list of params to json
  jsonparams <- jsonlite::toJSON(params,auto_unbox=T,pretty = F)
  
  #define URL to make request
  requestJobURL = paste0(urlBase,"analysis")
  #make request to GeneCodis
  request<-httr::POST(url = requestJobURL, body=jsonparams, encode="json", content_type("application/json"))
  print('Got analysis petition')
  print('Performing the analyses...')
  #check if analysis has finished
  while(checkState(params$gc4uid)!="SUCCESS"){
    #check invalid input
    if(checkInvalidInput(params$gc4uid)==TRUE){
      stop("It seems that you have provided an invalid input list. It could be also possible that the input does not match the selected organism or that we have no record of those in our database associated to the selected annotations. Sorry the inconveniences. Please go to the Help tab and check the allowed ids.")
    }
    #check unexpected error
    if(checkErrorStatus(params$gc4uid)==TRUE){
      stop(paste0("Please send the job ticket, ",params$gc4uid," to bioinfo@genyo.es, the server found an unexpected error. We will solve it as soon as possible."))
    }
    if(checkState(params$gc4uid)=="SUCCESS"){
      break
    }
  }
  print('Analysis finished')
  print('Generating results...')
  #make request to obtain results
  return(getResults(params,outputType))
}

#funtion to get the quality control of the input
getQualityControl <- function(gc4uid,qcname){
  
  #name to search in order to get quality control
  str_qc=(paste0(qcname,'div'))
  #get quality control url
  qcURL=paste0(urlBase,"job=",gc4uid)
  #get quality control content
  qc_content=httr::content(httr::GET(qcURL),"text")
  #indec of str_qc, always the second ocurrence in html
  str_qc_index=gregexpr(str_qc,qc_content)[[1]][2]
  #delimit search string between str_qc_index and end of html
  str_search=substr(qc_content,str_qc_index,nchar(qc_content))
  #check parameters inside html
  quality_control=list()
  quality_parameters=c("Input not in our database:","Universe not in our database:","Annotations not mapped to input:","Annotation universe:","Annotated input:","No annotated input:")
  #get info about parameters
  for(param in quality_parameters){
    p=getQualityControlClickableParameter(param,str_search)
    quality_control[[param]]=p
  }
  
  #rename data
  quality_parameters=c("Input_not_in_our_database","Universe_not_in_our_database","Annotations_not_mapped_to_input","Annotation_universe","Annotated_input","No_annotated_input")
  names(quality_control) <- quality_parameters
  
  return(quality_control)
}

#function to get quality info from the not clickable quality parameter 
getQualityControlNotClickableParameter <- function(param,text){
  param_info=c()
  #get index of occurrence of the parameter
  param_info=c(param_info,gregexpr(pattern=param,text)[[1]][1])
  #get index of the end of the line of parameter
  param_info=c(param_info,gregexpr("</p>",substr(text,param_info[1],nchar(text)))[[1]][1])
  #get info about the parameter
  param_info=c(param_info,gsub(".*?([0-9]+).*", "\\1", substr(text,param_info[1],param_info[1]+param_info[2])))
  #return as numeric
  return(as.numeric((param_info[3])))
}

#function to get quality info from the not clickable quality parameter 
getQualityControlClickableParameter <- function(param,text){
  param_info=c()
  #get index of occurrence of the parameter
  param_info=c(param_info,gregexpr(pattern=param,text)[[1]][1])
  #get supplementary indexes
  param_info=c(param_info,gregexpr(">",substr(text,param_info[1],nchar(text)))[[1]][1])
  subaux=substr(text,param_info[1],param_info[1]+param_info[2])
  #check if parameter is not clickable
  if(gregexpr("genyoLink",subaux)[[1]][1]==-1){
    #if not clickable call previous function
    return(getQualityControlNotClickableParameter(param,text))
  }else{
    aux_list=list()
    #get supplementary indexes and count number
    param_info=c(param_info,gregexpr("</a>",substr(text,param_info[1],nchar(text)))[[1]][1])
    param_info=c(param_info,gsub(".*?([0-9]+).*", "\\1", substr(text,param_info[1]+param_info[2],param_info[1]+param_info[3])))
    count_number=as.numeric((param_info[4]))
    aux_list["Count"]=count_number
    #get list of annotated
    aux_list["List"]=getInfoList(param_info,text)
    #return number and annotated list
    return(aux_list)
  }
}

#function to get list of genes of quality control variable
getInfoList <- function(param_info,text){
  #find genes in info file
  param_info=c(param_info,gregexpr("genes=",substr(text,param_info[1],nchar(text)))[[1]][1])
  param_info=as.numeric(param_info)
  param_info=c(param_info,gregexpr('\"',substr(text,param_info[1]+param_info[5],param_info[1]+param_info[2]))[[1]][1])
  param_info=as.numeric(param_info)
  #save genes string
  annotated_list=substr(text,param_info[1]+param_info[5]+nchar("genes=")-1,param_info[1]+param_info[5]+param_info[6]-1)
  param_info=as.numeric(param_info)
  #format genes string into list
  annotated_list=gsub('"',"",annotated_list)
  temp=strsplit(annotated_list,split = ",")
  
  return(temp)
}

#function to get results from launched analysis
getResults <- function(params,outputType){
  #define list to store urls
  urls=list()
  #define list to store name of tables
  dicKeys=list()
  #define quality controls result
  quality_controls=list()
  #define stats tables result
  stats_tables=list()
  #define list result
  results=list()
  #add jobID to result
  results["jobID"]=params$gc4uid
  #check if job has one or two inputs
  if(length(params$inputNames)==1){
    for(anot in params$annotations){
      #define url to access results
      strUrl=paste0(params$inputNames$input1unique,"-",anot)
      urlToAdd=paste0(urlBase,"results?job=",params$gc4uid,"&annotation=",strUrl)
      print(urlToAdd)
      #add url to url list
      urls=append(urls,urlToAdd)
      #add name of table to name list
      dicKeys=append(dicKeys,strUrl)
    }
    #check if job has coannotation
    if(params$coannotation=="coannotation_yes"){
      #define url to access results
      strUrl=paste0(params$inputNames$input1unique,"-CoAnnotation-",params$annotations[[1]],"_",params$annotations[[2]])
      urlToAdd=paste0(urlBase,"results?job=",params$gc4uid,"&annotation=",strUrl)
      print(urlToAdd)
      #add url to url list
      urls=append(urls,urlToAdd)
      #add name of table to name list
      dicKeys=append(dicKeys,strUrl)
    }
  }else{
    #if two inputs, define urls for each annotation, uniques and commons
    #first define urls for uniques annotations
    for(input in params$inputNames){
      for(anot in params$annotations){
        #define url to access results
        strUrl=paste0(input,"_uniques-",anot)
        urlToAdd=paste0(urlBase,"results?job=",params$gc4uid,"&annotation=",strUrl)
        print(urlToAdd)
        #add url to url list
        urls=append(urls,urlToAdd)
        #add name of table to name list
        dicKeys=append(dicKeys,strUrl)
      }
    }
    #define urls for commons annotations
    for(anot in params$annotations){
      #define url to access results
      strUrl=paste0(params$inputNames[[1]],"_",params$inputNames[[2]],"_commons-",anot)
      urlToAdd=paste0(urlBase,"results?job=",params$gc4uid,"&annotation=",strUrl)
      print(urlToAdd)
      #add url to url list
      urls=append(urls,urlToAdd)
      #add name of table to name list
      dicKeys=append(dicKeys,strUrl)
    }
    #check if job has coannotation
    if(params$coannotation=="coannotation_yes"){
      #define urls for commons annotations
      strUrl=paste0(params$inputNames[[1]],"_",params$inputNames[[2]],"_commons-CoAnnotation-",params$annotations[[1]],"_",params$annotations[[2]])
      urlToAdd=paste0(urlBase,"results?job=",params$gc4uid,"&annotation=",strUrl)
      print(urlToAdd)
      urls=append(urls,urlToAdd)
      dicKeys=append(dicKeys,strUrl)
      #define urls for uniques coannotations
      strUrl=paste0(params$inputNames[[1]],"_uniques-CoAnnotation-",params$annotations[[1]],"_",params$annotations[[2]])
      urlToAdd=paste0(urlBase,"results?job=",params$gc4uid,"&annotation=",strUrl)
      print(urlToAdd)
      urls=append(urls,urlToAdd)
      dicKeys=append(dicKeys,strUrl)
      
      strUrl=paste0(params$inputNames[[2]],"_uniques-CoAnnotation-",params$annotations[[1]],"_",params$annotations[[2]])
      urlToAdd=paste0(urlBase,"results?job=",params$gc4uid,"&annotation=",strUrl)
      print(urlToAdd)
      urls=append(urls,urlToAdd)
      dicKeys=append(dicKeys,strUrl)
    }
  }
  #make request to GeneCodis to each url
  for(i in 1:length(dicKeys)){
    
    request=httr::GET(urls[[i]])
    #check correct state of the request
    if(status_code(request)!=200){
      #check if request has invalid commons
      if(status_code(request)==404&&grep("commons",urls[[i]])){
        request_content=invalidCommons
      }else{
        #stop execution and show error code
        stop(paste0("Error ",status_code(request)," while obtaining results from ",urls[[i]]))
      }
    }else{
      #get table results
      request_content=httr::content(request,"text") 
      
      
      #add quality control to results
      name_qc=paste0(dicKeys[[i]],"_QualityControl")
      quality_controls[name_qc]=list(getQualityControl(params$gc4uid,dicKeys[[i]]))
    }
    
    #check output type
    if(outputType=="dataframe"){
      #if invalid commons show message instead of table
      if(request_content==invalidCommons){
        table=request_content
      }else{
        #save results table
        table=read.csv(text=request_content,header = TRUE,sep="\t")  
      }
    }else if(outputType=="text"){
      #save results text
      table=request_content  
    }else{
      #save results in dataframe by default
      table=read.csv(text=request_content,header = TRUE,sep="\t")  
    }
    #save elements in results list
    key=dicKeys[[i]]
    stats_tables[[key]]=table
  }
  
  #check email and send results 
  if(params$email!=''){
    print(paste0("Sending results to the email:",params$email))
  }
  #add quality controls and stats tables to results
  results[["quality_controls"]]=quality_controls
  results[["stats_tables"]]=stats_tables
  return(results)
}

#function to recover an existent job
recoverJob <- function(gc4uid,outputType){
  print("Recovering parameters from job...")
  #define url
  recoverURL=paste0(urlBase,"params/job=",gc4uid)
  #make request to genecodis
  request=httr::GET(recoverURL)
  params=httr::content(request,"parsed")
  #get results
  return(getResults(params,outputType))
}

getQualityControl2 <- function(gc4uid){
  qcURL=paste0(urlBase,"qc/job=",gc4uid)
  qcURL=paste0("http://localhost:5000/qc/job=",gc4uid)
  request=httr::GET(qcURL)
  params=httr::content(request,"parsed")
  quality_control=list()
  
  
  return(params)
}

#Ejemplo lanzar analisis
# resultado <- launchAnalysis(organism = "Homo sapiens",
#                             inputType = "genes",
#                             inputQuery = c('APOH','APP','COL3A1','COL5A2','CXCL6','PDGFA','PF4','PGLYRP1','POSTN','PRG2','PTK2','S100A4','SERPINA5','SLCO2A1','SPP1','STC1','THBD','TIMP1','TNFRSF21','VAV2','VCAN','VEGFA','VTN'),
#                             secondInputQuery = c('APOH','APP','COL3A1','COL5A2','CXCL6','FGFR1','FSTL1','ITGAV','JAG1','JAG2','KCNJ8','LPL','LRPAP1','LUM','MSX1','NRP1','OLR1'),
#                             annotationsDBs = c("GO_CC","GO_BP"),
#                             outputType = "dataframe",
#                             inputCoannotation = "yes",
#                             inputName1 = "prueba1",
#                             inputName2 = "prueba2",
#                             universeScope = "annotated",
#                             enrichmentStat = "hypergeom",
#                             inputEmail = "",
#                             coannotationAlgorithm = "fpgrowth")
#Ejemplo recuperar trabajo
# resultado <- recoverJob("qZVyO6Z6aN3Ztg","dataframe")
