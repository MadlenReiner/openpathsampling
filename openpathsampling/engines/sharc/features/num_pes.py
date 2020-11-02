#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 14:16:31 2020

@author: reiner
"""

variables = ['num_pes']
numpy = ['num_pes']
#dimensions = [1,0]

def netcdfplus_init(store):
    store.create_variable(
        'num_pes', 'int',
        #dimensions=(1,0),
        description="num_pes of simulation"
        )

# @property
# def num_pes(snapshot):
#     return snapshot.num_pes