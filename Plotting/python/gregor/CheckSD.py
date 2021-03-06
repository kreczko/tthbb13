#!/usr/bin/env python
"""
"""

########################################
# Imports
########################################

import os
import pickle
import socket # to get the hostname

# With CMSSW
if "CMSSW_VERSION" in os.environ.keys():
    from TTH.Plotting.Helpers.CompareDistributionsHelpers import *
    from TTH.Plotting.gregor.TopTaggingVariables import *

else:
    from TTH.Plotting.python.Helpers.CompareDistributionsHelpers import *
    from TTH.Plotting.python.gregor.TopTaggingVariables import *


########################################
# Define Input Files and
# output directory
########################################

if socket.gethostname() == "t3ui12":
    basepath = '/scratch/gregor/'
else:
    basepath = '/Users/gregor/'
                                         

files = {
    "zprime_m2000_v18" : "ntop_v18_zprime_m2000_1p_13tev-tagging",     
    "qcd_800_1000_v18" : "ntop_v18_qcd_800_1000_pythia8_13tev-tagging",
    "zprime_m2000_v19" : "ntop_v19_zprime_m2000_1p_13tev-tagging",     
    "qcd_800_1000_v19" : "ntop_v19_qcd_800_1000_pythia8_13tev-tagging",
}

pretty_file_names = {
    "zprime_m2000_v18" : "Z', fixed R_{micojet}",     
    "qcd_800_1000_v18" : "QCD, fixed R_{micojet}",
    "zprime_m2000_v19" : "Z', dynamic R_{micojet}", 
    "qcd_800_1000_v19" : "QCD, dynamic R_{micojet}",
}



# for the filename: basepath + filename + .root
full_file_names = {}
for k,v in files.iteritems():
    full_file_names[k] = basepath + v + "-weighted.root"

output_dir = "results/CheckSD/"


fiducial_cut = "((pt>801)&&(pt<999)&&(fabs(eta)<1.5))"


########################################
# Define plots and do fits
########################################

name = "sd_vars"
collection = globals()[name]

for var in collection:
    

    combinedPlot(var.name.replace("(","").replace(")",""),
                 [plot(pretty_file_names[sample], 
                       var.name,                    
                       '({0}&&{1})*weight'.format(fiducial_cut, var.extra_cut),
                       sample) for sample in files.keys()],
                 80, collection[0].range_min, collection[0].range_max, 
                 label_x   = "Shower Deconstruction log(#chi)",
                 label_y   = "A.U.",
                 axis_unit = "",
                 log_y     = False,
                 normalize = True,
                 legend_origin_x = 0.2, 
                 legend_origin_y = 0.6,
                 legend_size_x   = 0.2,
                 legend_size_y   = 0.05 * 4)

    combinedPlot(var.name.replace("(","").replace(")","")+"_isgood",
                 [plot(pretty_file_names[sample], 
                       var.extra_cut,
                       '({0})*weight'.format(fiducial_cut),
                       sample) for sample in files.keys()],
                 10, 0, 1.1, 1.5,
                 label_x   = "Valid SD Candidate",
                 label_y   = "A.U.",
                 axis_unit = "",
                 log_y     = False,
                 normalize = True,
                 legend_origin_x = 0.3, 
                 legend_origin_y = 0.7,
                 legend_size_x   = 0.2,
                 legend_size_y   = 0.05 * 4)

doWork(full_file_names, output_dir )




