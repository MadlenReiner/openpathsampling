#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 14:21:30 2020

@author: reiner
"""


variables = ['tmax']
numpy = ['tmax']
#dimensions = [1,0]

def netcdfplus_init(store):
    store.create_variable(
        'tmax', 'numpy.float32',
        #dimensions=(1,0),
        description="tmax of simulation"
        )

@property
def t_max(snapshot):
    return snapshot.tmax