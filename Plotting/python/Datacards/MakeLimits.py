########################################
# Imports
########################################

import imp, os, sys
import subprocess

from CombineHelper import LimitGetter


print "MakeLimits.py called from cwd={0}".format(os.getcwd())
########################################
# Setup
########################################

if not len(sys.argv) in [2,3]:
    print "Wrong number of arguments"
    print "Usage: "
    print "{0} datacard_file.py [group to process]".format(sys.argv[0])
    sys.exit()

# TODO: define input/output directories

# Get the datacard
dcard = imp.load_source("dcard", sys.argv[1])


# If we receive a group-name from command line, only process this group
# Otherwise do all of them
if len(sys.argv) == 2:
    groups_to_process = dcard.analysis.groups.keys()
else:
    group = sys.argv[2]

    # Make sure we have a valid group
    if not group in dcard.analysis.groups.keys():
        print group, "does not name a valid group. Available are:"
        print dcard.analysis.groups.keys()
        sys.exit()
    else:
        groups_to_process = [group]

    
print "Processing groups:", groups_to_process

# Prepare the limit getter
lg = LimitGetter("./")


########################################
# Actual work
########################################

for group_name in groups_to_process:

    group = dcard.analysis.groups[group_name]    
    print "Doing {0} consisting of {1} categories".format(group_name, len(group))    
    

    # Get all the per-category datacards and use combineCards to merge into one "group datacard)"
    input_dcard_names = ["shapes_{0}.txt".format(c.full_name) for c in group]
    add_dcard_command = ["combineCards.py"] + input_dcard_names 
    print "Running combineCards: {0}".format(" ".join(add_dcard_command))
    process = subprocess.Popen(add_dcard_command, 
                               stdout=subprocess.PIPE, 
                               #cwd=dcard.analysis.output_directory)
                               cwd="./")
    group_dcard = process.communicate()[0]

    # Write the group datacard to a file
    group_dcard_filename = os.path.join(
        #dcard.analysis.output_directory,
        "./",
        "shapes_group_{0}.txt".format(group_name)
    )
    group_dcard_file = open(group_dcard_filename, "w")
    group_dcard_file.write(group_dcard)
    group_dcard_file.close()
    print "Running limit on {0}".format(group_dcard_filename)
    # And run limit setting on it
    lg(group_dcard_filename)

# End loop over groups
