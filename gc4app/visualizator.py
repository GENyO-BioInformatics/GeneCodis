# import modin.pandas as pandas
import os,json, math, colorsys, matplotlib, numpy, pandas,re
from flask import Flask, request, render_template
from gc4app.commonthings import *
#from db.lib.gc4DBHandler import *

class GeneCodisResultsReporter:
    def __init__(self,outJobs,synonyms,organism,outDir):
        self.htmlReport = self.generateHTMLreport(outJobs,synonyms,organism,outDir)

    def generateHTMLreport(self,outJobs,synonyms,organism,outDir):
        print("Generating Plots")
        plotArgs = []
        inputs = [input for input in list(outJobs.keys()) if 'engenes' in outJobs[input]]
        for input in inputs:
            for engene in outJobs[input]['engenes']:
                API_URL=os.getenv('API_URL')
                engenebasenames = os.path.basename(engene).split("-")
                outJobs[input]['name'] = "-".join(engenebasenames[1:-1])
                annotation = outJobs[input]['engenes'][engene]['annotation']
                id = "-".join(engenebasenames[1:]).replace(annotation[0]+'___','CoAnnotation')
                annotation = 'CoAnnotation' if isinstance(annotation,list) else annotation
                outJobs[input]['engenes'][engene]['annotation'] = annotation
                resultPath = outJobs[input]['engenes'][engene]['results']
                mirnatargets = outJobs[input]['engenes'][engene]['mirnatargets']
                plotArgs = [resultPath,input,engene,annotation,id,mirnatargets,API_URL,organism] #
                plotUnit = self.generatePlotUnit(plotArgs) #
                outJobs[input]['engenes'][engene]['plot'] = plotUnit #
                outJobs[input]['engenes'][engene]['id'] = id
        print('OutJobs HTML')
        synonyms = [gene for synonym in synonyms for gene in synonyms[synonym]]
        synonyms.extend([gene for gene in synonyms])
        synonyms = list(set(synonyms))
        try:
            html = render_template("resultsD3.html",outJobs=outJobs,synonyms=synonyms,
                                   organism=organism,API_URL=os.getenv('API_URL'))
            print('try render_template')
        except:
            import jinja2
            template = jinja2.Template(open('web/templates/resultsD3.html').read())
            html = template.render(outJobs=outJobs,synonyms=synonyms,
                                   organism=organism,API_URL=os.getenv('API_URL'))
            print('jinja2.Template')
        print('RENDERED!')
        outFile = os.path.join(outDir,"report.html")
        save2File(outFile,html)

    def generatePlotUnit(self,plotArgs):
        resultPath,input,engene,annotation,id,mirnatargets,API_URL,organism = plotArgs
        print("readNformatResults")
        resultsTable = self.readNformatResults(resultPath)
        if isinstance(resultsTable,str):
            return(resultsTable)
        print("HTMLtablizing")
        totalresults = len(resultsTable.index)
        resultsshown = 100 if totalresults > 100 else totalresults
        totalresults = 'Showing {}/{} enriched terms.'.format(resultsshown,totalresults)
        resultsTable = resultsTable.iloc[0:100]
        table,tablejs = self.doHtmlTable(resultsTable,annotation,id,API_URL,organism)
        if len(mirnatargets) > 0:
            mirnatargets = [(mirna,', '.join(tgts)) for mirna,tgts in mirnatargets.items()]
            mirnatargetsDF = pandas.DataFrame(mirnatargets)
            mirnatargetsDF.columns = ['microRNA','target_genes']
            tablemt,tablejsmt = self.doHtmlTable(mirnatargetsDF,'micros',id+'mirnatargets',API_URL,organism)
            return ({'table':table,'js':tablejs,'totalresults':totalresults,'mirnas':{'table':tablemt,'js':tablejsmt}})
        else:
            return ({'totalresults':totalresults,'table':table,'js':tablejs})

    def readNformatResults(self,resultPath):
        resultsSize = os.stat(resultPath).st_size
        if resultsSize == 0:
            print('OUT!')
            return ("NO RESULTS")
        resultsTable = pandas.read_csv(resultPath,sep="\t",dtype=str)
        print('readNformatResults')
        results = len(resultsTable.index)
        if results == 0:
            print('OUT 2!')
            return ("NO RESULTS")      
        resultsTable['genes'] = resultsTable['genes'].str.replace(', ',',')
        resultsTable['annotation_id'] = resultsTable['annotation_id'].str.replace(',',', ')
        resultsTable['description'] = resultsTable['description'].str.replace(',',', ')
        return(resultsTable)

    def doHtmlTable(self,resultsTable,annotation,tableid,API_URL,organism):
        tableid += 'table'
        linkhtml = '<a href="{}" class="genyoLink" target="_blank">{}</a>'
        if annotation == 'micros':
            urlbase = self.getURLbase('miRBase')
            resultsTable.microRNA = [linkhtml.format(urlbase.format(mirna),mirna) for mirna in resultsTable.microRNA]
        else:
            if annotation not in ['CoAnnotation','LINCS','TAM_2','HMDD_v3']:            
                urlbase = self.getURLbase(annotation)
                resultsTable.description = [linkhtml.format(urlbase.format(resultsTable.annotation_id[resultsTable.description == term].tolist()[0]),term) for term in resultsTable.description]
            resultsTable[['pval_adj','relative_enrichment']] = resultsTable[['pval_adj','relative_enrichment']].apply(pandas.to_numeric)
            resultsTable['pval_adj'] = resultsTable['pval_adj'].map('{:,.2e}'.format)
            resultsTable['relative_enrichment'] = resultsTable['relative_enrichment'].map('{:,.2f}'.format)
            #cols2remove = ['annotation_id','input_size','genes_universe','pval','term_genes','genes','universe','annotsbias']
            cols2remove = ['annotation_id','input_size','genes_universe','pval','universe','annotsbias']
            resultsTable.drop(columns=cols2remove, errors='ignore',inplace=True)
            resultsTable.columns = [col.capitalize().replace('_',' ') if col != 'microRNA' else col for col in resultsTable.columns]
            resultsTable['Genes Count']=resultsTable['Genes found']+"/"+resultsTable['Term genes']
            column_names = ["Description", "Genes Count", "Pval adj","Relative enrichment","Genes"]
            resultsTable=resultsTable.reindex(columns=column_names)
            #resultsTable['Genes'] = resultsTable['Genes'].apply(lambda x: '<a class="genyoLink" href="http://example.com/{0}">link</a>'.format(x))
            resultsTable['Genes'] = resultsTable['Genes'].apply(lambda genes: '<a class="genyoLink" href="{0}/geneinfo?org={1}&genes={2}">{3}</a>'.format(API_URL,organism,genes,self.printGenes(genes)))
        
        table = resultsTable.to_html(index=False,table_id=tableid,
                                classes="display compact hover stripe row-border order-column",
                                border=0,justify="left",escape=False)
        table = table.replace('class="dataframe','style="width: 100%;" class="dataframe')
        js = """<script 
        
        type=\"text/javascript\">$(document).ready(function(){{ $('#{}').DataTable({{
        order: [[ 2, "asc" ]],
        scrollY:        "350px",
        scrollX:        true,
        scrollCollapse: true,
        paging:         false,
        retrieve: true,
        bInfo : false,
        autoWidth: true,
        }}).columns.adjust().draw();}});
        </script>""".format(tableid)
        return (table,js)
    
    #"columnDefs": [
    #            "targets": -1,
    #            "data": null,
    #            "defaultContent": '<button>Click!</button>',
    #    ]

    def getURLbase(self,annotation):
        annotURLdict = {
        "GO_CC":"http://amigo.geneontology.org/amigo/term/{}",
        "GO_BP":"http://amigo.geneontology.org/amigo/term/{}",
        "GO_MF":"http://amigo.geneontology.org/amigo/term/{}",
        "GO_COVID":"http://amigo.geneontology.org/amigo/term/{}",
        "HPO":"https://hpo.jax.org/app/browse/term/{}",
        "KEGG":"https://www.genome.jp/dbget-bin/www_bget?pathway:{}",
        "miRBase":"https://www.mirbase.org/textsearch.shtml?q={}",
        "miRTarBase":"http://mirtarbase.cuhk.edu.cn/php/search.php?opt=search_box&kw={}",
        "OMIM":"https://www.omim.org/entry/{}",
        "PharmGKB":"https://www.pharmgkb.org/chemical/{}",
        "Panther":"http://www.pantherdb.org/pathway/pathwayDiagram.jsp?catAccession={}",
        "MGI":"http://www.informatics.jax.org/vocab/mp_ontology/{}",
        "CTD":"http://ctdbase.org/detail.go?type=chem&acc={}",
        "DoRothEA": "https://www.genecards.org/cgi-bin/carddisp.pl?gene={}", #"http://jaspar.genereg.net/search?q=",
        "gene":"https://www.genecards.org/cgi-bin/carddisp.pl?gene={}",
        "WikiPathways":"https://www.wikipathways.org/index.php/Pathway:{}",
        "Reactome":"https://reactome.org/PathwayBrowser/#/{}",
        "MNDR":"http://www.rna-society.org/mndr/php_mysql/result.php?searchType=exact&p=1&rownum=0&dataset=Disease ID&keyword={}&category=All&species=All&datasource=Experiment&method=All&sco1=0.0&sco2=1.0",
        "LINCS":"{}", # https://clue.io/connection?url=macchiato.clue.io/builds/touchstone/v1.1/arfs/BRD-A31159102
        "TAM_2":"{}",
        "HMDD_v3":"{}",
        "CoAnnotation":"{}",
        'BioPlanet':'https://tripod.nih.gov/bioplanet/detail.jsp?pid={}&target=pathway',
        'DisGeNET':'https://www.disgenet.org/search/0/{}/'
        }
        return(annotURLdict[annotation])

    def printGenes(self,genes):
        
        if genes.count(',')>2:
            return genes[0:30]+"..."
        else:
            return genes[0:30]
