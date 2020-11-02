try:
    import simtk.openmm
    import simtk.openmm.app
except ImportError:
    pass
else:
    from openpathsampling.engines.features import *
    from openpathsampling.engines.features.shared import StaticContainer, KineticContainer
    from openpathsampling.engines.sharc.features import masses
    from openpathsampling.engines.sharc.features import instantaneous_temperature
    from openpathsampling.engines.sharc.features import traj_quantities
    from openpathsampling.engines.sharc.features import num_pes
    from openpathsampling.engines.sharc.features import tmax
