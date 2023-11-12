import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

# Brief: script that loops over numerical histo files
# in a specified directory, and  makes and saves the plots

def make_plots(pm_user, thrq_user, model):
    
    # pm_user   : central missing momentum setting (e.g. 500)
    # thrq_user :  central recoil angle (e.g. 28)
    # model     : Laget 'pwia' or 'fsi' 
    
    histos_file_path = 'yield_estimates/d2_fsi/histogram_data/pm%d_thrq%d_%s/' % (pm_user, thrq_user, model)
    
    for fname in os.listdir( histos_file_path ):

        hist_file = histos_file_path + fname

        df = pd.read_csv(hist_file, comment='#')

        print('Opening file -----> ', hist_file)
        # check if histo is 2D
        if "_vs_" or  "2Davg" in hist_file:
            
            xbins = len(df.xb[df.yb==df.yb[0]])
            ybins = len(df.yb[df.xb==df.xb[0]])
            zcont = np.array(df.zcont)
            counts =  np.sum(df.zcont)
            #if counts==0: break
            #xlabel = (((find('xlabel', fname)).split(':')[1]).strip()).replace('#', '\\')
            
            #hist2d = plt.hist2d(df.x0 ,df.y0, bins=xbins, ybins, weights=zcont, cmap = 'viridis', norm=LogNorm(), label='$Q^{2}=%s$ \n $P_{m}$=%s' % (jq2, ipm))
            hist2d = plt.hist2d(df.x0 ,df.y0, bins=(xbins, ybins), weights=zcont, cmap = 'viridis', norm=LogNorm() )
            plt.text(0.67*(df.x0[df.y0==df.y0[0]]).max(), 0.8*(df.y0[df.x0==df.x0[0]]).max(), '$\theta_{rq}=%d$ deg \n $P_{m}$=%d MeV \n (counts = %d)' % (thrq_user, pm_user, counts), fontsize=10)
            
            plt.colorbar()
            plt.show()
            
        # 2D averages are for projections
        #elif "2Davg" in hist_file: 

        # plot 1D histo, otherwise
        elif "_vs_" not in hist_file:
            # make plot of 1D histogram
            counts =  np.sum(df.ycont)
            #if counts==0: break
            #df.x0, df.ycont, np.sqrt(df.ycont)
            plt.hist(df.x0, bins=len(df.xb), weights=df.ycont, alpha=0.2, density=False, label='$\theta_{rq}=%d$ deg \n $P_{m}$=%d MeV \n (counts = %d)' % (thrq_user, pm_user, counts) )
            #plt.plot([1,2,3], [1,2,3], linestyle='None', mec='k', markersize=20, label=r'$Q^{2}=%s$, $P_{m}$=%s' % (jq2, ipm))
            plt.xlabel(r'x-label [units]')
            plt.ylabel(r'y-label [units]')
            plt.legend(frameon=False)
            plt.show()

            
make_plots(500, 70, 'pwia')
