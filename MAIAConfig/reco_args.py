import argparse
import os
from Gaudi.Configuration import *
from k4FWCore.parseArgs import parser
from Common.argutils import add_argument_once
from Tracking.seeding_presets import SEEDING_PRESETS

def get_reco_args():
    """
    Parse command line arguments for the reconstruction steering.
    """
    # Shared with digi_args; added once so the two can be combined in one job.
    add_argument_once(
        parser,
        "--DD4hepXMLFile",
        help="Compact detector description file",
        type=str,
        default=os.environ.get("k4geo_DIR", "")+"/MuColl/MAIA/compact/MAIA_v0/MAIA_v0.xml",
    )

    add_argument_once(
        parser,
        "--materialMapFile",
        help="Material map file",
        type=str,
        default=os.environ.get("ACTSTRACKING_DATA") + "/k4ActsTracking/data/MAIA_v0_gen3_material_map.json",
    )

    parser.add_argument(
        "--doTrackPerf",
        help="Run Performance Analysis on Tracking",
        action="store_true",
        default=True
    )

    parser.add_argument(
        "--use_dd4hep_field",
        help="Use DD4hep field",
        action="store_true",
        default=True
    )

    # CKF configuration. Command-line arguments rather than constants in
    # Tracking/CKF_tracking.py, so a condor job's configuration is fixed in its
    # Arguments at submit time: the configs directory is transferred when each
    # job *starts*, so an edit made after condor_submit reaches every job still
    # in the queue. The defaults are the nominal chain (inside-out, one pass,
    # VXD seeding).
    parser.add_argument(
        "--seeding",
        help="Seeding sensor selection, by name (see Tracking/seeding_presets.py)",
        choices=sorted(SEEDING_PRESETS),
        default="ITOTDisks_Minimal_v2",
    )

    parser.add_argument(
        "--ckfDirection",
        help="CKF first-pass direction: InOut propagates outward from the inner "
             "seed space point; OutIn starts on the outer one and propagates "
             "toward the beamline (PropagateBackward)",
        choices=["InOut", "OutIn"],
        default="OutIn",
    )

    parser.add_argument(
        "--twoWayCKF",
        help="Run a second CKF pass in the opposite direction from the smoothed "
             "first-pass end state and stitch it on (DoTwoWayCKF). "
             "--no-twoWayCKF turns it off explicitly",
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    parser.add_argument(
        "--seedDeduplication",
        help="Skip the CKF for a seed whose three hits are all on a track already "
             "found from an earlier seed (SeedDeduplication). "
             "--no-seedDeduplication turns it off explicitly",
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    parser.add_argument(
        "--hitTimeInTracking",
        help="4D tracking: hit times in the seeding time cuts and as a CKF "
             "measurement (UseHitTimeInCKF). --no-hitTimeInTracking turns both off",
        action=argparse.BooleanOptionalAction,
        default=True,
    )

    parser.add_argument(
        "--timeBetaHypothesis",
        help="Velocity (0 < beta <= 1) assumed by the 4D tracking: hit times are "
             "shifted by -|x| (1/beta - 1) / c before the seeding time cuts and "
             "the CKF (TimeBetaHypothesis); 1 = no shift",
        type=float,
        default=1.0,
    )

    parser.add_argument(
        "--seedDedupMinShared",
        help="Seed deduplication skips a seed once this many of its 3 hits are on "
             "an earlier track (SeedDeduplication_MinSharedMeasurements); 3 = all",
        type=int,
        choices=[1, 2, 3],
        default=3,
    )

    parser.add_argument(
        "--seedZMax",
        help="Maximum |z| [mm] of seed space points (SeedFinding_ZMax); points "
             "beyond it are dropped from seeding. 600 covers the barrels the "
             "barrel-only presets use; VXDNominal and ITOTDisks need >= 2210 "
             "(last IT disk)",
        type=float,
        default=2300.0,
    )

    parser.add_argument(
        "--seedImpactMax",
        help="Maximum transverse impact parameter |d0| [mm] of seeds (SeedFinding_ImpactMax)",
        type=float,
        default=100,
    )

    parser.add_argument(
        "--seedCollisionRegion",
        help="Half-length [mm] of the collision region in z that seeds must point "
             "back to (SeedFinding_CollisionRegion)",
        type=float,
        default=150,
    )

    parser.add_argument(
        "--seedMinPt",
        help="Minimum seed pT [GeV] (SeedFinding_MinPt); with SeedFinding_RMax "
             "1600 mm ACTS needs >= ~1.2 GeV",
        type=float,
        default=1.5,
    )

    parser.add_argument(
        "--seedDeltaZMax",
        help="Maximum |dz| [mm] between the hits of a seed doublet "
             "(SeedFinding_DeltaZMax); 0 = no cut",
        type=float,
        default=0,
    )

    parser.add_argument(
        "--seedZBins",
        help="Use the preset's z bins from SEEDING_Z_BINS (Tracking/seeding_presets.py) "
             "instead of SEEDING_Z_BIN_EDGES",
        action="store_true",
    )

    parser.add_argument(
        "--seedRMax",
        help="Maximum radius [mm] of seed space points (SeedFinding_RMax); "
             "needs RMax <= 2 x helix radius at seedMinPt",
        type=float,
        default=1600,
    )

    parser.add_argument(
        "--seedDeltaRMaxTop",
        help="Maximum dr [mm] between the middle and top hits of a seed "
             "(SeedFinding_DeltaRMaxTop); 0 = SeedFinding_DeltaRMax",
        type=float,
        default=0,
    )

    parser.add_argument(
        "--seedMaxPerSpM",
        help="Seeds kept per middle space point, minus one (SeedFilter_MaxSeedsPerSpM)",
        type=int,
        default=1,
    )

    parser.add_argument(
        "--seedCompatWeight",
        help="Seed weight added per compatible top space point, i.e. a 4th hit "
             "(SeedFilter_CompatSeedWeight); 0 = rank by d0/z0 only",
        type=float,
        default=0,
    )

    parser.add_argument(
        "--filterTracksD0",
        help="Maximum |d0| [mm] of SiTracks (FilterTracksAlg MaxD0)",
        type=float,
        default=10,
    )

    parser.add_argument(
        "--filterTracksZ0",
        help="Maximum |z0| [mm] of SiTracks (FilterTracksAlg MaxZ0)",
        type=float,
        default=10,
    )

    parser.add_argument(
        "--TrackingThreads",
        help="Number of threads used internally by the tracking algorithms "
             "(independent of the --numThreads Gaudi event-loop setting)",
        type=int,
        default=16,
    )

    # Shared with digi_args.
    add_argument_once(
        parser,
        "--doTrackerConing",
        help="Filter tracker hits into cones around the signal MC particles (BIB cleaning)",
        action="store_true",
        default=False,
    )

    # Shared with digi_args.
    add_argument_once(
        parser,
        "--doOverlayFull",
        help="Do BIB overlay",
        action="store_true",
        default=False,
    )

    add_argument_once(
        parser,
        "--doOverlayIP",
        help="Do incoherent pairs overlay",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--keepEverything",
        help="Write every collection to the reconstruction output, including "
             "the tracker and calorimeter hits that are otherwise dropped when "
             "an overlay is enabled",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--dropTrackerHits",
        help="Drop the tracker hit collections from the output when an overlay "
             "is enabled (they are kept by default, coned or not)",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--keepCaloHits",
        help="Keep the calorimeter hit collections in the output when an "
             "overlay is enabled (they are dropped by default)",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--pandoraSettings",
        help="Pandora settings XML. A bare file name is looked up in the "
             "PandoraSettings directory shipped with MAIAConfig (override it "
             "with MAIA_PANDORA_SETTINGS_DIR); an absolute or run-directory "
             "relative path is used as given",
        type=str,
        default="PandoraSettingsDefault.xml",
    )

    # CLUE args
    parser.add_argument(
        "--doCLUE",
        help="Enable CLUE clustering in addition to Pandora.",
        action="store_true"
    )

    parser.add_argument(
        "--clueCriticalDistance",
        help="Critical distance used to compute the local density in CLUE clustering",
        type=float,
        default=30,
    )

    parser.add_argument(
        "--clueMinLocalDensity",
        help="Minimum local density for a point to be promoted to a seed in CLUE clustering",
        type=float,
        default=0.1,
    )

    parser.add_argument(
        "--clueFollowerDistance",
        help="Maximum distance considered to search for followers in CLUE clustering",
        type=float,
        default=120,
    )

    parser.add_argument(
        "--clueSeedCriticalDistance",
        help="Critical distance used to promote a high density point as a seed in CLUE clustering; defaults to critical distance if set to -1.",
        type=float,
        default=-1,
    )

    # GNN CKF tracking args
    parser.add_argument(
        "--findGNNTracks",
        help="Additionally run the GNN track finder and seed a second CKF pass "
             "with its candidates, into the GNN* collections. The standard CKF "
             "chain is unaffected and keeps writing SiTracks",
        action="store_true",
        default=False,
    )

    add_argument_once(
        parser,
        "--modelBase",
        help="Path to base directory containing the GNN models",
        type=str,
        default=os.environ.get("MODEL_DIR", ""),
    )
    add_argument_once(
        parser,
        "--device",
        help="Device to run the GNN pipeline on: 'cpu' or 'cuda' (optionally 'cuda:<index>')",
        type=str,
        default="cpu",
    )

    return parser.parse_known_args()[0]
