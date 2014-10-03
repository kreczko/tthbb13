//Autogenerated
#include <TTree.h>
#include <string>
#include <map>
#define N_MAX 500
#define M_MAX 100
//these are simple 'sentinel values' for uninitialized variables
#define DEF_VAL_FLOAT -9999.0f
#define DEF_VAL_DOUBLE -9999.0d
#define DEF_VAL_INT -9999
#define FLOAT_EPS 0.0000001f
#define DOUBLE_EPS 0.0000001d
constexpr bool is_undef(int x) { return x==DEF_VAL_INT; };
constexpr bool is_undef(float x) { return fabs(x-DEF_VAL_FLOAT) < FLOAT_EPS; };
constexpr bool is_undef(double x) { return fabs(x-DEF_VAL_DOUBLE) < DOUBLE_EPS; };
#define SET_ZERO(x,n,y) for(int i=0;i<n;i++) {x[i]=y;}
#define SET_ZERO_2(x,n,y) for(int i=0;i<n;i++) { for(int j=0;j<n;j++) { x[i][j]=y; } }
class TTHTree {
public:
	TTHTree(TTree* _tree) { tree = _tree; };
	TTree* tree;
	double debug__time1c;
	double debug__time1r;
	int event__id;
	int event__json;
	int event__lumi;
	int event__run;
	float gen_jet__eta[N_MAX];
	int gen_jet__id[N_MAX];
	float gen_jet__mass[N_MAX];
	float gen_jet__phi[N_MAX];
	float gen_jet__pt[N_MAX];
	int gen_jet__status[N_MAX];
	int gen_jet__type[N_MAX];
	float gen_jet_parton__eta[N_MAX];
	int gen_jet_parton__id[N_MAX];
	float gen_jet_parton__mass[N_MAX];
	float gen_jet_parton__phi[N_MAX];
	float gen_jet_parton__pt[N_MAX];
	int gen_jet_parton__status[N_MAX];
	int gen_jet_parton__type[N_MAX];
	float gen_lep__eta[N_MAX];
	int gen_lep__id[N_MAX];
	float gen_lep__mass[N_MAX];
	float gen_lep__phi[N_MAX];
	float gen_lep__pt[N_MAX];
	int gen_lep__status[N_MAX];
	int gen_lep__type[N_MAX];
	float gen_met__phi;
	float gen_met__pt;
	float jet__bd_csv[N_MAX];
	float jet__ce_e[N_MAX];
	float jet__ch_e[N_MAX];
	float jet__el_e[N_MAX];
	float jet__energy[N_MAX];
	float jet__eta[N_MAX];
	int jet__id[N_MAX];
	float jet__mass[N_MAX];
	float jet__mu_e[N_MAX];
	float jet__ne_e[N_MAX];
	float jet__nh_e[N_MAX];
	float jet__ph_e[N_MAX];
	float jet__phi[N_MAX];
	float jet__pileupJetId[N_MAX];
	float jet__pt[N_MAX];
	int jet__type[N_MAX];
	float jet__vtx3DSig[N_MAX];
	float jet__vtx3DVal[N_MAX];
	float jet__vtxMass[N_MAX];
	float jet__vtxNtracks[N_MAX];
	int jet_toptagger__child_idx[N_MAX];
	float jet_toptagger__energy[N_MAX];
	float jet_toptagger__eta[N_MAX];
	float jet_toptagger__mass[N_MAX];
	float jet_toptagger__min_mass[N_MAX];
	int jet_toptagger__n_sj[N_MAX];
	float jet_toptagger__phi[N_MAX];
	float jet_toptagger__pt[N_MAX];
	float jet_toptagger__top_mass[N_MAX];
	float jet_toptagger__w_mass[N_MAX];
	float jet_toptagger_sj__energy[N_MAX];
	float jet_toptagger_sj__eta[N_MAX];
	float jet_toptagger_sj__mass[N_MAX];
	float jet_toptagger_sj__parent_idx[N_MAX];
	float jet_toptagger_sj__phi[N_MAX];
	float jet_toptagger_sj__pt[N_MAX];
	float lep__ch_iso[N_MAX];
	int lep__charge[N_MAX];
	float lep__dxy[N_MAX];
	float lep__dz[N_MAX];
	float lep__ec_iso[N_MAX];
	float lep__eta[N_MAX];
	float lep__hc_iso[N_MAX];
	int lep__id[N_MAX];
	int lep__id_bitmask[N_MAX];
	int lep__is_loose[N_MAX];
	int lep__is_medium[N_MAX];
	int lep__is_tight[N_MAX];
	float lep__mass[N_MAX];
	float lep__mva[N_MAX];
	float lep__p_iso[N_MAX];
	float lep__ph_iso[N_MAX];
	float lep__phi[N_MAX];
	float lep__pt[N_MAX];
	float lep__puch_iso[N_MAX];
	float lep__rel_iso[N_MAX];
	int lep__type[N_MAX];
	float lhe__ht;
	int lhe__n_b;
	int lhe__n_c;
	int lhe__n_e;
	int lhe__n_g;
	float lhe__n_j;
	int lhe__n_l;
	float met__phi;
	float met__pt;
	float met__pt__en_down;
	float met__pt__en_up;
	int n__jet;
	int n__jet_toptagger;
	int n__jet_toptagger_sj;
	int n__lep;
	int n__pv;
	int n__pvi;
	int pvi__bx[N_MAX];
	float pvi__n0[N_MAX];
	float pvi__ntrue[N_MAX];
	float weight__pu;
	float weight__pu_down;
	float weight__pu_up;
	float weight__trigger;
	float weight__trigger_down;
	float weight__trigger_up;
	void loop_initialize(void) {
		debug__time1c = DEF_VAL_DOUBLE;
		debug__time1r = DEF_VAL_DOUBLE;
		event__id = DEF_VAL_INT;
		event__json = DEF_VAL_INT;
		event__lumi = DEF_VAL_INT;
		event__run = DEF_VAL_INT;
		SET_ZERO(gen_jet__eta, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_jet__id, N_MAX, DEF_VAL_INT);
		SET_ZERO(gen_jet__mass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_jet__phi, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_jet__pt, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_jet__status, N_MAX, DEF_VAL_INT);
		SET_ZERO(gen_jet__type, N_MAX, DEF_VAL_INT);
		SET_ZERO(gen_jet_parton__eta, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_jet_parton__id, N_MAX, DEF_VAL_INT);
		SET_ZERO(gen_jet_parton__mass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_jet_parton__phi, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_jet_parton__pt, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_jet_parton__status, N_MAX, DEF_VAL_INT);
		SET_ZERO(gen_jet_parton__type, N_MAX, DEF_VAL_INT);
		SET_ZERO(gen_lep__eta, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_lep__id, N_MAX, DEF_VAL_INT);
		SET_ZERO(gen_lep__mass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_lep__phi, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_lep__pt, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(gen_lep__status, N_MAX, DEF_VAL_INT);
		SET_ZERO(gen_lep__type, N_MAX, DEF_VAL_INT);
		gen_met__phi = DEF_VAL_FLOAT;
		gen_met__pt = DEF_VAL_FLOAT;
		SET_ZERO(jet__bd_csv, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__ce_e, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__ch_e, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__el_e, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__energy, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__eta, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__id, N_MAX, DEF_VAL_INT);
		SET_ZERO(jet__mass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__mu_e, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__ne_e, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__nh_e, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__ph_e, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__phi, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__pileupJetId, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__pt, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__type, N_MAX, DEF_VAL_INT);
		SET_ZERO(jet__vtx3DSig, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__vtx3DVal, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__vtxMass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet__vtxNtracks, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger__child_idx, N_MAX, DEF_VAL_INT);
		SET_ZERO(jet_toptagger__energy, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger__eta, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger__mass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger__min_mass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger__n_sj, N_MAX, DEF_VAL_INT);
		SET_ZERO(jet_toptagger__phi, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger__pt, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger__top_mass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger__w_mass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger_sj__energy, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger_sj__eta, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger_sj__mass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger_sj__parent_idx, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger_sj__phi, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(jet_toptagger_sj__pt, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__ch_iso, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__charge, N_MAX, DEF_VAL_INT);
		SET_ZERO(lep__dxy, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__dz, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__ec_iso, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__eta, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__hc_iso, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__id, N_MAX, DEF_VAL_INT);
		SET_ZERO(lep__id_bitmask, N_MAX, DEF_VAL_INT);
		SET_ZERO(lep__is_loose, N_MAX, DEF_VAL_INT);
		SET_ZERO(lep__is_medium, N_MAX, DEF_VAL_INT);
		SET_ZERO(lep__is_tight, N_MAX, DEF_VAL_INT);
		SET_ZERO(lep__mass, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__mva, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__p_iso, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__ph_iso, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__phi, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__pt, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__puch_iso, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__rel_iso, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(lep__type, N_MAX, DEF_VAL_INT);
		lhe__ht = DEF_VAL_FLOAT;
		lhe__n_b = DEF_VAL_INT;
		lhe__n_c = DEF_VAL_INT;
		lhe__n_e = DEF_VAL_INT;
		lhe__n_g = DEF_VAL_INT;
		lhe__n_j = DEF_VAL_FLOAT;
		lhe__n_l = DEF_VAL_INT;
		met__phi = DEF_VAL_FLOAT;
		met__pt = DEF_VAL_FLOAT;
		met__pt__en_down = DEF_VAL_FLOAT;
		met__pt__en_up = DEF_VAL_FLOAT;
		n__jet = DEF_VAL_INT;
		n__jet_toptagger = DEF_VAL_INT;
		n__jet_toptagger_sj = DEF_VAL_INT;
		n__lep = DEF_VAL_INT;
		n__pv = DEF_VAL_INT;
		n__pvi = DEF_VAL_INT;
		SET_ZERO(pvi__bx, N_MAX, DEF_VAL_INT);
		SET_ZERO(pvi__n0, N_MAX, DEF_VAL_FLOAT);
		SET_ZERO(pvi__ntrue, N_MAX, DEF_VAL_FLOAT);
		weight__pu = DEF_VAL_FLOAT;
		weight__pu_down = DEF_VAL_FLOAT;
		weight__pu_up = DEF_VAL_FLOAT;
		weight__trigger = DEF_VAL_FLOAT;
		weight__trigger_down = DEF_VAL_FLOAT;
		weight__trigger_up = DEF_VAL_FLOAT;
	}
	void make_branches(void) {
		tree->Branch("event__id", &event__id, "event__id/I");
		tree->Branch("event__json", &event__json, "event__json/I");
		tree->Branch("event__lumi", &event__lumi, "event__lumi/I");
		tree->Branch("event__run", &event__run, "event__run/I");
		tree->Branch("lhe__n_b", &lhe__n_b, "lhe__n_b/I");
		tree->Branch("lhe__n_c", &lhe__n_c, "lhe__n_c/I");
		tree->Branch("lhe__n_e", &lhe__n_e, "lhe__n_e/I");
		tree->Branch("lhe__n_g", &lhe__n_g, "lhe__n_g/I");
		tree->Branch("lhe__n_l", &lhe__n_l, "lhe__n_l/I");
		tree->Branch("n__jet", &n__jet, "n__jet/I");
		tree->Branch("n__jet_toptagger", &n__jet_toptagger, "n__jet_toptagger/I");
		tree->Branch("n__jet_toptagger_sj", &n__jet_toptagger_sj, "n__jet_toptagger_sj/I");
		tree->Branch("n__lep", &n__lep, "n__lep/I");
		tree->Branch("n__pv", &n__pv, "n__pv/I");
		tree->Branch("n__pvi", &n__pvi, "n__pvi/I");
		tree->Branch("debug__time1c", &debug__time1c, "debug__time1c/D");
		tree->Branch("debug__time1r", &debug__time1r, "debug__time1r/D");
		tree->Branch("gen_jet__eta", gen_jet__eta, "gen_jet__eta[n__jet]/F");
		tree->Branch("gen_jet__id", gen_jet__id, "gen_jet__id[n__jet]/I");
		tree->Branch("gen_jet__mass", gen_jet__mass, "gen_jet__mass[n__jet]/F");
		tree->Branch("gen_jet__phi", gen_jet__phi, "gen_jet__phi[n__jet]/F");
		tree->Branch("gen_jet__pt", gen_jet__pt, "gen_jet__pt[n__jet]/F");
		tree->Branch("gen_jet__status", gen_jet__status, "gen_jet__status[n__jet]/I");
		tree->Branch("gen_jet__type", gen_jet__type, "gen_jet__type[n__jet]/I");
		tree->Branch("gen_jet_parton__eta", gen_jet_parton__eta, "gen_jet_parton__eta[n__jet]/F");
		tree->Branch("gen_jet_parton__id", gen_jet_parton__id, "gen_jet_parton__id[n__jet]/I");
		tree->Branch("gen_jet_parton__mass", gen_jet_parton__mass, "gen_jet_parton__mass[n__jet]/F");
		tree->Branch("gen_jet_parton__phi", gen_jet_parton__phi, "gen_jet_parton__phi[n__jet]/F");
		tree->Branch("gen_jet_parton__pt", gen_jet_parton__pt, "gen_jet_parton__pt[n__jet]/F");
		tree->Branch("gen_jet_parton__status", gen_jet_parton__status, "gen_jet_parton__status[n__jet]/I");
		tree->Branch("gen_jet_parton__type", gen_jet_parton__type, "gen_jet_parton__type[n__jet]/I");
		tree->Branch("gen_lep__eta", gen_lep__eta, "gen_lep__eta[n__lep]/F");
		tree->Branch("gen_lep__id", gen_lep__id, "gen_lep__id[n__lep]/I");
		tree->Branch("gen_lep__mass", gen_lep__mass, "gen_lep__mass[n__lep]/F");
		tree->Branch("gen_lep__phi", gen_lep__phi, "gen_lep__phi[n__lep]/F");
		tree->Branch("gen_lep__pt", gen_lep__pt, "gen_lep__pt[n__lep]/F");
		tree->Branch("gen_lep__status", gen_lep__status, "gen_lep__status[n__lep]/I");
		tree->Branch("gen_lep__type", gen_lep__type, "gen_lep__type[n__lep]/I");
		tree->Branch("gen_met__phi", &gen_met__phi, "gen_met__phi/F");
		tree->Branch("gen_met__pt", &gen_met__pt, "gen_met__pt/F");
		tree->Branch("jet__bd_csv", jet__bd_csv, "jet__bd_csv[n__jet]/F");
		tree->Branch("jet__ce_e", jet__ce_e, "jet__ce_e[n__jet]/F");
		tree->Branch("jet__ch_e", jet__ch_e, "jet__ch_e[n__jet]/F");
		tree->Branch("jet__el_e", jet__el_e, "jet__el_e[n__jet]/F");
		tree->Branch("jet__energy", jet__energy, "jet__energy[n__jet]/F");
		tree->Branch("jet__eta", jet__eta, "jet__eta[n__jet]/F");
		tree->Branch("jet__id", jet__id, "jet__id[n__jet]/I");
		tree->Branch("jet__mass", jet__mass, "jet__mass[n__jet]/F");
		tree->Branch("jet__mu_e", jet__mu_e, "jet__mu_e[n__jet]/F");
		tree->Branch("jet__ne_e", jet__ne_e, "jet__ne_e[n__jet]/F");
		tree->Branch("jet__nh_e", jet__nh_e, "jet__nh_e[n__jet]/F");
		tree->Branch("jet__ph_e", jet__ph_e, "jet__ph_e[n__jet]/F");
		tree->Branch("jet__phi", jet__phi, "jet__phi[n__jet]/F");
		tree->Branch("jet__pileupJetId", jet__pileupJetId, "jet__pileupJetId[n__jet]/F");
		tree->Branch("jet__pt", jet__pt, "jet__pt[n__jet]/F");
		tree->Branch("jet__type", jet__type, "jet__type[n__jet]/I");
		tree->Branch("jet__vtx3DSig", jet__vtx3DSig, "jet__vtx3DSig[n__jet]/F");
		tree->Branch("jet__vtx3DVal", jet__vtx3DVal, "jet__vtx3DVal[n__jet]/F");
		tree->Branch("jet__vtxMass", jet__vtxMass, "jet__vtxMass[n__jet]/F");
		tree->Branch("jet__vtxNtracks", jet__vtxNtracks, "jet__vtxNtracks[n__jet]/F");
		tree->Branch("jet_toptagger__child_idx", jet_toptagger__child_idx, "jet_toptagger__child_idx[n__jet_toptagger]/I");
		tree->Branch("jet_toptagger__energy", jet_toptagger__energy, "jet_toptagger__energy[n__jet_toptagger]/F");
		tree->Branch("jet_toptagger__eta", jet_toptagger__eta, "jet_toptagger__eta[n__jet_toptagger]/F");
		tree->Branch("jet_toptagger__mass", jet_toptagger__mass, "jet_toptagger__mass[n__jet_toptagger]/F");
		tree->Branch("jet_toptagger__min_mass", jet_toptagger__min_mass, "jet_toptagger__min_mass[n__jet_toptagger]/F");
		tree->Branch("jet_toptagger__n_sj", jet_toptagger__n_sj, "jet_toptagger__n_sj[n__jet_toptagger]/I");
		tree->Branch("jet_toptagger__phi", jet_toptagger__phi, "jet_toptagger__phi[n__jet_toptagger]/F");
		tree->Branch("jet_toptagger__pt", jet_toptagger__pt, "jet_toptagger__pt[n__jet_toptagger]/F");
		tree->Branch("jet_toptagger__top_mass", jet_toptagger__top_mass, "jet_toptagger__top_mass[n__jet_toptagger]/F");
		tree->Branch("jet_toptagger__w_mass", jet_toptagger__w_mass, "jet_toptagger__w_mass[n__jet_toptagger]/F");
		tree->Branch("jet_toptagger_sj__energy", jet_toptagger_sj__energy, "jet_toptagger_sj__energy[n__jet_toptagger_sj]/F");
		tree->Branch("jet_toptagger_sj__eta", jet_toptagger_sj__eta, "jet_toptagger_sj__eta[n__jet_toptagger_sj]/F");
		tree->Branch("jet_toptagger_sj__mass", jet_toptagger_sj__mass, "jet_toptagger_sj__mass[n__jet_toptagger_sj]/F");
		tree->Branch("jet_toptagger_sj__parent_idx", jet_toptagger_sj__parent_idx, "jet_toptagger_sj__parent_idx[n__jet_toptagger_sj]/F");
		tree->Branch("jet_toptagger_sj__phi", jet_toptagger_sj__phi, "jet_toptagger_sj__phi[n__jet_toptagger_sj]/F");
		tree->Branch("jet_toptagger_sj__pt", jet_toptagger_sj__pt, "jet_toptagger_sj__pt[n__jet_toptagger_sj]/F");
		tree->Branch("lep__ch_iso", lep__ch_iso, "lep__ch_iso[n__lep]/F");
		tree->Branch("lep__charge", lep__charge, "lep__charge[n__lep]/I");
		tree->Branch("lep__dxy", lep__dxy, "lep__dxy[n__lep]/F");
		tree->Branch("lep__dz", lep__dz, "lep__dz[n__lep]/F");
		tree->Branch("lep__ec_iso", lep__ec_iso, "lep__ec_iso[n__lep]/F");
		tree->Branch("lep__eta", lep__eta, "lep__eta[n__lep]/F");
		tree->Branch("lep__hc_iso", lep__hc_iso, "lep__hc_iso[n__lep]/F");
		tree->Branch("lep__id", lep__id, "lep__id[n__lep]/I");
		tree->Branch("lep__id_bitmask", lep__id_bitmask, "lep__id_bitmask[n__lep]/I");
		tree->Branch("lep__is_loose", lep__is_loose, "lep__is_loose[n__lep]/I");
		tree->Branch("lep__is_medium", lep__is_medium, "lep__is_medium[n__lep]/I");
		tree->Branch("lep__is_tight", lep__is_tight, "lep__is_tight[n__lep]/I");
		tree->Branch("lep__mass", lep__mass, "lep__mass[n__lep]/F");
		tree->Branch("lep__mva", lep__mva, "lep__mva[n__lep]/F");
		tree->Branch("lep__p_iso", lep__p_iso, "lep__p_iso[n__lep]/F");
		tree->Branch("lep__ph_iso", lep__ph_iso, "lep__ph_iso[n__lep]/F");
		tree->Branch("lep__phi", lep__phi, "lep__phi[n__lep]/F");
		tree->Branch("lep__pt", lep__pt, "lep__pt[n__lep]/F");
		tree->Branch("lep__puch_iso", lep__puch_iso, "lep__puch_iso[n__lep]/F");
		tree->Branch("lep__rel_iso", lep__rel_iso, "lep__rel_iso[n__lep]/F");
		tree->Branch("lep__type", lep__type, "lep__type[n__lep]/I");
		tree->Branch("lhe__ht", &lhe__ht, "lhe__ht/F");
		tree->Branch("lhe__n_j", &lhe__n_j, "lhe__n_j/F");
		tree->Branch("met__phi", &met__phi, "met__phi/F");
		tree->Branch("met__pt", &met__pt, "met__pt/F");
		tree->Branch("met__pt__en_down", &met__pt__en_down, "met__pt__en_down/F");
		tree->Branch("met__pt__en_up", &met__pt__en_up, "met__pt__en_up/F");
		tree->Branch("pvi__bx", pvi__bx, "pvi__bx[n__pvi]/I");
		tree->Branch("pvi__n0", pvi__n0, "pvi__n0[n__pvi]/F");
		tree->Branch("pvi__ntrue", pvi__ntrue, "pvi__ntrue[n__pvi]/F");
		tree->Branch("weight__pu", &weight__pu, "weight__pu/F");
		tree->Branch("weight__pu_down", &weight__pu_down, "weight__pu_down/F");
		tree->Branch("weight__pu_up", &weight__pu_up, "weight__pu_up/F");
		tree->Branch("weight__trigger", &weight__trigger, "weight__trigger/F");
		tree->Branch("weight__trigger_down", &weight__trigger_down, "weight__trigger_down/F");
		tree->Branch("weight__trigger_up", &weight__trigger_up, "weight__trigger_up/F");
	}
	void set_branch_addresses(void) {
		tree->SetBranchAddress("debug__time1c", &debug__time1c);
		tree->SetBranchAddress("debug__time1r", &debug__time1r);
		tree->SetBranchAddress("event__id", &event__id);
		tree->SetBranchAddress("event__json", &event__json);
		tree->SetBranchAddress("event__lumi", &event__lumi);
		tree->SetBranchAddress("event__run", &event__run);
		tree->SetBranchAddress("gen_jet__eta", gen_jet__eta);
		tree->SetBranchAddress("gen_jet__id", gen_jet__id);
		tree->SetBranchAddress("gen_jet__mass", gen_jet__mass);
		tree->SetBranchAddress("gen_jet__phi", gen_jet__phi);
		tree->SetBranchAddress("gen_jet__pt", gen_jet__pt);
		tree->SetBranchAddress("gen_jet__status", gen_jet__status);
		tree->SetBranchAddress("gen_jet__type", gen_jet__type);
		tree->SetBranchAddress("gen_jet_parton__eta", gen_jet_parton__eta);
		tree->SetBranchAddress("gen_jet_parton__id", gen_jet_parton__id);
		tree->SetBranchAddress("gen_jet_parton__mass", gen_jet_parton__mass);
		tree->SetBranchAddress("gen_jet_parton__phi", gen_jet_parton__phi);
		tree->SetBranchAddress("gen_jet_parton__pt", gen_jet_parton__pt);
		tree->SetBranchAddress("gen_jet_parton__status", gen_jet_parton__status);
		tree->SetBranchAddress("gen_jet_parton__type", gen_jet_parton__type);
		tree->SetBranchAddress("gen_lep__eta", gen_lep__eta);
		tree->SetBranchAddress("gen_lep__id", gen_lep__id);
		tree->SetBranchAddress("gen_lep__mass", gen_lep__mass);
		tree->SetBranchAddress("gen_lep__phi", gen_lep__phi);
		tree->SetBranchAddress("gen_lep__pt", gen_lep__pt);
		tree->SetBranchAddress("gen_lep__status", gen_lep__status);
		tree->SetBranchAddress("gen_lep__type", gen_lep__type);
		tree->SetBranchAddress("gen_met__phi", &gen_met__phi);
		tree->SetBranchAddress("gen_met__pt", &gen_met__pt);
		tree->SetBranchAddress("jet__bd_csv", jet__bd_csv);
		tree->SetBranchAddress("jet__ce_e", jet__ce_e);
		tree->SetBranchAddress("jet__ch_e", jet__ch_e);
		tree->SetBranchAddress("jet__el_e", jet__el_e);
		tree->SetBranchAddress("jet__energy", jet__energy);
		tree->SetBranchAddress("jet__eta", jet__eta);
		tree->SetBranchAddress("jet__id", jet__id);
		tree->SetBranchAddress("jet__mass", jet__mass);
		tree->SetBranchAddress("jet__mu_e", jet__mu_e);
		tree->SetBranchAddress("jet__ne_e", jet__ne_e);
		tree->SetBranchAddress("jet__nh_e", jet__nh_e);
		tree->SetBranchAddress("jet__ph_e", jet__ph_e);
		tree->SetBranchAddress("jet__phi", jet__phi);
		tree->SetBranchAddress("jet__pileupJetId", jet__pileupJetId);
		tree->SetBranchAddress("jet__pt", jet__pt);
		tree->SetBranchAddress("jet__type", jet__type);
		tree->SetBranchAddress("jet__vtx3DSig", jet__vtx3DSig);
		tree->SetBranchAddress("jet__vtx3DVal", jet__vtx3DVal);
		tree->SetBranchAddress("jet__vtxMass", jet__vtxMass);
		tree->SetBranchAddress("jet__vtxNtracks", jet__vtxNtracks);
		tree->SetBranchAddress("jet_toptagger__child_idx", jet_toptagger__child_idx);
		tree->SetBranchAddress("jet_toptagger__energy", jet_toptagger__energy);
		tree->SetBranchAddress("jet_toptagger__eta", jet_toptagger__eta);
		tree->SetBranchAddress("jet_toptagger__mass", jet_toptagger__mass);
		tree->SetBranchAddress("jet_toptagger__min_mass", jet_toptagger__min_mass);
		tree->SetBranchAddress("jet_toptagger__n_sj", jet_toptagger__n_sj);
		tree->SetBranchAddress("jet_toptagger__phi", jet_toptagger__phi);
		tree->SetBranchAddress("jet_toptagger__pt", jet_toptagger__pt);
		tree->SetBranchAddress("jet_toptagger__top_mass", jet_toptagger__top_mass);
		tree->SetBranchAddress("jet_toptagger__w_mass", jet_toptagger__w_mass);
		tree->SetBranchAddress("jet_toptagger_sj__energy", jet_toptagger_sj__energy);
		tree->SetBranchAddress("jet_toptagger_sj__eta", jet_toptagger_sj__eta);
		tree->SetBranchAddress("jet_toptagger_sj__mass", jet_toptagger_sj__mass);
		tree->SetBranchAddress("jet_toptagger_sj__parent_idx", jet_toptagger_sj__parent_idx);
		tree->SetBranchAddress("jet_toptagger_sj__phi", jet_toptagger_sj__phi);
		tree->SetBranchAddress("jet_toptagger_sj__pt", jet_toptagger_sj__pt);
		tree->SetBranchAddress("lep__ch_iso", lep__ch_iso);
		tree->SetBranchAddress("lep__charge", lep__charge);
		tree->SetBranchAddress("lep__dxy", lep__dxy);
		tree->SetBranchAddress("lep__dz", lep__dz);
		tree->SetBranchAddress("lep__ec_iso", lep__ec_iso);
		tree->SetBranchAddress("lep__eta", lep__eta);
		tree->SetBranchAddress("lep__hc_iso", lep__hc_iso);
		tree->SetBranchAddress("lep__id", lep__id);
		tree->SetBranchAddress("lep__id_bitmask", lep__id_bitmask);
		tree->SetBranchAddress("lep__is_loose", lep__is_loose);
		tree->SetBranchAddress("lep__is_medium", lep__is_medium);
		tree->SetBranchAddress("lep__is_tight", lep__is_tight);
		tree->SetBranchAddress("lep__mass", lep__mass);
		tree->SetBranchAddress("lep__mva", lep__mva);
		tree->SetBranchAddress("lep__p_iso", lep__p_iso);
		tree->SetBranchAddress("lep__ph_iso", lep__ph_iso);
		tree->SetBranchAddress("lep__phi", lep__phi);
		tree->SetBranchAddress("lep__pt", lep__pt);
		tree->SetBranchAddress("lep__puch_iso", lep__puch_iso);
		tree->SetBranchAddress("lep__rel_iso", lep__rel_iso);
		tree->SetBranchAddress("lep__type", lep__type);
		tree->SetBranchAddress("lhe__ht", &lhe__ht);
		tree->SetBranchAddress("lhe__n_b", &lhe__n_b);
		tree->SetBranchAddress("lhe__n_c", &lhe__n_c);
		tree->SetBranchAddress("lhe__n_e", &lhe__n_e);
		tree->SetBranchAddress("lhe__n_g", &lhe__n_g);
		tree->SetBranchAddress("lhe__n_j", &lhe__n_j);
		tree->SetBranchAddress("lhe__n_l", &lhe__n_l);
		tree->SetBranchAddress("met__phi", &met__phi);
		tree->SetBranchAddress("met__pt", &met__pt);
		tree->SetBranchAddress("met__pt__en_down", &met__pt__en_down);
		tree->SetBranchAddress("met__pt__en_up", &met__pt__en_up);
		tree->SetBranchAddress("n__jet", &n__jet);
		tree->SetBranchAddress("n__jet_toptagger", &n__jet_toptagger);
		tree->SetBranchAddress("n__jet_toptagger_sj", &n__jet_toptagger_sj);
		tree->SetBranchAddress("n__lep", &n__lep);
		tree->SetBranchAddress("n__pv", &n__pv);
		tree->SetBranchAddress("n__pvi", &n__pvi);
		tree->SetBranchAddress("pvi__bx", pvi__bx);
		tree->SetBranchAddress("pvi__n0", pvi__n0);
		tree->SetBranchAddress("pvi__ntrue", pvi__ntrue);
		tree->SetBranchAddress("weight__pu", &weight__pu);
		tree->SetBranchAddress("weight__pu_down", &weight__pu_down);
		tree->SetBranchAddress("weight__pu_up", &weight__pu_up);
		tree->SetBranchAddress("weight__trigger", &weight__trigger);
		tree->SetBranchAddress("weight__trigger_down", &weight__trigger_down);
		tree->SetBranchAddress("weight__trigger_up", &weight__trigger_up);
	}
};
