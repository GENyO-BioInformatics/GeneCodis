# GC4 JSONs WorkFlow

## 1 Parameters

```js
##### Single
{
    "email": "correo@correo.com",
    "inputSupport": [1-100],
    "inputtype": "genes|tfs",
    "pvalCorrection": "fdr|permutations|none",
    "test": ["hypergeometric","chiSquare"],
    "organism": "...",
    "annotations": ["..."],
    "universe": ["..."],
    "input": {
        "input": ["..."]
    },
    "jobName": "jobName",
    "inputNames": {
        "input": "inputName" # jobName
    }
}
##### Comparative (specifics)
{   
    "input": {
        "input": ["..."],
        "input2": ["..."]
    },
    "inputNames": {
        "input": "inputName",
        "input2": "input2Name"
    }
}
```
## 2 Generate engenes
```js
##### Single
{  
    "input1unique":
    {
    "engenes":{
        jobdir+"/engene_inputName_coAnnotation": {
            "annotation": [>2],
            "noAnnotated": ["..."], # input genes not here, in coannot will be  empty
            "universe": 0-9+|["..."], # user list or number of the universe
            "annotated": ["..."], # valid input
            "coannot": True # flag
        },
        jobdir+"/engene_inputName_annot1": {
            "annotation": "annot1",
            "coannot": False,  
            [...]
        },
        jobdir+"/engene_inputName_annot2": {
            "annotation": "annot2",
            [...]
        },
    },
    "notInDB":{
        "invalidInput":["..."], # input not in our db
        "notMapped":["..."], # annots selected but with 0 input associated
        "invalidUniverse":["..."] # input universe not in our db
      }
    },
    "synonyms":{...} # input genes that are the same, do not generate if NONE
 }
#### Comparative (specifics)
{  
    "input1unique":{
        "engenes":{
            jobdir+"/engene_inputName_coAnnotation": {...}, # same as in single
            jobdir+"/engene_inputName_annot1": {...},
            jobdir+"/engene_inputName_annot2": {...}
        },
        "notInDB":{...}
    },  
    "input2unique":{
        "engenes":{
            jobdir+"/engene_input2Name_coAnnotation": {...},
            jobdir+"/engene_input2Name_annot1": {...},
            jobdir+"/engene_input2Name_annot2": {...}
        },
        "notInDB":{...}
    },  
    "common":{
        "engenes":{
            jobdir+"/engene_inputName&input2Name_coAnnotation": {...},
            jobdir+"/engene_inputName&input2Name_annot1": {...},
            jobdir+"/engene_inputName&input2Name_annot2": {...}
        },
        "notInDB":{...}
    },
    "synonyms":{...}
}
##### WARNINGS
    # If all the input or universe is invalid
{  
    "input1unique":
    {
        "engenes":{}, # empty dict
        "notInDB":{...} # here we expect to found all the input
    }
}        
```
