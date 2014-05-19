def Bad_Convolve_Grid(data_grid, gauss_radius=20):
    l_width = 380-220
    b_width = 90-0
    l_gridnum, b_gridnum = data_grid.shape
    l_Gaussnum = round((2.*l_gridnum/l_width)*gauss_radius)
    b_Gaussnum = round((2.*b_gridnum/b_width)*gauss_radius)
   
    sigma = gauss_radius/2.
    l_grid, b_grid = np.mgrid[-gauss_radius:gauss_radius:1j*l_width/2, \
                             -gauss_radius:gauss_radius:1j*b_width/2]

    Gaussian_Filter = np.exp(-1.*((l_grid/sigma)**2+(b_grid/sigma)**2))
    Filtered_Data = ndimage.filters.convolve(data_grid, \
                           Gaussian_Filter, mode='constant')
    
    print 'Gaussian_Filter: ',Gaussian_Filter.shape
    print 'Gaussian_Filter: ',Gaussian_Filter
    print Gaussian_Filter
    return Filtered_Data

    
def Convolve_Grid(data_grid, gaussian_radius=1./2):
    '''
    Convolve data_grid and data_weights with a Gaussian radius 4 deg and
    characteristic decay 2 deg
    '''
    n_u, n_v = data_grid.shape
    u_grid, v_grid = np.mgrid[0:n_u, 0:n_v]
    u_grid -= (n_u-1)/2
    b_grid -= (n_v-1)/2
    
    sigma_u = u_grid[-1]/gaussian_radius
    sigma_v = v_grid[-1]/gaussian_radius
    Gaussian_Filter = np.exp(-(u_grid/sigma_u)**2 - (b_grid/sigma_v)**2)
    

    
    # print u_grid
    # l_Gaussnum = round(2*(1.*l_gridnum/l_width)*gauss_radius)
 #    b_Gaussnum = round(2*(1.*b_gridnum/b_width)*gauss_radius)
 #    
 #    sigma = gauss_radius/2.
 #    l_grid, b_grid = np.mgrid[-gauss_radius:gauss_radius:1j*l_Gaussnum, \
 #                              -gauss_radius:gauss_radius:1j*b_Gaussnum]
 # 
 #    Gaussian_Filter = np.exp(-1.*((l_grid/sigma)**2+(b_grid/sigma)**2))
 #    Filtered_Data = ndimage.filters.convolve(data_grid, \
 #                            Gaussian_Filter, mode='constant')
    # return Filtered_Data    
    
def Good_Convolve(data_grid, sigma=2.):
    '''
    sigma in degrees
    '''
    l_width = 380-220
    b_width = 90-0
    
    frac = 8
    
    n_l, n_b = data_grid.shape
    l_grid, b_grid = np.mgrid[-(n_l-1)/frac:(n_l-1)/frac, -(n_b-1)/frac:(n_b-1)/frac]
    # print l_grid
    # print (n_l-1)/4
    
    
    sigma_l = sigma/l_width*(n_l-1)/4
    sigma_b = sigma/b_width*(n_b-1)/4
    Gaussian_Kernel = np.exp(-(l_grid/sigma_l)**2 -(b_grid/sigma_b)**2 )
    Filtered_Data = ndimage.filters.convolve(data_grid, \
                           Gaussian_Kernel, mode='constant')
    
    
        
    
    
    
def Plot_The_Grid(Image_Grid):
    fig = plt.figure()
    plt.plot(Image_Grid['l'],Image_Grid['b'],'ro')
    plt.show()
    plt.spy(data_weights.T, markersize=5)
    plt.show()
