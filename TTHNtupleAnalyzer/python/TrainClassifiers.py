#######################################
# Imports
########################################

from TrainClassifiersBase import *


########################################
# Configuration
########################################

brs = ["evt", 
       "pt", "eta", "top_size", 
       "ak08_pt",
       "ak08_tau3", "ak08_tau2",
       "ak08softdropz10b00forbtag_btag", 
       "ak08softdropz10b00_mass",
       "ak08softdropz10b00_masscal",

       "ak08puppi_tau3", "ak08puppi_tau2",
       "ak08puppisoftdropz10b00forbtag_btag", 
       "ak08puppisoftdropz10b00_mass",
       "ak08puppisoftdropz10b00_masscal",

       "ak08_emap", 
       #"ak08_ptmap", 
       #"ak08_massmap", 
       #"ak08_chargemap"
]

to_plot = [["pt", 800, 1000, "Parton pT [GeV]"],
           ["eta", -3, 3, "Parton eta"],
           ["top_size", 0, 3, "Top Size"],
           ["ak08_tau3_over_tau2",0, 1., "AK08 tau3/tau2"],
           ["ak08softdropz10b00forbtag_btag", 0, 1., "AK08 b-tag discriminator"],
           ["ak08softdropz10b00_mass", 0, 300, "AK08 softdrop mass [GeV]"],
           ["ak08softdropz10b00_masscal", 0, 300, "AK08 softdrop mass [GeV]"],

           ["ak08puppi_tau3_over_tau2",0, 1., "AK08 Puppi tau3/tau2"],
           ["ak08puppisoftdropz10b00forbtag_btag", 0, 1., "AK08 Puppi b-tag discriminator"],
           ["ak08puppisoftdropz10b00_mass", 0, 300, "AK08 Puppi softdrop mass [GeV]"],
           ["ak08puppisoftdropz10b00_masscal", 0, 300, "AK08 Puppi calibrated softdrop mass [GeV]"],
           ]

default_params = {        

    "architecture" : "2dconv",

    # Parameters for 1d architecture
    "1d_n_layers"    : 1,
    "1d_n_nodes"     : 512,
    "1d_dropout"     : 0.3,

    # Parameters for 2d or 3d convolutional architecture    
    "n_blocks"       : 1,    
    "n_conv_layers"  : 2,        
    "conv_nfeat"     : 2,
    "conv_size"      : 4,
    "pool_size"      : 0,
    "n_dense_layers" : 1,
    "n_dense_nodes"  : 8,

    # Common parameters
    "lr"          : 0.01,
    "decay"       : 1e-6,
    "momentum"    : 0.9,            
    "nb_epoch"    : 200,
}

colors = ['black', 'red','blue','green','orange','green','magenta']

class_names = {0: "background",
               1: "signal"}

classes = sorted(class_names.keys())

plot_inputs    = False

infname_sig = "ntop_x3_zprime_m2000-tagging-weighted.root"
infname_bkg = "ntop_x3_qcd_800_1000-tagging-weighted.root"

n_batches = 20

min_pt = 801
max_pt = 999
max_eta = 1.5
min_reco_pt = 500

fiducial_cut = "(pt>{0}) && (pt<{1}) && (fabs(eta) < {2}) && (ak08_pt > {3})".format(min_pt, 
                                                                                     max_pt, 
                                                                                     max_eta,
                                                                                     min_reco_pt)

cut_test  = fiducial_cut  + "&& (evt%4==1)"
cut_train = fiducial_cut +  "&& (evt%4==3)"


########################################
# Read in NN parameters
########################################

params = {}
for param in default_params.keys():

    if param in os.environ.keys():
        cls = default_params[param].__class__
        value = cls(os.environ[param])
        params[param] = value
    else:
        params[param] = default_params[param]


########################################
# Prepare data and scalers
########################################

datagen_train = datagen(cut_train, brs, infname_sig, infname_bkg, n_batches=n_batches)
datagen_test  = datagen(cut_test, brs, infname_sig, infname_bkg, n_batches=n_batches)

scaler_emap = StandardScaler()  

for _ in range(2):
    scaler_emap.partial_fit(get_data_flatten(datagen_train.next(), ["ak08_emap"]))

print "Preparing Scalers: Done..."

# Define a generator for the inputs we need

def generate_data_emap(datagen):

    while True:

        df = datagen.next()

        # transform-expand-reshape-expand
        X = np.expand_dims(np.expand_dims(
            scaler_emap.transform(get_data_flatten(df, ["ak08_emap"])), axis=-1
        ).reshape(-1,32,32), axis=1)

        print X.shape

        y = np_utils.to_categorical(df["is_signal_new"].values)
        
        yield X,y

#
#
#def get_data_emap_2d(df):
#    tmp  = get_data_emap(df)
#    print tmp.shape
#    tmp2 =  np.expand_dims(tmp, axis=-1)
#    print tmp2.shape
#    n_lines = tmp2.shape[0]
#    tmp3 = tmp2.reshape(n_lines, 32, 32)
#    print tmp3.shape
#    tmp4 = np.expand_dims(tmp3, axis=1)    
#    print tmp4.shape
#    return tmp4
#

#def get_data_3d(df, varlist):
#
#    emap      = get_data_emap(df, ["ak08_emap"])
#    chargemap = get_data_chargemap(df, ["ak08_chargemap"])
#
#    n_lines = len(emap)
#
#    emap_shaped      = np.expand_dims(np.expand_dims(emap,      axis=-1).reshape(n_lines, 32,32), axis=1)
#    chargemap_shaped = np.expand_dims(np.expand_dims(chargemap, axis=-1).reshape(n_lines, 32,32), axis=1)
#
#    return np.append(emap_shaped, chargemap_shaped, axis=1)


def model_1d(params):

    activ = lambda : Activation('relu')

    model = Sequential()

    nclasses = 2

    # 1D Model
    model.add(Dense(params["1d_n_nodes"], input_dim = 256))
    model.add(activ())
    model.add(Dropout(params["1d_dropout"]))

    for ilayer in range(params["1d_n_layers"]):  
        model.add(Dense(params["1d_n_nodes"]))
        model.add(activ())                   
        model.add(Dropout(params["1d_dropout"]))

    model.add(Dense(nclasses))
    model.add(Activation('softmax'))

    return model

def model_2d(params):

    activ = lambda : Activation('relu')
    model = Sequential()

    channels = 1
    nclasses = 2

    for i_block in range(params["n_blocks"]):
        for i_conv_layer in range(params["n_conv_layers"]):

            if i_conv_layer == 0 and i_block ==0:
                model.add(ZeroPadding2D(padding=(1, 1), input_shape=(1, 32, 32)))
            else:
                model.add(ZeroPadding2D(padding=(1, 1)))

            model.add(Convolution2D(params["conv_nfeat"],
                                    params["conv_size" ], 
                                    params["conv_size" ]))
            model.add(activ())

        if params["pool_size"] > 0:
            model.add(MaxPooling2D(pool_size=(params["pool_size"], params["pool_size"])))

    model.add(Flatten())

    for i_dense_layer in range(params["n_dense_layers"]):
        model.add(Dense(params["n_dense_nodes"]))
        model.add(activ())    

    model.add(Dense(nclasses))
    model.add(Activation('softmax'))

    return model

def model_3d(params):

    channels = 1
    nclasses = 2

    activ = lambda : Activation('relu')
    model = Sequential()

    for i_block in range(params["n_blocks"]):
        for i_conv_layer in range(params["n_conv_layers"]):

            if i_conv_layer == 0 and i_block ==0:
                model.add(ZeroPadding2D(padding=(1, 1), input_shape=(2, 32, 32)))
            else:
                model.add(ZeroPadding2D(padding=(1, 1)))

            model.add(Convolution2D(params["conv_nfeat"],
                                    params["conv_size" ], 
                                    params["conv_size" ]))
            model.add(activ())

        if params["pool_size"] > 0:
            model.add(MaxPooling2D(pool_size=(params["pool_size"], params["pool_size"])))

    model.add(Flatten())

    for i_dense_layer in range(params["n_dense_layers"]):
        model.add(Dense(params["n_dense_nodes"]))
        model.add(activ())    

    model.add(Dense(nclasses))
    model.add(Activation('softmax'))
    
    return model


classifiers = [

#    Classifier("BDT",
#               "scikit", 
#               {},
#               True,
#               lambda x :get_data_vars(x, ["ak08_tau3", 
#                                           "ak08_tau2", 
#                                           "ak08softdropz10b00forbtag_btag", 
#                                           "ak08softdropz10b00_mass"]),               
#               GradientBoostingClassifier(
#                   n_estimators=200,
#                   learning_rate=0.1,
#                   max_leaf_nodes = 6,
#                   min_samples_split=1,
#                   min_samples_leaf=1,
#                   subsample=0.8,
#                   verbose = True,
#                )),
#
#    Classifier("BDT-nob",
#               "scikit", 
#               {},
#               True,
#               lambda x :get_data_vars(x, ["ak08_tau3", 
#                                           "ak08_tau2",                        
#                                           "ak08softdropz10b00_mass"]),               
#               GradientBoostingClassifier(
#                   n_estimators=200,
#                   learning_rate=0.1,
#                   max_leaf_nodes = 6,
#                   min_samples_split=1,
#                   min_samples_leaf=1,
#                   subsample=0.8,
#                   verbose = True,
#                )),

    Classifier("NNXd", 
               "keras",
               params,
               False,
               generate_data_emap(datagen_train),
               model_2d(params)
               )
    
]


########################################
# Plot inputs
########################################

if plot_inputs:
    
    # 1D Variables
    for plotvar in to_plot:

        br = plotvar[0]
        xmin = plotvar[1]
        xmax = plotvar[2]
        name = plotvar[3]

        plt.clf()

        for cls in classes:
            plt.hist(df.loc[df["is_signal_new"]==cls,br].as_matrix(),
                     color=colors[cls+1], 
                     bins=np.linspace(xmin,xmax,50),
                     normed=True, 
                     alpha=0.4,
                     label = class_names[cls]
            )    
            
        plt.xlabel(name, fontsize=16)
        plt.ylabel("Fraction of Jets", fontsize=16)
        plt.legend(loc=0)

        plt.savefig("input_{0}.png".format(br))


    for cls in classes:

        plt.clf()
        for i_br, br in enumerate(["ak08softdropz10b00_mass",
                                   "ak08softdropz10b00_masscal", 
                                   #"ak08puppisoftdropz10b00_mass",
                                   #"ak08puppisoftdropz10b00_masscal"
                               ]):
       
            xmin = 120
            xmax = 220
            name = br

            names = {"ak08softdropz10b00_mass"         : "CHS, Uncal.",
                     "ak08softdropz10b00_masscal"      : "CHS, Cal.",
                     "ak08puppisoftdropz10b00_mass"    : "Puppi, Uncal.",
                     "ak08puppisoftdropz10b00_masscal" : "Puppi, Cal.",
                     }

            plt.hist(df.loc[(df["pass_tau"]==True) & (df["is_signal_new"]==cls) & (df_tmp["keep"]==True), br].as_matrix(),
                     color=colors[i_br], 
                     edgecolor = colors[i_br], 
                     bins=np.linspace(xmin,xmax,50),
                     normed=True, 
                     histtype="step",
                     label = names[br]
                )    

        plt.xlabel("Mass [GeV]", fontsize=16)
        plt.ylabel("Fraction of Jets", fontsize=16)
        plt.legend(loc=0)

        plt.savefig("input_mass_{0}.png".format(cls))

    print "Plotting 1D inputs: Done..."

    # 2D maps
    for map_name in ["ak08_emap", "ak08_chargemap"]:

        X = dtrain[map_name].values.flatten()

        for idx in range(20):
            map_1d = X[idx]
            map_2d = map_1d.reshape(32,32)

            plt.clf()

            plt.imshow(map_2d, interpolation = 'spline36')
            #plt.colorbar(map_2d)
            plt.savefig("maps/{0}_{1}.png".format(map_name, idx))

    print "Plotting 2D inputs: Done..."


########################################
# Train/Load classifiers and make ROCs
########################################

[clf.prepare() for clf in classifiers]
#[rocplot(clf, dtest, classes, class_names) for clf in classifiers]
#multirocplot(classifiers, dtest)

 






