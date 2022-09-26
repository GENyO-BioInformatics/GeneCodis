"use strict";

const fs = require('fs');
const path = require('path');
const ejs = require('ejs');
// const fetch = require('node-fetch');

function getFormJSON(formJSON){
  var contents = fs.readFileSync(formJSON);
  var jsonContent = JSON.parse(contents);
  return  jsonContent
}

function divideAnnotations(annots){
  var funRex = 'GO|Pathway|Mouse|Reac|BioPla';
  var regRex = 'miRTar|DoR';
  var mirnasRex = 'TAM|HMDD|MNDR'
  var mirnas = annots.filter(s =>s.match(mirnasRex));
  var functional = annots.filter(s => s.match(funRex));
  var regulatory = annots.filter(s => s.match(regRex));
  var perRex = `${funRex}|${regRex}|${mirnasRex}`;
  var perturbats = annots.filter(s =>!s.match(perRex));
  return {'functional':functional.join('\n'),
          'perturbats':perturbats.join('\n'),
          'regulatory':regulatory.join('\n'),
          'mirnas':mirnas.join('\n')}
}

function getFormEntries(infoannot,webdata){
  var annotHTMLbase = '<input type="checkbox" hidden name="annotations" onchange="limitCheckBoxes()" id="_anno_" value="_anno_" class="gc4checkbox">\n<label for="_anno_" title="_fullname_" class="defaultlabel">_annoName_</label>';
  var annotsForm = Object.keys(infoannot).map(function(annotation){
      var annoName = infoannot[annotation]['webname'];
      var fullname = infoannot[annotation]['fullname'];
      var annotHTML = annotHTMLbase.replace(/_anno_/g, annotation);
      var annotHTML = annotHTML.replace(/_annoName_/g, annoName);
      var annotHTML = annotHTML.replace(/_fullname_/g, fullname);
      return annotHTML;
  });
  var orgHTMLbase = '<option value="_taxid_">_taxName_</option>';
  var orgsForm = Object.keys(webdata).map(function(taxID){
    var orgHTML = orgHTMLbase.replace(/_taxid_/g, taxID);
    var orgHTML = orgHTML.replace(/_taxName_/g, webdata[taxID].name);
    return orgHTML;
  });
  return {'annotsForm':divideAnnotations(annotsForm),
          'orgsForm':orgsForm.join('\n')};
}

function compileFile(inputFile, outDir){
    const filename = path.parse(inputFile).name;
    console.log("-",filename);
    const template = fs.readFileSync(inputFile, 'utf-8');
    const html = ejs.render(template, {filename:inputFile,
                                       annotsForm:annotsForm,
                                       orgsForm:orgsForm,
                                       changelog:changelog
                                       });
    fs.writeFileSync(path.join(outDir,filename+".html"), html);
}

function getFiles(baseDir){
    return fs.readdirSync(baseDir).map((f)=>path.join(baseDir,f));
}

function clearDirectoryFromHtml(dir){
    const pages=getFiles(dir);
    for(const page of pages){
        if(path.extname(page)===".html"){
            fs.unlinkSync(page)
        }
    }
}

var formJSON = './db/maintenance/info/data_in_web.json'
var webdata = getFormJSON(formJSON);
var formJSON = './db/maintenance/info/info_annotation.json'
var infoannot = getFormJSON(formJSON);
var formThingies = getFormEntries(infoannot,webdata);
var annotsForm = formThingies.annotsForm;
var orgsForm = formThingies.orgsForm;
var changelog = fs.readFileSync('changelog.txt');

const pagesDirectory=path.join(__dirname, "pages");
const docsDirectory=path.join(__dirname,"..","htmls");

clearDirectoryFromHtml(docsDirectory);
var pages = getFiles(pagesDirectory);
for(const file of pages){
    compileFile(file, docsDirectory);
}
