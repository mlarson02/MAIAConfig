'''-------------------------------------------------------------'''
'''  Named seeding-sensor selections for CKFTrackingAlg          '''
'''-------------------------------------------------------------'''
# Picked with --seeding on the reco command line (reco.submit SEEDING), so the
# selection is fixed per job at submit time rather than read out of an edited
# CKF_tracking.py when the job starts.
#
# Each entry is the SeedingSensorsCellIDs list: CellIDSelector strings ORed
# together, each a comma-separated conjunction of <field>:<value>[|<value>...]
# against the readout "system:5,side:-2,layer:6,module:11,sensor:8". Omitted
# fields are wildcards. MAIA_v0 systems:
#   1 = VXD Barrel   2 = VXD Endcap
#   3 = IT  Barrel   4 = IT  Endcap
#   5 = OT  Barrel   6 = OT  Endcap
#
# Deliberately free of Gaudi imports, so reco.sh can check a name with plain
# python3 before it stages in the input.

SEEDING_PRESETS = {
    # All VXD layers (barrel + every endcap layer; doublet partners cannot pair,
    # dR < SeedFinding_DeltaRMin) + all IT endcap disks. IT disk 6 is at z 2190,
    # so this needs seedZMax >= ~2210 (default 2300).
    "VXDNominal": ["system:1", "system:2", "system:4"],

    # main's seeding (VXD barrel + VXD endcap 1, 3, 5) + VXD endcap 7 + IT disk 0:
    # >= 3 seed stations up to |eta| 2.38 (main: 1.93). Still within main's
    # seedZMax 600 / z edges; IT disk 0 reaches r 427, so seedRMax >= 450.
    "VXDMinimal": ["system:1", "system:2,layer:1|3|5|7", "system:4,layer:0"],

    # Barrel only, one subdetector each. Seeds exist only where a track crosses
    # all three barrel layers: OT barrel |eta| < 0.77
    "VXD": ["system:1"],
    "IT":  ["system:3"],
    "OT":  ["system:5"],

    # IT + OT, barrels and endcap disks: a seed exists out to the end of the tracker 
    "ITOTDisks": ["system:3", "system:4", "system:5", "system:6"],

    # Minimal outermost subset of ITOTDisks with >= 3 seed layers for |eta| < 2.44
    # (OutsideInTrackingStudies/seedingLayerScan.C): IT barrel 2, IT disks 3-5,
    # OT barrel 0-1, all OT disks.
    "ITOTDisks_Minimal": ["system:3,layer:2", "system:4,layer:3|4|5", "system:5,layer:0|1", "system:6"],

    # v2: >= 4 seed layers for |eta| < 2.44, one spare for a missing hit
    # (seedingLayerScan.C(2.44, 4)): v1 + IT barrel 1 + IT disk 2.
    "ITOTDisks_Minimal_v2": ["system:3,layer:1|2", "system:4,layer:2|3|4|5", "system:5,layer:0|1", "system:6"],

    # v3: ITOTDisks minus IT barrel 0 and IT disk 0 (the BIB-heaviest IT layers,
    # -30% seed hits); IT disk 1 kept for >= 5 seed layers at |eta| 1.21-2.08,
    # where v2's 4 left seeding dips.
    "ITOTDisks_Minimal_v3": ["system:3,layer:1|2", "system:4,layer:1|2|3|4|5|6", "system:5", "system:6"],

    # v4: ITOTDisks minus IT disks 0 and 1 (v3 showed IT barrel 0 is needed);
    # only 4 seed layers at |eta| 1.69-2.08, -10% seed hits.
    "ITOTDisks_Minimal_v4": ["system:3", "system:4,layer:2|3|4|5|6", "system:5", "system:6"],
}

# SeedFinding_DeltaRMax [mm] per preset; missing = 400.
SEEDING_DELTA_R_MAX = {
    # k4ActsTracking default (what MAIA used before 2026-09-12).
    "VXDNominal": 80,
    "VXDMinimal": 80,
}

# SeedFinding_zBinEdges per preset; missing = [] = one z bin over ±seedZMax.
# Edges replace seedZMax as the grid range (SPs outside are dropped) and must
# lie in [-seedZMax, seedZMax), else CKFTrackingAlg falls back to [].
SEEDING_Z_BIN_EDGES = {
    # Jackson's 4d-tracking edges: one bin per VXD disk pair, barrel split at ±20/±70.
    "VXD": ["-599", "-240", "-160", "-100", "-70", "-20", "20", "70", "100", "160", "240", "599"],
    # main's edges; IT disk 0 (z 524) shares the last bin with VXD disks 6/7.
    "VXDMinimal": ["-599", "-240", "-160", "-100", "-70", "-20", "20", "70", "100", "160", "240", "599"],
}


def _symmetric(edges):
    """[e1, e2, ...] -> ["-..", "-e2", "-e1", "e1", "e2", ..] (strings, as the property takes)."""
    return [str(-e) for e in reversed(edges)] + [str(e) for e in edges]


# z bin edges used with --seedZBins (submit key zbins=1, added 2026-11-10); without
# it SEEDING_Z_BIN_EDGES above applies. Need seedZMax > 2299. Seeding pairs hits
# only in the same or a neighbouring z bin (SeedFinding_z{Top,Bottom}BinLen = 1).
SEEDING_Z_BINS = {
    # main's VXD edges (one bin per VXD disk pair) + one bin per IT disk: like
    # main, only z-adjacent disks pair.
    "VXDNominal": _symmetric([20, 70, 100, 160, 240, 400, 666, 950, 1235, 1519, 1803, 2068, 2299]),
    "VXDMinimal": _symmetric([20, 70, 100, 160, 240, 599]),
    # Edges growing ~2x outward: adjacent barrel layers (r ratio <= 2.1, also with
    # drmaxtop=650) stay within one bin. Mostly a speed-up; disks are barely split.
    "ITOTDisks_Minimal":    _symmetric([150, 350, 750, 1500, 2299]),
    "ITOTDisks_Minimal_v2": _symmetric([150, 350, 750, 1500, 2299]),
    "ITOTDisks_Minimal_v3": _symmetric([150, 350, 750, 1500, 2299]),
    # ~3x with IT barrel 0 (r 127 -> 340 is 2.7x).
    "ITOTDisks":            _symmetric([100, 300, 900, 2299]),
    "ITOTDisks_Minimal_v4": _symmetric([100, 300, 900, 2299]),
}

# SeedFinding_RMax [mm] with --seedRMax unset is 1600 (CKF_tracking.py). Seed hits
# beyond it are dropped, and ACTS needs RMax <= 2 x helix radius at seedMinPt
# (1333 mm at 1 GeV in 5 T), so outside-in presets cannot go below ~1.2 GeV.
