from GaudiKernel.Constants import INFO, WARNING, DEBUG
from Configurables import ActsGeoSvc, CKFTrackingAlg, CKFTrackingFromSeedsAlg, ACTSDuplicateRemoval, FilterTracksAlg, TrackTruthAlg
from Tracking.seeding_presets import SEEDING_PRESETS, SEEDING_Z_BIN_EDGES, SEEDING_Z_BINS, SEEDING_DELTA_R_MAX

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
                   inflateCovarianceTwoWay = True, twoWayInflateCovarianceFactor = 25.0):
    """
    Create a new CKFTrackingAlg instance for CKF tracking.

    Seeding, direction and two-way come from the command line (reco_args.py),
    so that a condor job's configuration is fixed when it is submitted:

      --seeding     Name of the seeding sensor selection, looked up in
                    Tracking/seeding_presets.py.

      --ckfDirection OutIn
                    Find tracks outside-in (PropagateBackward): start the first
                    pass on the OUTER seed SP and propagate backward through the
                    seed's middle and inner SPs toward the beamline. Combined
                    with two-way, the second (forward) pass then extends the
                    track outward past the outer seed SP.

      --twoWayCKF   Run a second CKF pass in the opposite direction from the
                    smoothed innermost/outermost first-pass state and stitch it
                    onto the first-pass chain. Recovers hits the first pass
                    could not reach (e.g. VXD hits after a forward first pass,
                    or OT hits after a backward first pass).

      --seedDeduplication
                    Skip the CKF for a seed whose three hits are all on a track
                    already found from an earlier seed.

      --no-hitTimeInTracking
                    3D tracking: no seeding time cuts and no hit time in the
                    CKF. Both assume beta = 1, which loses slow particles.

      --timeBetaHypothesis
                    Keep 4D tracking for a slow particle instead: hit times are
                    shifted by -|x| (1/beta - 1) / c (TimeBetaHypothesis), so a
                    particle of that beta from the origin looks like beta = 1.

      inflateCovarianceTwoWay / twoWayInflateCovarianceFactor
                    Inflate the covariance handed to the second pass so the
                    acceptance window is not artificially tight after
                    smoothing. Ignored without two-way.
    """
    twoWay            = args.twoWayCKF
    hitTime           = getattr(args, "hitTimeInTracking", True)   # 4D: seed time cuts + CKF hit time
    timeBeta          = getattr(args, "timeBetaHypothesis", 1.0)   # beta assumed for the hit times
    propagateBackward = args.ckfDirection == "OutIn"
    if getattr(args, "seedZBins", False):
        if args.seeding not in SEEDING_Z_BINS:
            raise ValueError(f"--seedZBins: no SEEDING_Z_BINS entry for seeding '{args.seeding}'")
        zBinEdges = SEEDING_Z_BINS[args.seeding]
    else:
        zBinEdges = SEEDING_Z_BIN_EDGES.get(args.seeding, [])
    # CKFTrackingAlg would only warn and fall back to [] (no z bins) otherwise.
    if any(not -args.seedZMax <= float(e) < args.seedZMax for e in zBinEdges):
        raise ValueError(f"SeedFinding_zBinEdges {zBinEdges} must lie in [-seedZMax, seedZMax) = "
                         f"[-{args.seedZMax}, {args.seedZMax})")
    return CKFTrackingAlg(
        "Reconstructor",
        RunCKF = True,
        CKF_Chi2CutOff = 12,
        # Hits with chi2CutOff <= local chi2 < chi2CutOffOutlier are kept as outliers; above -> hole.
        CKF_Chi2CutOffOutlier = 25,
        UseBranchStopper = True,
        BranchStopper_MaxHoles = 1,
        BranchStopper_MaxOutliers = 1,
        BranchStopper_MinMeasurements = 8,
        BranchStopper_PtMin = 1.0,
        BranchStopper_PtMinMeasurements = 4,
        SeedFinding_RMax = getattr(args, "seedRMax", 1600),
        # CKF_NumMeasurementsCutOff: controls the CKF branching during track extension.
        # Set to 1 to keep only the best candidate.
        CKF_NumMeasurementsCutOff = 1,
        SeedFinding_MinPt = args.seedMinPt * 1000,  # GeV -> MeV
        SeedFinding_ImpactMax = args.seedImpactMax,
        SeedFinding_SigmaScattering = 50,
        SeedFinding_CollisionRegion = args.seedCollisionRegion,
        SeedFinding_RadLengthPerSeed = 0.1,
        SeedFinding_DoubletTimeCutNSigma = 3 if hitTime else -1,   # <= 0: off
        SeedFinding_TripletTimeChi2Max = 12 if hitTime else -1,
        SeedFinding_InteractionPointCut = True,
        SeedFilter_CompatSeedWeight = getattr(args, "seedCompatWeight", 0),
        SeedFilter_MaxSeedsPerSpM = getattr(args, "seedMaxPerSpM", 1),
        InitialTrackError_QOverP = 0.03,
        SeedFinding_zBinEdges = zBinEdges,
        UseHitTimeInCKF = hitTime,
        HitTimeResolutions = {"system:1|2": 0.03, "system:3|4|5|6": 0.06},
        SeedFinding_DeltaRMin = 5,
        SeedFinding_DeltaRMax = SEEDING_DELTA_R_MAX.get(args.seeding, 400),
        SeedFinding_DeltaRMaxTop = getattr(args, "seedDeltaRMaxTop", 0),  # 0: = DeltaRMax
        SeedFinding_ZMax = args.seedZMax,
        SeedingSensorsCellIDs = SEEDING_PRESETS[args.seeding],
        AddEndcapCaloState = True,
        DoTwoWayCKF = twoWay,
        SeedDeduplication = args.seedDeduplication,
        # Set only when not the default 3, so k4Acts builds without the property still run.
        **({"SeedDeduplication_MinSharedMeasurements": args.seedDedupMinShared}
           if args.seedDedupMinShared != 3 else {}),
        # Set only when not 1 (no shift), likewise.
        **({"TimeBetaHypothesis": timeBeta} if timeBeta != 1.0 else {}),
        # Set only when > 0 (cut on), likewise.
        **({"SeedFinding_DeltaZMax": args.seedDeltaZMax}
           if getattr(args, "seedDeltaZMax", 0) > 0 else {}),
        PropagateBackward = propagateBackward,
        InflateCovarianceTwoWay = True,
        TwoWayInflateCovarianceFactor = 100.0,
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

def track_filter_cfg(args, name = "Filterer", input = "DedupedTracks", output = "SiTracks"):
    """
    Create a new FilterTracksAlg instance for filtering tracks.
    Parametrised like deduper_cfg, with the standard CKF chain as default;
    the |d0| / |z0| cuts come from --filterTracksD0 / --filterTracksZ0.
    """
    return FilterTracksAlg(
        name,
        InputTrackCollectionName = [input],
        MinPt = "1.0",
        MaxD0 = args.filterTracksD0,
        MaxZ0 = args.filterTracksZ0,
        NHitsInner = "0",
        NHitsOuter = "0",
        NHitsTotal = "8",
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
