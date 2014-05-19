#!/usr/bin/env python
import cPickle as pkl
import numpy as np
import matplotlib.pyplot as plt
import Plotting_Wrappers as wrap

with open('image-files/data_l_212.00_b_004.00_grid_002_001_process.pkl') as f:
    Data = pkl.load(f)

print Data

wrap.Plot_Data(Data)
plt.show()