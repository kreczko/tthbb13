#!/bin/bash
import sys, re, shutil
from copy import deepcopy
import subprocess
import json

from splitLumi import getLumiListInFiles, chunks 
from FWCore.PythonUtilities.LumiList import LumiList
das_client = "/afs/cern.ch/user/v/valya/public/das_client.py"

#Each time you call multicrab.py, you choose to submit jobs from one of these workflows
workflows = [
    "data", #real data
    "data_leptonic", #real data, SL and DL only
    "leptonic", #ttH with SL/DL decays
    "leptonic_nome", #ttH with SL/DL decays
    "hadronic", #ttH with FH decays
    "QCD_nome", #QCD samples without MEM
    "pilot", #ttH sample only, with no MEM
    "signal", #signal sample with common config
    "testing", #single-lumi jobs, a few samples
    "localtesting", #run combined jobs locally
    "localtesting_withme", #run combined jobs locally
    "testing_withme", #single-lumi jobs, a few samples
    "allmc_nome", # SL, DL and FH, no matrix element
    "testing_hadronic_withme" #single-lumi jobs, a few samples   
]

import argparse
parser = argparse.ArgumentParser(description='Submits crab jobs')
parser.add_argument('--workflow', action="store", required=True, help="Type of workflow to run", type=str, choices=workflows)
parser.add_argument('--tag', action="store", required=True, help="the version tag for this run, e.g. VHBBHeppyV22_tthbbV10_test1")
args = parser.parse_args()

localtesting = "localtesting" in args.workflow

#list of configurations that we are using, should be in TTH/MEAnalysis/python/
me_cfgs = {
    "default": "MEAnalysis_cfg_heppy.py",
    "cMVA": "MEAnalysis_cfg_heppy.py",
    "nome": "cfg_noME.py",
    "leptonic": "cfg_leptonic.py",
    "hadronic": "cfg_FH.py",
}

sets_data = [
    "/DoubleEG/Run2016B-PromptReco-v1/MINIAOD",
    "/DoubleEG/Run2016B-PromptReco-v2/MINIAOD",
    "/DoubleEG/Run2016C-PromptReco-v2/MINIAOD",
    "/DoubleEG/Run2016D-PromptReco-v2/MINIAOD",
    "/DoubleEG/Run2016E-PromptReco-v2/MINIAOD",
    "/DoubleEG/Run2016F-PromptReco-v2/MINIAOD",

    "/DoubleMuon/Run2016B-PromptReco-v1/MINIAOD",
    "/DoubleMuon/Run2016B-PromptReco-v2/MINIAOD",
    "/DoubleMuon/Run2016C-PromptReco-v2/MINIAOD",
    "/DoubleMuon/Run2016D-PromptReco-v2/MINIAOD",
    "/DoubleMuon/Run2016E-PromptReco-v2/MINIAOD",
    "/DoubleMuon/Run2016F-PromptReco-v2/MINIAOD",

    "/MuonEG/Run2016B-PromptReco-v1/MINIAOD",
    "/MuonEG/Run2016B-PromptReco-v2/MINIAOD",
    "/MuonEG/Run2016C-PromptReco-v2/MINIAOD",
    "/MuonEG/Run2016D-PromptReco-v2/MINIAOD",
    "/MuonEG/Run2016E-PromptReco-v2/MINIAOD",
    "/MuonEG/Run2016F-PromptReco-v2/MINIAOD",

    "/SingleElectron/Run2016B-PromptReco-v1/MINIAOD",
    "/SingleElectron/Run2016B-PromptReco-v2/MINIAOD",
    "/SingleElectron/Run2016C-PromptReco-v2/MINIAOD",
    "/SingleElectron/Run2016D-PromptReco-v2/MINIAOD",
    "/SingleElectron/Run2016E-PromptReco-v2/MINIAOD",
    "/SingleElectron/Run2016F-PromptReco-v2/MINIAOD",

    "/SingleMuon/Run2016B-PromptReco-v1/MINIAOD",
    "/SingleMuon/Run2016B-PromptReco-v2/MINIAOD",
    "/SingleMuon/Run2016C-PromptReco-v2/MINIAOD",
    "/SingleMuon/Run2016D-PromptReco-v2/MINIAOD",
    "/SingleMuon/Run2016E-PromptReco-v2/MINIAOD",
    "/SingleMuon/Run2016F-PromptReco-v2/MINIAOD",

#    "/BTagCSV/Run2016B-PromptReco-v1/MINIAOD",
#    "/BTagCSV/Run2016B-PromptReco-v2/MINIAOD",
#    "/BTagCSV/Run2016C-PromptReco-v2/MINIAOD",
#    "/BTagCSV/Run2016D-PromptReco-v2/MINIAOD",
#    "/BTagCSV/Run2016E-PromptReco-v2/MINIAOD",
#    "/BTagCSV/Run2016F-PromptReco-v2/MINIAOD",

    "/JetHT/Run2016B-PromptReco-v1/MINIAOD",
    "/JetHT/Run2016B-PromptReco-v2/MINIAOD",
    "/JetHT/Run2016C-PromptReco-v2/MINIAOD",
    "/JetHT/Run2016D-PromptReco-v2/MINIAOD",
    "/JetHT/Run2016E-PromptReco-v2/MINIAOD",
    "/JetHT/Run2016F-PromptReco-v1/MINIAOD",
]

#all available datasets.
datasets = {}
datanames = []
for sd in sets_data:
    name = "-".join(sd.split("/")[1:3])
    datanames += [name]
    datasets[name] = {
        "ds": sd,
        "maxlumis": -1,
        "perjob": 10,
        "runtime": 10,
        "mem_cfg": me_cfgs["nome"],
        "script": 'heppy_crab_script_data.sh'
    }
datasets.update({
    'ttHTobb': {
        "ds": '/ttHTobb_M125_13TeV_powheg_pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["default"],
        "script": 'heppy_crab_script.sh'
    },
    'ttHTobb_tranche3': {
        "ds": '/ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8/RunIISpring16MiniAODv2-premix_withHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["default"],
        "script": 'heppy_crab_script.sh'
    },
    'ttHToNonbb_tranche3': {
        "ds": '/ttHToNonbb_M125_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8/RunIISpring16MiniAODv2-premix_withHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["default"],
        "script": 'heppy_crab_script.sh'
    },
    'ttHToNonbb': {
        "ds": '/ttHToNonbb_M125_13TeV_powheg_pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["default"],
        "script": 'heppy_crab_script.sh'
    },

    'TTbar_inc': {
        "ds": '/TT_TuneCUETP8M1_13TeV-powheg-pythia8/RunIISpring16MiniAODv2-PUSpring16RAWAODSIM_reHLT_80X_mcRun2_asymptotic_v14_ext3-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 50,
        "runtime": 20,
        "mem_cfg": me_cfgs["default"],
        "script": 'heppy_crab_script.sh'
    },
    'TTbar_inc_scaleup': {
        "ds": '/TT_TuneCUETP8M1_13TeV-powheg-scaleup-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["default"],
        "script": 'heppy_crab_script.sh'
    },
    'TTbar_inc_scaledown': {
        "ds": '/TT_TuneCUETP8M1_13TeV-powheg-scaledown-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["default"],
        "script": 'heppy_crab_script.sh'
    },

    'TTbar_sl': {
        "ds": '/TTToSemiLeptonic_13TeV-powheg/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext1-v2/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'TTbar_sl_tranche3': {
        "ds": '/TTToSemilepton_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8/RunIISpring16MiniAODv2-premix_withHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 150,
        "runtime": 20,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'TTbar_sl_scaleup': {
        "ds": '/TTToSemiLeptonic_13TeV_ScaleUp-powheg/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'TTbar_sl_scaledown': {
        "ds": '/TTToSemiLeptonic_13TeV_ScaleDown-powheg/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'TTbar_sl1': {
        "ds": '/TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'TTbar_sl2': {
        "ds": '/TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'TTbar_dl': {
        "ds": '/TTTo2L2Nu_13TeV-powheg/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext1-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'TTbar_dl_tranche3': {
        "ds": '/TTTo2L2Nu_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8/RunIISpring16MiniAODv2-premix_withHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 150,
        "runtime": 20,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    
    'ww': {
        "ds": '/WW_TuneCUETP8M1_13TeV-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'wz': {
        "ds": '/WZ_TuneCUETP8M1_13TeV-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'zz': {
        "ds": '/ZZ_TuneCUETP8M1_13TeV-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'ttw_wlnu': {
        "ds": '/TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8/RunIISpring16MiniAODv2-premix_withHLT_80X_mcRun2_asymptotic_v14-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'ttw_wqq': {
        "ds": '/TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'ttz_zqq': {
        "ds": '/TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    
    'wjets_ht_100_200': {
        "ds": '/WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext1-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    
    'wjets_ht_200_400': {
        "ds": '/WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'wjets_ht_400_600': {
        "ds": '/WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'wjets_ht_600_800': {
        "ds": '/WJetsToLNu_HT-600To800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    
    'wjets_ht_800_1200': {
        "ds": '/WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext1-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'wjets_ht_1200_2500': {
        "ds": '/WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },


    'wjets_ht_2500_inf': {
        "ds": '/WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },

    'dy_10_50': {
        "ds": '/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'dy_50_inf': {
        "ds": '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISpring16MiniAODv1-PUSpring16_80X_mcRun2_asymptotic_2016_v3-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 40,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    
    'st_t': {
        "ds": '/ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'stbar_t': {
        "ds": '/ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'st_tw': {
        "ds": '/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v2/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'stbar_tw': {
        "ds": '/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },
    'st_s': {
        "ds": '/ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 20,
        "runtime": 10,
        "mem_cfg": me_cfgs["leptonic"],
        "script": 'heppy_crab_script.sh'
    },


    'QCD300': {
        "ds": '/QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 500,
        "runtime": 40,
        "mem_cfg": me_cfgs["hadronic"],
        "script": 'heppy_crab_script.sh'
    },
    'QCD300_ext1': {
        "ds": '/QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext1-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 500,
        "runtime": 40,
        "mem_cfg": me_cfgs["hadronic"],
        "script": 'heppy_crab_script.sh'
    },
    'QCD500': {
        "ds": '/QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 500,
        "runtime": 40,
        "mem_cfg": me_cfgs["hadronic"],
        "script": 'heppy_crab_script.sh'
    },
    'QCD500_ext1': {
        "ds": '/QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext1-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 500,
        "runtime": 40,
        "mem_cfg": me_cfgs["hadronic"],
        "script": 'heppy_crab_script.sh'
    },
    'QCD700': {
        "ds": '/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 300,
        "runtime": 40,
        "mem_cfg": me_cfgs["hadronic"],
        "script": 'heppy_crab_script.sh'
    },
    'QCD700_ext1': {
        "ds": '/QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext1-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 300,
        "runtime": 40,
        "mem_cfg": me_cfgs["hadronic"],
        "script": 'heppy_crab_script.sh'
    },
    'QCD1000': {
        "ds": '/QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext1-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 200,
        "runtime": 40,
        "mem_cfg": me_cfgs["hadronic"],
        "script": 'heppy_crab_script.sh'
    },
    'QCD1500': {
        "ds": '/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext1-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 100,
        "runtime": 40,
        "mem_cfg": me_cfgs["hadronic"],
        "script": 'heppy_crab_script.sh'
    },
    'QCD2000': {
        "ds": '/QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring16MiniAODv2-PUSpring16_80X_mcRun2_asymptotic_2016_miniAODv2_v0_ext1-v1/MINIAODSIM',
        "maxlumis": -1,
        "perjob": 100,
        "runtime": 40,
        "mem_cfg": me_cfgs["hadronic"],
        "script": 'heppy_crab_script.sh'
    },
})

#now we construct the workflows from all the base datasets
workflow_datasets = {}
workflow_datasets["leptonic"] = {}
for k in [
        "ttHTobb", "ttHToNonbb",
        "ttHTobb_tranche3", "ttHToNonbb_tranche3",
        "TTbar_inc",
        "TTbar_inc_scaleup", "TTbar_inc_scaledown",
        "TTbar_sl",
        "TTbar_sl_scaleup", "TTbar_sl_scaledown",
        "TTbar_sl1", "TTbar_sl2",
        "TTbar_dl"
    ]:
    D = deepcopy(datasets[k])
    D["mem_cfg"] = "cfg_leptonic.py"
    workflow_datasets["leptonic"][k] = D

workflow_datasets["signal"] = {}
for k in ["ttHTobb", "ttHToNonbb", "TTbar_inc"]:
    D = deepcopy(datasets[k])
    workflow_datasets["signal"][k] = D

workflow_datasets["leptonic_nome"] = {}
for k in [
        #"ttHTobb",
        #"ttHToNonbb",
        #"ttHTobb_tranche3", "ttHToNonbb_tranche3",
        "TTbar_inc",
        #"TTbar_inc_scaleup", "TTbar_inc_scaledown",
        #"TTbar_sl",
        #"TTbar_sl_tranche3",
        #"TTbar_sl_scaleup",
        #"TTbar_sl_scaledown",
        #"TTbar_sl1", "TTbar_sl2",
        #"TTbar_dl",
        #"TTbar_dl_tranche3",
        #"ww", "wz", "zz",
        #"st_t", "stbar_t",
        #"st_tw", "stbar_tw",
        #"st_s",
        #"ttw_wlnu",
        #"ttw_wqq",
        #"ttz_zqq",
        # "wjets_ht_100_200",
        # "wjets_ht_200_400",
        # "wjets_ht_400_600",
        # "wjets_ht_600_800",
        # "wjets_ht_800_1200",
        # "wjets_ht_1200_2500",
        # "wjets_ht_2500_inf",
        #"dy_10_50",
        #"dy_50_inf"
    ]:
    D = deepcopy(datasets[k])

    D["mem_cfg"] = "cfg_noME.py"
    workflow_datasets["leptonic_nome"][k] = D

workflow_datasets["data"] = {}
for k in datasets.keys():
    if "data" in datasets[k]["script"]:
        D = deepcopy(datasets[k])
#        D["maxlumis"] = 1
        workflow_datasets["data"][k] = D

workflow_datasets["data_leptonic"] = {}
for k in datasets.keys():
    # Ignore hadronic
    if "JetHT" in k or "BTagCSV" in k:
        continue
    
    if "data" in datasets[k]["script"]:
        D = deepcopy(datasets[k])
        workflow_datasets["data_leptonic"][k] = D



workflow_datasets["hadronic"] = {}
for k in datasets.keys():
    if "QCD" in k or "ttH" in k or "TTbar_inc" in k:
        D = deepcopy(datasets[k])
        D["mem_cfg"] = me_cfgs["hadronic"]
#        D["maxlumis"] = 1
        workflow_datasets["hadronic"][k] = D

workflow_datasets["QCD_nome"] = {}
for k in datasets.keys():
    if "QCD" in k:
        D = deepcopy(datasets[k])
        D["mem_cfg"] = me_cfgs["nome"]
        workflow_datasets["QCD_nome"][k] = D


workflow_datasets["allmc_nome"] = {}
for k in datasets.keys():
    if "QCD" in k or k in ["ttHTobb", "ttHToNonbb", "TTbar_inc", "TTbar_sl1", "TTbar_sl2", "TTbar_dl"] :
        D = deepcopy(datasets[k])
        D["mem_cfg"] = me_cfgs["nome"]
        workflow_datasets["allmc_nome"][k] = D


#Pilot job for updating transfer functions, retraining BLR
workflow_datasets["pilot"] = {}
pilot_name = 'ttHTobb'
D = deepcopy(datasets[pilot_name])
D["perjob"] = 20
D["mem_cfg"] = me_cfgs["nome"]
workflow_datasets["pilot"][pilot_name] = D

#1-lumi per job, 10 job testing of a few samples
workflow_datasets["testing"] = {}

for k in ["ttHTobb", "TTbar_inc", "SingleMuon-Run2016B-PromptReco-v2"]:
    D = deepcopy(datasets[k])
    D["maxlumis"] = 40
    D["perjob"] = 2
    if "data" in D["script"]:
        D["maxlumis"] = 200
        D["perjob"] = 10
    D["runtime"] = 2
    D["mem_cfg"] = "cfg_noME.py"
    workflow_datasets["testing"][k] = D

datasets_local = {
    "mc": {
        "mem_cfg": me_cfgs["nome"],

        "script": 'heppy_crab_script.sh'
    },
    "data": {
        "maxlumis": -1,
        "mem_cfg": me_cfgs["nome"],
        "script": 'heppy_crab_script_data.sh'
    }
}

workflow_datasets["localtesting"] = {}
for k in ["mc", "data"]:
    D = deepcopy(datasets_local[k])
    D["mem_cfg"] = "cfg_noME.py"
    workflow_datasets["localtesting"][k] = D

workflow_datasets["localtesting_withme"] = {}
for k in ["mc", "data"]:
    D = deepcopy(datasets_local[k])
    D["mem_cfg"] = me_cfgs["leptonic"]
    workflow_datasets["localtesting_withme"][k] = D

workflow_datasets["testing_withme"] = {}
for k in ["ttHTobb", "TTbar_inc", "SingleMuon-Run2016B-PromptReco-v1"]:
    D = deepcopy(datasets[k])
    D["perjob"] = int(D["perjob"]/10)
    D["maxlumis"] = 100 * D["perjob"]
    D["runtime"] = int(D["runtime"]/5)
    D["mem_cfg"] = me_cfgs["default"]
    workflow_datasets["testing_withme"][k] = D

workflow_datasets["testing_hadronic_withme"] = {}
for k in ["ttHTobb", "TTbar_inc", "QCD1000", "JetHT-Run2016B-PromptReco-v1"]:
    D = deepcopy(datasets[k])
    D["perjob"] = int(5)
    D["maxlumis"] = 10 * D["perjob"]
    D["runtime"] = int(D["runtime"]/5)
    D["mem_cfg"] = me_cfgs["hadronic"]
    workflow_datasets["testing_hadronic_withme"][k] = D

#Now select a set of datasets
sel_datasets = workflow_datasets[args.workflow]

if __name__ == '__main__':
    from CRABAPI.RawCommand import crabCommand
    from CRABClient.UserUtilities import getUsernameFromSiteDB

    def submit(config):
        res = crabCommand('submit', config = config)
    
    def localsubmit(config, dname, opts):
        TMPDIR = "/scratch/{0}/crab_work/{1}/crab_{2}".format(os.environ["USER"], args.tag, dname)
        CMSSW_VERSION = "CMSSW_8_0_19"
        workdir = os.path.join(TMPDIR, CMSSW_VERSION, "work")
        try: 
            shutil.rmtree(TMPDIR)
        except Exception as e:
            pass
        os.makedirs(TMPDIR)
        os.system("cd {0}".format(TMPDIR))
        pwd = os.getcwd() 
        os.chdir(TMPDIR)
        os.system("scramv1 project CMSSW {0}".format(CMSSW_VERSION))
        os.makedirs(workdir)
        os.chdir(pwd)
        for inf in config.JobType.inputFiles + [config.JobType.scriptExe, 'PSet_local.py']:
            shutil.copy(inf, os.path.join(workdir, os.path.basename(inf)))
        os.system("cp -r $CMSSW_BASE/lib {0}/".format(workdir)) 
        os.system("mv {0}/PSet_local.py {0}/PSet.py".format(workdir)) 
        os.system("cp {0} {1}/x509_proxy".format(os.environ["X509_USER_PROXY"], workdir)) 
        os.system("cp -r $CMSSW_BASE/lib/slc*/proclib {0}/lib/slc*/".format(workdir)) 
        os.system('find $CMSSW_BASE/src/ -path "*/data/*" -type f | sed -s "s|$CMSSW_BASE/||" > files')
        os.system('cp files $CMSSW_BASE/; cd $CMSSW_BASE; for f in `cat files`; do cp --parents $f {0}/; done'.format(workdir))
        runfile = open(workdir+"/run.sh", "w")
        runfile.write(
"""
#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
scram b ProjectRename
eval `scramv1 runtime -sh`
scram b
env
./{0} 1 {1}
""".format(config.JobType.scriptExe, " ".join(config.JobType.scriptArgs)).strip() + '\n'
)
        runfile.close()
        os.system('chmod +x {0}/run.sh'.format(workdir))
        os.system('cd {0}/{1};eval `scram runtime -sh`;scram b;'.format(TMPDIR, CMSSW_VERSION))
        archive_name = "_".join([dname, args.workflow, args.tag])
        os.system('cd {0};tar zcfv job_{1}.tar.gz {2} > {1}.log'.format(TMPDIR, archive_name, CMSSW_VERSION))
        os.system("cp {0}/job_{1}.tar.gz ./".format(TMPDIR, archive_name))
        #os.system("cp -r $CMSSW_BASE/src {0}/".format(workdir)) 

    from CRABClient.UserUtilities import config
    config = config()
    submitname = args.tag
    config.General.workArea = 'crab_projects/' + submitname
    config.General.transferLogs = True

    config.JobType.pluginName = 'Analysis'
    config.JobType.psetName = 'heppy_crab_fake_pset.py'
    config.JobType.maxMemoryMB = 2500

    import os
    os.system("tar czf python.tar.gz --directory $CMSSW_BASE python `find $CMSSW_BASE/src -name python | perl -pe s#$CMSSW_BASE/## `")
    os.system("tar czf data.tar.gz --dereference --directory $CMSSW_BASE/src/TTH/MEAnalysis root")
    if not "testing" in args.workflow: 
        os.system("make -sf $CMSSW_BASE/src/TTH/Makefile get_hashes")
        os.system("echo '\n\n{0}\n-------------' >> $CMSSW_BASE/src/TTH/logfile.md".format(submitname))
        os.system("cat $CMSSW_BASE/src/TTH/hash >> $CMSSW_BASE/src/TTH/logfile.md")
    
    vhbb_dir = os.environ.get("CMSSW_BASE") + "/src/VHbbAnalysis/Heppy/test"
    tth_data_dir = os.environ.get("CMSSW_BASE") + "/src/TTH/MEAnalysis/data"
    config.JobType.inputFiles = [
        'hash',
        'analyze_log.py',
        'FrameworkJobReport.xml',
        'env.sh',
        'setenv_sklearn_cmssw.sh',
        'post.sh',
        'heppy_config.py',
        'heppy_config_data.py',
        'heppy_crab_script.py',
        'python.tar.gz',
        'data.tar.gz',
        "MEAnalysis_heppy.py",
        tth_data_dir + '/BDT.pickle',
        vhbb_dir + '/MVAJetTags_620SLHCX_Phase1And2Upgrade.db',
        vhbb_dir + '/combined_cmssw.py',
        vhbb_dir + '/vhbb.py',
        vhbb_dir + '/vhbb_combined.py',
        vhbb_dir + '/TMVAClassification_BDT.weights.xml',
        vhbb_dir + '/puData.root',
        vhbb_dir + '/puDataMinus.root',
        vhbb_dir + '/puDataPlus.root',
        vhbb_dir + '/puMC.root',
        vhbb_dir + '/json.txt',
        vhbb_dir + '/triggerEmulation.root',
        vhbb_dir + "/Zll-spring15.weights.xml",
        vhbb_dir + "/Wln-spring15.weights.xml",
        vhbb_dir + "/Znn-spring15.weights.xml",
        vhbb_dir + "/VBF-spring15.weights.xml",
        vhbb_dir + "/ttbar-spring16-80X.weights.xml",
        vhbb_dir + "/ttbar-spring16-500k-13d-300t.weights.xml",
        vhbb_dir + '/TMVA_blikelihood_vbf_cmssw76_h21trained.weights.xml'
    ]

    config.Data.inputDBS = 'global'
    config.Data.splitting = 'LumiBased'
    config.Data.publication = True
    config.Data.ignoreLocality = False
    config.Data.allowNonValidInputDataset = True

    #config.Site.whitelist = ["T2_CH_CSCS", "T1_US_FNAL", "T2_DE_DESY", "T1_DE_KIT"]
    #config.Site.blacklist = ["T2_US_Florida", "T2_US_MIT", "T2_US_Wisconsin", "T2_US_Vanderbilt"]

    config.Site.storageSite = "T2_CH_CSCS"

    #loop over samples
    for sample in sel_datasets.keys():
        print 'submitting ' + sample, sel_datasets[sample]
        
        mem_cfg = sel_datasets[sample]["mem_cfg"]
        config.JobType.scriptExe = sel_datasets[sample]["script"]
        
        if not localtesting:
            dataset = sel_datasets[sample]["ds"]
            nlumis = sel_datasets[sample]["maxlumis"]
            perjob = sel_datasets[sample]["perjob"]
            runtime_min = sel_datasets[sample].get("runtime_min", sel_datasets[sample]["runtime"]*60)

            config.JobType.maxJobRuntimeMin = runtime_min
            config.General.requestName = sample + "_" + submitname
            config.Data.inputDataset = dataset
            config.Data.unitsPerJob = perjob
            config.Data.totalUnits = nlumis
            config.Data.outputDatasetTag = submitname
            try:
                config.Data.outLFNDirBase = '/store/user/{0}/tth/'.format(getUsernameFromSiteDB()) + submitname
            except Exception as e:
                config.Data.outLFNDirBase = '/store/user/{0}/tth/'.format(os.environ["USER"]) + submitname

        config.JobType.scriptArgs = ['ME_CONF={0}'.format(mem_cfg)]
        if localtesting:
            localsubmit(config, sample, sel_datasets[sample])
        else:
            try:
                submit(config)
            except Exception as e:
                print e
                print "skipping"
                                                                                                                                                                                                                   
