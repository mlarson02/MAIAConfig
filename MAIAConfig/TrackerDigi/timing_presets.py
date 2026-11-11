'''-------------------------------------------------------------'''
'''  Named tracker timing windows for digitisation              '''
'''-------------------------------------------------------------'''
# Picked with --timing on the digi command line (digi.submit TIMING), so the
# windows are fixed per job at submit time rather than read out of edited
# config files when the job starts.
#
# The windows [ns] are applied twice, and both must be set together:
#   overlay    OverlayTimingRandomMix keeps a signal or BIB SimTrackerHit only
#              if its time-of-flight-corrected time is inside this window;
#              everything else never reaches the digitiser.
#   digitiser  DDPlanarDigi then applies its own window (UseTimeWindow,
#              CorrectTimesForPropagation).
# The overlay window must enclose the digitiser window: widening only the
# digitiser accepts nothing new beyond the overlay window.
#
# Deliberately free of Gaudi imports, so digi.sh can check a name with plain
# python3 before it stages in the input.

TIMING_PRESETS = {
    "nominal": {
        "overlay":   {"vertex": [-0.18, 0.18], "inner": [-0.36, 0.36], "outer": [-0.36, 0.36]},
        "digitiser": {"vertex": [-0.09, 0.15], "inner": [-0.18, 0.30], "outer": [-0.18, 0.30]},
    },
    # "Loose" digitiser windows of the timing-criteria table; overlay keeps
    # the nominal lower edges and opens up to the digitiser upper edges.
    "loose": {
        "overlay":   {"vertex": [-0.18, 0.40], "inner": [-0.36, 2.20], "outer": [-0.36, 10.0]},
        "digitiser": {"vertex": [-0.09, 0.40], "inner": [-0.18, 2.20], "outer": [-0.18, 10.0]},
    },
    "extended": {
        "overlay":   {"vertex": [-0.5, 15.0], "inner": [-0.5, 15.0], "outer": [-0.5, 15.0]},
        "digitiser": {"vertex": [-0.5, 15.0], "inner": [-0.5, 15.0], "outer": [-0.5, 15.0]},
    },
}
