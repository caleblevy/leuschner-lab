#!/usr/bin/env python
'''Script for quick modifications of data should something go wrong. '''
from Load_Data import Data_Generator, Save_Raw_Data
import numpy as np
import os

''' Do whatever  '''
for Data in Data_Generator('data-process'):
    print Data['Raw']
    del Data['Raw']['left_Ax']
    del Data['Raw']['right_Ax']
    Save_Raw_Data(Data)
''' Check whatever'''
for Data in Data_Generator('data-process'):
    print Data['Raw']