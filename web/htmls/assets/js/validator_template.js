// FORM HANDLER // FORM HANDLER // FORM HANDLER // FORM HANDLER // FORM HANDLER
// orgsAnnots is an object globally loaded from the main html

function uncheckallannots(){
  var checkedannots = [...document.querySelectorAll('[name="annotations"]:checked')];
  checkedannots.map(function(annot) {
    annot.checked = false;
  });
}

function checkallannots(){
  var availableannots = [...document.querySelectorAll('[name="annotations"]:not(:disabled)')];
  availableannots.map(function(annot) {
    annot.checked = true;
  });
}

function disableAnotsLabels() {
  var annots = [...document.querySelectorAll('[name="annotations"]')];
  var inputtypes = [...document.querySelectorAll('[name="inputtype"]')];
  var labels = annots.concat(inputtypes);
  for (label in labels) {
    if (labels[label].disabled) {
      labels[label].parentElement.className += ' is-disabled';
    } else {
      labels[label].parentElement.className = labels[label].parentElement.className.replaceAll(' is-disabled', '');
    };
  };
};

function disableAllAnots() {
  let annots = [...document.getElementsByName('annotations')];
  annots.map(function(annot) {
    annot.checked = false;
    annot.disabled = true;
  });
  disableAnotsLabels();
};

function getOrgSelected() {
  let orgs = document.getElementsByName('organism')[0].options;
  for (org in orgs) {
    if (orgs[org].selected) {
      return ({
        'taxid': orgs[org].value,
        'name': orgs[org].innerText
      });
    }
  }
};

function disableInputTypes(orgid) {
  let mirnas = document.getElementById('mirnas').checked;
  let tfs = document.getElementById('tfs').checked;
  let cpgs = document.getElementById('cpgs').checked;
  if (['9606', '10090'].includes(orgid)) {
    document.getElementById('tfs').disabled = false;
    document.getElementById('mirnas').disabled = false;
    if (orgid == "9606") {
      document.getElementById('cpgs').disabled = false;
    } else {
      document.getElementById('cpgs').disabled = true;
    }
  } else if (['7955', '7227', '10116', '9823'].includes(orgid)) {
    document.getElementById('tfs').disabled = true;
    document.getElementById('cpgs').disabled = true;
    document.getElementById('mirnas').disabled = false;
  } else {
    // ['9913','6239','9615','9031','3702','39947','559292','227321','511145','237561'].includes(orgid)
    document.getElementById('tfs').disabled = true;
    document.getElementById('cpgs').disabled = true;
    document.getElementById('mirnas').disabled = true;
  }
  let mirnasDis = document.getElementById('mirnas').disabled;
  let tfsDis = document.getElementById('tfs').disabled;
  let cpgsDis = document.getElementById('cpgs').disabled;
  if (mirnas && mirnasDis) {
    document.getElementById('genes').checked = true;
  } else if (tfs && tfsDis) {
    document.getElementById('genes').checked = true;
  } else if (cpgs && cpgsDis) {
    document.getElementById('genes').checked = true;
  }
}

// function enableAnotsByOrgValue(){
//   let orgid = getOrgSelected().taxid;
//   disableAllAnots();
//   let annotIDs = orgsAnnots[orgid];
//   annotIDs.map(function(annotID){
//     document.getElementById(annotID).disabled = false;
//   });
//   disableAnnotsByInputType();
//   disableAnotsLabels();
// }

function checkAnnotsEnabled(annots) {
  for (i = 0; i < annots.length; i++) {
    if (annots[i].disabled == false) {
      document.getElementById(annots[i].id).checked = true;
    };
  };
  disableAnotsLabels();
}

function uncheckDisabled() {
  var annots = [...document.querySelectorAll(`[name="annotations"]:checked`)];
  for (i = 0; i < annots.length; i++) {
    if (annots[i].disabled == false) {
      document.getElementById(annots[i].id).checked = true;
    };
  };
}

function disableAlgByInputType(){
  let hypergeom = document.getElementById('hypergeom').checked;
  let wallenius = document.getElementById('wallenius').checked;
  let genes = document.getElementById('genes').checked;
  let tfs = document.getElementById('tfs').checked;
  let cpgs = document.getElementById('cpgs').checked;
  let mirnas = document.getElementById('mirnas').checked;
  
  if(genes){
    document.getElementById('wallenius').disabled = true;
    document.getElementById('wallenius').parentElement.className += ' is-disabled';
    document.getElementById('hypergeom').checked=true;
  }

  if(tfs || cpgs){
    document.getElementById('wallenius').disabled = false;
    document.getElementById('wallenius').parentElement.classList.remove("is-disabled");
    document.getElementById('wallenius').checked=true;
  }

  if(mirnas){
    document.getElementById('wallenius').disabled = false;
    document.getElementById('wallenius').parentElement.classList.remove("is-disabled");
    document.getElementById('hypergeom').checked=true;
  }
}

function disableAnnotsByInputType() {
  var annots = [...document.querySelectorAll(`[name="annotations"]:checked`)];
  let orgid = getOrgSelected().taxid.toString();
  disableInputTypes(orgid);
  disableAllAnots();
  let annotIDs = orgsAnnots[orgid];
  annotIDs.map(function(annotID) {
    document.getElementById(annotID).disabled = false;
  });
  let mirnas = document.getElementById('mirnas').checked;
  let wallenius = document.getElementById('wallenius').checked;
  let tfs = document.getElementById('tfs').checked;
  let genes = document.getElementById('genes').checked;
  let cpgs = document.getElementById('cpgs').checked;
  let notargets = document.getElementById('miRTarBase').disabled;
  if (genes || tfs || cpgs || wallenius) {
    document.getElementById('MNDR').checked = false;
    document.getElementById('TAM_2').checked = false;
    document.getElementById('HMDD_v3').checked = false;
    document.getElementById('MNDR').disabled = true;
    document.getElementById('TAM_2').disabled = true;
    document.getElementById('HMDD_v3').disabled = true;
    if (tfs) {
      document.getElementById('DoRothEA').disabled = true;
      document.getElementById('DoRothEA').checked = false;
    }
    document.getElementById('mirconverter').style.display = 'none';
    document.getElementById('mirconverter').className = '';
  }
  if (mirnas) {
    document.getElementById('miRTarBase').checked = false;
    document.getElementById('miRTarBase').disabled = true;
    if (mirnas && notargets) {
      let mndr = document.getElementById('MNDR').checked;
      let tam = document.getElementById('TAM_2').checked;
      let hmdd = document.getElementById('HMDD_v3').checked;
      let mndrAv = document.getElementById('MNDR').disabled;
      let tamAv = document.getElementById('TAM_2').disabled;
      let hmddAv = document.getElementById('HMDD_v3').disabled;
      disableAllAnots();
      document.getElementById('MNDR').disabled = mndrAv;
      document.getElementById('TAM_2').disabled = tamAv;
      document.getElementById('HMDD_v3').disabled = hmddAv;
      document.getElementById('MNDR').checked = mndr;
      document.getElementById('TAM_2').checked = tam;
      document.getElementById('HMDD_v3').checked = hmdd;
    };
    document.getElementById('mirconverter').style.display = '';
    document.getElementById('mirconverter').className = 'tile is-flex is-flex-grow-0';
  };
  let coannotation = document.getElementById('coannotation_yes').checked;
  if (coannotation) {
    if (annots.length == 2) {
      for (idx in annots) {
        if (annots[idx].disabled) {
          annots[idx].checked = false;
        } else {
          annots[idx].click();
        }
      }
    } else {
      checkAnnotsEnabled(annots);
    }
  } else {
    checkAnnotsEnabled(annots);
  }
  countAnnotSelected();
  disableAnotsLabels();
}

function comparingMode() {
  var comparing = document.getElementById('comparing').style.display;
  if (comparing == '') {
    document.getElementById('comparing').previousElementSibling.className = "tile is-vertical";
    document.getElementById('comparing').style.display = 'none';
    document.getElementsByName('inputName')[0].style.display = 'none';
    document.getElementsByName('input2')[0].value = '';
    document.getElementsByName('input2Name')[0].value = '';
  } else {
    document.getElementsByName('inputName')[0].style.display = '';
    document.getElementById('comparing').style.display = '';
    document.getElementById('comparing').previousElementSibling.className = "tile is-vertical is-6 pr-2"
    document.getElementById('comparing').className = "tile is-vertical is-6 pl-2"
  }
  addCounter();
}

function showParentNextSibling(evt) {
  const cousin = evt.currentTarget;
  const nextSibl = cousin.parentElement.nextElementSibling;
  if (nextSibl.style.display === "none") {
    cousin.className = 'button label is-fullwidth select toggle active';
    nextSibl.style.display = "flex";
  } else {
    cousin.className = 'button label is-fullwidth select toggle';
    nextSibl.style.display = "none";
  }
}

function showfilename(evt) {
  evt.currentTarget.nextElementSibling.nextElementSibling.innerText = evt.currentTarget.files[0].name;
}

function removefile(inputname) {
  document.getElementsByName(inputname)[0].value = '';
  document.getElementsByName(inputname)[0].nextElementSibling.nextElementSibling.innerText = '...';
}

function closeAllSelect(elmnt) {
  let x, y, i, arrNo = [];
  x = document.getElementsByClassName("select-items");
  y = document.getElementsByClassName("select-selected");
  for (i = 0; i < y.length; i++) {
    if (elmnt == y[i]) {
      arrNo.push(i);
    } else {
      y[i].classList.remove("select-arrow-active");
    }
  }
  for (i = 0; i < x.length; i++) {
    if (arrNo.indexOf(i)) {
      x[i].classList.add("select-hide");
    }
  }
}

function getexample(textbox) {
  let orgExample = {
    // 9913  bos_taurus
    '9913': {
      'genes': {
        'list': ['CTNNB1', 'ADAM17', 'AXIN1', 'AXIN2', 'CCND2', 'CSNK1E', 'CTNNB1', 'CUL1', 'DKK1', 'DKK4', 'DLL1', 'DVL2', 'FRAT1', 'FZD1', 'FZD8', 'GNAI1', 'HDAC11', 'HDAC2', 'HDAC5', 'HEY1', 'HEY2', 'JAG1', 'JAG2', 'KAT2A', 'LEF1', 'MAML1', 'MYC', 'NCOR2', 'NCSTN', 'NKD1', 'NOTCH1', 'NOTCH4', 'NUMB', 'PPARD', 'PSEN2', 'PTCH1', 'RBPJ', 'SKP2', 'TCF7', 'TP53', 'WNT1', 'WNT5B', 'WNT6'],
        'description': "genes up-regulated by activation of wnt signaling through accumulation of beta catenin (source: msigdb)"
      }
    },
    // 6239  caenorhabditis_elegans
    '6239': {
      'genes': {
        'list': ['cnnm-1', 'cnnm-5', 'gld-1', 'cnnm-3', 'atx-2', 'cnnm-4', 'pab-1', 'cnnm-2', 'fer-1', 'alg-3', 'noca-1', 'wee-1.3', 'vha-11', 'gsk-3', 'atg-18'],
        "description": "genes related to reproduction events"
      }
    },
    // 9615  canis_familiaris
    '9615': {
      'genes': {
        'list': ['AMOT', 'CDK5R1', 'CDK6', 'CELSR1', 'CNTFR', 'CRMP1', 'DPYSL2', 'ETS2', 'GLI1', 'GPR56', 'HEY1', 'HEY2', 'L1CAM', 'LDB1', 'MYH9', 'NF1', 'NKX6-1', 'NRCAM', 'NRP1', 'NRP2', 'OPHN1', 'PLG', 'PML', 'PTCH1', 'RASA1', 'RTN1', 'SCG2', 'SHH', 'SLIT1', 'THY1', 'TLE1', 'TLE3', 'UNC5C', 'VEGFA', 'VLDLR'],
        'description': "genes up-regulated by activation of hedgehog signaling (source: msigdb)"
      }
    },
    // 7955  danio_rerio
    '7955': {
      'genes': {
        'list': ['arrb1', 'ccnd1', 'cul1', 'dtx1', 'dtx2', 'dtx4', 'fbxw11', 'fzd1', 'fzd5', 'heyl', 'jag1', 'kat2a', 'lfng', 'notch1a', 'notch2', 'notch3', 'nle1', 'notchl', 'notch1b', 'sbno1', 'sbno2a', 'dner', 'prkca', 'psen2', 'psenen', 'rbx1', 'skp1', 'tcf7l2', 'wnt2', 'wnt5a'],
        "description": "notch signaling genes"
      },
      'mirnas': {
        'list': ['mirlet7a-4', 'mirlet7f', 'dre-miR-10a-5p', 'dre-miR-10b-5p', 'dre-miR-199-5p', 'dre-miR-214', 'dre-miR-219-5p', 'dre-miR-223', 'dre-miR-430a-3p', 'dre-miR-451', 'dre-miR-1', 'dre-miR-9-5p', 'dre-miR-21', 'dre-miR-29b', 'dre-miR-30a-5p', 'dre-miR-30b', 'dre-miR-30c-5p', 'dre-miR-30d', 'dre-miR-30e-5p', 'dre-miR-125b-5p', 'dre-miR-138-5p', 'dre-miR-140-5p', 'dre-miR-143', 'dre-miR-145-5p', 'dre-miR-150', 'dre-miR-155', 'dre-miR-206-3p', 'dre-miR-216b', 'dre-miR-499-5p', 'dre-miR-3906', 'dre-miR-203a-3p', 'dre-miR-430b-3p', 'dre-miR-430c-3p', 'dre-miR-92a-3p', 'dre-miR-126a-3p', 'dre-miR-133a-3p', 'dre-miR-133b-3p', 'dre-miR-133c-3p', 'dre-miR-142a-3p', 'dre-miR-144-3p', 'dre-miR-200a-3p', 'dre-miR-200b-3p'],
        'description': 'miRNAs involved in development processes'
      }
    },
    // 7227  drosophila_melanogaster
    '7227': {
      'mirnas': {
        'list': ['mir-9a', 'mir-2a-1', 'mir-1', 'mir-34', 'mir-7', 'mir-79', 'mir-8', 'mir-13b-1', 'dme-miR-5-5p', 'dme-miR-12-5p', 'dme-miR-263a-5p', 'dme-miR-283-5p', 'dme-miR-287-3p', 'dme-miR-263b-5p', 'dme-miR-288-3p', 'dme-miR-iab-4-5p', 'dme-miR-iab-8-5p', 'dme-miR-4-3p', 'dme-miR-6-3p', 'dme-miR-11-3p', 'dme-miR-13a-3p', 'dme-miR-14-3p', 'dme-miR-278-3p', 'dme-miR-92b-3p', 'dme-bantam-3p', 'dme-miR-308-3p', 'dme-miR-310-3p', 'dme-miR-311-3p', 'dme-miR-312-3p', 'dme-miR-313-3p', 'dme-miR-2c-3p', 'mir-279', 'mir-2b-1', 'dme-let-7-5p', 'dme-miR-315-5p', 'dme-miR-124-3p'],
        'description': 'miRNAs involved in development processes'
      },
      'genes': {
        'list': ['trbl', 'melt', 'step', 'PIP4K', 'Mob4', 'CycG', 'mts', 'Lst8', 'PRAS40', 'wrd', 'Lar', 'DENR', 'Pten', 'rictor', 'Tsc1', 'Ns3', 'poly', 'Mkp3', 'dock', 'Ptp61F'],
        "description": "insulin receptor signaling genes"
      }
    },
    // 9031  gallus_gallus
    '9031': {
      'genes': {
        'list': ['CTNNB1', 'ADAM17', 'AXIN1', 'AXIN2', 'CCND2', 'CSNK1E', 'CTNNB1', 'CUL1', 'DKK1', 'DKK4', 'DLL1', 'DVL2', 'FZD1', 'FZD8', 'GNAI1', 'HDAC11', 'HDAC2', 'HDAC5', 'HEY1', 'HEY2', 'JAG1', 'JAG2', 'KAT2A', 'LEF1', 'MAML1', 'MYC', 'NCOR2', 'NCSTN', 'NKD1', 'NOTCH1', 'NUMB', 'PPARD', 'PSEN2', 'PTCH1', 'RBPJ', 'SKP2', 'TCF7', 'TP53', 'WNT1', 'WNT5B', 'WNT6'],
        "description": "genes up-regulated by activation of wnt signaling through accumulation of beta catenin (source: msigdb)"
      }
    },
    // 9606  homo_sapiens
    '9606': {
      'cpgs': {
        'list': ['cg12862002', 'cg11807238', 'cg08466770', 'cg03996150', 'cg11081441', 'cg03269045', 'cg07892276', 'cg12560128', 'cg20163324', 'cg22833204', 'cg06671069', 'cg03320783', 'cg08817962', 'cg00474889', 'cg02228675', 'cg20724781', 'cg15113090', 'cg17990983', 'cg22963452', 'cg13155430', 'cg25484698', 'cg04640194', 'cg09151598', 'cg12652301', 'cg06740354', 'cg20161089', 'cg07348311', 'cg25800166', 'cg09969248', 'cg08596817', 'cg12987761', 'cg21052403', 'cg17114584', 'cg21730677', 'cg09354037', 'cg10311754', 'cg24948564', 'cg03538095', 'cg27066543', 'cg02988155', 'cg24805898', 'cg05338155', 'cg00493400', 'cg18766080', 'cg23684711', 'cg21135483', 'cg21930140', 'cg20729846', 'cg19764540', 'cg22281505'],
        "description": "CpG sites associated with lupus signature genes"
      },
      'tfs': {
        'list': ['FOSL2', 'NR3C1', 'ARNTL', 'SOX2', 'SRF', 'STAT6', 'NFATC2', 'ATF6'],
        'description': 'List of human TFs'
      },
      'genes': {
        'list': ['APOH', 'APP', 'COL3A1', 'COL5A2', 'CXCL6', 'FGFR1', 'FSTL1', 'ITGAV', 'JAG1', 'JAG2', 'KCNJ8', 'LPL', 'LRPAP1', 'LUM', 'MSX1', 'NRP1', 'OLR1', 'PDGFA', 'PF4', 'PGLYRP1', 'POSTN', 'PRG2', 'PTK2', 'S100A4', 'SERPINA5', 'SLCO2A1', 'SPP1', 'STC1', 'THBD', 'TIMP1', 'TNFRSF21', 'VAV2', 'VCAN', 'VEGFA', 'VTN'],
        "description": "genes up-regulated during formation of blood vessels/angiogenesis (source: msigdb)"
      },
      'mirnas': {
        'list': ['hsa-mir-133a-1', 'hsa-miR-133a-3p', 'hsa-miR-133a-5p', 'hsa-mir-133a-2', 'hsa-mir-133b', 'hsa-miR-133b', 'hsa-mir-1-1', 'hsa-miR-1-3p', 'hsa-miR-1-5p', 'hsa-mir-1-2', 'hsa-mir-328', 'hsa-miR-328-5p', 'hsa-miR-328-3p', 'hsa-mir-212', 'hsa-miR-212-3p', 'hsa-miR-212-5p', 'hsa-mir-208a', 'hsa-miR-208a-5p', 'hsa-miR-208a-3p'],
        'description': 'Use case of GeneCodis 4 article, heart disorder associated miRNAs'
      }
    },
    // 10090  mus_musculus
    '10090': {
      'mirnas': {
        'list': ['mmu-miR-138-5p', 'mmu-miR-145a-5p', 'mmu-miR-146a-5p', 'mmu-miR-155-5p', 'mmu-miR-200b-5p', 'mmu-miR-122-5p', 'mmu-let-7a-5p', 'mmu-let-7b-5p', 'mmu-let-7c-5p', 'mmu-miR-18a-5p', 'mmu-miR-20a-5p', 'mmu-miR-34a-5p', 'mmu-miR-181b-5p', 'mmu-miR-451a', 'mmu-miR-124-3p', 'mmu-miR-128-3p', 'mmu-miR-24-3p', 'mmu-miR-200a-3p', 'mmu-miR-21a-3p', 'mmu-miR-22-3p', 'mmu-miR-26b-3p', 'mmu-miR-27a-3p', 'mmu-miR-101b-3p', 'mmu-miR-19a-3p', 'mmu-miR-421-3p'],
        'description': 'miRNAs involved in cancer'
      },
      'tfs': {
        "list": ['Relb', 'Arntl', 'Nfkb2', 'Fosl1', 'Sox2', 'Srf', 'Stat6', 'Nfatc2', 'Atf6'],
        "description": 'Lists of TFs of mouse'
      },
      'genes': {
        'list': ['Acan', 'Aspn', 'Bcan', 'Bgn', 'Chad', 'Chadl', 'Dcn', 'Epyc', 'Esm1', 'Fmod', 'Hapln1', 'Hapln2', 'Hapln3', 'Hapln4', 'Hspg2', 'Impg1', 'Impg2', 'Kera', 'Lum', 'Ncan', 'Nepn', 'Nyx', 'Ogn', 'Omd', 'Optc', 'Podn', 'Podnl1', 'Prelp', 'Prg2', 'Prg3', 'Prg4', 'Spock1', 'Spock2', 'Spock3', 'Srgn', 'Vcan'],
        'description': "genes related to proteoglycans"
      }
    },
    // 10116  rattus_norvegicus
    '10116': {
      'mirnas': {
        'list': ['rno-miR-21-5p', 'rno-miR-26b-5p', 'rno-miR-34a-5p', 'rno-miR-96-5p', 'rno-miR-138-5p', 'rno-miR-142-5p', 'rno-miR-145-5p', 'rno-miR-146a-5p', 'rno-miR-192-5p', 'rno-miR-218a-5p', 'rno-miR-215', 'rno-miR-499-5p', 'rno-let-7g-5p', 'rno-miR-27a-3p', 'rno-miR-29a-3p', 'rno-miR-124-3p', 'rno-miR-130a-3p', 'rno-miR-132-3p', 'rno-miR-193a-3p', 'rno-miR-200c-3p', 'rno-miR-200a-3p', 'rno-miR-200b-3p', 'rno-miR-320-3p', 'rno-miR-375-3p', 'rno-miR-92b-3p'],
        'description': 'miRNAs involved in cancer'
      },
      'genes': {
        'list': ['Traf4', 'Ikbkg', 'Ppp1r9a', 'Ghrl', 'Stk3', 'Dusp18', 'Alkal1', 'Arrb1', 'Hexim2', 'Apc', 'Ibtk', 'Ksr1', 'Hgs', 'Rack1', 'Mlst8', 'Wnt5a', 'Ager', 'Axin2', 'Mre11', 'Cish', 'Erbb2', 'Dnaja3', 'Ephb4', 'Mmd2'],
        "description": "genes related to protein kinase activity"
      }
    },
    // 9823  sus_scrofa
    '9823': {
      'mirnas': {
        'list': ['MIRLET7G', 'MIRLET7E', 'ssc-miR-125b', 'ssc-miR-145-5p', 'ssc-miR-26a', 'ssc-miR-124a', 'ssc-miR-1', 'ssc-miR-378', 'ssc-miR-199a-5p', 'ssc-miR-181d-5p', 'ssc-miR-374b-5p', 'ssc-miR-19b', 'ssc-miR-187', 'ssc-miR-150', 'ssc-miR-221-3p', 'ssc-miR-143-3p', 'ssc-miR-27b-3p', 'ssc-miR-361-3p', 'ssc-miR-296-3p', 'ssc-miR-7134-3p'],
        'description': "Example list of miRNAs from Sus scrofa"
      },
      'genes': {
        'list': ['ACHE', 'AMOT', 'CDK5R1', 'CDK6', 'CELSR1', 'CNTFR', 'CRMP1', 'DPYSL2', 'ETS2', 'GLI1', 'GPR56', 'HEY1', 'HEY2', 'L1CAM', 'LDB1', 'MYH9', 'NF1', 'NKX6-1', 'NRCAM', 'NRP1', 'NRP2', 'OPHN1', 'PLG', 'PML', 'PTCH1', 'RASA1', 'RTN1', 'SCG2', 'SHH', 'SLIT1', 'THY1', 'TLE1', 'TLE3', 'UNC5C', 'VEGFA', 'VLDLR'],
        'description': "enes up-regulated by activation of hedgehog signaling (source: msigdb)"
      }
    },
    // 3702  arabidopsis_thaliana
    '3702': {
      'genes': {
        'list': ['AG', 'AGL15', 'AGL20', 'AP1', 'AP2', 'AP3', 'BBX10', 'CRY2', 'ETT', 'FLC', 'GAS41', 'GNC', 'JAG', 'LFY', 'MAF1', 'PEP', 'PHYB', 'PI', 'SEP3', 'SHL1', 'SVP', 'PHYA', 'PHYD', 'PHYE', 'CRY1', 'CKA1', 'SPY', 'LHY', 'LUX', 'ELF3', 'ELF4', 'FKF1'],
        'description': "flower development genes"
      }
    },
    // 39947  oryza_sativa
    '39947': {
      'genes': {
        'list': ["LOC4333030", "LOC4330922", "LOC107275667", "LOC4346120", "LOC4345833", "LOC4345832", "LOC4345831", "LOC4345514", "LOC4345425", "LOC4344391"],
        "description": ""
      }
    },
    // 559292  saccharomyces_cerevisiae
    '559292': {
      'genes': {
        'list': ['ATR1', 'VMA11', 'MMT2', 'FLC1', 'PMA2', 'SKS1', 'FEX1', 'AMF1', 'RIM2', 'GDT1', 'DTR1', 'SEC66', 'RTC2', 'AGP2', 'VMA2', 'YMC2', 'TOM5', 'ARR3', 'SGE1', 'PUT4', 'MRS2', 'VMA4', 'PDR10'],
        'description': "genes related to transmembrane transport"
      }
    },
    // 227321  aspergillus_nidulans
    '227321': {
      'genes': {
        'list': ['AN3386.2', 'AN3612.2', 'AN6431.2', 'AN6791.2', 'AN7084.2', 'AN6496.2', 'AN9126.2', 'AN7084.2'],
        'description': 'Secondary metabolism genes'
      }
    },
    // 237561 candida albicans
    '237561': {
      'genes': {
        'list': ['MEP1', 'MLT1', 'YMC2', 'GNP3', 'VPH1', 'HGT7', 'PHO84', 'JEN2', 'PHO89', 'RSP5', 'SSC1', 'TIM17', 'KAR2', 'SEC62', 'DAL52', 'ATP19', 'PEX14', 'OPT2', 'HGT16'],
        'description': "genes related to transmembrane transport"
      }
    },
    // 511145  escherichia_coli_str_k_12_substr_mg1655
    '511145': {
      'genes': {
        'list': ['rutA', 'ssuD', 'leuB', 'ubiF', 'grxA', 'folM', 'ygiN', 'lsrG', 'epd', 'glpA', 'ubiI', 'aceA', 'ilvC', 'ubiH', 'tas', 'epmC', 'ybbO', 'leuB', 'fnr', 'relE', 'tas', 'hmp'],
        'description': 'genes related to oxido-reduction'
      }
    }
  }
  let organism = getOrgSelected();
  var inputtype = document.querySelector('input[name="inputtype"]:checked').id;
  try {
    var example = orgExample[organism.taxid.toString()][inputtype]['list'];
  } catch {
    var inputtype = 'genes';
    var example = orgExample[organism.taxid.toString()][inputtype]['list'];
    document.getElementById(inputtype).checked = true;
  }
  let description = orgExample[organism.taxid.toString()][inputtype]['description'];
  disableAllAnots();
  disableAnnotsByInputType();
  let wallenius = document.getElementById('wallenius').checked;
  if (organism.taxid == '9606' && inputtype == 'mirnas') {
    document.getElementById('KEGG').enabled = true;
    document.getElementById('KEGG').checked = true;
    if(!wallenius){
      document.getElementById('HMDD_v3').enabled = true;
      document.getElementById('HMDD_v3').checked = true;
    }
  } else if (organism.taxid == '9823' && inputtype == 'mirnas') {
    if(!wallenius){
      document.getElementById('MNDR').enabled = true;
      document.getElementById('MNDR').checked = true;
    }    
  } else if (['3702', '7955'].includes(organism.taxid) && inputtype == 'mirnas' ||
    (['9606', '10090'].includes(organism.taxid) && inputtype == 'tfs')) {
    document.getElementById('KEGG').enabled = true;
    document.getElementById('Reactome').enabled = true;
    document.getElementById('KEGG').checked = true;
    document.getElementById('Reactome').checked = true;
  } else {
    document.getElementById('GO_BP').enabled = true;
    document.getElementById('GO_CC').enabled = true;
    document.getElementById('GO_BP').checked = true;
    document.getElementById('GO_CC').checked = true;
  }
  document.getElementsByName('jobName')[0].value = `${organism.name} example`;
  document.getElementsByName(textbox)[0].value = example.join("\n");
  document.getElementById('exdesc').innerText = description;
  addCounter();
  disableAnotsLabels();
}

function clearinputBox(textbox) {
  document.getElementsByName(textbox)[0].value = '';
  document.getElementById('exdesc').innerText = '';
  document.getElementsByName('jobName')[0].value = '';
  addCounter();
}

function clickDropDown(value, dropdownName) {
  document.getElementsByName(dropdownName)[0].value = value;
  // let opts = document.getElementsByName(dropdownName)[0].options;
  // let optsdivs = document.getElementsByClassName(myclass);
  // for (opt in opts){
  //     if(opts[opt].value == value){
  //         opts[opt].selected = true;
  //         const optname = opts[opt].innerText;
  //         for (optdiv in optsdivs){
  //           if(optsdivs[optdiv].innerText == optname){
  //             optsdivs[optdiv].click();
  //           }
  //         }
  //       break
  //     }
  // }
}

function checkBoxesById(params, ids) {
  var ids = ids.map(function(id) {
    return (params[id]);
  });
  var ids = ids.flat();
  ids.map(function(id) {
    document.getElementById(id).click();
  });
}

function valueFormByName(params, names) {
  for (aname in names) {
    var name = names[aname];
    if (typeof params[name] == 'object' & !Array.isArray(params[name])) {
      if (Object.keys(params[name]).length == 2) {
        document.getElementById('comparative').click();
      }
      let keys = Object.keys(params[name]);
      valueFormByName(params[name], keys);
      continue
    }
    var thevalue = params[name];
    if (['string', 'number'].includes(typeof(thevalue))) {
      var thevalue = [String(thevalue)];
    }
    document.getElementsByName(name)[0].value = thevalue.join('\n');
  }
}

function recoverParams(params) {
  clickDropDown(params.organism, 'organism');
  checkBoxesById(params, ['inputtype','coannotation','annotations','stat','algorithm','scope']);
  valueFormByName(params, ['jobName', 'email', 'inputSupport', 'input', 'universe']);
  if (params.universe.length > 1) {
    document.querySelector('button.toggle').click();
  }
  changeLimits();
}

function disableAllannotDownBtns(able) {
  let annotDownBtns = [...document.getElementsByClassName("annotDownBtn")];
  annotDownBtns.map(function(annotDownBtn) {
    annotDownBtn.disabled = able;
  });
}

function allowannotDownBtns() {
  disableAllannotDownBtns(true);
  let taxid = document.getElementsByName('taxid')[0].value
  if (taxid == 'all') {
    disableAllannotDownBtns(false);
  } else {
    let annotIDs = orgsAnnots[taxid];
    annotIDs.map(function(annotID) {
      document.getElementsByName(annotID)[0].disabled = false;
    });
  }
}
// FORM HANDLER // FORM HANDLER // FORM HANDLER // FORM HANDLER // FORM HANDLER

// VALIDATION // VALIDATION // VALIDATION // VALIDATION // VALIDATION // VALIDATION
function isDisabled(test) {
  return (test.disabled === true);
}

function isChecked(test) {
  return (test.checked === true);
}

function isUnChecked(test) {
  return (test.checked === false);
}

function isFalse(test) {
  return (test === false);
}

function validateCheckBoxes(name, id) {
  let selected = document.querySelectorAll(`[name="${name}"]:checked`).length;
  if (selected >= 1) {
    removeWarning(id, name);
    return (true);
  }
  raiseWarning(id, name, 'Select at least one');
  return (false);
}

function reOpenRestAnnots(annots) {
  let orgid = getOrgSelected().taxid;
  enableAnotsByOrgValue(orgid);
  annots.map(function(annot) {
    annot.disabled = false;
    annot.checked = true;
  });
}

function limitCheckBoxes(limit = 2) {
  let coannotation = document.getElementById('coannotation_yes').checked;
  var annots = [...document.querySelectorAll(`[name="annotations"]:checked`)];
  if (!coannotation) {
    disableAnnotsByInputType();
    checkAnnotsEnabled(annots);
    return;
  }
  let len = countAnnotSelected();
  if (len >= limit) {
    disableAllAnots();
    annots.slice(0, 2).map(function(annot) {
      annot.disabled = false;
    });
  } else {
    disableAnnotsByInputType();
  }
  checkAnnotsEnabled(annots);
  countAnnotSelected();
  disableAnotsLabels();
}

function countAnnotSelected() {
  let len = document.querySelectorAll('[name="annotations"]:checked').length;
  let coannotation = document.getElementById('coannotation_yes').checked;
  var annotcounter = ` (${len}/2)`;
  if (!coannotation) {
    var annotcounter = ''
  };
  document.getElementById('annotscounter').innerText = ` ${annotcounter}`;
  return (len);
}

function changeLimits() {
  let coannotation = document.getElementById('coannotation_yes').checked;
  if (coannotation) {
    document.getElementById('limitbtn1').style.display = '';
    document.getElementById('limitbtn2').style.display = '';
    document.getElementById('fpgrowth').parentElement.className = 'pr-5';
    document.getElementById('fpgrowth').checked = true;
    document.getElementById('fpmax').parentElement.className = 'pr-5';
    document.getElementById('fpmax').checked = false;
    document.getElementById('fpgrowth').disabled = false;
    document.getElementById('fpmax').disabled = false;
    document.getElementById('inputSupport').disabled = false;
    document.getElementById('inputSupport').value = '10';
    document.getElementById('selectallbtns').style.display = 'none';
  } else {
    document.getElementById('limitbtn1').style.display = 'none';
    document.getElementById('limitbtn2').style.display = 'none';
    document.getElementById('fpgrowth').parentElement.className = 'is-disabled pr-5';
    document.getElementById('fpgrowth').checked = false;
    document.getElementById('fpmax').parentElement.className = 'is-disabled pr-5';
    document.getElementById('fpmax').checked = false;
    document.getElementById('fpgrowth').disabled = true;
    document.getElementById('fpmax').disabled = true;
    document.getElementById('inputSupport').disabled = true;
    document.getElementById('inputSupport').value = '-';
    document.getElementById('selectallbtns').style.display = '';
  }
  limitCheckBoxes();
  addCounter();
}

function validateTextBox(name, id, limit = null) {
  let textBox = document.getElementsByName(name)[0];
  if (textBox.value == '') {
    raiseWarning(name, id, 'Introduce your query list');
    textBox.scrollIntoView();
    return (false);
  }
  let coannotation = document.getElementById('coannotation_yes').checked;
  if (coannotation) {
    if (limit != null) {
      var len = inputCounter(name);
      if (len > limit) {
        raiseWarning(name, id, 'The limit of 1000 elements has been passed');
        textBox.scrollIntoView();
        return (false);
      }
    }
  }
  removeWarning(name, id);
  return (true);
}

function fitToLimit(name) {
  let textBox = document.getElementsByName(name)[0];
  let input = textBox.value.split(/\r?\n/).filter(e => e !== '').slice(0, 1000);
  document.getElementsByName(name)[0].value = input.join("\n");
  addCounter();
}

function addCounter() {
  let coannotation = document.getElementById('coannotation_yes').checked;
  var lentxt = '';
  var len2txt = '';
  if (coannotation) {
    var len = inputCounter('input');
    var lentxt = `(${len}/1000)`;
    let iscomparative = document.getElementById('comparative').checked;
    if (iscomparative) {
      var len2 = inputCounter('input2');
      var len2txt = ` - (${len2}/1000)`;
    }
  }
  document.getElementById("inputcounter").innerText = `${lentxt}${len2txt}`;
  countAnnotSelected();
}

function inputCounter(name) {
  let textBox = document.getElementsByName(name)[0];
  var len = 0;
  if (textBox.value != "") {
    let inputelements = textBox.value.split(/\r?\n/);
    var len = inputelements.filter(e => e !== '').length;
  }
  return (len);
}

function validateTextBoxes() {
  let validators = [validateTextBox('input', 'input', 1000)];
  let customuniverse = document.getElementsByName('universe')[0].value;
  if (customuniverse != '') {
    validators.push(validateTextBox('universe', 'universe'));
  }
  let comparative = document.getElementById('comparative').checked;
  if (comparative) {
    validators.push(validateTextBox('input2', 'input', 1000));
  }
  if (validators.some(isFalse)) {
    return (false);
  }
  return (true);
}

function validateForm() {
  let annotations = validateCheckBoxes('annotations', 'annotationsrow');
  let textBox = validateTextBoxes();
  let email = validateEmail('email', '');
  let validators = [annotations, textBox, email];
  if (validators.some(isFalse)) {
    return (false);
  }
  sendData();
  return (true);
}

function validateEmail() {
  let mailregex = /[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/;
  emailstr = document.getElementsByName('email')[0].value;
  if (emailstr == '') {
    removeWarning('email', '');
    return (true);
  }
  if (!mailregex.test(emailstr)) {
    raiseWarning('email', '', 'Introduce a valid email');
    return (false);
  } else {
    removeWarning('email', '');
    return (true);
  }
}

function raiseMaintenance() {
  document.getElementById('analysis').innerHTML = "\
  <div class='notification is-warning'>{}<p>\
  We are carrying out maintance tasks, excuse the inconveniences.\
  </p></div>";
}

function raiseWarning(name, id, msg) {
  var classtowarn = document.getElementsByName(name)[0].className;
  if (!classtowarn.includes('warningsquare')) {
    document.getElementsByName(name)[0].className = classtowarn.concat(' warningsquare');
    var title = document.getElementsByName(name)[0];
    var newid = name;
  }
  if (id != '') {
    var classtowarn = document.getElementById(id).className;
    if (!classtowarn.includes('warningtitle')) {
      document.getElementById(id).className = classtowarn.concat(' warningtitle');
    }
    var title = document.getElementById(id);
    var newid = id;
  }
  var newid = newid.concat('warningtext');
  var elementExists = document.getElementById(newid);
  if (!elementExists) {
    var text = document.createElement('p');
    text.id = newid
    text.innerText = msg;
    text.className = 'warningtext';
    title.insertAdjacentElement('afterend', text);
  } else {
    elementExists.innerText = msg;
  }
}

function removeWarning(name, id) {
  if (id != '') {
    let originalClass = document.getElementById(id).className.replace(' warningtitle', '');
    document.getElementById(id).className = originalClass;
    var newid = id.concat('warningtext');
    var elementExists = document.getElementById(newid);
    if (!!elementExists) {
      document.getElementById(newid).remove()
    }
  } else {
    var newid = name.concat('warningtext');
    var elementExists = document.getElementById(newid);
    if (!!elementExists) {
      document.getElementById(newid).remove()
    }
  }
  let originalClass = document.getElementsByName(name)[0].className.replace(' warningsquare', '');
  document.getElementsByName(name)[0].className = originalClass;
}
// VALIDATION // VALIDATION // VALIDATION // VALIDATION // VALIDATION // VALIDATION

// TABS Navigation // TABS Navigation // TABS Navigation // TABS Navigation
function closeTabs(button) {
    let alltabs = [...button.parentElement.nextElementSibling.children];
    for (i = 0; i < alltabs.length; i++) {
        alltabs[i].className = 'tabcontent hidden';
    }
    let tabbtns = [...button.parentElement.children];
    for (i = 0; i < tabbtns.length; i++) {
        if (tabbtns[i].className == 'tab hidden'){
          continue
        };
        tabbtns[i].className = 'tab';
    };
};

function openTab2(evt, tabID){
  let button = evt.currentTarget;
  let btnclassname = button.className;
  closeTabs(button);
  button.className = 'tab active';
  let alltabs = [...button.parentElement.nextElementSibling.children];
  for (i = 0; i < alltabs.length; i++) {
      if (alltabs[i].id == tabID){
        checkEnvironment(tabID);
        alltabs[i].className = 'tabcontent';
      };
  };
  try{
    var datatablesearches = document.querySelectorAll(`[type="search"]`);
    for(let i=0,l=datatablesearches.length;i<l;i++){
      datatablesearch = datatablesearches[i];
      datatablesearch.value = 'a';
      datatablesearch.dispatchEvent(new Event("input"));
      datatablesearch.value = '';
      datatablesearch.dispatchEvent(new Event("input"));
    }
  }catch{
    document.querySelector('.tertiary > .active').click();
  };
};

async function downResults(results,wordcloud="False"){
  getResults(results,download=true);
}


function openTab(evt, tabID) {
  let button = evt.currentTarget;
  if (button.parentElement.className.includes('panel-tabs')) {
    var tabbuttons = [...button.parentElement.children];
  } else if (button.className.includes('panel-block')) {
    var tabbuttons = [...button.parentElement.querySelectorAll(".panel-block")];
    var visopts = [...button.parentElement.parentElement.querySelectorAll('[id$="opts"]')];
  } else {
    var tabbuttons = [...button.parentElement.parentElement.children];
  }
  let target = document.getElementById(tabID);
  let tabscontent = [...target.parentNode.children];
  for (i = 0; i < tabscontent.length; i++) {
    tabscontent[i].style = "display:none;";
    try {
      visopts[i].style = "display:none;";
    } catch {}
  }
  for (i = 0; i < tabbuttons.length; i++) {
    tabbuttons[i].className = tabbuttons[i].className.replace('is-active', '');
  }
  if (button.parentElement.className.includes('panel-tabs')){
    button.className = button.className.concat(' is-active');
    target.querySelector('.panel-block').click();
  }
  if (button.className.includes('panel-block')) {
    button.className = button.className.concat(' is-active');
  } else {
    button.parentElement.className = button.parentElement.className.concat(' is-active');
  }
  document.getElementById(tabID).style = "";
  if (button.className.includes('panel-block')) {
    try {
      createDataTable(`#${tabID.replace('div','table')}`);
      document.getElementById(tabID.replace('div','opts')).style = "";
    } catch {
      console.log('no table found');
    }
  }
};

function createDataTable(tabID) {
  $(document).ready(function() {
    $(`${tabID}`).DataTable({
      order: [
        [5, "asc"]
      ],
      scrollY: "150px",
      scrollX: true,
      scrollCollapse: true,
      paging: false,
      retrieve: true,
      fixedColumns: true,
      bInfo: false
    }).columns.adjust().draw();
  });
}

function showList(mylist) {
  let mylistStr = mylist.join("\n");
  let tab = window.open('about:blank', '_blank');
  tab.document.write(`<pre style="word-wrap: break-word; white-space: pre-wrap;">${mylistStr}</pre>`);
  tab.document.close();
}
// TABS Navigation // TABS Navigation // TABS Navigation // TABS Navigation

// FORM SENDING // FORM SENDING // FORM SENDING // FORM SENDING // FORM SENDING

async function transformirnas(){
  var action = document.getElementsByName('mirconverteraction')[0].value
  var target = document.getElementsByName('mirconvertertarget')[0].value
  var input1 = document.getElementsByName('input')[0].value;
  var input1 = input1.replace(/ /g, '').replace(/\r?\n/g,',');
  var input2 = document.getElementsByName('input2')[0].value;
  if (input2 != '') {
    let input2 = input2.replace(/ /g, '').replace(/\r?\n/g,',');
    var endpoint = `API_URL/mirnas?mirnas=${input2}&action=${action}&target=${target}`;
    try {
      const response = await fetch(endpoint, {
        method: 'get'
      });
      if (response.ok) {
        var mytxt = await response.text();
        document.getElementsByName('input2')[0].value = mytxt;
      } else {
        serverIsDown('response not ok getGC4uid',mytxt);
      }
    } catch {
      serverIsDown('catch getGC4uid',mytxt);
    }
  };
  var endpoint = `API_URL/mirnas?mirnas=${input1}&action=${action}&target=${target}`;
  try {
    const response = await fetch(endpoint, {
      method: 'get'
    });
    if (response.ok) {
      var mytxt = await response.text();
      document.getElementsByName('input')[0].value = mytxt;
    } else {
      serverIsDown('response not ok getGC4uid',mytxt);
    }
  } catch {
    serverIsDown('catch getGC4uid',mytxt);
  }
}

function openTabResults(){
  document.querySelector('#resultstab').style.display = '';
  document.querySelector('#results').style.display = '';
  document.querySelector('#resultstab').children[0].click();
}

function loadWaiting(gc4uid) {
  var waitHTML = `
    <div class="tile is-vertical" id="waiting">\
    <p id="jobticket">\
        Use this link, \
        <a class="genyoLink" href="API_URL/job=${gc4uid}">API_URL/job=${gc4uid}</a>, \
        to recover your job when it is \
        finished and also to inform us \
        in case of any issue.\
    </p>\
    <figure class="image p-4">\
      <img style="width:40%;height:auto;margin:auto;" src="assets/images/dnawaiting.gif">\
    </figure>\
    <pre id="statep">1 - Creating job...</pre>\
    </div>`;
    document.getElementById('results').innerHTML = waitHTML;
    openTabResults();
}

function finishWaiting() {
  document.getElementById('waiting').remove();
}

function serverIsDown(msg,jobticket) {
  let mytxt = `<div class='notification is-warning'><p>\
    Please send the job ticket ${jobticket} to bioinfo@genyo.es, the server found an unexpected \
    error. We will solve it as soon as possible.\
    </p></div>`;
  finishWaiting();
  document.getElementById('results').innerHTML = mytxt;
  console.log(msg);
}

function cleanData(object) {
  if (object.algorithm == null){
    object.algorithm = 'fpgrowth';
  }
  if (object.inputSupport != null){
    object.inputSupport = parseInt(object.inputSupport);
  }else{
    object.inputSupport = 0;
  }
  object.organism = parseInt(object.organism);
  let input1 = object.input.replace(/ /g, '');
  input1 = input1.split(/\r?\n/).filter(function(ele) {
    return ele != '';
  });
  if (object.input2 != '') {
    let input2 = object.input2.replace(/ /g, '');
    input2 = input2.split(/\r?\n/).filter(function(ele) {
      return ele != '';
    });
    object.input = {
      "input": input1,
      "input2": input2
    };
    object.inputName = object.inputName != '' ? object.inputName : 'input1';
    object.input2Name = object.input2Name != '' ? object.input2Name : 'input2';
    object.inputNames = {
      "input": object.inputName.replace(/[\W]+/g, "_"),
      "input2": object.input2Name.replace(/[\W]+/g, "_")
    };
  } else {
    object.input = {
      "input": input1
    };
    object.jobName = object.jobName != '' ? object.jobName.replace(/[\W]+/g, "_") : 'input1';
    object.inputNames = {
      "input1unique": object.jobName.replace(/[\W]+/g, "_")
    };
  };
  if (object.universe == ''){
    object.universe = [];
  }else{
    object.universe = object.universe.replace(/ /g, '');
    object.universe = object.universe.split(/\r?\n/).filter(function(ele) {
      return ele != '';
    });
  }
  if (Object.prototype.toString.call(object.annotations) === "[object String]") {
    object.annotations = [object.annotations]
  };
  delete object.input2;
  delete object.inputName;
  delete object.input2Name;
  delete object.mirconvertertarget;
  delete object.mirconverteraction;
  return object;
}

function form2CleanObj() {
  const form = document.getElementById('gc4form');
  const formdata = new FormData(form);
  let object = {};
  formdata.forEach(function(value, key) {
    if (key in object) {
      var current = object[key];
      if (!Array.isArray(current)) {
        current = object[key] = [current];
      }
      current.push(value);
    } else {
      object[key] = value;
    }
  });
  return cleanData(object);
};

async function getGC4uid() {
  try {
    const response = await fetch("API_URL/createjob", {
      method: 'get'
    });
    if (response.ok) {
      const mytxt = await response.text();
      return (mytxt);
    } else {
      serverIsDown('response not ok getGC4uid',mytxt);
    }
  } catch {
    serverIsDown('catch getGC4uid',mytxt);
  }
}

async function getstate(gc4uid) {
  try {
    var response = await fetch(`API_URL/checkstate?job=${gc4uid}`, {
      method: 'get'
    });
    var state = await response.text();
    var state = await JSON.parse(state);
    return (state);
  } catch {
    serverIsDown('not ok getstate',gc4uid);
  }
}

async function checkstate(gc4uid) {
  var status = await getstate(gc4uid);
  while (status.state == "PENDING") {
    document.getElementById('statep').innerText = status.log;
    var status = await getstate(gc4uid);
    await new Promise(r => setTimeout(r, 5000));
  }
  toJobURL(gc4uid);
}

function toJobURL(gc4uid) {
  window.open(`API_URL/analysisResults?job=${gc4uid}`, "_self");
}

async function sendData(relaunch = false) {
  document.getElementById('results').innerHTML = '';
  let data = form2CleanObj();
  if (relaunch == false) {
    let gc4uid = await getGC4uid();
    data.gc4uid = gc4uid;
  } else {
    data.gc4uid = window.location.href.split("=")[1];
  }
  loadWaiting(data.gc4uid);
  try {
    fetch("API_URL/analysis", {
      method: 'post',
      body: JSON.stringify(data),
      headers: {
        'Content-Type': 'application/json',
      }
    });
    await new Promise(r => setTimeout(r, 8000));
    toJobURL(data.gc4uid);
  } catch {
    serverIsDown('catch sendData',data.gc4uid);
  }
}

async function downloadAnnot(annot) {
  const nomen = document.getElementsByName('nomenclature')[0].value;
  const org = document.getElementsByName('taxid')[0].value;
  const endpoint = `API_URL/database?annotation=${annot.toLowerCase()}&nomenclature=${nomen}&organism=${org}`
  try {
    window.open(endpoint, "_self");
  } catch {
    serverIsDown('catch downloadAnnot','');
  }
}

async function getResults(annotation,download=false) {
  const jobticket = window.location.href.split("job=")[1];
  const endpoint = `API_URL/results?job=${jobticket}&annotation=${annotation}`
  if (download){
    window.open(endpoint.concat('&download=True'), "_self");
  }else{
    var resp = await fetch(endpoint);
    var tsvtxt = await resp.text();
    let mydata = await d3.tsvParse(tsvtxt, conversor);
    return mydata;
  }
};

function checkEnvironment(){
  if (window.location.href.includes('devgenecodis') || window.location.href.includes('localhost')) {
    if (document.getElementById("devwarning") != null) {
      document.getElementById("devwarning").remove();
    }
    var para = document.createElement("div");
    para.id = 'devwarning';
    para.className = "notification is-warning mb-0";
    para.innerHTML = "<p>Please be informed, this is \
    beta version of GeneCodis 4.</p>"
    var sibling = document.getElementsByClassName('hero-head')[0];
    sibling.parentNode.insertBefore(para, sibling.nextSibling);
    var meta = document.createElement('meta');
    meta.name = "robots";
    meta.content = "noindex";
    document.getElementsByTagName('head')[0].appendChild(meta);
  }
}

////////////////////////////////////////////////////////////////////////////////
////////////////////////// D3 implementations patata!///////////////////////////
////////////////////////////////////////////////////////////////////////////////
function conversor(d) {
  return d3.autoType(d);
}

function creatHoVar(id, datafiltered) {
  var allSizes = {
    big: {
      width: 1000,
      height: 1000,
      margin: {
        top: 10,
        right: 10,
        bottom: 10,
        left: 10
      },
      padding: 0.3
    }
  };
  var sizes = allSizes.big,
    margin = sizes.margin,
    padding = sizes.padding
  sizes.height = datafiltered[datafiltered.length - 1].barheight;
  var width = sizes.width,
    height = sizes.height;
  var xClass = "axis axis--x",
    yClass = "axis axis--y";

  // svg-box
  // place for the future chart. Includes chart body, legend, and axes

  var chart1 = d3.select(`#${id}`)
    .append("svg")
    .attr("id", `${id}svg`)
    .attr("width", '100%')
    .attr("height", "auto")
    .attr("viewBox", `0 0 ${width} ${height + 60}`)
    .attr("xmlns", "http://www.w3.org/2000/svg");

  var y = d3.scaleBand().rangeRound([0, height]).padding(padding),
    x = d3.scaleLinear().rangeRound([0, width]);

  // chart boby
  var g = chart1.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // axes-X (object)
  var axesX = g.append("g")
    .attr("class", xClass)
    .attr("transform", "translate(100," + height + ")");

  // axes-Y (object)
  var axesY = g.append("g")
    .attr("class", yClass)
    .attr("transform", "translate(100,0)");
  // X-axes text
  chart1.append("text")
  .attr("y", height + 50)
  .attr("x", width / 2 + 70)
  .text("-log10(Pval Adj)")
  .style("font-size", "15px")

  y.domain(datafiltered.map(function(d) {
    return d.description;
  }));
  var maxVal = d3.max(datafiltered, function(d) {
    return d.logPval;
  });
  x.domain([0, maxVal]);

  // xAxes, yAxes (axes)
  var xAxes = d3.axisBottom(x);
  var yAxes = d3.axisLeft(y).tickValues([]);

  // append data to axes
  axesX.call(xAxes);
  axesY.call(yAxes);
  // .selectAll(".tick text")
  // .call(d3.util.wrap, margin.left);

  var rangeValues = datafiltered.map(function(d) {
    return d.genes_found
  });
  var myColorbc = d3.scaleLinear().domain([d3.min(rangeValues), d3.max(rangeValues)]).range(["#ffbaba", "#ed2939"]);
  var uColor = rangeValues.filter(onlyUnique);
  var seq_color = [];
  var min_genes = d3.min(uColor);
  var max_genes = d3.max(uColor);
  for (var i = min_genes; i <= max_genes; i++) {
    seq_color.push(i);
  }
  seq_color.sort((a, b) => b - a);

  var tooltip = d3.select(`#${id}`).append("div").attr("class", "toolTip");

  // bar for each data element
  g.selectAll(".bar")
    .data(datafiltered)
    .enter().append("rect")
    .attr('x', width / 50)
    .attr('y', height / 250)
    .attr("class", "bar")
    .attr("x", 100)
    .attr("y", function(d) {
      return y(d.description);
    })
    .attr("width", function(d) {
      return x(d.logPval);
    })
    .attr("height", y.bandwidth())
    .attr("fill", function(d) {
      return myColorbc(d.genes_found)
    })
    .append("title")
    .text(function(d) {
      return "Term: " + d.description + '\nPval Adj: ' + d.pval_adj + "\nGenes: " + d.genes;
    })
    .attr('x', width / 50)
    .attr('y', height / 250);

  var tt = 80;
  var truncated_text = datafiltered.map(function(d) {
    return d.description;
  });
  for (var i = 0; i < truncated_text.length; i++) {
    if (truncated_text[i].length > tt) {
      datafiltered[i].truncated_text = truncated_text[i].substr(0, tt) + "...";
    } else {
      datafiltered[i].truncated_text = truncated_text[i];
    }
  }

  var fontsize = datafiltered[datafiltered.length - 1].fontsize

  g.selectAll("tt")
    .data(datafiltered)
    .enter().append("text")
    .attr("x", 100)
    .attr("y", function(d) {
      return y(d.description) + y.bandwidth() / 2;
    })
    .text(function(d, i) {
      return d.truncated_text;
    })
    .attr("font-size", `${fontsize}px`);

  var svgLegend = chart1.append('svg')
    .attr("width", 200);
  var defs = svgLegend.append('defs');

  // append a linearGradient element to the defs and give it a unique id
  var linearGradient = defs.append('linearGradient')
    .attr('id', `lg${id}`);

  // horizontal gradient
  linearGradient
    .attr("x1", "0%")
    .attr("y1", "0%")
    .attr("x2", "0%")
    .attr("y2", "100%");

  // append multiple color stops by using D3's data/enter step
  linearGradient.selectAll("stop")
    .data([{
        offset: "0%",
        color: "#ed2939"
      },
      {
        offset: "100%",
        color: "#ffbaba"
      }
    ])
    .enter().append("stop")
    .attr("offset", function(d) {
      return d.offset;
    })
    .attr("stop-color", function(d) {
      return d.color;
    });


  // draw the rectangle and fill with gradient
  svgLegend.append("rect")
    .attr("x", 50)
    .attr("y", 30)
    .attr("width", 20)
    .attr("height", 150)
    .style("fill", `url(#lg${id})`);

  svgLegend.append("text")
    .attr("x", 75)
    .attr("y", 35)
    .text(max_genes);

  svgLegend.append("text")
    .attr("x", 75)
    .attr("y", 185)
    .text(min_genes);

  svgLegend
    .attr("class", "axis")
    .append("g")
    .attr("transform", "translate(0, 40)");

  var legendTitle = chart1.append("text")
    .attr("transform", "translate(20,175) rotate(270)")
    .attr("dy", ".35em")
    .text("Number of genes");

  function onlyUnique(value, index, self) {
    return self.indexOf(value) === index;
  }
};

//////////////////////////////////////////////////////////////////

function createNetwork(id, datafiltered, genesShow,geneLabelShow,
  laChSt = -10, laLiDis = 10, laLiSt = 2,
  noChSt = -200, noLiDis = 20, noLiSt = 1,
  xSt = 0.1, ySt = 0.1) {
  var allSizes = {
    big: {
      width: 1000,
      height: 1000,
      margin: {
        top: 10,
        right: 20,
        bottom: 10,
        left: 20
      },
      padding: 0.3
    }
  };
  var sizes = allSizes.big,
    margin = sizes.margin,
    padding = sizes.padding;
  sizes.height = datafiltered[datafiltered.length - 1].barheight
  var
    width = sizes.width - margin.left - margin.right,
    height = sizes.height - margin.top - margin.bottom;
  var xClass = "axis axis--x",
    yClass = "axis axis--y";

  var nodes = [],
    links = [];
  var initialScaleData = datafiltered.map(function(d) {
    return +d.logPval
  });
  initialScaleData.push(5);
  initialScaleData.push(10);
  var min_value_size = d3.min(initialScaleData);
  var max_value_size = d3.max(initialScaleData);
  var newScaledData = [];
  var linearScale = d3.scaleLinear().domain([min_value_size, max_value_size]).range([5, 10]);
  var logPvals = datafiltered.map(function(d) {
    return +d.logPval;
  });
  var terms = datafiltered.map(function(d) {
    return d.description;
  });
  var pvals = datafiltered.map(function(d) {
    return +d.pval_adj;
  })
  var genes = datafiltered.map(function(d) {
    return d.genes;
  });
  var genes_found = datafiltered.map(function(d) {
    return d.genes_found;
  });
  for (var i = 0; i < logPvals.length; i++) {
    nodes.push({
      "description": terms[i].trimStart(),
      "group": 1,
      "pval": pvals[i],
      "size": linearScale(logPvals[i]),
      'genes': genes[i],
      "col": genes_found[i],
      "id": terms[i].trimStart().replace(/[\W_]+/g, '')
    });
    gene = genes[i].split(",");
    for (var j = 0; j < gene.length; j++) {
      nodes.push({
        "description": gene[j].trimStart(),
        "group": 2,
        "pval": 1,
        "size": 2,
        'genes': 0,
        "id": gene[j].trimStart().replace(/[\W_]+/g, '')
      })
      links.push({
        "source": terms[i].trimStart(),
        "target": gene[j].trimStart()
      })
    }
  }

  var obj = {};
  for (var i = 0, len = nodes.length; i < len; i++) {
    obj[nodes[i]['description']] = nodes[i];
  }
  nodes = [];
  for (var key in obj) {
    nodes.push(obj[key]);
  }

  var graph = {
    "nodes": nodes,
    "links": links
  };
  var label = {
    'nodes': [],
    'links': []
  };

  graph.nodes.forEach(function(d, i) {
    label.nodes.push({
      node: d
    });
    label.nodes.push({
      node: d
    });
    label.links.push({
      source: i * 2,
      target: i * 2 + 1
    });
  });

  var labelLayout = d3.forceSimulation(label.nodes)
    .force("charge", d3.forceManyBody().strength(laChSt))
    .force("link", d3.forceLink(label.links).distance(laLiDis).strength(laLiSt));

  var graphLayout = d3.forceSimulation(graph.nodes)
    .force("charge", d3.forceManyBody().strength(noChSt))
    .force("center", d3.forceCenter(width / 2, height / 2)) // make network always return to center
    .force("link", d3.forceLink(graph.links).id(function(d) {
      return d.description;
    }).distance(20).strength(1))
    .force("x", d3.forceX(width / 2).strength(xSt))
    .force("y", d3.forceY(height / 2).strength(ySt))
    .on("tick", ticked);

  var adjlist = [];

  graph.links.forEach(function(d) {
    adjlist[d.source.index + "-" + d.target.index] = true;
    adjlist[d.target.index + "-" + d.source.index] = true;
  });

  function neigh(a, b) {
    return a == b || adjlist[a + "-" + b];
  }

  var chart3 = d3.select(`#${id}`)
      .append("svg")
      .attr("id", `${id}svg`)
      .attr("width", '100%')
      .attr("height", "auto")
      .attr("viewBox", `0 0 ${width} ${height+10}`)
      .attr("xmlns", "http://www.w3.org/2000/svg");

  var container = chart3.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var zoom = d3.zoom().scaleExtent([.1, 8]).on("zoom", function() { container.attr("transform", d3.event.transform); })
  chart3.call(zoom).on("dblclick.zoom", null);


  if (genesShow == true) {
    var link = container.append("g").attr("class", "links")
      .selectAll("line")
      .data(graph.links)
      .enter()
      .append("line")
      .attr("stroke", "#aaa")
      .attr("stroke-width", "0.5px");
  } else {
    var link = container.append("g").attr("class", "links")
      .selectAll("line")
      .data(graph.links)
      .enter()
      .append("line")
      .attr("stroke", "#aaa")
      .attr("stroke-width", "0.5px")
      .attr("opacity", 0);
  }

  var rangeValues = graph.nodes.map(function(d) {
    return d.size
  });
  rangeValues = rangeValues.filter(function(element) {
    return element !== undefined;
  });

  var myColornt = d3.scaleLinear().domain([d3.min(genes_found), d3.max(genes_found)]).range(["#bdd2ff", "#5688f0"]);

  if (genesShow == true) {
    var node = container.append("g").attr("class", "nodes")
      .selectAll("g")
      .data(graph.nodes)
      .enter()
      .append("circle")
      .attr("r", function(d) {
        if (d.group == 1) {
          return d.size;
        } else {
          return 3;
        }
      })
      .attr("fill", function(d) {
        if (d.group == 1) {
          return myColornt(d.col);
        } else {
          return "orange"
        }
      })
  } else {
    var node = container.append("g").attr("class", "nodes")
      .selectAll("g")
      .data(graph.nodes)
      .enter()
      .append("circle")
      .attr("r", function(d) {
        if (d.group == 1) {
          return d.size;
        } else {
          return 3;
        }
      })
      .attr("fill", function(d) {
        if (d.group == 1) {
          return myColornt(d.col);
        } else {
          return "orange"
        }
      })
      .attr("opacity", function(d) {
        if (d.group == 1) {
          return 1;
        } else {
          return 0
        }
      });
  }
    node.append("title")
      .text(function(d) {
        if (d.group == 1) {
          return "Term: " + d.description + '\nPval Adj: ' + d.pval + "\nGenes: " + d.genes;
        } else {
          return d.description
        }
      })
      .attr('x', width / 50)
      .attr('y', height / 250);

  if (genesShow == true) {

    if (geneLabelShow == true){

      var node2neighbors = {};
      var clickableNodes = [];
      for (var i =0; i < graph.nodes.length; i++){
        var name = graph.nodes[i].id;
        clickableNodes.push(name);
        node2neighbors[name] = graph.links.filter(function(d){
          return d.source.id == name || d.target.id == name;
        }).map(function(d){
          return d.source.id == name ? d.target.id : d.source.id;
        });
      }

      node.on("click", function(n){
        // Determine if current node's neighbors and their links are visible
        var active   = n.active ? false : true; // toggle whether node is active
        var newOpacity = active ? 1 : 0;

        // Extract node's name and the names of its neighbors
        var name  = n.id;
        var neighbors  = node2neighbors[name];
        for (var i = 0; i < neighbors.length; i++){
          d3.select(`text#${id}${neighbors[i]}`).transition()
          .duration(750)
          .style("opacity", newOpacity);
        }

        d3.select(`text#${id}${name}`).transition()
        .duration(750)
        .style("opacity", newOpacity);

        // d3.select("#"+ name).transition()
        // .duration(750)
        // .style("opacity", newOpacity);
        // Update whether or not the node is active
        n.active = active;
      });
    } else{
      var node2neighbors = {};
      var clickableNodes = [];
      for (var i =0; i < graph.nodes.length; i++){
        var name = graph.nodes[i].id;
        clickableNodes.push(name);
        node2neighbors[name] = graph.links.filter(function(d){
          return d.source.id == name || d.target.id == name;
        }).map(function(d){
          return d.source.id == name ? d.target.id : d.source.id;
        });
      }

      node.on("click", function(n){
        // Determine if current node's neighbors and their links are visible
        var active   = n.active ? false : true; // toggle whether node is active
        var newOpacity = active ? 1 : 0;

        // Extract node's name and the names of its neighbors
        var name  = n.id;
        var neighbors  = node2neighbors[name];

        d3.select(`text#${id}${name}`).transition()
        .duration(750)
        .style("opacity", newOpacity);

        // d3.select("#"+ name).transition()
        // .duration(750)
        // .style("opacity", newOpacity);
        // Update whether or not the node is active
        n.active = active;
      });
    }
  }

  if (genesShow == true) {
    var geneopacity = 0;
  }else{
    var geneopacity = 1;
  }

  var labelNode = container.append("g").attr("class", "labelNodes")
    .selectAll("text")
    .data(label.nodes)
    .enter()
    .append("text")
    .text(function(d, i) {
      return i % 2 == 0 ? "" : d.node.description;
    })
    .style("fill", function(d) {
      if (d.node.group == 1) {
        return '#000';
      } else {
        return '#555';
      }
    })
    .style("font-family", "Arial")
    .style("font-size", function(d) {
      if (d.node.group == 1) {
        return '11px';
      } else {
        return '9px';
      }
    })
    .style("opacity", function(d) {
      if (d.node.group == 1) {
        return geneopacity;
      } else {
        return 0
      }
    })
    .style("pointer-events", "none");

  // to prevent mouseover/drag capture

  function ticked() {
    node.attr("transform", function(d) {
      return "translate(" + fixna(Math.max(d.size, Math.min(width - d.size, d.x))) + "," + fixna(Math.max(100, Math.min(height - d.size, d.y))) + ")";
    });
    link.attr("x1", function(d) {
        return fixna(Math.max(3, Math.min(width - 3, d.source.x)));
      })
      .attr("y1", function(d) {
        return fixna(Math.max(100, Math.min(height - 3, d.source.y)));
      })
      .attr("x2", function(d) {
        return fixna(Math.max(3, Math.min(width - 3, d.target.x)));
      })
      .attr("y2", function(d) {
        return fixna(Math.max(100, Math.min(height - 3, d.target.y)));
      });

    labelLayout.alphaTarget(0.3).restart();
    //arrangeLabels(labelNode);

    labelNode.each(function(d, i) {
      if (i % 2 == 0) {
        d.x = d.node.x;
        d.y = d.node.y;
      } else {
        var b = this.getBBox();
        var diffX = d.x - d.node.x;
        var diffY = d.y - d.node.y;

        var dist = Math.sqrt(diffX * diffX + diffY * diffY);

        var shiftX = b.width * (diffX - dist) / (dist * 2);
        shiftX = Math.max(-b.width, Math.min(0, shiftX));
        var shiftY = 16;
        this.setAttribute("transform", "translate(" + shiftX + "," + shiftY + ")");
        this.setAttribute("id",id+d.node.id);
      }
    });

    labelNode.attr("transform", function(d) {
      return "translate(" + fixna(d.x) + "," + fixna(d.y) + ")";
      // return "translate(" + fixna(Math.max(3, Math.min(width - 3, d.x))) + "," + fixna(Math.max(100, Math.min(height - 3, d.y))) + ")";
    });
  }

  function fixna(x) {
    if (isFinite(x)) return x;
    return 0;
  }

  function focus(d) {
    var index = d3.select(d3.event.target).datum().index;
    // node.style("opacity", function(o) {
    //   return neigh(index, o.index) ? 1 : 0.1;
    // });
    labelNode.attr("display", function(o) {
      return neigh(index, o.node.index) ? "block" : "none";
    });
    // link.style("opacity", function(o) {
    //   return o.source.index == index || o.target.index == index ? 1 : 0.1;
    // });
    labelNode.style("opacity", 1);
  }

  function unfocus() {
    labelNode.attr("display", "block");
    labelNode.style("opacity", 0.7);
    node.style("opacity", 1);
    link.style("opacity", 1);
  }

  function updateLink(link) {
    link.attr("x1", function(d) {
        return fixna(Math.max(3, Math.min(width - 3, d.source.x)));
      })
      .attr("y1", function(d) {
        return fixna(Math.max(3, Math.min(height - 3, d.source.y)));
      })
      .attr("x2", function(d) {
        return fixna(Math.max(3, Math.min(width - 3, d.target.x)));
      })
      .attr("y2", function(d) {
        return fixna(Math.max(3, Math.min(height - 3, d.target.y)));
      });
  }

  function updateNode(node) {
    node.attr("transform", function(d) {
      return "translate(" + fixna(Math.max(d.size, Math.min(width - d.size, d.x))) + "," + fixna(Math.max(d.size, Math.min(height - d.size, d.y))) + ")";
      //return "translate(" + fixna(d.x) + "," + fixna(d.y) + ")";
    });
    //    node.attr("cx", function(d) { return d.x = Math.max(radius, Math.min(width - radius, d.x)); })
    //        .attr("cy", function(d) { return d.y = Math.max(radius, Math.min(height - radius, d.y)); });
  }

  function dragstarted(d) {
    d3.event.sourceEvent.stopPropagation();
    if (!d3.event.active) graphLayout.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  };

  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  };

  function dragended(d) {
    if (!d3.event.active) graphLayout.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  };

  chart3.append("text").attr("x", 245).attr("y", 15).text("Number of genes");

  seq_color = [d3.min(genes_found), d3.max(genes_found)]
  legend = chart3.selectAll(".legend").data(seq_color).enter().append("g").attr("class", "legend")
    .attr("transform", function(d, i) {
      return "translate(" + (240 + 55) + "," + (45 + i * 20) + ")";
    });

  legend.append("circle").attr("r", 5).style("fill", myColornt);
  legend.append("text").attr("x", 10).attr("y", 0).attr("dy", ".35em").text(String);

  var circle_sizes = graph.nodes.map(function(d) {
    if (d.group == 1) {
      return d.size
    }
  });
  circle_sizes = circle_sizes.filter(function(element) {
    return element !== undefined;
  });

  circle_sizes.forEach(function(element, index, array) {
    array[index] = parseFloat(element.toFixed(2));
  });

  logPvals = [d3.min(logPvals).toFixed(2), d3.max(logPvals).toFixed(2)];
  circle_sizes = [d3.min(circle_sizes), d3.max(circle_sizes)];

  max_circle = d3.max(circle_sizes);

  // Add legend: circles
  chart3.append("text").attr("x", 105).attr("y", 15).text("-log10(Pval Adj)");
  chart3.selectAll("legend")
    .data(circle_sizes)
    .enter()
    .append("circle")
    .attr("cx", 155)
    .attr("cy", function(d, i) {
      return 35 + i * max_circle + i * 15;
    })
    .attr("r", function(d) {
      return d
    })
    .style("fill", "none")
    .attr("stroke", "black");

  chart3.selectAll("legend")
    .data(logPvals)
    .enter()
    .append("text")
    .attr("x", 160 + max_circle)
    .attr("y", function(d, i) {
      return 35 + i * max_circle + i * 10;
    })
    .attr("dy", ".35em")
    .text(String);

  chart3.append("text").attr("x", 20).attr("y", 15).text('Genes');
  chart3.append("circle").attr("cx", 35).attr("cy", 35).attr("r", 10).attr("fill", "orange");
  chart3.append("text").attr("x", 20).attr("y", 65).text("Annotations");
  chart3.append("circle").attr("cx", 35).attr("cy", 85).attr("r", 10).attr("fill", "#5688f0");
};

function downloadSVG(id) {
  var svg = document.getElementById(`${id}svg`);
  const base64doc = btoa(unescape(encodeURIComponent(svg.outerHTML)));
  const a = document.createElement('a');
  const e = new MouseEvent('click');
  a.download = `${id}_GeneCodis4.svg`;
  a.href = 'data:image/svg+xml;base64,' + base64doc;
  a.dispatchEvent(e);
};

function downloadPNG(id) {
  var svgElt = document.getElementById(`${id}svg`);
  saveSvgAsPng(svgElt, `${id}_GeneCodis4.png`);
};

function preprocessData(data) {
  for (i = 0; i < data.length; i++) {
    if (i > 9) {
      var diff = i - 9;
      data[i].barheight = 700 + diff * 10;
    } else {
      data[i].barheight = 700;
    };
    if (i < 20) {
      data[i].font = 14;
    } else {
      data[i].font = 12;
    };
    data[i].description = data[i].description.replace(/, /g, ';').replace(/; /g, ', ').replace(/;/g, '; ');//.replace(/[\W_]+/g, ', ')
    data[i].logPval = -Math.log10(+data[i].pval_adj);
  };
  return (data);
};

function filterData(data, top) {
  let dataFiltered = preprocessData(data.slice(0, top));
  return (dataFiltered);
};

async function initSlider(sld, topterms = 10) {
  var sldp = sld.parentElement.parentElement.previousElementSibling;
  var sldTbox = sld.parentElement.nextElementSibling.children[0];
  var data = await getResults(sldp.id.replace('sliderval', ''));
  if (data.length < 50) {
    topterms = data.length;
    sld.max = topterms;
    if (topterms < 10) {
      sld.value = topterms;
      sldTbox.value = topterms;
      sldTbox.placeholder = topterms;
      sldp.innerText = `Showing top ${topterms} terms (${topterms} max):`;
    } else {
      sld.value = 10;
      sldTbox.value = 10;
      sldTbox.placeholder = 10;
      sldp.innerText = `Showing top 10 terms (${topterms} max):`;
    }
  } else {
    sldp.innerText = `Showing top ${topterms} terms (50 max):`;
  };
}

async function updateVisualizations2(id,topterms=10){
  var data = await getResults(id);
  var datafiltered = filterData(data,topterms);
  var msg = document.getElementById(`${id}sliderval`).innerText.split(' (');
  msg[0] = `Visualizations generated for ${topterms} top terms`;
  document.getElementById(`${id}sliderval`).innerText = msg.join(' (');
  document.getElementById(`${id}network`).innerHTML = '';
  document.getElementById(`${id}wordcloud`).innerHTML = '';
  document.getElementById(`${id}barchart`).innerHTML = '';
  createNetwork2(`${id}network`,datafiltered);
  creatWordCloud2(`${id}wordcloud`,datafiltered);
  creatHoVar2(`${id}barchart`,datafiltered);
};

async function updateVisualizations(id, input = false, topterms = 10) {
  var genesShow = document.getElementById(`${id}hidegenes`).checked;
  var geneLabelShow = document.getElementById(`${id}hidelabelgenes`).checked;
  var slider = document.getElementById(`${id}slider`);
  var txbox = document.getElementById(`${id}txbox`);
  if (input){
    if (input.type == "range") {
      txbox.value = slider.value;
    } else {
      slider.value = txbox.value;
    }
  }
  var topterms = slider.value;
  var data = await getResults(id);
  var datafiltered = filterData(data, topterms);
  var msg = document.getElementById(`${id}sliderval`).innerText.split(' (');
  msg[0] = `Showing top ${topterms} terms`;
  document.getElementById(`${id}sliderval`).innerText = msg.join(' (');
  document.getElementById(`${id}network`).innerHTML = '';
  document.getElementById(`${id}barchart`).innerHTML = '';
  createNetwork(`${id}network`, datafiltered, genesShow,geneLabelShow);
  creatHoVar(`${id}barchart`, datafiltered);
};

function move2anchor(id) {
  var anchor = document.querySelector(`#${id}`);
  anchor.scrollIntoView()
}

function creatWordCloud(id,datafiltered) {
  var width = 700, height = 700;

  if (id.includes("CoAnn")) {
    var terms = datafiltered.map(function(d) { return d.description; });
    var terms = terms.join('; ').split("; ");
    const countOccurrences = arr => arr.reduce((prev, curr) => (prev[curr] = ++prev[curr] || 1, prev), {});
    var unique_lots = countOccurrences(terms);
    const entries = Object.entries(unique_lots);
    var word_entries = [];
    for (const [term, count] of entries) {
      var dictobj = {"text":"", "count":0};
      dictobj["count"] = count;
      dictobj["text"] = term;
      word_entries.push(dictobj);
    }
  } else {
    var sizes = datafiltered.map(function(d) { return d.logPval;});
    var terms =  datafiltered.map(function(d) { return d.description; });
    var word_entries = [];
    var max_size = d3.max(datafiltered.map(function(d) { return d.logPval;}));
    for (i = 0; i < terms.length; i++) {
      var dictobj = {"text":"", "count":0};
      dictobj["count"] = sizes[i] / max_size;
      dictobj["text"] = terms[i];
      word_entries.push(dictobj);
    }
  }

  let fill = d3.scaleOrdinal(d3.schemeCategory10);
  let size = d3.scaleLinear().domain([0, d3.max(word_entries, d => d.count)]).range([10, 30]);
  let word_cloud_data = word_entries.map( function(d) {return { text: d.text, size: size(d.count)};});

  var	chart2 = d3.select(`#${id}`)
                 .append("svg")
                 .attr("id", `${id}svg`)
                 .attr("width", `${width}`)
                 .attr("height", `${height}`)
                 .attr("viewBox", `0 0 ${height} ${width}`)
                 .attr("xmlns", "http://www.w3.org/2000/svg");
                 // .attr("width", 700)
                 // .attr("height", 700)

  let layout = d3.layout.cloud()
    .size([height, width])
    .words(word_cloud_data)
    .padding(1.5)
    .rotate(d => ~~(Math.random() * 2) * -45)
    .fontSize(d => d.size)
    .on("end", draw);

  layout.start();

  function draw(words) {
    chart2.append("g")
    .attr("transform", `translate(${height/2} ${width/2})`)
      .selectAll("text")
      .data(words)
      .enter().append("text")
      .style("fill", (d, i) => { d.color = fill(i); return d.color; })
      .style("text-anchor", "middle")
      .attr("transform", d => "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")")
      .text(d => d.text)
      .style("font-size", d => d.size + "px");
    }
}

// TESTING THE Network
// var id = 'Homo_sapiens_example-GO_BP';
// var topterms = '10';
// var data = await getResults(id);
// var datafiltered = filterData(data,topterms);
// document.getElementById(`${id}network`).innerHTML = '';
// createNetwork(`${id}network`,datafiltered,true,
//                       laChSt=-10,laLiDis=10,laLiSt=2,
//                       noChSt=-200,noLiDis=20,noLiSt=1,
//                       xSt=0,ySt=0);


function creatHoVar2(id,datafiltered){
  var allSizes = { big: { width: 1000, height: 1000, margin: {top: 10, right: 10, bottom: 10, left: 10}, padding: 0.3}};
  var sizes = allSizes.big, margin = 	sizes.margin, padding = sizes.padding
  sizes.height = datafiltered[datafiltered.length - 1].barheight;
  var width = sizes.width - margin.left - margin.right,
      height = sizes.height - margin.top - margin.bottom;
  var xClass = "axis axis--x",yClass = "axis axis--y";

  // svg-box
  // place for the future chart. Includes chart body, legend, and axes

  var chart1 = d3.select(`#${id}`)
               .append("svg")
               .attr("id", `${id}svg`)
               .attr("width", `${width}`)
               .attr("height", `${height}`)
               .attr("viewBox", `0 0 ${width+110} ${height+60}`)
               .attr("xmlns", "http://www.w3.org/2000/svg");
               // .attr("width", sizes.width)
               // .attr("height", sizes.height)

  // scales
  // rangeRound: set range and round the resulting value to the nearest integer.

  var y = d3.scaleBand().rangeRound([0,height]).padding(padding),
      x = d3.scaleLinear().rangeRound([0, width]);

  // chart boby
  var g = chart1.append("g")
             .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // axes-X (object)
  var axesX = g.append("g")
               .attr("class", xClass)
               .attr("transform", "translate(100," + height + ")");

  // axes-Y (object)
  var axesY = g.append("g")
               .attr("class", yClass)
               .attr("transform", "translate(100,0)");
  // X-axes text
    chart1.append("text").attr("y",height + 50).attr("x",width/2+70).text("-log10(Pval Adj)").style("font-size","15px")

      y.domain(datafiltered.map(function(d) { return d.description; }));
      var maxVal = d3.max(datafiltered, function(d) { return d.logPval; });
      x.domain([0, maxVal]);

      // xAxes, yAxes (axes)
      var xAxes = d3.axisBottom(x);
      var yAxes = d3.axisLeft(y).tickValues([]);

      // append data to axes
      axesX.call(xAxes);
      axesY.call(yAxes);
      // .selectAll(".tick text")
      // .call(d3.util.wrap, margin.left);

      var rangeValues = datafiltered.map(function(d) {return d.genes_found});
      var myColorbc = d3.scaleLinear().domain([d3.min(rangeValues),d3.max(rangeValues)]).range(["#ffbaba","#ed2939"]);
      var uColor = rangeValues.filter(onlyUnique);
      var seq_color = [];
      var min_genes = d3.min(uColor);
      var max_genes = d3.max(uColor);
      for (var i=min_genes; i <= max_genes; i++){
        seq_color.push(i);
      }
      seq_color.sort((a, b) => b - a);

      var tooltip = d3.select(`#${id}`).append("div").attr("class", "toolTip");

      // bar for each data element
      g.selectAll(".bar")
        .data(datafiltered)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", 100)
        .attr("y", function(d) { return y(d.description); })
        .attr("width", function(d) { return x(d.logPval); })
        .attr("height", y.bandwidth())
        .attr("fill", function(d){return myColorbc(d.genes_found) })
        .on("mousemove", function(d){
           d3.select(this).attr("fill", "#DB7093");
           tooltip.style("left", d3.event.pageX - 50 + "px")
                  .style("top", d3.event.pageY - 70 + "px")
                  .style("display", "inline-block")
                  .html("<span style='color:blue'>Description: </span> <spanstyle='color:black'>"+d.description+"</spanstyle><hr/><span style='color:blue'>Annotation Id: </span> <spanstyle='color:black'>"+d.annotation_id+"</spanstyle><hr/><span style='color:blue'>Pval Adj: </span><spanstyle='color:black'>"+d.pval_adj+"</spanstyle><hr/><span style='color:blue'>Genes: </span><spanstyle='color:black'>"+d.genes+"</spanstyle><hr/>");
          })
        .on("mouseout", function(d, i) {
            tooltip.style("display", "none");
            d3.select(this).attr("fill", function(d) {return myColorbc(d.genes_found);
          })});

            var tt = 80;
            var truncated_text =  datafiltered.map(function(d) { return d.description; });
            for (var i = 0; i < truncated_text.length; i++){
              if(truncated_text[i].length > tt){
                datafiltered[i].truncated_text = truncated_text[i].substr(0,tt) + "...";
              } else{
                datafiltered[i].truncated_text = truncated_text[i];
              }
            }

            var fontsize = datafiltered[datafiltered.length - 1].fontsize

            g.selectAll("tt")
            .data(datafiltered)
            .enter().append("text")
            .attr("x", 100)
            .attr("y", function(d) { return y(d.description) + y.bandwidth()/2; })
            .text(function(d,i) { return d.truncated_text; })
            .attr("font-size", fontsize +"px");




            var svgLegend = chart1.append('svg')
                  .attr("width",200);
            var defs = svgLegend.append('defs');

            	// append a linearGradient element to the defs and give it a unique id
            var linearGradient = defs.append('linearGradient')
            		.attr('id', `lg${id}`);

            // horizontal gradient
            linearGradient
              .attr("x1", "0%")
              .attr("y1", "0%")
              .attr("x2", "0%")
              .attr("y2", "100%");

            // append multiple color stops by using D3's data/enter step
            linearGradient.selectAll("stop")
              .data([
                {offset: "0%", color: "#ed2939"},
                {offset: "100%", color: "#ffbaba"}
              ])
              .enter().append("stop")
              .attr("offset", function(d) {
                return d.offset;
              })
              .attr("stop-color", function(d) {
                return d.color;
              });


            // draw the rectangle and fill with gradient
            svgLegend.append("rect")
              .attr("x", 50)
              .attr("y", 30)
              .attr("width", 20)
              .attr("height", 150)
              .style("fill", `url(#lg${id})`);

            svgLegend.append("text")
             .attr("x",75)
             .attr("y",35)
             .text(max_genes);

             svgLegend.append("text")
              .attr("x",75)
              .attr("y",185)
              .text(min_genes);


            svgLegend
              .attr("class", "axis")
              .append("g")
              .attr("transform", "translate(0, 40)");

      var legendTitle = chart1.append("text")
      .attr("transform", "translate(20,175) rotate(270)")
      .attr("dy", ".35em")
      .text("Number of genes");

      function onlyUnique(value, index, self) {return self.indexOf(value) === index;}
};

//////////////////////////////////////////////////////////////////////////////////

function creatWordCloud2(id,datafiltered) {
  var width = 700, height = 700;

  if (id.includes("CoAnn")) {
    var terms = datafiltered.map(function(d) { return d.description; });
    var terms = terms.join('; ').split("; ");
    const countOccurrences = arr => arr.reduce((prev, curr) => (prev[curr] = ++prev[curr] || 1, prev), {});
    var unique_lots = countOccurrences(terms);
    const entries = Object.entries(unique_lots);
    var word_entries = [];
    for (const [term, count] of entries) {
      var dictobj = {"text":"", "count":0};
      dictobj["count"] = count;
      dictobj["text"] = term;
      word_entries.push(dictobj);
    }
  } else {
    var sizes = datafiltered.map(function(d) { return d.logPval;});
    var terms =  datafiltered.map(function(d) { return d.description; });
    var word_entries = [];
    var max_size = d3.max(datafiltered.map(function(d) { return d.logPval;}));
    for (i = 0; i < terms.length; i++) {
      var dictobj = {"text":"", "count":0};
      dictobj["count"] = sizes[i] / max_size;
      dictobj["text"] = terms[i];
      word_entries.push(dictobj);
    }
  }

  let fill = d3.scaleOrdinal(d3.schemeCategory10);
  let size = d3.scaleLinear().domain([0, d3.max(word_entries, d => d.count)]).range([10, 30]);
  let word_cloud_data = word_entries.map( function(d) {return { text: d.text, size: size(d.count)};});

  var	chart2 = d3.select(`#${id}`)
                 .append("svg")
                 .attr("id", `${id}svg`)
                 .attr("width", `${width}`)
                 .attr("height", `${height}`)
                 .attr("viewBox", `0 0 ${height} ${width}`)
                 .attr("xmlns", "http://www.w3.org/2000/svg");
                 // .attr("width", 700)
                 // .attr("height", 700)

  let layout = d3.layout.cloud()
    .size([height, width])
    .words(word_cloud_data)
    .padding(1.5)
    .rotate(d => ~~(Math.random() * 2) * -45)
    .fontSize(d => d.size)
    .on("end", draw);

  layout.start();

  function draw(words) {
    chart2.append("g")
    .attr("transform", `translate(${height/2} ${width/2})`)
      .selectAll("text")
      .data(words)
      .enter().append("text")
      .style("fill", (d, i) => { d.color = fill(i); return d.color; })
      .style("text-anchor", "middle")
      .attr("transform", d => "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")")
      .text(d => d.text)
      .style("font-size", d => d.size + "px");
    }
}

//////////////////////////////////////////////////////////////////

function createNetwork2(id,datafiltered) {
  var allSizes = { big: { width: 1000, height: 1000, margin: {top: 10, right: 20, bottom: 10, left: 20}, padding: 0.3}};
  var sizes = allSizes.big, margin = 	sizes.margin, padding = sizes.padding;
  sizes.height = datafiltered[datafiltered.length - 1].barheight
  var
    width = sizes.width - margin.left - margin.right,
    height = sizes.height - margin.top - margin.bottom;
  var xClass = "axis axis--x",
    yClass = "axis axis--y";

  var nodes = [],links = [];
  var initialScaleData = datafiltered.map(function(d){return +d.logPval});
  initialScaleData.push(5);
  initialScaleData.push(25);
  var min_value_size = d3.min(initialScaleData);
  var max_value_size = d3.max(initialScaleData);
  var newScaledData = [];
  var linearScale = d3.scaleLinear().domain([min_value_size,max_value_size]).range([5,25]);
  var logPvals = datafiltered.map(function(d){return +d.logPval;});
  var terms = datafiltered.map(function(d){return d.description;});
  var annotations = datafiltered.map(function(d){return d.annotation_id.toString();})
  var pvals = datafiltered.map(function(d){return +d.pval_adj;})
  var genes = datafiltered.map(function(d){return d.genes;});
  var genes_found = datafiltered.map(function(d){return d.genes_found;});
  for (var i = 0; i < logPvals.length; i++) {
    nodes.push({"id":terms[i],"group":1,"pval":pvals[i],"size":linearScale(logPvals[i]),
            "annotation":annotations[i],'genes':genes[i],"col":genes_found[i]});
    gene = genes[i].split(",");
    for (var j = 0; j < gene.length; j++){
      nodes.push({"id":gene[j],"group":2,"pval":1,"size":5,"annotation":0,'genes':0})
      links.push({"source":terms[i],"target":gene[j]})
    }
  }

  var obj = {};
  for ( var i=0, len=nodes.length; i < len; i++ ){
    obj[nodes[i]['id']] = nodes[i];
  }
  nodes = [];
  for ( var key in obj ){
    nodes.push(obj[key]);
  }

  var graph = {"nodes":nodes,"links":links};
  var label = {
      'nodes': [],
      'links': []
  };

  graph.nodes.forEach(function(d, i) {
      label.nodes.push({node: d});
      label.nodes.push({node: d});
      label.links.push({
          source: i * 2,
          target: i * 2 + 1
      });
  });

  var labelLayout = d3.forceSimulation(label.nodes)
      .force("charge", d3.forceManyBody().strength(-50))
      .force("link", d3.forceLink(label.links).distance(0).strength(2));

  var graphLayout = d3.forceSimulation(graph.nodes)
      .force("charge", d3.forceManyBody().strength(-5000))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("link", d3.forceLink(graph.links).id(function(d) {return d.id; }).distance(100).strength(1))
      .force("x", d3.forceX(width / 2).strength(1))
      .force("y", d3.forceY(height / 2).strength(1))
      .on("tick", ticked);


  var adjlist = [];

  graph.links.forEach(function(d) {
      adjlist[d.source.index + "-" + d.target.index] = true;
      adjlist[d.target.index + "-" + d.source.index] = true;
  });

  function neigh(a, b) {
      return a == b || adjlist[a + "-" + b];
  }
  var chart3 = d3.select(`#${id}`)
                 .append("svg")
                 .attr("id", `${id}svg`)
                 .attr("width", `100%`)
                 .attr("height", `${height}px`)
                 .attr("viewBox", `0 0 ${width} ${height+10}`)
                 .attr("xmlns", "http://www.w3.org/2000/svg");
                 // .attr("width", 1000)
                 // .attr("height", 1000)

  var container = chart3.append("g")
                        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // chart3.call(
  //     d3.zoom()
  //         .scaleExtent([.1, 4])
  //         .on("zoom", function() { container.attr("transform", d3.event.transform); })
  // );

  var link = container.append("g").attr("class", "links")
      .selectAll("line")
      .data(graph.links)
      .enter()
      .append("line")
      .attr("stroke", "#aaa")
      .attr("stroke-width", "0.5px");

  var rangeValues = graph.nodes.map(function(d) {return d.size});
  rangeValues = rangeValues.filter(function( element ) {return element !== undefined;});

  var myColornt = d3.scaleLinear().domain([d3.min(genes_found),d3.max(genes_found)]).range(["#bdd2ff","#5688f0"]);

  var node = container.append("g").attr("class", "nodes")
      .selectAll("g")
      .data(graph.nodes)
      .enter()
      .append("circle")
      .attr("r", function(d) { if (d.group == 1) {return d.size; }
                               else {return 3;}
                             })
      .attr("fill",function(d){
        if (d.group == 1) {return myColornt(d.col);}
        else { return "orange" }
      })

      node.append("title")
          .text(function(d) {
            if (d.group == 1){return "Term: " + d.id + '\nAnnotation: ' + d.annotation_id + '\nPval Adj: ' + d.pval + "\nGenes: "+d.genes; }
            else {return d.id}
          })
          .attr('x', width / 50)
          .attr('y', height / 250);

  node.on("mouseover", focus).on("mouseout", unfocus);

  node.call(
      d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended)
  );

  var labelNode = container.append("g").attr("class", "labelNodes")
      .selectAll("text")
      .data(label.nodes)
      .enter()
      .append("text")
      .text(function(d, i) { return i % 2 == 0 ? "" : d.node.id; })
      .style("fill", "#555")
      .style("font-family", "Arial")
      .style("font-size", 12)
      .style("pointer-events", "none"); // to prevent mouseover/drag capture

  node.on("mouseover", focus).on("mouseout", unfocus);

  function ticked() {

      node.attr("transform", function(d) {
        return "translate(" + fixna(Math.max(d.size, Math.min(width - d.size, d.x))) + "," + fixna(Math.max(100, Math.min(height - d.size, d.y))) + ")";
        //return "translate(" + fixna(d.x) + "," + fixna(d.y) + ")";
      });

      // link.call(updateLink);
      link.attr("x1", function(d) { return fixna(Math.max(3, Math.min(width - 3, d.source.x))); })
          .attr("y1", function(d) { return fixna(Math.max(100, Math.min(height - 3, d.source.y))); })
          .attr("x2", function(d) { return fixna(Math.max(3, Math.min(width - 3, d.target.x))); })
          .attr("y2", function(d) { return fixna(Math.max(100, Math.min(height - 3, d.target.y))); });


      labelLayout.alphaTarget(0.3).restart();
      labelNode.each(function(d, i) {
          if(i % 2 == 0) {
              d.x = d.node.x;
              d.y = d.node.y;
          } else {
              var b = this.getBBox();

              var diffX = d.x - d.node.x;
              var diffY = d.y - d.node.y;

              var dist = Math.sqrt(diffX * diffX + diffY * diffY);

              var shiftX = b.width * (diffX - dist) / (dist * 2);
              shiftX = Math.max(-b.width, Math.min(0, shiftX));
              var shiftY = 16;
              this.setAttribute("transform", "translate(" + shiftX + "," + shiftY + ")");
          }
      });
      labelNode.attr("transform", function(d) {
        // return "translate(" + fixna(d.x) + "," + fixna(d.y) + ")";
         return "translate(" + fixna(Math.max(3, Math.min(width - 3, d.x))) + "," + fixna(Math.max(100, Math.min(height - 3, d.y))) + ")";
      });

  }

  function fixna(x) {
      if (isFinite(x)) return x;
      return 0;
  }

  function focus(d) {
      var index = d3.select(d3.event.target).datum().index;
      node.style("opacity", function(o) {
          return neigh(index, o.index) ? 1 : 0.1;
      });
      labelNode.attr("display", function(o) {
        return neigh(index, o.node.index) ? "block": "none";
      });
      link.style("opacity", function(o) {
          return o.source.index == index || o.target.index == index ? 1 : 0.1;
      });
  }

  function unfocus() {
     labelNode.attr("display", "block");
     node.style("opacity", 1);
     link.style("opacity", 1);
  }

  function updateLink(link) {

      // link.attr("x1", function(d) { return fixna(d.source.x); })
      //     .attr("y1", function(d) { return fixna(d.source.y); })
      //     .attr("x2", function(d) { return fixna(d.target.x); })
      //     .attr("y2", function(d) { return fixna(d.target.y); });
      link.attr("x1", function(d) { return fixna(Math.max(3, Math.min(width - 3, d.source.x))); })
          .attr("y1", function(d) { return fixna(Math.max(3, Math.min(height - 3, d.source.y))); })
          .attr("x2", function(d) { return fixna(Math.max(3, Math.min(width - 3, d.target.x))); })
          .attr("y2", function(d) { return fixna(Math.max(3, Math.min(height - 3, d.target.y))); });
  }

  function updateNode(node) {
    node.attr("transform", function(d) {
      return "translate(" + fixna(Math.max(d.size, Math.min(width - d.size, d.x))) + "," + fixna(Math.max(d.size, Math.min(height - d.size, d.y))) + ")";
      //return "translate(" + fixna(d.x) + "," + fixna(d.y) + ")";
    });
//    node.attr("cx", function(d) { return d.x = Math.max(radius, Math.min(width - radius, d.x)); })
//        .attr("cy", function(d) { return d.y = Math.max(radius, Math.min(height - radius, d.y)); });
  }

  function dragstarted(d) {
      d3.event.sourceEvent.stopPropagation();
      if (!d3.event.active) graphLayout.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
  };

  function dragged(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
  };

  function dragended(d) {
      if (!d3.event.active) graphLayout.alphaTarget(0);
      d.fx = null;
      d.fy = null;
  };

  chart3.append("text").attr("x", 245).attr("y", 15).text("Number of genes");

  seq_color = [d3.min(genes_found),d3.max(genes_found)]
  legend = chart3.selectAll(".legend").data(seq_color).enter().append("g").attr("class", "legend")
  .attr("transform", function(d, i) { return "translate(" + (240+55) + "," + (45 + i * 20) + ")"; });

  legend.append("circle").attr("r",5).style("fill", myColornt);
  legend.append("text").attr("x", 10).attr("y", 0).attr("dy", ".35em").text(String);

  var circle_sizes = graph.nodes.map(function(d) { if (d.group == 1) {return d.size}});
  circle_sizes = circle_sizes.filter(function( element ) {return element !== undefined;});

  circle_sizes.forEach(function(element, index, array){
    array[index] = parseFloat(element.toFixed(2));
  });

  logPvals = [d3.min(logPvals).toFixed(2),d3.max(logPvals).toFixed(2)];
  circle_sizes = [d3.min(circle_sizes),d3.max(circle_sizes)];

  max_circle = d3.max(circle_sizes);

  // Add legend: circles
  chart3.append("text").attr("x", 105).attr("y", 15).text("-log10(Pval Adj)");
  chart3.selectAll("legend")
    .data(circle_sizes)
    .enter()
    .append("circle")
    .attr("cx", 155)
    .attr("cy", function(d, i) { return 35 + i * max_circle + i * 15;})
    .attr("r", function(d){ return d })
    .style("fill", "none")
    .attr("stroke", "black");

    chart3.selectAll("legend")
      .data(logPvals)
      .enter()
      .append("text")
      .attr("x", 160+max_circle)
      .attr("y", function(d, i) { return 35 + i * max_circle + i * 10;})
      .attr("dy", ".35em")
      .text(String);

  chart3.append("text").attr("x",20).attr("y",15).text('genes');
  chart3.append("circle").attr("cx",35).attr("cy",35).attr("r",10).attr("fill","orange");
  chart3.append("text").attr("x",20).attr("y",65).text("Annotations");
  chart3.append("circle").attr("cx",35).attr("cy",85).attr("r",10).attr("fill","#5688f0");

};

async function initSlider2(sld, topterms=10){
  var sldp = sld.previousElementSibling;
  var data = await getResults(sldp.id.replace('sliderval',''));
  if (data.length < 50){
    topterms = data.length;
    sld.max = topterms;
    if(topterms < 10){
      sld.value = topterms;
      sldp.innerText = `Visualizations generated for ${topterms} top terms (${topterms} max):`;
    }else{
      sld.value = 10;
      sldp.innerText = `Visualizations generated for 10 top terms (${topterms} max):`;
    }
  }else{
    sldp.innerText = `Visualizations generated for ${topterms} top terms (50 max):`;
  };
}

function recoverParams2(params){
  clickDropDown(params.organism,'organism','gc4org');
  checkBoxesById(params,['annotations','inputtype','coannotation']);
  let annots = [...document.querySelectorAll('[name="annotations"]:checked')];
  valueFormByName(params,['jobName','email','inputSupport','input','universe']);
  if (params.universe.length > 1){
    document.getElementsByName('universe')[0].hidden = false;
    clickDropDown('custom','universemode','gc4org');
    document.querySelector('.advancedbtn').click();
  }
  changeLimits();
}

function adjustDisplaying(){
  if(document.getElementsByName("listaInput1")[0].className=="tile is-flex is-flex-grow-0"){
    document.getElementsByName("listaInput1")[0].className=""
    document.getElementById("fileName1").style="max-width:10em;flex: 0 0 100%;"
    document.getElementById("leftmargined").style.marginLeft = "0px"; 
    //console.log(document.getElementsByName("doc_file")[0].style.marginLeft)

  }else{
    document.getElementsByName("listaInput1")[0].className="tile is-flex is-flex-grow-0"
    document.getElementById("fileName1").style=""
    document.getElementById("leftmargined").style.marginLeft = "5px";
    //document.getElementById("botonEjemplo1")[0].style.marginLeft = "10px"; 
  }

  if(document.getElementsByName("listaInput2")[0].className=="tile is-flex is-flex-grow-0"){
    document.getElementsByName("listaInput2")[0].className=""
    document.getElementById("fileName2").style="max-width:10em;flex: 0 0 100%;"
    //document.getElementById("doc_file2")[0].style.marginLeft = "0px"; 
  }else{
    document.getElementsByName("listaInput2")[0].className="tile is-flex is-flex-grow-0"
    //document.getElementById("doc_file2")[0].style.marginLeft = "10px";
    document.getElementById("fileName2").style="" 
  }
}

function HighlightArea(ev){
  ev.preventDefault();
  //console.log("evento highlight",ev)
  const ele = document.getElementsByName('input');
  //console.log("dragging funcionando")
  ele.className="textarea has-fixed-size dragging"
  
}

function resetFile(filename) {
  if(filename=="doc_file1"){
    var inputlabel="fileName1"
  }
  if(filename=="doc_file2"){
    var inputlabel="fileName2"
  }
  if(filename=="doc_file3"){
    var inputlabel="fileName3"
  }
  const file =document.getElementById(filename);
  file.value = '';
  document.getElementById(inputlabel).innerHTML ="No file selected"
}

function printDataFromFile(filename) {
  //let organism = getOrgSelected();
  //var inputtype = document.querySelector('input[name="inputtype"]:checked').id;
  var fileToLoad = document.getElementById(filename).files[0];
  //console.log(fileToLoad)
  if(filename=="doc_file1"){
    var inputname="input"
    var inputlabel="fileName1"
  }
  if(filename=="doc_file2"){
    var inputname="input2"
    var inputlabel="fileName2"
  }
  if(filename=="doc_file3"){
    var inputname="universe"
    var inputlabel="fileName3"
  }
  var fileReader = new FileReader();

  /* if(fileToLoad.name.endsWith(".csv")){
    //const shell = import('shelljs')
    //var extension = fileToLoad.name.substr(fileToLoad.name.lastIndexOf("."),fileToLoad.name.length);
    //var newfilename=fileToLoad.name.substr(0,fileToLoad.name.lastIndexOf("."));
    //newfilename=newfilename+".txt";
    //console.log("nuevo nombre",newfilename)
    var texts = fileReader.readAsText(fileToLoad);
    //const { exec } = require("child_process");
    exec("pandoc {0} -f {1} -t plain -s -o {2}".format(fileToLoad.name,extension,newfilename),
        function (error, stdout, stderr) {
            console.log('stdout: ' + stdout);
            console.log('stderr: ' + stderr);
            if (error !== null) {
                console.log('exec error: ' + error);
            }
        });
  }*/
  fileReader.onload = function(fileLoadedEvent){
      var textFromFileLoaded = fileLoadedEvent.target.result;
      console.log(textFromFileLoaded)
      document.getElementsByName(inputname).innerText = textFromFileLoaded;
      //console.log(document.getElementsByName(inputname).innerText);
      textFromFileLoaded=document.getElementsByName(inputname).innerText.replaceAll(/^\s*$(?:\r\n?|\n)/gm, "")
      if(document.getElementsByName(inputname).innerText.includes('"')){
        textFromFileLoaded=document.getElementsByName(inputname).innerText.replaceAll('"','');
      }
      if(document.getElementsByName(inputname).innerText.includes("“")){
        textFromFileLoaded=document.getElementsByName(inputname).innerText.replaceAll("“","");
        textFromFileLoaded=textFromFileLoaded.replaceAll("”","");
      }
      if(document.getElementsByName(inputname).innerText.includes("'")){
        textFromFileLoaded=document.getElementsByName(inputname).innerText.replaceAll("'","");
      }
      textFromFileLoaded=textFromFileLoaded.replaceAll("\t","\n")
      if(fileToLoad.name.endsWith(".csv")){
        textFromFileLoaded=textFromFileLoaded.replaceAll(";","\n")
        textFromFileLoaded=textFromFileLoaded.replaceAll(",","\n")
        textFromFileLoaded=textFromFileLoaded.replaceAll("”","")
        textFromFileLoaded=textFromFileLoaded.replaceAll(" ","\n")
        textFromFileLoaded=textFromFileLoaded.replaceAll("“","")

      }
      textFromFileLoaded=textFromFileLoaded.replaceAll(";","\n")
      textFromFileLoaded=textFromFileLoaded.replaceAll(",","\n")
      textFromFileLoaded=textFromFileLoaded.replaceAll(/^\s*$(?:\r\n?|\n)/gm,"")

      //textFromFileLoaded=textFromFileLoaded.replaceAll("\n","")
      document.getElementsByName(inputname)[0].value=textFromFileLoaded;
      document.getElementById(inputlabel).innerHTML =fileToLoad.name
      addCounter();
  };
  fileReader.readAsText(fileToLoad, "UTF-8");
  
}

function allowDrop(ev) {
  ev.preventDefault();
}

function _ondragleave(inputid){
  console.log("inputid de leave:",inputid)
  var holder = document.getElementById(inputid);
  console.log("salieno")
  holder.className = 'textarea has-fixed-size'; 
  return false;
}
function _ondragenter(e,inputid){
  e.preventDefault(); 
  var holder = document.getElementById(inputid);
  console.log("entrando")
  var fileToLoad = e.dataTransfer;
  console.log("file to load",fileToLoad)
  holder.className = 'textarea has-fixed-size dragging'; 
  return false;
}

function drop(ev,inputname) {
  ev.preventDefault();
  console.log("evento",ev)
  //var inputname = ev.explicitOriginalTarget.attributes[0].nodeValue
      if(inputname=="input"){
        var filename="doc_file1"
        var inputlabel="fileName1"
        var inputid="holder"
      }
      if(inputname=="input2"){
        var filename="doc_file2"
        var inputlabel="fileName2"
        var inputid="holder2"
      }
      if(inputname=="universe"){
        var filename="doc_file3"
        var inputlabel="fileName3"
        var inputid="holder3"
      }
  //fichero arrastrado a la textarea: filetoload
  var fileToLoad = ev.dataTransfer.files[0];
  document.getElementById(inputid).className = 'textarea has-fixed-size'; 
  //console.log("file to load",fileToLoad)
  //comprobamos que el fichero sea un txt o un csv
  if(fileToLoad.name.endsWith(".csv") || fileToLoad.name.endsWith(".txt")){
      //cargamos fileReader para leer el contenido del fichero
      
      document.getElementById(filename).files=ev.dataTransfer.files;
      document.getElementById(inputlabel).innerHTML =document.getElementById(filename).files[0].name

      var fileReader = new FileReader();
      fileReader.onload = function(fileLoadedEvent){
      var textFromFileLoaded = fileLoadedEvent.target.result;
      document.getElementsByName(inputname).innerText = textFromFileLoaded;
      textFromFileLoaded=document.getElementsByName(inputname).innerText.replaceAll(/^\s*$(?:\r\n?|\n)/gm, "")
      console.log(document.getElementsByName(inputname).innerText)
      console.log(textFromFileLoaded)
      if(document.getElementsByName(inputname).innerText.includes('"')){
        textFromFileLoaded=document.getElementsByName(inputname).innerText.replaceAll('"','');
      }
      console.log(document.getElementsByName(inputname).innerText)
      console.log(textFromFileLoaded)
      if(document.getElementsByName(inputname).innerText.includes("“")){
        textFromFileLoaded=document.getElementsByName(inputname).innerText.replaceAll("“","");
        textFromFileLoaded=textFromFileLoaded.replaceAll("”","");
      }
      console.log(document.getElementsByName(inputname).innerText)
      console.log(textFromFileLoaded)

      if(document.getElementsByName(inputname).innerText.includes("'")){
        textFromFileLoaded=document.getElementsByName(inputname).innerText.replaceAll("'","");
      }
      console.log(document.getElementsByName(inputname).innerText)
      console.log(textFromFileLoaded)
      console.log
      textFromFileLoaded=textFromFileLoaded.replaceAll("\t","\n")
      if(fileToLoad.name.endsWith(".csv")){
          textFromFileLoaded=textFromFileLoaded.replaceAll(";","\n")
          textFromFileLoaded=textFromFileLoaded.replaceAll(" ","\n")
          textFromFileLoaded=textFromFileLoaded.replaceAll(",","\n")
          textFromFileLoaded=textFromFileLoaded.replaceAll("”","")
          textFromFileLoaded=textFromFileLoaded.replaceAll("“","")

      }
      textFromFileLoaded=textFromFileLoaded.replaceAll(";","\n")
      textFromFileLoaded=textFromFileLoaded.replaceAll(",","\n")
      textFromFileLoaded=textFromFileLoaded.replaceAll(/^\s*$(?:\r\n?|\n)/gm,"")

      console.log(document.getElementsByName(inputname).innerText)
      console.log(textFromFileLoaded)

      //textFromFileLoaded=textFromFileLoaded.replaceAll("\n","")
      document.getElementsByName(inputname)[0].value=textFromFileLoaded;
      addCounter();
    };
    fileReader.readAsText(fileToLoad, "UTF-8");
  }
  ev.preventDefault();

} 