#!/usr/bin/env python
import numpy as np
import Plotting_Wrappers as wrap
from Pickle_Data import Save_Pickle, Data_Generator
import matplotlib.pyplot as plt
import cPickle as pkl
import pylab

# pylab.rcParams['xtick.major.pad']='8'
# pylab.rcParams['ytick.major.pad']='8'

with open('image-files/Excize_Point.pkl') as Excize_File:
    Excize = pkl.load(Excize_File)
    
Smooth = Excize['Smooth']
    
right_Ax = Smooth['right_Ax']
right = Smooth['right']

left_Ax = Smooth['left_Ax']
left = Smooth['left']

Excize_Plot = plt.figure()
ax1 = plt.gca()
ax1.plot(right_Ax,right/1.5, color='blue')
ax1.set_xlim([right_Ax[0], right_Ax[-1]])
ax1.tick_params(axis='x', colors='blue')
ax1.ticklabel_format(axis='x', style='plain', useOffset=False)
for tick in ax1.xaxis.get_major_ticks():
    tick.label.set_fontsize(14)
plt.xlabel('Frequencies (MHz)',fontsize=18)
ax1.set_yticklabels([])
plt.ylabel('Amplitude (Arbitrary Units)',fontsize=18)

ax2 = ax1.twiny()
ax2.plot(left_Ax,left, color='green')
ax2.set_xlim([left_Ax[0], left_Ax[-1]])
ax2.tick_params(axis='x', colors='green')
ax2.ticklabel_format(axis='x', style='plain', useOffset=False)
# ax2.set_xlabel(axis='x',labelpad=10)
for tick in ax2.xaxis.get_major_ticks():
    tick.label.set_fontsize(14)

r_low,r_high = Excize['right-spectrum-inds']
l_low,l_high = Excize['left-spectrum-inds']

plt.plot(left_Ax[r_low:r_high],left[r_low:r_high], color='purple', linewidth=2)
plt.plot(left_Ax[l_low:l_high],left[l_low:l_high], color='red', linewidth=2)

plt.plot(left_Ax[r_low:r_high],right[r_low:r_high]/1.5, color='purple', linewidth=2)
plt.plot(left_Ax[l_low:l_high],right[l_low:l_high]/1.5, color='red', linewidth=2)

# plt.title('Excized Regions', fontsize=20)
plt.savefig('image-files/Excized_Regions.pdf')


# plt.plot(right_Ax[l_low:l_high],right[l_low:l_high]*1.5, color='purple')
# ax2 = ax1.twiny()
# ax2.plot(left_Ax, left, color='green')
# 
#     
# Smooth = Excize['Smooth']
# Excize_Plot = plt.figure()
# ax1 = plt.gca()
# ax1.plot(Smooth['right_Ax'],Smooth['right']*1.5,color='blue')
# ax1.set_xlim([Smooth['left_Ax'][0], Smooth['left']], )
# ax2 = ax1.twiny()
# ax2.plot(Smooth['right_Ax'],Smooth['right'],color='green')
# 
# ax = plt.gca()
# ax.set_xlim([Smooth['left_Ax'][0], Smooth['left_Ax'][-1]])
# wrap.X_Label('Frequencies (MHz)',False)
# ax.tick_params(axis='x',colors='blue')
# ax.set_yticklabels([])
# wrap.Y_Label('Amplitudes (Arbitrary Units)')
# 
# ax2 = ax.twiny()




plt.show()