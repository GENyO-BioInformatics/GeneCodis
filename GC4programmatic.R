library(httr)
library(jsonlite)
library(RCurl)
#change to your GC$libR.R location
source("~/Desktop/GeneCodis4.0/GC4libR.R")

# some Examples 

#resultado2 <- queryGenes(c("JAG1","JAG2"),c("9606","9913"),c("kegg","wikipathways"))
# resultado <- launchAnalysis(organism = "Homo sapiens",
#                             inputType = "mirnas",
#                             inputQuery = c("hsa-mir-133a-1","hsa-miR-133a-3p","hsa-miR-133a-5p","hsa-mir-133a-2","hsa-mir-133b"),
#                             secondInputQuery = c("hsa-mir-133a-1","hsa-miR-133a-3p","hsa-miR-133a-5p","hsa-miR-212-5p","hsa-mir-208a","hsa-miR-208a-5p","hsa-miR-208a-3p"),
#                             annotationsDBs = c("KEGG","Reactome","BioPlanet","GO_BP","GO_CC"),
#                             inputCoannotation = "no",
#                             inputName1 = "prueba1",
#                             inputName2 = "prueba2",
#                             universeScope = "annotated",
#                             enrichmentStat = "wallenius",
#                             inputEmail = "",
#                             coannotationAlgorithm = "fpgrowth")
resultado <- launchAnalysis(organism = "Homo sapiens",
                            inputType = "tfs",
                            inputQuery = c("STAT2","IRF9"),
                            annotationsDBs = c("KEGG","Reactome","BioPlanet"),
                            inputCoannotation = "coannotation_yes",
                            inputName1 = "prueba1",
                            universeScope = "annotated",
                            enrichmentStat = "wallenius",
                            inputEmail = "",
                            coannotationAlgorithm = "fpgrowth")
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
# resultado <- launchAnalysis(organism = "Homo sapiens",
#                             inputType = "genes",
#                             inputQuery = c('dgerfgedgfgfd'),
#                             annotationsDBs = c("GO_CC","GO_BP"),
#                             outputType = "dataframe",
#                             inputCoannotation = "yes",
#                             inputName1 = "prueba1",
#                             universeScope = "annotated",
#                             enrichmentStat = "hypergeom",
#                             inputEmail = "",
#                             coannotationAlgorithm = "fpgrowth")
