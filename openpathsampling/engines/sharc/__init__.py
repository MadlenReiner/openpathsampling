#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 10:24:54 2020

@author: Madlen Maria Reiner
"""

def missing_sharc():
    raise RuntimeError("Install SHARC to use this feature")
def requires_mdtraj():
    raise RuntimeError("This requires MDTraj, which is not installed")

import os
import sys

try:
    sys.path.insert(0, os.environ["SHARC"])
    import mdtraj
    # import SHARC_Analytical
    # not possible because it is Python 2
except KeyError:
    HAS_SHARC = False
    Engine = missing_sharc()
except ImportError:
    Engine = requires_mdtraj()
else:
    from openpathsampling.engines.sharc.engine import SharcEngine as Engine
    #from .engine import ExternalMDSnapshot
    from openpathsampling.engines.sharc import features
    from openpathsampling.engines.sharc.snapshot import SharcSnapshot

#from openpathsampling.engines import NoEngine, SnapshotDescriptor
