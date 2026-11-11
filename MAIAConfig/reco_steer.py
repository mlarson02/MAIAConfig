'''-------------------------------------------------------------'''
''' Reconstruction Steering File for the Muon Collider Detector '''
'''-------------------------------------------------------------'''
import os, sys
# Make this directory importable so the domain-folder modules (Tracking/,
# ParticleFlow/, ...) and the Common/ helpers resolve regardless of PYTHONPATH.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reco_args import get_reco_args
from recoAlgList import makeRecoAlgList
from Common.steering import build_application, drop_calorimeter_hits, drop_tracker_hits, drop_overlay_sim_hits

# Collect arguments and build the reconstruction algorithm list
args = get_reco_args()
algList = makeRecoAlgList(args)

# Read the digitisation output, write the reconstruction output
app = build_application(
    args, algList,
    #input_files = ["/ospool/uc-shared/project/futurecolliders/larsonma/muon_pT0_50GeV_theta10_170/digi_NoBIB_uncone/muon_pT0_50GeV_theta10_170_digi.edm4hep.root"],
    input_files = ["/ospool/uc-shared/project/futurecolliders/larsonma/muon_0_50GeV_theta10_170_d0PCA_300_10kEv_gen/digi_NoBIB_coned_extended_timing_rawtime/muon_0_50GeV_theta10_170_d0PCA_300_10kEv_gen_digi.edm4hep.root"],
    output_file = "muon_0_50GeV_theta10_170_d0_dz_0_300_NoBIB_ITOTDisks_OutIn_d0_300_CR_500_reco.edm4hep.root",
    histo_file = "reco_histograms.root",
)

# With BIB, the tracker hits are kept (coned or not: the hit-level tracking
# studies need them) and the calorimeter hits are dropped, as they are the
# bulk of the event and unused here. Coned runs also drop the overlaid sim
# hits and the uncone hit links (see drop_overlay_sim_hits). --dropTrackerHits
# / --keepCaloHits flip either half; --keepEverything writes the full event.
overlay_on = args.doOverlayIP or args.doOverlayFull
keep_tracker_hits = args.keepEverything or not args.dropTrackerHits
keep_calo_hits = args.keepEverything or args.keepCaloHits
drop_overlay = overlay_on and args.doTrackerConing and not args.keepEverything

if overlay_on and not keep_tracker_hits:
    drop_tracker_hits()
if overlay_on and not keep_calo_hits:
    drop_calorimeter_hits()
if drop_overlay:
    drop_overlay_sim_hits()

# Recorded in the job log: which hit collections a given output does and does
# not contain is otherwise only discoverable by opening the file.
print(f"[reco_steer] overlay={'on' if overlay_on else 'off'} "
      f"coning={'on' if args.doTrackerConing else 'off'} -> "
      f"tracker hits {'KEPT' if (keep_tracker_hits or not overlay_on) else 'DROPPED'}, "
      f"overlay sim hits + uncone hit links {'DROPPED' if drop_overlay else 'KEPT'}, "
      f"calorimeter hits {'KEPT' if (keep_calo_hits or not overlay_on) else 'DROPPED'}")

# Per-algorithm timing via the Gaudi Auditor Service; the ChronoStatSvc table
# is printed to stdout (the job log) at finalize. User time is CPU summed over
# all threads, so with the tracking's internal TBB threads (--TrackingThreads)
# it exceeds the run time: elapsed time is the wall-clock one. Global message
# level raised to INFO not to be suppressed by the WARNING default.
from GaudiKernel.Constants import INFO
from Configurables import AuditorSvc, ChronoStatSvc
app.OutputLevel = INFO
app.AuditAlgorithms = True
app.ExtSvc += [
    AuditorSvc("AuditorSvc", Auditors = ["ChronoAuditor"]),
    ChronoStatSvc(
        PrintUserTime = True,
        PrintSystemTime = True,
        PrintEllapsedTime = True,
    ),
]
