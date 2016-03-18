import plotlib, json, copy
import sparse, ROOT, multiprocessing, sys
ROOT.TH1.AddDirectory(False)

mc_samples = [
    "ttH_hbb", "ttH_nonhbb", "ttbarPlus2B", "ttbarPlusBBbar", "ttbarPlusB", "ttbarPlusCCbar", "ttbarOther",
    "ww", "wz", "zz",
]
data_samples = [
    "SingleMuon",
    "SingleElectron",
    "DoubleMuon",
    "DoubleEG",
    "MuonEG"
]

systs = [            
    ("_CMS_scale_jUp", "_CMS_scale_jDown"),
    ("_CMS_ttH_CSVLFUp", "_CMS_ttH_CSVLFDown"),
    ("_CMS_ttH_CSVHFUp", "_CMS_ttH_CSVHFDown"),
    ("_CMS_ttH_CSVHFStats1Up", "_CMS_ttH_CSVHFStats1Down"),
    ("_CMS_ttH_CSVHFStats2Up", "_CMS_ttH_CSVHFStats2Down"),
    ("_CMS_ttH_CSVLFStats1Up", "_CMS_ttH_CSVLFStats1Down"),
    ("_CMS_ttH_CSVLFStats2Up", "_CMS_ttH_CSVLFStats2Down"),
    ("_CMS_ttH_CSVcErr1Up", "_CMS_ttH_CSVcErr1Down"),
    ("_CMS_ttH_CSVcErr2Up", "_CMS_ttH_CSVcErr2Down")
]

def replace_out(samp):
    if samp in ["ww", "wz", "zz"]:
        return "diboson"
    return samp
def make_rule_cut(basehist, cuts, variables, catname, histname):
    rules = []
    for samp in mc_samples:
        samp_out = replace_out(samp)
        d = {
            "input": "{0}/{1}".format(samp, basehist),
            "cuts": str(cuts),
            "project": str(variables),
            "output": "{0}/{1}/{2}".format(samp_out, catname, histname),
        }
        rules += [d]
        for syst in systs:
            systname = syst[0].replace("Up", "")
            for sd in syst:
                d2 = copy.deepcopy(d)
                d2["input"] += sd
                d2["output"] += sd
                rules += [d2]
    for samp in data_samples:
        if "sl/" in basehist:
            if samp == "SingleMuon":
                cuts = [("leptonFlavour", 1, 2)] + cuts
            elif samp == "SingleElectron":
                cuts = [("leptonFlavour", 2, 3)] + cuts
            else:
                continue
        elif "dl/" in basehist:
            if samp == "DoubleMuon":
                cuts = [("leptonFlavour", 3, 4)] + cuts
            elif samp == "MuonEG":
                cuts = [("leptonFlavour", 4, 5)] + cuts
            elif samp == "DoubleEG":
                cuts = [("leptonFlavour", 5, 6)] + cuts
            else:
                continue
        d = {
            "input": "{0}/{1}".format(samp, basehist),
            "cuts": str(cuts),
            "project": str(variables),
            "output": "data/{1}/{2}".format(samp, catname, histname),
        }

        rules += [d]
    return rules


def apply_rules(args):
    infile, rules = args
    infile_tf = ROOT.TFile.Open(infile)
    hdict = {}
    for rule in rules:
        cuts = eval(rule["cuts"])
        hk = rule["output"]
        h = infile_tf.Get(str(rule["input"]))
        dummy = False
        if h == None:
            h = infile_tf.Get(str("ttH_hbb/sl/sparse"))
            dummy = True
            cuts = []
        variables = eval(rule["project"])
        vnames = [v[0] for v in variables]
        ret = sparse.apply_cuts_project(h, cuts, vnames)
        if dummy:
            ret.Scale(0)
            ret.SetEntries(0)
        ret.SetName(rule["output"].split("/")[-1])
        if len(variables) == 1:
            ret.Rebin(variables[0][1])
        elif len(variables) == 2:
            ret.Rebin2D(variables[0][1], variables[0][2])
        if hdict.has_key(hk):
            hdict[hk] += ret
        else:
            hdict[hk] = ret
    infile_tf.Close()
    return hdict

def apply_rules_parallel(infile, rules, ncores=4):
    p = multiprocessing.Pool(ncores)
    inputs = [
        (infile, [r]) for r in rules
    ]
    rets = p.map(apply_rules, inputs)
    ret = reduce(sparse.add_hdict, rets)
    p.close()
    return ret


if __name__ == "__main__":
    rules = []
    for var in [
        ("mem_SL_0w2h2t", 4),
        ("common_bdt", 4),
        ("Wmass", 1),
        ]:
        for cutname, cut in [
            ("sl_jge6_tge4", [('numJets', 6, 8), ('nBCSVM', 4, 6)]),
            ("sl_jge6_t3", [('numJets', 6, 8), ('nBCSVM', 3, 4)]),
            ("sl_jge6_t2", [('numJets', 6, 8), ('nBCSVM', 2, 3)]),
            ("sl_j5_tge4", [('numJets', 5, 6), ('nBCSVM', 4, 6)]),
            ("sl_j5_t3", [('numJets', 5, 6), ('nBCSVM', 3, 4)]),
            ]:
            rules += make_rule_cut("sl/sparse", cut, [var], cutname, var[0])

        for cutname, cut in [
            ("dl_jge4_tge4", [('numJets', 4, 6), ('nBCSVM', 4, 6)]),
            ]:
            rules += make_rule_cut("dl/sparse", cut, [var], cutname, var[0])

    of = open("rules.json", "w")
    of.write(json.dumps(rules, indent=2))
    of.close()

    infile = sys.argv[1]
    rulefile = open("rules.json")
    rules = json.loads(rulefile.read())
    print "processing {0} rules".format(len(rules))
    hdict = apply_rules_parallel(infile, rules)
    print "saving {0} histograms".format(len(hdict))
    sparse.save_hdict(sys.argv[2], hdict)
