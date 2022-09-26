# -*- coding: utf-8 -*-
#!/usr/bin/python

from lib.gc4DBHandler import *


#### Example 1 Single List. Human. 2 Annotation. Genes not TFs. With synonyms and false names. Whole Universe ####
organism_id = "9606"
universe = []
annotations = ["CTD","KEGG"]
jobDir = 'examples/job_single_list/'
input = {'input':["APOH","APP","COL3A1","COL5A2","CXCL6","FGFR1","FSTL1","ITGAV","JAG1","JAG2","KCNJ8","LPL","LRPAP1","LUM","MSX1","NRP1","OLR1","PDGFA","PF4","PGLYRP1","POSTN","PRG2","PTK2","S100A4","SERPINA5","SLCO2A1","SPP1","STC1","THBD","TIMP1","TNFRSF21","VAV2","VCAN","VEGFA","VTN"]}
inputNames = {'input1unique':'Example_1'}
flag_TFs="genes"
inputtype = "genes"
coannotation = True
stat = "wallenius"
out_dictionary = checkNgenerate(input,organism_id,universe,annotations,jobDir,inputtype,inputNames,coannotation,stat)

organism_id = "9606"
universe = []
annotations = ["CTD","KEGG"]
jobDir = 'examples/job_mirna/'
input = {'input':["hsa-mir-181a-2","hsa-mir-181a-1","hsa-miR-181a-5p","hsa-miR-181a-3p"]}
inputNames = {'input1unique':'Example_1'}
flag_TFs="genes"
inputtype = "mirnas"
coannotation = True
stat = "wallenius"
out_dictionary = checkNgenerate(input,organism_id,universe,annotations,jobDir,inputtype,inputNames,coannotation,stat)
