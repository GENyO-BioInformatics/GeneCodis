library(dorothea)

data(dorothea_hs, package = "dorothea")
data(dorothea_mm, package = "dorothea")

dorothea_hs$org = "9606"
dorothea_mm$org = "10090"

filter_and_write <- function(dorothea_table,confidence){
  dorothea_table = dorothea_table[dorothea_table$confidence <= confidence,c(1,3,5)]
  org = unique(dorothea_table$org)
  filename = paste0("data/",org,"_dorothea.tsv")
  write.table(dorothea_table,filename,sep="\t",row.names = F,quote = F)
}

filter_and_write(dorothea_hs,"A")
filter_and_write(dorothea_mm,"A")
