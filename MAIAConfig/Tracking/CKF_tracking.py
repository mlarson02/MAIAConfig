from GaudiKernel.Constants import INFO, WARNING, DEBUG
from Configurables import ActsGeoSvc, CKFTrackingAlg, CKFTrackingFromSeedsAlg, ACTSDuplicateRemoval, FilterTracksAlg, TrackTruthAlg

import os

def ActsGeoSvc_cfg(args):
    """Configure the ACTS GeoSvc.
    Set use_dd4hep_field=True to make ACTS use the real, position-dependent
    DD4hep field.
    """
    return ActsGeoSvc(
        "ActsGeoSvc",
        UseDD4hepBField=args.use_dd4hep_field,
        MaterialMapFile = args.materialMapFile,
    )

def CKFTracker_cfg(args,
                   inflateCovarianceTwoWay = True, twoWayInflateCovarianceFactor = 100.0):
    """
    Create a new CKFTrackingAlg instance for CKF tracking.

    Two-way / outside-in track finding are hard-coded here (toggle by editing
    the twoWay/outsideIn constants below):

      twoWay        Run a second CKF pass in the opposite direction from the
                    smoothed innermost/outermost first-pass state and stitch it
                    onto the first-pass chain. Recovers hits the first pass
                    could not reach (e.g. VXD hits after a forward first pass,
                    or OT hits after a backward first pass).

      outsideIn     Reverse the first-pass direction: propagate backward from
                    the OUTER seed SP inward. Combined with twoWay, the second
                    (forward) pass then extends the track outward into the
                    outer tracker.

      inflateCovarianceTwoWay / twoWayInflateCovarianceFactor
                    Inflate the covariance handed to the second pass so the
                    acceptance window is not artificially tight after
                    smoothing. Ignored when twoWay=False.
    """
    # Hard-coded two-way / outside-in
    twoWay    = True
    outsideIn = True
    return CKFTrackingAlg(
        "Reconstructor",
        RunCKF = True,
        CKF_Chi2CutOff = 10,
        # Hits with chi2CutOff <= local chi2 < chi2CutOffOutlier are kept as outliers; above -> hole.
        CKF_Chi2CutOffOutlier = 25,
        # CKF branch stopper: terminate fake branches early instead of extending
        # them through the whole detector, aligned with the downstream selection
        # (>= 8 hits, <= 2 holes).
        UseBranchStopper = True,
        BranchStopper_MaxHoles = 2,
        BranchStopper_MaxOutliers = 3,
        BranchStopper_MinMeasurements = 8,
        BranchStopper_PtMin = 0.5,
        BranchStopper_PtMinMeasurements = 4,
        SeedFinding_RMax = 1600,
        SeedFinding_MinPt = 1500,
        SeedFinding_ImpactMax = 3,
        # CKF_NumMeasurementsCutOff: controls the CKF branching during track extension.
        # Set to 1 to keep only the best candidate.
        CKF_NumMeasurementsCutOff = 2,
        SeedFinding_SigmaScattering = 50,
        SeedFinding_CollisionRegion = 6,
        SeedFinding_RadLengthPerSeed = 0.1,
        SeedFinding_DeltaRMin = 5,
        SeedFinding_DeltaRMax = 400,
        # Seed space-point filtering: CellIDSelector selection strings ORed together.
        # Each string is a comma-separated conjunction of <field>:<value>[|<value>...]
        # constraints, decoded against the DD4hep readout string
        #   "system:5,side:-2,layer:6,module:11,sensor:8"  (GlobalTrackerReadoutID)
        # Fields omitted from a selection act as wildcards.
        #
        # MAIA_v0 system IDs (from k4geo/.../MAIA_v0/MAIA_v0.xml):
        #   1 = VXD Barrel      2 = VXD Endcap
        #   3 = IT  Barrel      4 = IT  Endcap
        #   5 = OT  Barrel      6 = OT  Endcap
        #
        # Active line: VXD Barrel (all layers) + VXD Endcap layers 1,2,3.
        #SeedingSensorsCellIDs = ["system:1", "system:2,layer:1|2|3"],
        # --- Alternative seeding sensor selections (commented out) ---
        # VXD barrel only:
        SeedingSensorsCellIDs = ["system:1"],
        # IT barrel only:
        #SeedingSensorsCellIDs = ["system:3"],
        # OT barrel only:
        #SeedingSensorsCellIDs = ["system:5"],
        # Current config restricted to barrel (drops VXD Endcap layers 1|2|3):
        # SeedingSensorsCellIDs = ["system:1"],
        AddEndcapCaloState = True,
        # Two-way / outside-in (all default off; no behaviour change unless enabled).
        #DoTwoWayCKF = twoWay,
        #DoOutsideInCKF = outsideIn,
        #InflateCovarianceTwoWay = inflateCovarianceTwoWay,
        #TwoWayInflateCovarianceFactor = twoWayInflateCovarianceFactor,
        OutputTrackCollection = "AllTracks",
        OutputSeedCollection = "SeedTracks",
        InputTrackerHitCollection = "MergedTrackerHits",
        InputTrackerHitRelationCollection = "MergedTrackerHitsRelations",
        NumThreads = args.TrackingThreads,
        OutputLevel = INFO,
    )

def CKFFromSeeds_cfg(args):
    """
    Create a CKFTrackingFromSeedsAlg instance that runs the CKF using the track
    candidates from the GNN track finder as seeds instead of internal seeding.
    Writes to its own collections so it can run alongside CKFTracker_cfg.
    """
    return CKFTrackingFromSeedsAlg(
        "SeededCKFReconstructor",
        CKF_Chi2CutOff = 10,
        CKF_NumMeasurementsCutOff = 1,
        MinSeedHits = 3,
        InputTrackerHitCollection = "MergedTrackerHits",
        InputSeedTrackCollection = "GNNTrackCandidates",
        OutputTrackCollection = "GNNAllTracks",
        OutputSeedCollection = "GNNSeededTracks",
        NumThreads = args.TrackingThreads,
        OutputLevel = INFO,
    )

def deduper_cfg(name = "Deduper", input = "AllTracks", output = "DedupedTracks"):
    """
    Create a new ACTSDuplicateRemoval instance for removing duplicate tracks.
    The names are parameters so the GNN-seeded pass can run its own instance
    over the GNN* collections; the defaults are the standard CKF chain.
    """
    return ACTSDuplicateRemoval(
        name,
        InputTrackCollectionName = [input],
        OutputTrackCollectionName = [output],
        OutputLevel = INFO
    )

def track_filter_cfg(name = "Filterer", input = "DedupedTracks", output = "SiTracks"):
    """
    Create a new FilterTracksAlg instance for filtering tracks.
    Parametrised like deduper_cfg, with the standard CKF chain as default.
    """
    return FilterTracksAlg(
        name,
        InputTrackCollectionName = [input],
        MinPt = "0.5",
        MaxD0 = 10,
        MaxZ0 = 10,
        NHitsInner = "0",
        NHitsOuter = "0",
        NHitsTotal = "7",
        NHitsVertex = "0",
        MaxHoles = 2,
        OutputTrackCollectionName = [output],
        OutputLevel = INFO
    )

def track_truth_all_tracks_cfg(args):
    """
    Truth matching for AllTracks -> AllTracksRelations.
    """
    return TrackTruthAlg(
        "TruthMatcher_AllTracks",
        NumThreads = args.TrackingThreads,
        InputTrackCollectionName = ["AllTracks"],
        InputTrackerHit2SimTrackerHitRelationName = ["MergedTrackerHitsRelations"],
        OutputParticle2TrackRelationName = ["AllTracksRelations"],
        OutputLevel = INFO
    )

def track_truth_deduped_cfg(args):
    """
    Truth matching for DedupedTracks -> DedupedTracksRelations.
    """
    return TrackTruthAlg(
        "TruthMatcher_Deduped",
        NumThreads = args.TrackingThreads,
        InputTrackCollectionName = ["DedupedTracks"],
        InputTrackerHit2SimTrackerHitRelationName = ["MergedTrackerHitsRelations"],
        OutputParticle2TrackRelationName = ["DedupedTracksRelations"],
        OutputLevel = INFO
    )
