from GaudiKernel.Constants import INFO, WARNING
from Configurables import DDPlanarDigi
from Common.overlay_utils import overlay_input
from TrackerDigi.timing_presets import TIMING_PRESETS

def VXDBarrel_cfg(args):
    """
    Create a new vertex barrel instance with the given parameters.
    """
    inputHitCollections = overlay_input("VertexBarrelCollection", args)
    return DDPlanarDigi(
        "VXDBarrelDigitiser",
        # Raw hit times (ToF correction only in the window cut): the 4D seeding / CKF expects them.
        CorrectTimesForPropagation = False,
        CorrectTimeWindowForPropagation = True,
        IsStrip = False,
        ResolutionT = [0.03],
        ResolutionU = [0.005],
        ResolutionV = [0.005],
        SubDetectorName = "Vertex",
        # From the --timing preset, together with the overlay window.
        TimeWindowMin = [TIMING_PRESETS[args.timing]["digitiser"]["vertex"][0]],
        TimeWindowMax = [TIMING_PRESETS[args.timing]["digitiser"]["vertex"][1]],
        UseTimeWindow = True,
        SimTrackHitCollectionName = inputHitCollections,
        SimTrkHitRelCollection = ["VXDBarrelHitsRelations"],
        TrackerHitCollectionName = ["VXDBarrelHits"],
        ForceHitsOntoSurface = True,
        OutputLevel = INFO
    )

def VXDEndcap_cfg(args):
    """
    Create a new vertex endcap instance with the given parameters.
    """
    inputHitCollections = overlay_input("VertexEndcapCollection", args)
    return DDPlanarDigi(
        "VXDEndcapDigitiser",
        # Raw hit times (ToF correction only in the window cut): the 4D seeding / CKF expects them.
        CorrectTimesForPropagation = False,
        CorrectTimeWindowForPropagation = True,
        IsStrip = False,
        ResolutionT = [0.03],
        ResolutionU = [0.005],
        ResolutionV = [0.005],
        SubDetectorName = "Vertex",
        # From the --timing preset, together with the overlay window.
        TimeWindowMin = [TIMING_PRESETS[args.timing]["digitiser"]["vertex"][0]],
        TimeWindowMax = [TIMING_PRESETS[args.timing]["digitiser"]["vertex"][1]],
        UseTimeWindow = True,
        SimTrackHitCollectionName = inputHitCollections,
        SimTrkHitRelCollection = ["VXDEndcapHitsRelations"],
        TrackerHitCollectionName = ["VXDEndcapHits"],
        ForceHitsOntoSurface = True,
        OutputLevel = INFO
    )
