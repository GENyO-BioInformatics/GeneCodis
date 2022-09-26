# GeneCodis4.0 Data Base

This repository has the functions and dependencies to build and use the database of GeneCodis and generate the engene-format file.  

## 1. Build Database

In the repository [maintenance](maintenance/) you can find the information related to build the database.

## 2. Engene-format File

When users insert the input variables in GeneCodis, we convert these values to a file named engene in wich we collect the information of all annotations by gene and the gene introduced by the user. It consists on three columns that are:
  1. **Internal ID of the gene** whose characters are GC-tax_id-XXXX
  2. **Annotations associated** separated by commas
  3. **0 / GeneSymbol == ausence / presence in our input**

Each *engene* is specific of each job and there are as many jobs as annotations are selected plus one to perform the modular enrichment.

You can find some examples of engene-format files in [examples](examples/) directory.

## 3. Generate Engene-format File

All required functions to generate engene-format file are located in [lib/gc4DBHandler.py](lib/gc4DBHandler.py) directory. These functions are used in the module [gc4app](../gc4app) and there you can find information of how use them.

However, we provided a script named (queries_examples.py)[queries_examples.py] where you can generate engene-format files in local without running GeneCodis4.

The input variables are the following:

```python

organism_id = "9606" # tax identifier, ie 9606 is human
universe = [] # universe used. Empty if we want to use the whole universe, in the other case, insert a list of elements
annotations = ["CTD","KEGG"] # List of annotations
jobDir = 'examples/job_single_list/' # Dir to save the engenes

# List of input genes
input = {'input':["APOH","APP","COL3A1","COL5A2","CXCL6","FGFR1","FSTL1","ITGAV","JAG1","JAG2","KCNJ8","LPL","LRPAP1","LUM","MSX1","NRP1","OLR1","PDGFA","PF4","PGLYRP1","POSTN","PRG2","PTK2","S100A4","SERPINA5","SLCO2A1","SPP1","STC1","THBD","TIMP1","TNFRSF21","VAV2","VCAN","VEGFA","VTN"]}

inputNames = {'input1unique':'Example_1'}
#Select if genes are treat as genes ir TFs
flag_TFs="genes"
#Select if the input are genes, mirnas or cpgs
inputtype = "genes"
# Indicate if you would like to do coannotation
coannotation = True
# Indicate the statistical method (wallenius or hypergeom)
stat = "wallenius"

# Run this function that generate the engene-format file
out_dictionary = checkNgenerate(input,organism_id,universe,annotations,jobDir,inputtype,inputNames,coannotation,stat)
```

checkNgenerate function apply two different steps: first we check the input and them we generate the engene.

### 3.1. Checking Functions

In this section we built some functions in order to correct and extract invalid input information. Genes, annotations and universe are evaluated and corrected.

This function returns three object.

* The corrected list of input values
* The corrected list of universe in case of user add a universe list

```python
## input variables ##
input = {'input':["APOH","APP","COL3A1","COL5A2","ham","letter","badname"]}
organism_id = "9606"
universe = ["APOH","APP","COL3A1","COL5A2","CXCL6","FGFR1","FSTL1","ITGAV","JAG1","JAG2","KCNJ8","LPL","LRPAP1","LUM","MSX1","NRP1","OLR1","PDGFA","PF4","PGLYRP1","POSTN","PRG2","PTK2","S100A4","SERPINA5","SLCO2A1","SPP1","STC1","THBD","TIMP1","TNFRSF21","VAV2","VCAN","VEGFA","VTN"]

# Output of checking module
# GC identifiers are used always as key in the dictionaries

stats
{'input1unique': {'input': [{'GC-9606-15316': 'APOH'},
   {'GC-9606-29187': 'COL5A2'},
   {'GC-9606-29207': 'COL3A1'},
   {'GC-9606-30360': 'APP'}],
  'invalidInput': ['ham', 'letter', 'bad_name'],
  'inputName': 'Example_1',
  'mirnatargets': {}}}

  universe

['GC-9606-10413','GC-9606-38712','GC-9606-16875','GC-9606-38044','GC-9606-4332','GC-9606-5722','GC-9606-20678','GC-9606-9989','GC-9606-10808','GC-9606-15189','GC-9606-32030','GC-9606-32036','GC-9606-22553','GC-9606-37974','GC-9606-41977','GC-9606-3663','GC-9606-2084','GC-9606-4415','GC-9606-26525','GC-9606-10774','GC-9606-22461','GC-9606-32133','GC-9606-3587','GC-9606-4246','GC-9606-15316','GC-9606-24686','GC-9606-29207','GC-9606-25384','GC-9606-1847','GC-9606-29187','GC-9606-12497','GC-9606-30175','GC-9606-40031','GC-9606-13507','GC-9606-30360']
```

#### 3.2. Querying Functions

In this section we built some functions in order to run queries to database and generate engene-format file. The main function is generate_engene that takes some information from input and processed by checking section.

```python
final_result
{'examples/job_single_list/engene-Example_1-CoAnnotation': {'annotation': ['CTD',
   'KEGG'],
  'noAnnotated': [],
  'universe': ['S100A4','POSTN','FSTL1','FGFR1','PF4','SPP1','APOH','SERPINA5','VAV2','VEGFA','JAG1','JAG2','STC1','KCNJ8','OLR1','LRPAP1','COL5A2','COL3A1','MSX1','APP','NRP1','VCAN','ITGAV','SLCO2A1','PTK2','TNFRSF21','PDGFA','TIMP1','LPL','THBD','PRG2','LUM','PGLYRP1','VTN','CXCL6'],
  'annotated': ['APOH', 'COL5A2', 'COL3A1', 'APP'],
  'coannot': True},
 'examples/job_single_list/engene-Example_1-CTD': {'annotation': 'CTD',
  'noAnnotated': [],
  'universe': ['S100A4','POSTN','FSTL1','FGFR1','PF4','SPP1','APOH','SERPINA5','VAV2','VEGFA','JAG1','JAG2','STC1','KCNJ8','OLR1','LRPAP1','COL5A2','COL3A1','MSX1','APP','NRP1','VCAN','ITGAV','SLCO2A1','PTK2','TNFRSF21','PDGFA','TIMP1','LPL','THBD','PRG2','LUM','PGLYRP1','VTN','CXCL6'],
  'annotated': ['APOH', 'COL5A2', 'COL3A1', 'APP'],
  'coannot': False},
 'examples/job_single_list/engene-Example_1-KEGG': {'annotation': 'KEGG',
  'noAnnotated': [],
  'universe': ['S100A4','POSTN','FSTL1','FGFR1','PF4','SPP1','APOH','SERPINA5','VAV2','VEGFA','JAG1','JAG2','STC1','KCNJ8','OLR1','LRPAP1','COL5A2','COL3A1','MSX1','APP','NRP1','VCAN','ITGAV','SLCO2A1','PTK2','TNFRSF21','PDGFA','TIMP1','LPL','THBD','PRG2','LUM','PGLYRP1','VTN','CXCL6'],
  'annotated': ['APOH', 'COL5A2', 'COL3A1', 'APP'],
  'coannot': False}}
```

Also engene files are generated in the corresponding directory


#### 3.3. Final Result

After merging the two dictionaries obtained from checking and generate_engene we obtained this scheme:

```python
out_dictionary
{'input1unique': {'engenes': {'examples/job_single_list/engene-Example_1-CoAnnotation': {'annotation': ['CTD',
     'KEGG'],
    'noAnnotated': [],
    'universe': 35,
    'annotated': ['APOH', 'COL5A2', 'COL3A1', 'APP'],
    'coannot': True,
    'mirnatargets': {}},
   'examples/job_single_list/engene-Example_1-CTD': {'annotation': 'CTD',
    'noAnnotated': [],
    'universe': 35,
    'annotated': ['APOH', 'COL5A2', 'COL3A1', 'APP'],
    'coannot': False,
    'mirnatargets': {}},
   'examples/job_single_list/engene-Example_1-KEGG': {'annotation': 'KEGG',
    'noAnnotated': [],
    'universe': 29,
    'annotated': ['APOH', 'COL5A2', 'COL3A1', 'APP'],
    'coannot': False,
    'mirnatargets': {}}},
  'notInDB': {'invalidInput': ['ham', 'letter', 'bad_name'],
   'notMapped': [],
   'invalidUniverse': []}},
 'synonyms': {}}
```
