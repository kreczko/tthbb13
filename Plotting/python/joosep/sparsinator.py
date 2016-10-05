from __future__ import print_function

import ROOT

import sys, os
from collections import OrderedDict
import logging
LOG_MODULE_NAME = logging.getLogger(__name__)
    
import numpy as np
from TTH.MEAnalysis.samples_base import getSitePrefix, samples_nick, get_prefix_sample, PROCESS_MAP, TRIGGERPATH_MAP
from TTH.Plotting.Datacards.sparse import save_hdict

from TTH.CommonClassifier.db import ClassifierDB

class BufferedTree:
    """Class with buffered TTree access, so that using tree.branch does not load the entry twice
    
    Attributes:
        branches (dict string->branch): TTree branches
        buf (dict string->data): The buffer, according to branch name
        iEv (int): Current event
        maxEv (int): maximum number of events in the TTree
        tree (TTree): Underlying TTree
    """
    def __init__(self, tree):
        self.tree = tree
        self.branches = {}
        for br in self.tree.GetListOfBranches():
            self.branches[br.GetName()] = br
        self.buf = {}
        self.iEv = 0
        self.maxEv = int(self.tree.GetEntries())
        
    def __getattr__(self, attr):
        if self.branches.has_key(attr):
            if self.buf.has_key(attr):
                return self.buf[attr]
            else:
                val = getattr(self.tree, attr)
                self.buf[attr] = val
                return val
        else:
            raise KeyError(
                "Could not find key={0}".format(attr)
            )
    
    def __iter__(self):
        return self
    
    def next(self):
        if self.iEv > self.maxEv:
            raise StopIteration
        self.buf = {}
        self.iEv += 1
        self.tree.GetEntry(self.iEv)
        return self

    def GetEntries(self):
        return self.tree.GetEntries()


def assign_process_label(process, event):
    """ In case the you need to decide which process an event falls into based on the event itself.

    Args:
        process (string): the input process
        event (dict string->data): the event data
    """
    if process == "ttbarUnsplit":
        ttCls = event["ttCls"]
        if ttCls == 51:
            _process = "ttbarPlusB"
        elif ttCls == 52:
            _process = "ttbarPlus2B"
        elif ttCls >= 53:
            _process = "ttbarPlusBBbar"
        elif ttCls in [41, 42, 43, 44, 45]:
            _process = "ttbarPlusCCbar"
        else:
            _process = "ttbarOther"
        return _process 
    elif samples_nick.has_key(process):
        return samples_nick[process]
    return process

def logit(x):
    return np.log(x/(1.0 - x))

class Func:
    """Describes a function that gets a value from a branch
    
    Attributes:
        branch (string): Name of the branch
        func (function TTree->value): Getter function
    """
    def __init__(self, branch, **kwargs):
        self.branch = branch
        self.func = kwargs.get("func",
            lambda ev, branch=self.branch: getattr(ev, branch)
        )

    def __call__(self, event):
        return self.func(event)

class Var:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.typ = kwargs.get("type")
        
        self.present = True

        #in case function not defined, just use variable name
        self.nominal_func = kwargs.get("nominal", Func(self.name))
        self.funcs_schema = kwargs.get("funcs_schema", {})

        self.systematics_funcs = kwargs.get("systematics", {})
        self.schema = kwargs.get("schema", ["mc", "data"])

    def fillSystematicsSuffix(self, systematics):
        """Fills the systematic function table with suffix lookup functions
        
        Args:
            systematics (list of string): Systematics to use
        
        Returns:
            nothing
        """
        self.systematics_funcs = {}
        for syst in systematics:
            for sdir in ["Up", "Down"]:
                suffix = syst + sdir
                self.systematics_funcs[suffix] = Func(
                    self.name + "_" + suffix,
                    func=lambda ev, suff=suffix, fallback=self.name: getattr(ev, suff, fallback)
                )

    def getValue(self, event, schema, systematic="nominal"):
                
        if self.present:
            try:
                if systematic == "nominal" or not self.systematics_funcs.has_key(systematic):
                    return self.funcs_schema.get(schema, self.nominal_func)(event)
                else:
                    return self.systematics_funcs[systematic](event)
            except:  
                print (self.name + " " + systematic + " DEACTIVATED")
                self.present = False
                return 0
        else:            
            return 0
                    

class Desc:
    """Event description with varying systematics
    
    Attributes:
        variables_dict (dict of string->Var): Variables in the event
    """

    def __init__(self, systematics, variables=[]):
        """Creates the event description based on a list of variables
        
        Args:
            systematics (list of string): systematics to use for variable lookup
            variables (list, optional): Variables to use
        """

        for v in variables:
            if v.systematics_funcs == "suffix":
                v.fillSystematicsSuffix(systematics)

        self.variables_dict = OrderedDict([(v.name, v) for v in variables])

    def getValue(self, event, schema="mc", systematic="nominal"):
        """Returns a dict with the values of all the variables given a systematic
        
        Args:
            event (TTree): The underlying data TTree
            schema (str, optional): The schema of the data, e.g. "mc", "data"
            systematic (str, optional): The systematic to use
        
        Returns:
            dict of string->data: The values of all the variables
        """
        ret = OrderedDict()
        for vname, v in self.variables_dict.items():
            if schema in v.schema:
                ret[vname] = v.getValue(event, schema, systematic)
        return ret

def event_as_str(ret):
    NA = "NA"
    ret2 = {}
    ret2.update(ret)
    ret2["jets_p4_spherical"] = ",\n".join([
        "    jet(pt={:.2f} eta={:.2f} phi={:.2f} m={:.2f})".format(
            lv.Pt(), lv.Eta(), lv.Phi(), lv.M()
        ) for lv in ret["jets_p4"]
    ])

    r = """
Event(
  run:lumi:event = {run}:{lumi}:{evt}
  syst = {syst}
  numJets = {numJets}
  nBCSVM = {nBCSVM} nBCMVAM = {nBCMVAM}
  blr_CSV = {btag_LR_4b_2b_btagCSV_logit:.2f} blr_cMVA = {btag_LR_4b_2b_btagCMVA_logit:.2f}
  jets_p4 =
{jets_p4_spherical}
  mem_SL_0w2h2t_p = {mem_SL_0w2h2t_p:.4f} mem_SL_1w2h2t_p = {mem_SL_1w2h2t_p:.4f} mem_SL_2w2h2t_p = {mem_SL_2w2h2t_p:.4f}
  ttCls = {ttCls}
)
""".format(**ret2).strip()
    return r

def lv_p4s(pt, eta, phi, m, btagCSV=-100):
    ret = ROOT.TLorentzVector()
    ret.SetPtEtaPhiM(pt, eta, phi, m)
    setattr(ret, "btagCSV", btagCSV)
    return ret


# Calculate lepton SF on the fly
# Currently only add muons
# TODO: Add electrons as well
def calc_lepton_SF(ev):
    
    weight = 1.

    # Leading muon
    if ev.nleps >= 1:
        if abs(ev.leps_pdgId[0] == 13):
            weight *= ev.leps_SF_IdCutTight[0]
            weight *= ev.leps_SF_IsoTight[0]
        
    # Subleading muon
    if ev.nleps >= 2:
        if abs(ev.leps_pdgId[1] == 13):
            weight *= ev.leps_SF_IdCutTight[1]
            weight *= ev.leps_SF_IsoTight[1]

    return weight
    
class Axis:
    def __init__(self, name, nbins, lo, hi, func):
        self.name = name
        self.nbins = nbins 
        self.lo = lo
        self.hi = hi
        self.func = func

    def getValue(self, event):
        return self.func(event)

class SparseOut:
    def __init__(self, name, cut, axes, outdir):
        """
        Creates a sparse histogram.
        name (string): name of the histogram, will also be used for the ROOT file
        cut (function event -> bool): decides if this event should be filled 
        axes (list of Axis objects): defines the axes of this sparse histogram
        outdir (TDirectory): the output directory where the THnSparse will be saved
        """
        self.cut = cut
        self.axes = axes

        #create the bin arrays
        nbinVec = getattr(ROOT, "std::vector<int>")()
        minVec = getattr(ROOT, "std::vector<double>")()
        maxVec = getattr(ROOT, "std::vector<double>")()
        for ax in axes:
            nbinVec.push_back(ax.nbins)
            minVec.push_back(ax.lo)
            maxVec.push_back(ax.hi)
        ROOT.gROOT.cd()
        self.hist = ROOT.THnSparseF(
            name,
            name,
            len(axes),
            nbinVec.data(),
            minVec.data(),
            maxVec.data(),
        )
        #make sure this histogram is saved
        outdir.Add(self.hist)
        for iax, ax in enumerate(self.axes):
            self.hist.GetAxis(iax).SetName(ax.name)
            self.hist.GetAxis(iax).SetTitle(ax.name)

        self.hist.Sumw2()
    
    def fill(self, event, weight=1.0):
        """
        Fill this sparse histogram based on the values defined in the axes.
        event (dict of string->object): the data of this event (under a certain systematic assumption)
        weight (float): weight to be used for this event:w
        
        """
        #Very important: need to use double, not float (despite name THnSparseF pointing to float)
        valVec = getattr(ROOT, "std::vector<double>")()

        #loop over defined axes, calculate values
        for ax in self.axes:
            v = ax.getValue(event)
            #Very important: manually treat underflow and overflow, put into first or last bin!
            if v <= ax.lo:
                v = ax.lo
            #value of last bin
            elif v >= ax.hi:
                v = ax.hi - float(ax.hi - ax.lo)/float(ax.nbins)

            valVec.push_back(v)
        #print([v for v in valVec], "w={0}".format(weight))

        #Very important: here we need to take the pointer to the start of the value vector with std::vector<double)::data() -> double*
        #otherwise the THnSparse is filled, but with garbage and will result in TBrowser segfaults later 
        return self.hist.Fill(valVec.data(), weight)

def get_schema(sample):
    process = samples_nick[sample]
    if "data" in process:
        schema = "data"
    else:
        schema = "mc"
    return schema

def createOutputs(config, axes, dirs, systematics):
    """Creates an output dictionary with fillable objects in TDirectories based on categories and systematics. 
    
    Args:
        config (ConfigParser): Configuration with sparsinator info
        axes (dict of string->list of Axes): Dictionary of various kinds of Axes to save 
        dirs (dict of string->TDirectory): dictionary of output directories
        systematics (list of string): list of systematics for which to create outputs
    
    Returns:
        dict of string->output: Dictionary of fillable outputs
    """
    outdict_syst = {}
    categories = config.get("sparsinator", "categories").split()
 
    for syst in systematics: 
        syststr = ""
        if syst != "nominal":
            syststr = "_" + syst

        outdict = {}

        for cat in categories:
            cat_name = config.get(cat, "name")
            axes_name = config.get(cat, "axes")
            flag = config.get(cat, "flag")

            dirs[cat_name].cd()
            outdict["{0}/sparse".format(cat_name)] = SparseOut(
                "sparse" + syststr,
                lambda ev, flag=flag: ev[flag] == 1,
                axes[axes_name],
                dirs[cat_name]
            )

        outdict_syst[syst] = outdict
    return outdict_syst

def pass_HLT_sl_mu(event):
    pass_hlt = event["HLT_ttH_SL_mu"]
    return event["is_sl"] and pass_hlt and int(abs(event["leps_pdgId"][0])) == 13

def pass_HLT_sl_el(event):
    pass_hlt = event["HLT_ttH_SL_el"]
    return event["is_sl"] and pass_hlt and int(abs(event["leps_pdgId"][0])) == 11

def pass_HLT_dl_mumu(event):
    pass_hlt = event["HLT_ttH_DL_mumu"]
    st = sum(map(abs, event["leps_pdgId"]))
    return event["is_dl"] and pass_hlt and st == 26

def pass_HLT_dl_elmu(event):
    pass_hlt = event["HLT_ttH_DL_elmu"]
    st = sum(map(abs, event["leps_pdgId"]))
    return event["is_dl"] and pass_hlt and st == 24

def pass_HLT_dl_elel(event):
    pass_hlt = event["HLT_ttH_DL_elel"]
    st = sum(map(abs, event["leps_pdgId"]))
    return event["is_dl"] and pass_hlt and st == 22

def pass_HLT_fh(event):
    pass_hlt = event["HLT_ttH_FH"]
    return event["is_fh"] and pass_hlt ## FIXME add: st == ??

def triggerPath(event):
    if event["is_sl"] and pass_HLT_sl_mu(event):
        return TRIGGERPATH_MAP["m"]
    elif event["is_sl"] and pass_HLT_sl_el(event):
        return TRIGGERPATH_MAP["e"]
    elif event["is_dl"] and pass_HLT_dl_mumu(event):
        return TRIGGERPATH_MAP["mm"]
    elif event["is_dl"] and pass_HLT_dl_elmu(event):
        return TRIGGERPATH_MAP["em"]
    elif event["is_dl"] and pass_HLT_dl_elel(event):
        return TRIGGERPATH_MAP["ee"]
    elif event["is_fh"] and pass_HLT_fh(event):
        return TRIGGERPATH_MAP["fh"]
    return 0

def main(analysis, file_names, sample_name, ofname, skip_events=0, max_events=-1):
    """Summary
    
    Args:
        analysis (Analysis): The main Analysis object used to configure sparsinator
        file_names (list of string): the PFN of the files to process
        sample_name (string): Name of the current sample
        ofname (string): Name of the file
        skip_events (int, optional): Number of events to skip
        max_events (int, optional): Number of events to process
    
    Returns:
        nothing
    
    Raises:
        Exception: Description
    """



    MEM_SF = analysis.config.getfloat("sparsinator", "mem_sf")

    # Create pairs of (systematic_name, weight function), which will be used on the
    # nominal event to create reweighted copies of the event. The systematic names
    # here will define the output histograms like
    # ttH/sl/sparse -> nominal event
    # ttH/sl/sparse_CMS_ttH_CSVJESUp -> event with btagWeight with JES up variation
    # ...
    
    systematic_weights = []
    btag_weights = []

    systematics_event = []

    #Optionally add systematics
    if analysis.config.get("sparsinator", "add_systematics"):

        systematics_event = analysis.config.get("systematics", "event").split()

        #systematics with weight

        #create b-tagging systematics
        for sdir in ["up", "down"]:
            for syst in ["cferr1", "cferr2", "hf", "hfstats1", "hfstats2", "jes", "lf", "lfstats1", "lfstats2"]:
                for tagger in ["CSV", "CMVAV2"]:
                    bweight = "btagWeight{0}_{1}_{2}".format(tagger, sdir, syst)
                    #make systematic outputs consistent in Up/Down naming
                    sdir_cap = sdir.capitalize()
                    systematic_weights += [
                        ("CMS_ttH_{0}{1}{2}".format(tagger, syst, sdir_cap), lambda ev, bweight=bweight:
                            ev["puWeight"] * ev["triggerEmulationWeight"] * ev["lep_SF_weight"] * ev[bweight])
                    ]
                    btag_weights += [bweight]

        systematic_weights += [
                ("puUp", lambda ev: ev["btagWeightCSV"] * ev["triggerEmulationWeight"] * ev["lep_SF_weight"] * ev["puWeightUp"]),
                ("puDown", lambda ev: ev["btagWeightCSV"] * ev["triggerEmulationWeight"] * ev["lep_SF_weight"] * ev["puWeightDown"]),
                ("unweighted", lambda ev: 1.0)
        ]


    extra_vars =  ["topCandidate_fRec",
                   "topCandidate_pt",
                   "topCandidate_ptcal",
                   "topCandidate_mass",
                   "topCandidate_masscal",
                   "topCandidate_n_subjettiness",
                   "topCandidate_n_subjettiness_groomed",
                
                   "higgsCandidate_secondbtag_subjetfiltered", 
                   "higgsCandidate_bbtag", 
                   "higgsCandidate_tau1", 
                   "higgsCandidate_tau2", 
                   "higgsCandidate_mass", 
                   "higgsCandidate_mass_softdropz2b1filt", 
                   "higgsCandidate_sj12massb_subjetfiltered", 
                   "higgsCandidate_sj12masspt_subjetfiltered", 
                
                   "multiclass_class",
                   "multiclass_proba_ttb",
                   "multiclass_proba_tt2b",
                   "multiclass_proba_ttbb",
                   "multiclass_proba_ttcc",
                   "multiclass_proba_ttll"]

    #create the event description
    desc = Desc(
        systematics_event,
        [
        Var(name="run"),
        Var(name="lumi"),
        Var(name="evt"),

        Var(name="is_sl"),
        Var(name="is_dl"),
        Var(name="is_fh"),

        Var(name="nfatjets"),
        Var(name="fatjets_pt"),
        Var(name="fatjets_eta"),
        Var(name="fatjets_mass"),

        Var(name="leps_pt"),
        Var(name="leps_eta"),

        Var(name="numJets", systematics="suffix"),
        Var(name="nBCSVM", systematics="suffix"),
        Var(name="nBCMVAM", systematics="suffix"),
        
        Var(name="Wmass", systematics="suffix"),

        Var(name="btag_LR_4b_2b_btagCSV_logit",
            nominal=Func("blr_CSV", func=lambda ev: logit(ev.btag_LR_4b_2b_btagCSV)),
        ),
        Var(name="btag_LR_4b_2b_btagCMVA_logit",
            nominal=Func("blr_cMVA", func=lambda ev: logit(ev.btag_LR_4b_2b_btagCMVA)),
        ),

        Var(name="leps_pdgId", nominal=Func("leps_pdgId", func=lambda ev: [int(ev.leps_pdgId[i]) for i in range(ev.nleps)])),

        Var(name="jets_p4",
            nominal=Func(
                "jets_p4",
                func=lambda ev: [lv_p4s(ev.jets_pt[i], ev.jets_eta[i], ev.jets_phi[i], ev.jets_mass[i], ev.jets_btagCSV[i]) for i in range(ev.njets)]
            ),
            systematics = {
                "CMS_scale_jUp": Func(
                    "jets_p4_JESUp",
                    func=lambda ev: [lv_p4s(ev.jets_pt[i]*float(ev.jets_corr_JESUp[i])/float(ev.jets_corr[i]), ev.jets_eta[i], ev.jets_phi[i], ev.jets_mass[i], ev.jets_btagCSV[i]) for i in range(ev.njets)]
                ),
                "CMS_scale_jDown": Func(
                    "jets_p4_JESDown",
                    func=lambda ev: [lv_p4s(ev.jets_pt[i]*float(ev.jets_corr_JESDown[i])/float(ev.jets_corr[i]), ev.jets_eta[i], ev.jets_phi[i], ev.jets_mass[i], ev.jets_btagCSV[i]) for i in range(ev.njets)]
                ),
                "CMS_res_jUp": Func(
                    "jets_p4_JERUp",
                    func=lambda ev: [lv_p4s(ev.jets_pt[i]*float(ev.jets_corr_JERUp[i])/float(ev.jets_corr_JER[i]) if ev.jets_corr_JER[i]>0 else 0.0, ev.jets_eta[i], ev.jets_phi[i], ev.jets_mass[i], ev.jets_btagCSV[i]) for i in range(ev.njets)]
                ),
                "CMS_res_jDown": Func(
                    "jets_p4_JERDown",
                    func=lambda ev: [lv_p4s(ev.jets_pt[i]*float(ev.jets_corr_JERDown[i])/float(ev.jets_corr_JER[i]) if ev.jets_corr_JER[i]>0 else 0.0, ev.jets_eta[i], ev.jets_phi[i], ev.jets_mass[i], ev.jets_btagCSV[i]) for i in range(ev.njets)]
                )
            }
        ),

        Var(name="mem_SL_0w2h2t_p",
            nominal=Func("mem_p_SL_0w2h2t", func=lambda ev, sf=MEM_SF: ev.mem_tth_SL_0w2h2t_p/(ev.mem_tth_SL_0w2h2t_p + sf*ev.mem_ttbb_SL_0w2h2t_p) if getattr(ev,"mem_tth_SL_0w2h2t_p",0)>0 else 0.0),
        ),
        Var(name="mem_SL_1w2h2t_p",
            nominal=Func("mem_p_SL_1w2h2t", func=lambda ev, sf=MEM_SF: ev.mem_tth_SL_1w2h2t_p/(ev.mem_tth_SL_1w2h2t_p + sf*ev.mem_ttbb_SL_1w2h2t_p) if getattr(ev,"mem_tth_SL_1w2h2t_p",0)>0 else 0.0),
        ),
        Var(name="mem_SL_2w2h2t_p",
            nominal=Func("mem_p_SL_2w2h2t", func=lambda ev, sf=MEM_SF: ev.mem_tth_SL_2w2h2t_p/(ev.mem_tth_SL_2w2h2t_p + sf*ev.mem_ttbb_SL_2w2h2t_p) if getattr(ev,"mem_tth_SL_2w2h2t_p",0)>0 else 0.0),
        ),
        Var(name="mem_DL_0w2h2t_p",
            nominal=Func("mem_p_DL_0w2h2t", func=lambda ev, sf=MEM_SF: ev.mem_tth_DL_0w2h2t_p/(ev.mem_tth_DL_0w2h2t_p + sf*ev.mem_ttbb_DL_0w2h2t_p) if getattr(ev,"mem_tth_DL_0w2h2t_p",0)>0 else 0.0),
        ),
        Var(name="mem_FH_4w2h2t_p",
            nominal=Func("mem_p_FH_4w2h2t", func=lambda ev, sf=MEM_SF: ev.mem_tth_FH_4w2h2t_p/(ev.mem_tth_FH_4w2h2t_p + sf*ev.mem_ttbb_FH_4w2h2t_p) if getattr(ev,"mem_tth_FH_4w2h2t_p",0)>0 else 0.0),
        ),
        Var(name="mem_FH_3w2h2t_p",
            nominal=Func("mem_p_FH_3w2h2t", func=lambda ev, sf=MEM_SF: ev.mem_tth_FH_3w2h2t_p/(ev.mem_tth_FH_3w2h2t_p + sf*ev.mem_ttbb_FH_3w2h2t_p) if getattr(ev,"mem_tth_FH_3w2h2t_p",0)>0 else 0.0),
        ),
        Var(name="mem_FH_4w2h1t_p",
            nominal=Func("mem_p_FH_4w2h1t", func=lambda ev, sf=MEM_SF: ev.mem_tth_FH_4w2h1t_p/(ev.mem_tth_FH_4w2h1t_p + sf*ev.mem_ttbb_FH_4w2h1t_p) if getattr(ev,"mem_tth_FH_4w2h1t_p",0)>0 else 0.0),
        ),
        Var(name="mem_FH_0w0w2h2t_p",
            nominal=Func("mem_p_FH_0w0w2h2t", func=lambda ev, sf=MEM_SF: ev.mem_tth_FH_0w0w2h2t_p/(ev.mem_tth_FH_0w0w2h2t_p + sf*ev.mem_ttbb_FH_0w0w2h2t_p) if getattr(ev,"mem_tth_FH_0w0w2h2t_p",0)>0 else 0.0),
        ),
        Var(name="mem_FH_0w0w2h1t_p",
            nominal=Func("mem_p_FH_0w0w2h1t", func=lambda ev, sf=MEM_SF: ev.mem_tth_FH_0w0w2h1t_p/(ev.mem_tth_FH_0w0w2h1t_p + sf*ev.mem_ttbb_FH_0w0w2h1t_p) if getattr(ev,"mem_tth_FH_0w0w2h1t_p",0)>0 else 0.0),
        ),

        Var(name="HLT_ttH_DL_mumu", funcs_schema={"mc": lambda ev: 1.0, "data": lambda ev: ev.HLT_ttH_DL_mumu}),
        Var(name="HLT_ttH_DL_elel", funcs_schema={"mc": lambda ev: 1.0, "data": lambda ev: ev.HLT_ttH_DL_elel}),
        Var(name="HLT_ttH_DL_elmu", funcs_schema={"mc": lambda ev: 1.0, "data": lambda ev: ev.HLT_ttH_DL_elmu}),
        Var(name="HLT_ttH_SL_el", funcs_schema={"mc": lambda ev: 1.0, "data": lambda ev: ev.HLT_ttH_SL_el}),
        Var(name="HLT_ttH_SL_mu", funcs_schema={"mc": lambda ev: 1.0, "data": lambda ev: ev.HLT_ttH_SL_mu}),
        Var(name="HLT_ttH_FH", funcs_schema={"mc": lambda ev: 1.0, "data": lambda ev: ev.HLT_ttH_FH}),

        Var(name="lep_SF_weight", 
            funcs_schema={"mc": lambda ev: calc_lepton_SF(ev), 
                          "data": lambda ev: 1.0}),


    #MC-only branches
        Var(name="ttCls", schema=["mc"]),
        Var(name="puWeight", schema=["mc"]),
        Var(name="puWeightUp", schema=["mc"]),
        Var(name="puWeightDown", schema=["mc"]),
        Var(name="triggerEmulationWeight", schema=["mc"]),



        #nominal b-tag weight, systematic weights added later
        Var(name="btagWeightCSV", schema=["mc"]),
        Var(name="btagWeightCMVAV2", schema=["mc"]),
        ] +
        [Var(name=bw, schema=["mc"]) for bw in btag_weights] + [Var(name=br) for br in extra_vars]
    )

    # Create the axes we want in the sparse histogram
    # Axis we will want to have in all sparse histograms
    axes_basic_all = [
        Axis("process", 20, 0, 20, lambda ev: ev["process"]),
        Axis("triggerPath", 20, 0, 20, lambda ev: ev["triggerPath"]),
        Axis("counting", 1, 0, 1, lambda ev: ev["counting"]),
        Axis("parity", 1, 0, 1, lambda ev: ev["evt"]%2==0),

        Axis("numJets", 5, 3, 8, lambda ev: ev["numJets"]),
        Axis("nBCSVM", 4, 1, 5, lambda ev: ev["nBCSVM"]),
        Axis("nBCMVAM", 4, 1, 5, lambda ev: ev["nBCMVAM"]),

        Axis("jetsByPt_0_pt", 50, 0, 400, lambda ev: ev["jets_p4"][0].Pt()),
        
        Axis("btag_LR_4b_2b_btagCSV_logit", 30, -5, 10, lambda ev: ev["btag_LR_4b_2b_btagCSV_logit"]),
        Axis("btag_LR_4b_2b_btagCMVA_logit", 30, -5, 10, lambda ev: ev["btag_LR_4b_2b_btagCMVA_logit"]),

        Axis("common_bdt", 36, -1, 1, lambda ev: ev["common_bdt"]),
        Axis("common_mem", 36, 0, 1, lambda ev: ev["common_mem"]),
    ]

    axes_basic_sl = [
        Axis("leps_0_pt", 50, 0, 300, lambda ev: ev["leps_pt"][0]),
    ]

    axes_basic_dl = [
        Axis("leps_0_pt", 50, 0, 300, lambda ev: ev["leps_pt"][0]),
    ]

    axes_basic_fh = [
        Axis("mem_FH_4w2h2t_p", 36, 0, 1, lambda ev: ev["mem_FH_4w2h2t_p"]),
        Axis("mem_FH_3w2h2t_p", 36, 0, 1, lambda ev: ev["mem_FH_3w2h2t_p"]),
        Axis("mem_FH_4w2h1t_p", 36, 0, 1, lambda ev: ev["mem_FH_4w2h1t_p"]),
        Axis("mem_FH_0w0w2h2t_p", 36, 0, 1, lambda ev: ev["mem_FH_0w0w2h2t_p"]),
        Axis("mem_FH_0w0w2h1t_p", 36, 0, 1, lambda ev: ev["mem_FH_0w0w2h1t_p"]),
    ]

    axes_extra_sl = [    
        Axis("Wmass", 100, 50, 150, lambda ev: ev["Wmass"]),
        
        Axis("jetsByPt_1_pt", 50, 0, 400, lambda ev: ev["jets_p4"][1].Pt()),
        Axis("jetsByPt_2_pt", 50, 0, 400, lambda ev: ev["jets_p4"][2].Pt()),

        Axis("jetsByPt_0_btagCSV", 50, -1, 1, lambda ev: ev["jets_p4"][0].btagCSV),

        Axis("jetsByPt_0_eta", 50, -2.5, 2.5, lambda ev: ev["jets_p4"][0].Eta()),
        Axis("jetsByPt_1_eta", 50, -2.5, 2.5, lambda ev: ev["jets_p4"][1].Eta()),
        Axis("jetsByPt_2_eta", 50, -2.5, 2.5, lambda ev: ev["jets_p4"][2].Eta()),

        Axis("fatjetByPt_0_pt", 50, 0, 600, lambda ev: ev["fatjets_pt"][0] if ev["nfatjets"] else -100),
        Axis("fatjetByPt_0_eta", 50, -2.5, 2.5, lambda ev: ev["fatjets_eta"][0] if ev["nfatjets"] else -100),
        Axis("fatjetByPt_0_mass", 50, 0, 600, lambda ev: ev["fatjets_mass"][0] if ev["nfatjets"] else -100),

        Axis("leps_0_eta", 50, -2.5, 2.5, lambda ev: ev["leps_eta"][0]),

        Axis("topCandidate_fRec", 50, 0, 0.4, lambda ev: ev["topCandidate_fRec"][0] if len(ev["topCandidate_pt"]) else -100),
        Axis("topCandidate_pt", 50, 150, 600, lambda ev: ev["topCandidate_pt"][0] if len(ev["topCandidate_pt"]) else -100),
        Axis("topCandidate_ptcal", 50, 150, 600, lambda ev: ev["topCandidate_ptcal"][0] if len(ev["topCandidate_pt"]) else -100),
        Axis("topCandidate_mass", 50, 0, 250, lambda ev: ev["topCandidate_mass"][0] if len(ev["topCandidate_pt"]) else -100),
        Axis("topCandidate_masscal", 50, 0, 250, lambda ev: ev["topCandidate_masscal"][0] if len(ev["topCandidate_pt"]) else -100),
        Axis("topCandidate_n_subjettiness", 50, 0, 1, lambda ev: ev["topCandidate_n_subjettiness"][0] if len(ev["topCandidate_pt"]) else -100),
        Axis("topCandidate_n_subjettiness_groomed", 50, 0, 1, lambda ev: ev["topCandidate_n_subjettiness_groomed"][0] if len(ev["topCandidate_pt"]) else -100),

        Axis("higgsCandidate_secondbtag_subjetfiltered", 50, -1,1, lambda ev: ev["higgsCandidate_secondbtag_subjetfiltered"][0] if len(ev["higgsCandidate_mass"]) else -100),
        Axis("higgsCandidate_bbtag", 50, -1, 1, lambda ev: ev["higgsCandidate_bbtag"][0] if len(ev["higgsCandidate_mass"]) else -100),
        Axis("higgsCandidate_tau1", 50, 0, 1, lambda ev: ev["higgsCandidate_tau1"][0] if len(ev["higgsCandidate_mass"]) else -100),
        Axis("higgsCandidate_tau2", 50, 0, 1, lambda ev: ev["higgsCandidate_tau2"][0] if len(ev["higgsCandidate_mass"]) else -100),

        Axis("higgsCandidate_mass", 50, 0, 200, lambda ev: ev["higgsCandidate_mass"][0] if len(ev["higgsCandidate_mass"]) else -100),
        Axis("higgsCandidate_mass_softdropz2b1filt", 50, 0, 200, lambda ev: ev["higgsCandidate_mass_softdropz2b1filt"][0] if len(ev["higgsCandidate_mass"]) else -100),
        Axis("higgsCandidate_sj12massb_subjetfiltered", 50, 0, 200, lambda ev: ev["higgsCandidate_sj12massb_subjetfiltered"][0] if len(ev["higgsCandidate_mass"]) else -100),
        Axis("higgsCandidate_sj12masspt_subjetfiltered", 50, 0, 200, lambda ev: ev["higgsCandidate_sj12masspt_subjetfiltered"][0] if len(ev["higgsCandidate_mass"]) else -100),

        Axis("multiclass_class", 7, -0.5, 6.5, lambda ev:     ev["multiclass_class"]),
        Axis("multiclass_proba_ttb", 40, 0, 0.7, lambda ev:   ev["multiclass_proba_ttb"]),
        Axis("multiclass_proba_tt2b", 40, 0, 0.7, lambda ev:  ev["multiclass_proba_tt2b"]),
        Axis("multiclass_proba_ttbb", 40, 0, 0.7, lambda ev:  ev["multiclass_proba_ttbb"]),
        Axis("multiclass_proba_ttcc", 40, 0, 0.7, lambda ev:  ev["multiclass_proba_ttcc"]),
        Axis("multiclass_proba_ttll", 40, 0, 0.7,  lambda ev: ev["multiclass_proba_ttll"]),

    ]

    axes_extra_dl = []
    axes_extra_fh = []

    # DEFINE SL AXES
    axes_sl = axes_basic_all + axes_basic_sl
    if analysis.config.get("sparsinator", "extra_sl"):
            axes_sl += axes_extra_sl

    # DEFINE DL AXES
    axes_dl = axes_basic_all + axes_basic_dl
    if analysis.config.get("sparsinator", "extra_dl"):
        axes_dl += axes_extra_dl

    # DEFINE FH AXES
    axes_fh = axes_basic_all + axes_basic_fh
    if analysis.config.get("sparsinator", "extra_fh"):
        axes_fh += axes_extra_fh

    AXES = {
        "sl": axes_sl,
        "dl": axes_dl,
        "fh": axes_fh,
    }


    if len(file_names) == 0:
        raise Exception("No files specified, probably a mistake")
    if max_events == 0:
        raise Exception("No events specified, probably a mistake")

    sample = analysis.get_sample(sample_name)
    schema = sample.schema
    process = sample.process
    
    do_classifier_db = analysis.config.get("sparsinator", "do_classifier_db")
    if do_classifier_db:
        cls_db = ClassifierDB(filename=sample.classifier_db_path)
    
    #configure systematic scenarios according to MC/Data
    if schema == "mc":
        systematics_event = ["nominal"] + systematics_event
        systematics_weight = [k[0] for k in systematic_weights]
    elif schema == "data":
        systematics_event = ["nominal"]
        systematics_weight = []

    all_systematics = systematics_event+systematics_weight
   
    dirs = {}
    outfile = ROOT.TFile(ofname, "RECREATE")
    dirs["sample"] = outfile.mkdir(sample_name)
    dirs["sample"].cd()
    dirs["sl"] = dirs["sample"].mkdir("sl")
    dirs["dl"] = dirs["sample"].mkdir("dl")
    dirs["fh"] = dirs["sample"].mkdir("fh")
    
    #pre-create output histograms
    outdict_syst = createOutputs(analysis.config, AXES, dirs, all_systematics)

    nevents = 0
    counters = OrderedDict()
    counters["triggerPath"] = {}

    #Main loop
    for file_name in file_names:
        print("opening {0}".format(file_name))
        tf = ROOT.TFile.Open(file_name)
        events = BufferedTree(tf.Get("tree"))
        print("looping over {0} events".format(events.GetEntries()))
       
        iEv = 0

        #Loop over events
        for event in events:
            nevents += 1
            iEv += 1
            if nevents < skip_events:
                continue
            if max_events > 0:
                if nevents > (skip_events + max_events):
                    logging.info("event loop: breaking due to MAX_EVENTS: {0} > {1} + {2}".format(
                        nevents, skip_events, max_events
                    ))
                    break

            #apply some basic preselection
            if not (event.is_sl or event.is_dl or event.is_fh):
                continue
            if not event.numJets >= 3:
                continue
            if not (event.nBCSVM>=2 or event.nBCMVAM>=2):
                continue
            if schema == "data" and not event.json:
                continue

            for syst in systematics_event:
                ret = desc.getValue(event, schema, syst)
                proc_label = assign_process_label(process, ret)
                ret["process"] = PROCESS_MAP[proc_label]
                ret["syst"] = syst
                ret["counting"] = 0
                ret["leptonFlavour"] = 0
                ret["triggerPath"] = triggerPath(ret)
                if not counters["triggerPath"].has_key(ret["triggerPath"]):
                    counters["triggerPath"][ret["triggerPath"]] = 0
                counters["triggerPath"][ret["triggerPath"]] += 1

                ret["weight_nominal"] = 1.0
                if schema == "mc":
                    ret["weight_nominal"] *= ret["puWeight"] * ret["btagWeightCSV"] * ret["triggerEmulationWeight"] * ret["lep_SF_weight"]
            
                ret["common_mem"] = 0
                ret["common_bdt"] = 0
                if do_classifier_db:
                    syst_index = int(analysis.config.get(syst, "index"))
                    db_key = (int(event.run), int(event.lumi), int(event.evt), syst_index)
                    if cls_db.data.has_key(db_key):
                        classifiers = cls_db.get(db_key)
                        ret["common_bdt"] = classifiers.bdt
                        if classifiers.mem_p_sig > 0:
                            ret["common_mem"] = classifiers.mem_p_sig / (classifiers.mem_p_sig + float(MEM_SF) * classifiers.mem_p_bkg)
                    else:
                        ret["common_bdt"] = -99
                        ret["common_mem"] = -99
                print(ret["common_bdt"], ret["common_mem"])

                #Fill the base histogram
                for (k, v) in outdict_syst[syst].items():
                    weight = ret["weight_nominal"]
                    if v.cut(ret):
                        v.fill(ret, weight)
               
                #nominal event, fill also histograms with systematic weights
                if syst == "nominal" and schema == "mc":
                    for (syst_weight, weightfunc) in systematic_weights:
                        weight = weightfunc(ret)
                        for (k, v) in outdict_syst[syst_weight].items():
                            if v.cut(ret):
                                v.fill(ret, weight)

            #end of loop over event systematics
        #end of loop over events
        tf.Close()
    #end of loop over file names

    print("processed {0} events".format(nevents))
    print("writing output")
    print(counters)
    outfile.Write()
    outfile.Close()

if __name__ == "__main__":
    from TTH.Plotting.Datacards.AnalysisSpecificationFromConfig import analysisFromConfig

    if os.environ.has_key("FILE_NAMES"):
        file_names = map(getSitePrefix, os.environ["FILE_NAMES"].split())
        prefix, sample = get_prefix_sample(os.environ["DATASETPATH"])
        skip_events = int(os.environ.get("SKIP_EVENTS", 0))
        max_events = int(os.environ.get("MAX_EVENTS", 0))
        an_name, analysis = analysisFromConfig(os.environ.get("ANALYSIS_CONFIG",))

    else:
        file_names = map(getSitePrefix, [
            "/store/user/jpata/tth/Sep14_leptonic_nome_v1/ttHTobb_M125_13TeV_powheg_pythia8/Sep14_leptonic_nome_v1/160914_142604/0000/tree_1.root",
            "/store/user/jpata/tth/Sep14_leptonic_nome_v1/ttHTobb_M125_13TeV_powheg_pythia8/Sep14_leptonic_nome_v1/160914_142604/0000/tree_10.root",
            "/store/user/jpata/tth/Sep14_leptonic_nome_v1/ttHTobb_M125_13TeV_powheg_pythia8/Sep14_leptonic_nome_v1/160914_142604/0000/tree_100.root",
            "/store/user/jpata/tth/Sep14_leptonic_nome_v1/ttHTobb_M125_13TeV_powheg_pythia8/Sep14_leptonic_nome_v1/160914_142604/0000/tree_101.root",
            "/store/user/jpata/tth/Sep14_leptonic_nome_v1/ttHTobb_M125_13TeV_powheg_pythia8/Sep14_leptonic_nome_v1/160914_142604/0000/tree_102.root",
        ])
        prefix = ""
        sample = "ttHTobb_M125_13TeV_powheg_pythia8"
        skip_events = 0
        max_events = 10000
        an_name, analysis = analysisFromConfig(os.environ["CMSSW_BASE"] + "/src/TTH/Plotting/python/Datacards/config_sldl.cfg")
    main(analysis, file_names, sample, "out.root", skip_events, max_events)
