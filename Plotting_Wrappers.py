#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np

def New_Plot(*args,**kwargs):
    Fig = plt.figure()
    plt.plot(*args,**kwargs)
    plt.axis("tight")        
    return Fig

'''Assume Plot is already around'''
def X_Label(Label,Sci=False):
    plt.xlabel(Label,fontsize=18)
    if Sci:
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))     
    ax = plt.gca()
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(12)
        
def Y_Label(Label,Sci=False):
    plt.ylabel(Label,fontsize=18)
    if Sci:
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))       
    ax = plt.gca()
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(12)
        
def Make_Title_Coords(Data):
    '''
    Make title out of l and b values
    '''
    l = Data['l']
    b = Data['b']
    Lon = r'$l=%s^\circ$'%str(l)[:3]
    Lat = r'$b=%s^\circ$'%str(b)[:3]
    Loc = Lat+' '+Lon
    return Loc
        
def Plot_Data(Data,Cal=False):
    """
    Plot Data['right'] and Data['left'], and if Cal=True, calibration data as well
    """
    Raw = Data['Raw']
    print Raw
    Smooth = Data['Smooth']
    coord = Make_Title_Coords(Data)
    Data['Raw']['left_Ax'] = np.linspace(1415.9,1427.9, 8192)
    # LO freq = 1271.9 MHz ----> centered on 1421.9 MHz, range (1415.9 to 1427.9)
    # LO freq = 1268.9 MHz ----> centered on 1418.9 MHz, range (1412.9 to 1424.9)
    
    New_Plot(Raw['left_Ax'],Raw['left'])
    X_Label('Frequency (Hz)')
    Y_Label('Amplitude (' + r'$100$' + 'K)')
    plt.title('Left-shifted raw spectral profile for '+coord,fontsize=20)
    plt.savefig('image-files/Raw_Plot.png')
    
    New_Plot(Smooth['left_Ax'],Smooth['left'])
    X_Label('Frequency (Hz)')
    Y_Label('Amplitude (' + r'$100$' + 'K)')
    plt.title('Left-shifted smoothed spectral profile for '+coord,fontsize=20)
    plt.savefig('image-files/Smoothed_Plot.png')
    
       #  
    # New_Plot(Raw['left_Ax'],Raw['left'])
    # X_Label('Frequency (Hz)')
    # Y_Label('Amplitude (' + r'$100$' + 'K)')
    # plt.title('Left-shifted raw spectral profile for '+coord,fontsize=20)
    # 
    # New_Plot(Smooth['left_Ax'],Smooth['left'])
    # X_Label('Frequency (Hz)')
    # Y_Label('Amplitude (' + r'$100$' + 'K)')
    # plt.title('Left-shifted smoothed spectral profile for '+coord,fontsize=20)
    # 
    # 