#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from Pickle_Data import Save_Pickle, Data_Generator
from scipy.signal import fftconvolve
import Plotting_Wrappers as wrap
import cPickle as pkl
import pylab

CONVOLVE = False

def Generate_Image_Grid():
    '''
    Instantiates the existing keys of the iamge grid and makes arrays from the data.
    '''
    Image_Grid = {} # Final grid for the North Polar Spur
    Image_Grid['l'] = []
    Image_Grid['b'] = []
    Image_Grid['col-density'] = []
    Image_Grid['vel-center'] = []
    Image_Grid['dispersion'] = []
    
    for Data in Data_Generator(Save_Dir='data-image',Data_Dir='data-image'):
        for key in Image_Grid:
            Image_Grid[key].append(Data[key])
            
    for key in Image_Grid:
        Image_Grid[key] = np.array(Image_Grid[key])
    
    print 'Number of points: ',len(Image_Grid['l'])
        
    return Image_Grid

def Spherical_to_Cartesian(r,theta, phi):
    '''
    Project theta and phi from coordinates of points on the unit sphere into
    cartesian coordinates using the Wikipedia convention.
    '''
    x = r * np.cos(theta) * np.sin(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(phi)
    return x, y, z
    
def Add_Cartesian_Coordinates(Image_Grid):
    '''
    Get the cartesian projection of our grid onto the Earth. 
    
    l = longitude = theta
    b = lattitude = phi
    '''
    l = np.radians(Image_Grid['l'])
    b = np.radians(Image_Grid['b'])
    x,y,z = Spherical_to_Cartesian(1., l, b)
    Image_Grid['x'] = x
    Image_Grid['y'] = y
    
def Generate_Data_Grid(l_vals, b_vals, data_vals):
    '''
    Give me an image grid, and I give you a sparse array of Karto's specified
    size with the nonzero points being the image/velocity pixels.
    '''
    zero_pos = (850, 0)
    data_weights = np.zeros([1701, 901])
    data_grid = np.zeros([1701, 901])
    cell_size = 0.1 # radians? Degrees?
    
    for idx in range(len(l_vals)):
        b_val = b_vals[idx]
        l_val = l_vals[idx]
        if l_val < 180:
            del_l = ((l_val + 360) - 295)*np.cos(np.radians(b_val))
        else:
            del_l = (l_val - 295)*np.cos(np.radians(b_val))
        x_pos = round(del_l/cell_size + zero_pos[0])
        y_pos = round(b_val/cell_size + zero_pos[1])
        
        data_grid[x_pos, y_pos] += data_vals[idx]
        data_weights[x_pos, y_pos] += 1
    
    return data_grid, data_weights
    
def Make_Gaussian_Grid(data_grid, gaussian_radius=4., m=1000,n=1000):
    '''
    Convolve data grid with a Gaussian; m and n are default size of grid, sigma
    is size of scale height in degrees. Project/excise grid directly to obtain
    scale height.
    '''
    l_width = 380-220
    b_width = 90-0
    num_l, num_b = data_grid.shape
    l_grid, b_grid = np.mgrid[0:m, 0:n]
    # Treat as integers
    l_grid -= m/2
    b_grid -= n/2
    sigma_l = (gaussian_radius/l_width)*num_l
    sigma_b = (gaussian_radius/b_width)*num_b
    Gaussian_Filter = np.exp(-(l_grid/sigma_l)**2 -(b_grid/sigma_b)**2)
    return Gaussian_Filter

def Add_Background_Grid(Image_Grid):
    '''
    Create basic image grid to stay sane and orgamanized!
    '''
    l_vals = Image_Grid['l']
    b_vals = Image_Grid['b']
    Image_Grid['col-grid'], Image_Grid['weights-grid'] = Generate_Data_Grid(l_vals,b_vals, Image_Grid['col-density'])
    Image_Grid['vel-grid'], Image_Grid['weights-grid'] = Generate_Data_Grid(l_vals,b_vals, Image_Grid['vel-center'])
    Image_Grid['disp-grid'], Image_Grid['weights-grid'] = Generate_Data_Grid(l_vals,b_vals, Image_Grid['dispersion'])
    
    Image_Grid['Gaussian'] = Make_Gaussian_Grid(Image_Grid['vel-grid'])
    

def Make_Convolved_Grids(Image_Grid):
    '''
    Just go through the mechanical motions to make the dang convolvatated grids.
    '''
    Gaussian = Image_Grid['Gaussian']
    
    Grids = ['col-grid', 'vel-grid', 'disp-grid', 'weights-grid']
    for item in Grids:
        item_conv = item[:-4]+'conv'
        Image_Grid[item_conv] = fftconvolve(Image_Grid[item],Gaussian,mode='same')

def Save_Image_Grid(Image_Grid):
    with open('/Users/caleblevy/galaxy-lab/langley/Image_Grid.pkl','w') as Image_File:
        pkl.dump(Image_Grid,Image_File)            
    
def Load_Image_Grid():
    with open('/Users/caleblevy/galaxy-lab/langley/Image_Grid.pkl') as Image_File:
        Image_Grid = pkl.load(Image_File)
    return Image_Grid
    
def Prepare_Plotting_Grids(Image_Grid):
    Data_Sets = ['vel-conv', 'col-conv', 'disp-conv']
    zero_inds = np.where(Image_Grid['weights-conv'] < 0.001)
    Image_Grid['weights-conv'][zero_inds] = 1.
    for item in Data_Sets:
        Image_Grid[item][zero_inds] = 50.
        Image_Grid[item[:-5]+'-image'] = np.flipud((Image_Grid[item]/Image_Grid['weights-conv']).T)
        
def Tick_Maker(fig):
    plt.figure(fig.number)
    ax = plt.gca()
    b_labels = [item.get_text() for item in ax.get_yticklabels()]
    b_vals = np.linspace(0,90, len(b_labels))
    for ind,val in enumerate(b_vals):
        b_labels[ind] = str(val)
        print b_labels[ind]
    ax.set_yticklabels(b_labels)
    
    
    # l_labels = np.concatenate([np.linspace(220,340, 7), np.linspace(0,20,2)])
    # l_labels = [str(round(lab)) for lab in l_labels]    
    l_labels = [item.get_text() for item in ax.get_xticklabels()]
    l_vals = np.linspace(210, 380, len(l_labels))
    l_vals[-1] = 20
    for ind,val in enumerate(l_vals):
        l_labels[ind] = str(val)
    
    ax.set_xticklabels(l_labels)
    
    
        
def Plot_Images(Image_Grid):
    Images = ['vel-image', 'col-image', 'disp-image']
    
    I = 0
    for image in Images:
        fig = plt.figure()
        im = plt.imshow(Image_Grid[image],aspect='auto')
        im.set_extent([0,1,0,1])
        
        Tick_Maker(fig)    
        im.set_extent([0,1,0,1])
        wrap.X_Label('Longitude (Degrees)')
        wrap.Y_Label('Latitude (Degrees)')
        if I == 0:
            plt.title('Velocity (km/sec)',fontsize=20)
        elif I == 1:
            plt.title('Column Density '+r'(cm$^{-2}$)',fontsize=20)
        elif I == 2:
            plt.title('Velocity Dispersion (km/sec)',fontsize=20)
        I += 1
        
        plt.set_cmap('pink')
        plt.colorbar()
        plt.savefig('image-files/'+image+'.pdf')

        
        
    
        
        
    # print 'inds: ',np.where(Image_Grid['vel-weights-conv'] < 0.001)

    # Image_Grid['vel-conv'][zero_inds] = 0.
    # Image_Grid['vel-weights-conv'][zero_inds] = 1.
    # Image_Grid['Vel_Image'] = np.flipud((Image_Grid['vel-conv']/Image_Grid['vel-weights-conv']).T)
    # 
    # plt.imshow(Image_Grid['Vel_Image'])
    # plt.set_cmap('pink')
    # plt.colorbar()
    # plt.show()

    
if __name__ == '__main__':
    if CONVOLVE:
        Image_Grid = Generate_Image_Grid()
        Add_Background_Grid(Image_Grid)
        Make_Convolved_Grids(Image_Grid)
        Save_Image_Grid(Image_Grid)
    else:
        Image_Grid = Load_Image_Grid()
        Prepare_Plotting_Grids(Image_Grid)
        for key in Image_Grid:
            print key,': ',Image_Grid[key]
            print
        Plot_Images(Image_Grid)