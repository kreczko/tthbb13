import os
import glob
import FWCore.ParameterSet.Config as cms
from TTH.MEAnalysis.samples_base import *
import ROOT

cmssw_base = os.environ["CMSSW_BASE"]

version = "Sep22"

samples = [
    "gc/datasets/had_V24_4/TT_TuneCUETP8M1_13TeV-powheg-pythia8.txt",
    "gc/datasets/had_V24_4/ttHToNonbb_M125_13TeV_powheg_pythia8.txt",
    "gc/datasets/had_V24_4/ttHTobb_M125_13TeV_powheg_pythia8.txt",
    "gc/datasets/had_V24_4/JetHT.txt",
    "gc/datasets/had_V24_4/QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8.txt",
    "gc/datasets/had_V24_4/QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8.txt",
    "gc/datasets/had_V24_4/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8.txt",
    "gc/datasets/had_V24_4/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8.txt",
    "gc/datasets/had_V24_4/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8.txt",
    "gc/datasets/had_V24_4/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8.txt",
]

samples = ["$CMSSW_BASE/src/TTH/MEAnalysis/" + s for s in samples]

sampfiles = {}
samples_dict = {}

samp_py = open("samples.py", "w")

samp_py.write("# THIS IS AN AUTOGENERATED FILE\n")
samp_py.write("# Made by prepareSamples.py\n")
samp_py.write("# do NOT modify (except to skip individual samples)\n\n\n")

samp_py.write('import FWCore.ParameterSet.Config as cms\n')
samp_py.write('from TTH.MEAnalysis.samples_base import *\n\n')

samp_py.write('version = "' + version + '"\n')

samp_py.write("samples_dict = {\n")
for sample in samples:

    isMC = True
    sampname = sample.split("/")[-1]
    sampname = sampname.replace(".txt", "")
    if sampname in ["SingleMuon", "SingleElectron", "DoubleEG", "DoubleMuon", "MuonEG"]:
        isMC = False
    x = """ 
        "{0}": cms.PSet(
            name     = cms.string("{0}"),
            nickname = cms.string("{0}"),
            isMC     = cms.bool({2}),
            treeName = cms.string("vhbb/tree"),
            subFiles = cms.vstring(get_files("{1}")),
        ),
    """.format(sampname, sample, isMC)
    samp_py.write(x)

samp_py.write("}\n")
samp_py.close()
