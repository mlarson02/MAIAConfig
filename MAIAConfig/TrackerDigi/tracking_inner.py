from GaudiKernel.Constants import INFO, WARNING
from Configurables import DDPlanarDigi
from Common.overlay_utils import overlay_input
from TrackerDigi.timing_presets import TIMING_PRESETS

def ITBarrel_cfg(args):
    """
    Create a new inner barrel digitiser instance with the given parameters.
    """
    inputHitCollections = overlay_input("InnerTrackerBarrelCollection", args)
    return DDPlanarDigi(
        "InnerBarrelDigitiser",
        # Raw hit times (ToF correction only in the window cut): the 4D seeding / CKF expects them.
        CorrectTimesForPropagation = False,
        CorrectTimeWindowForPropagation = True,
        IsStrip = False,
        ResolutionT = [0.06],
        ResolutionU = [0.007],
        ResolutionV = [0.09],
        SubDetectorName = "InnerTrackers",
        # From the --timing preset, together with the overlay window.
        TimeWindowMin = [TIMING_PRESETS[args.timing]["digitiser"]["inner"][0]],
        TimeWindowMax = [TIMING_PRESETS[args.timing]["digitiser"]["inner"][1]],
        UseTimeWindow = True,
        SimTrackHitCollectionName = inputHitCollections,
        SimTrkHitRelCollection = ["ITBarrelHitsRelations"],
        TrackerHitCollectionName = ["ITBarrelHits"],
        ForceHitsOntoSurface = True,
        OutputLevel = INFO
    )

def ITEndcap_cfg(args):
    """
    Create a new inner endcap digitiser instance with the given parameters.
    """
    inputHitCollections = overlay_input("InnerTrackerEndcapCollection", args)
    return DDPlanarDigi(
        "InnerEndcapDigitiser",
        # Raw hit times (ToF correction only in the window cut): the 4D seeding / CKF expects them.
        CorrectTimesForPropagation = False,
        CorrectTimeWindowForPropagation = True,
        IsStrip = False,
        ResolutionT = [0.06],
        ResolutionU = [0.007],
        ResolutionV = [0.09],
        SubDetectorName = "InnerTrackers",
        # From the --timing preset, together with the overlay window.
        TimeWindowMin = [TIMING_PRESETS[args.timing]["digitiser"]["inner"][0]],
        TimeWindowMax = [TIMING_PRESETS[args.timing]["digitiser"]["inner"][1]],
        UseTimeWindow = True,
        SimTrackHitCollectionName = inputHitCollections,
        SimTrkHitRelCollection = ["ITEndcapHitsRelations"],
        TrackerHitCollectionName = ["ITEndcapHits"],
        ForceHitsOntoSurface = True,
        OutputLevel = INFO
    )
