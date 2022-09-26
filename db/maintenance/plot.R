genes = read.delim("raw_sql/gene_table.tsv",stringsAsFactors = F)
annotation = read.delim("raw_sql/annotation_table.tsv",stringsAsFactors = F)
organisms = read.delim("raw_sql/taxonomy_table.tsv",stringsAsFactors = F)
genes = merge(x=genes,y=organisms,by.x = "organism",by.y = "taxonomy_id")
organisms = as.character(unique(genes$output_name))
annotation$annotation_source = gsub("_"," ",annotation$annotation_source)
annotationSource = unique(annotation$annotation_source)
annotationSource <- annotationSource[!annotationSource %in% c("cpgs")]
annotation_type = data.frame(Ann=c("GO BP", "GO CC","GO MF","KEGG","MGI","Reactome","WikiPathways","Panther",
                                   "DoRothEA","miRTarBase","MNDR","TAM 2", "HMDD v3",
                                   "CTD","HPO","OMIM","LINCS","PharmGKB"),
                             Type = c(rep("Functional",8),rep("Regulatory",5),rep("Perturbation",5)))

library(reshape)
library(ggplot2)
library(grid)
organism = "Homo sapiens"
for (organism in organisms){
  orgGenes = genes[genes$output_name == organism,"id"]
  universe = annotation[annotation$id %in% orgGenes,]
  universeLength = length(unique(universe$id))
  orgGenesLength = length(unique(orgGenes))
  statsData = data.frame(matrix(nrow = 0,ncol = 3))
  colnames(statsData) = c("ann","count","type")
  for (ann in annotationSource){
    type = annotation_type[annotation_type$Ann == ann,"Type"]
    annotatedGenes = length(unique(universe[universe$annotation_source == ann,"id"]))
    statsData = rbind(statsData,data.frame(ann=ann,count=annotatedGenes,type=type))
  }
  statsData[statsData$count == 0,"count"] = NA
  statsData = na.omit(statsData)
  facet_strip_color = c("#C1D13A","#2B9A58","#B83369")
  
  statsData$count = statsData$count / orgGenesLength
  
  genSp <- unlist(strsplit(organism,split = ' '))
  spname <- paste0(substring(genSp[1],1,1),'. ',genSp[2])
  ############################ PLOT ######################################
  ggplot(data = statsData, aes(x=ann,y=count))+
    geom_bar(stat="identity",fill="gray",width=1)+
    facet_grid(cols = vars(type),scales = "free",space = "free")+
    theme_bw()+
    geom_hline(yintercept=universeLength / orgGenesLength, 
               color = "#005322", size=2)+
    theme(plot.title = element_text(face = "italic"),
          text=element_text(size=9, family = "serif"),axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1),
          panel.background = element_rect(fill = "transparent"), # bg of the panel
          plot.background = element_rect(fill = "transparent", color = NA))+
    scale_y_continuous(limits=c(0,1))+
    labs(title = paste0(spname), x = element_blank(), y = element_blank())
  autowidth = 0.6 * length(statsData$count)
  ggsave(filename = paste0(organism,"_prop_genes.svg"),bg = "transparent", width = autowidth, height = 8, units = 'cm')
}
