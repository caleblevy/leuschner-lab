#!/usr/bin/env python
import cPickle as pkl
with open('data-process/data_l_001.52_b_030.00_grid_015_008_process.pkl') as f:
    data = pkl.load(f)
    
print data
print
for I,J in enumerate(data['Raw']['left_Ax']):
    print I,'   ',J
    
for I,J in enumerate(data['Raw']['right_Ax']):
    print I,'   ',J
