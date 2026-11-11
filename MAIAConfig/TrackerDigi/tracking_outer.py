from GaudiKernel.Constants import INFO, WARNING
from Configurables import DDPlanarDigi
from Common.overlay_utils import overlay_input
from TrackerDigi.timing_presets import TIMING_PRESETS

def OTBarrel_cfg(args):
    """
    Create a new outer barrel digitiser instance with the given parameters.
    """
    inputHitCollections = overlay_input("OuterTrackerBarrelCollection", args)
    return DDPlanarDigi(
        "OTBarrelDigitiser",
        # Raw hit times (ToF correction only in the window cut): the 4D seeding / CKF expects them.
        CorrectTimesForPropagation = False,
        CorrectTimeWindowForPropagation = True,
        IsStrip = False,
        ResolutionT = [0.06],
        ResolutionU = [0.007],
        ResolutionV = [0.09],
        SubDetectorName = "OuterTrackers",
        # From the --timing preset, together with the overlay window.
        TimeWindowMin = [TIMING_PRESETS[args.timing]["digitiser"]["outer"][0]],
        TimeWindowMax = [TIMING_PRESETS[args.timing]["digitiser"]["outer"][1]],
        UseTimeWindow = True,
        SimTrackHitCollectionName = inputHitCollections,
        SimTrkHitRelCollection = ["OTBarrelHitsRelations"],
        TrackerHitCollectionName = ["OTBarrelHits"],
        ForceHitsOntoSurface = True,
        OutputLevel = INFO
    )

def OTEndcap_cfg(args):
    """
    Create a new outer endcap digitiser instance with the given parameters.
    """
    inputHitCollections = overlay_input("OuterTrackerEndcapCollection", args)
    return DDPlanarDigi(
        "OTEndcapDigitiser",
        # Raw hit times (ToF correction only in the window cut): the 4D seeding / CKF expects them.
        CorrectTimesForPropagation = False,
        CorrectTimeWindowForPropagation = True,
        IsStrip = False,
        ResolutionT = [0.06],
        ResolutionU = [0.007],
        ResolutionV = [0.09],
        SubDetectorName = "OuterTrackers",
        # From the --timing preset, together with the overlay window.
        TimeWindowMin = [TIMING_PRESETS[args.timing]["digitiser"]["outer"][0]],
        TimeWindowMax = [TIMING_PRESETS[args.timing]["digitiser"]["outer"][1]],
        UseTimeWindow = True,
        SimTrackHitCollectionName = inputHitCollections,
        SimTrkHitRelCollection = ["OTEndcapHitsRelations"],
        TrackerHitCollectionName = ["OTEndcapHits"],
        ForceHitsOntoSurface = True,
        OutputLevel = INFO
    )
