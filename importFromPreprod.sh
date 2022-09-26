#!/bin/bash


scp -r genecodis@192.168.2.34:GeneCodis4.0/web/htmls/jobs/$2/* web/htmls/jobs/$1/.
sed -i 's/'$2'/'$1'/g' web/htmls/jobs/$1/report.html
echo -e '<script type="text/javascript" src="https://cdn.pydata.org/bokeh/release/bokeh-2.0.0.min.js"></script>\n<script type="text/javascript" src="https://cdn.pydata.org/bokeh/release/bokeh-widgets-2.0.0.min.js"></script>\n<script type="text/javascript" src="https://cdn.pydata.org/bokeh/release/bokeh-tables-2.0.0.min.js"></script>' >> web/htmls/jobs/$1/report.html
sed -i 's/'$2'/'$1'/g' web/htmls/jobs/$1/commands.sh
sed -i 's/'$2'/'$1'/g' web/htmls/jobs/$1/params.json
