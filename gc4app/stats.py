from scipy.stats import hypergeom, fisher_exact, chi2_contingency, binom, nchypergeom_wallenius

from scipy.interpolate import *
from pygam import LogisticGAM, s
import numpy, math

DEs = [0,1,0,1,0,0,0,1,1,1,0,0,1,0,1,1,0,0,1,0,1,0,0,1,1,1,0,0,1,0,1,0,0,0,0,0,1,1,0,0,1,0,1,1,0,0,1,0,0,0,1,0,0,0,1,0,0,1,1,0,1,0,0,0,0,1,1,1,1,1,1,1,0,0,0,1,0,1,1,1,1,1,1,1,0,1,1,1,0,1,0,1,0,0,1,0,0,1,0,1]
lens = [7618,3644,8573,9698,8530,5514,1100,5594,4924,3071,5187,7137,8389,7593,1164,1803,9866,2737,8988,9180,8432,9872,2300,3188,9853,7320,8838,6536,8490,4965,9832,1861,8316,7789,1028,8998,4605,6765,2507,3813,3591,5775,7975,5715,1600,5667,9847,3738,7801,4704,8996,3483,7471,3108,6621,7822,6549,7605,9498,3841,3999,5903,2383,2935,4551,3743,9493,8306,4409,2257,4707,7427,2306,3319,9400,7468,8720,2399,1011,7981,1334,4900,1516,9415,3163,8619,8032,6245,8230,5784,6477,7552,2441,6149,1790,7484,2061,5538,4260,354]

from pygam import LogisticGAM, s
def getGAModds(lens,DEs):
    x = numpy.array(lens)
    y = numpy.array(DEs)
    ww = numpy.argsort(x) # ww
    size = math.ceil(len(y) / 10)
    low = sum(y[ww][0:size])
    hi = sum(y[ww][(len(y) - size):len(y)])
    if hi <= low:
        reflectionFactor = 10^10
        x = reflectionFactor - x
        newX = x
    else:
        newX = x
        x = numpy.insert(x,0,0)
        y = numpy.insert(y,0,0)

    x = numpy.array([[x1] for x1 in x])
    y = numpy.array([[y1] for y1 in y])
    lams = np.exp(np.random.rand(100, 1))
    gam = LogisticGAM(s(0,n_splines=6,spline_order=3)).gridsearch(x,y,lam=lams)
    probs = gam.predict_proba(x)
    odds = probs / (1 - probs)
    return(odds)

def hypergeometric(popSize,popAnnot,inputSize,inputAnnot):
    """
    popSize = i.e. all the genes of a genome or system M
    popAnnot = i.e. all the genes of GO:XXXXXX n
    inputSize = i.e. the genes selected N
    inputAnnot = i.e. the genes selected of that GO:XXXXXX x
    """
    pval = hypergeom(popSize,popAnnot,inputSize).pmf(inputAnnot)
    return(pval)

def wallenius(popSize,popAnnot,inputSize,inputAnnot,odds=0.5):
    pval = nchypergeom_wallenius(popSize,popAnnot,inputSize,odds).pmf(inputAnnot)
    return(pval)

def getContiTable(popSize,popAnnot,inputSize,inputAnnot):
    inputNotAnnot = inputSize - inputAnnot
    popAnnotNotInput = popAnnot - inputAnnot
    popNotAnnotNotInput = popSize - inputAnnot - inputNotAnnot - popAnnotNotInput
    contingencyTable = [[inputAnnot,    popAnnotNotInput],
                        [inputNotAnnot, popNotAnnotNotInput]]
    return(contingencyTable)

def fisherExact(popSize,popAnnot,inputSize,inputAnnot):
    """
    same params of hypergeometric()
    """
    contingencyTable = getContiTable(popSize,popAnnot,inputSize,inputAnnot)
    oddsratio, pvalue = fisher_exact(contingencyTable)
    return(oddsratio, pvalue)

def chi2(popSize,popAnnot,inputSize,inputAnnot):
    """
    same params of hypergeometric()
    """
    contingencyTable = getContiTable(popSize,popAnnot,inputSize,inputAnnot)
    stat,pvalue,dof,expected = chi2_contingency(contingencyTable)
    return(pvalue)

def


#
# popSize=6000
# popAnnot=100
# inputSize=80
# inputAnnot=10
#
# hypergeometric(popSize,popAnnot,inputSize,inputAnnot)
# fisherExact(popSize,popAnnot,inputSize,inputAnnot)
# chi2(popSize,inputSize,popAnnot,inputAnnot)
