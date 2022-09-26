import json, pandas, glob, os, math, itertools
pandas.options.mode.chained_assignment = None


os.makedirs("html_files",exist_ok = True)
os.makedirs("processed_tables",exist_ok = True)
tables = glob.glob("raw_tables/*.tsv")
tables = [table.replace("\\","/") for table in tables]
for table in tables:
    dataframe = pandas.read_csv(table,sep="\t",dtype=str)
    dataframe['barheight'] = [700]*len(dataframe.index)
    dataframe['font'] = [14]*len(dataframe.index)
    for i in range(len(dataframe.index)):
        if i > 9:
            diff = i - 9
            dataframe.barheight[i] = 700 + diff * 10
            if i < 20:
                dataframe.font[i] = 14
            else:
                dataframe.font[i] = 12
    terms = dataframe.term.tolist()
    terms = [x.replace(",",";") for x in terms]
    terms = [x.replace("; ",", ") for x in terms]
    terms = [x.replace(";","; ") for x in terms]
    dataframe['term'] = terms
    anns = dataframe.annotation.tolist()
    anns = [x.replace(",","; ") for x in anns]
    dataframe['annotation'] = anns
    dataframe["logPval"] = [-math.log(float(dataframe['hyp_pval_adj'].tolist()[i])) for i in range(len(dataframe.index))]
    csv_file = table.replace(".tsv",".csv")
    csv_file = csv_file.replace("raw_tables","processed_tables")
    dataframe.to_csv(csv_file,index=None)
    # infodata.map(function(d){
    #         d.barheight = 700; d.font = 14;
    #         d.term = d.term.replace(/','/g, ';').replace(/'; '/g, ', ').replace(/';'/g, '; ');
    #         d.annotation = d.annotation.replace(/','/g, '; ');
    #         d.logPval = -Math.log(+d.hyp_pval_adj);
    #         });
    # for (i = 0; i < infodata.length; i++) {
    #     if(i > 9){
    #         var diff = i - 9;
    #         infodata[i].barheight = 700 + diff * 10;
    #     };
    #     if(i < 20){
    #         infodata[i].font = 14;
    #     }else{
    #         infodata[i].font = 12;
    #     };
    # };

    with open("templateVisualization.html") as reader:
        html_content = reader.read()
    html_content = html_content.replace("tablefile","../"+csv_file)
    htmlfile = table.replace(".tsv",".html")
    htmlfile = htmlfile.replace("raw_tables/","html_files/")
    with open(htmlfile, "w") as writer:
        writer.write(html_content)
