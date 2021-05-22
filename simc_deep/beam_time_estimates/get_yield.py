import math
from scipy import optimize
import LT.box as B
from LT.datafile import dfile
import numpy as np
import matplotlib.pyplot as plt
import numpy.ma as ma
import sys                                     
import os                                                                                                       
from sys import argv  
import matplotlib
from matplotlib import *
from mpl_toolkits.axes_grid1.inset_locator import (inset_axes, InsetPosition, mark_inset)

from matplotlib import rc
rc('text', usetex=True)
plt.rcParams["font.family"] = "Times New Roman"


def MC_study(thrq=0, pm_set=0, model='fsi', rad='rad', Ib=1, time=1, clr='k',rel_err_flg=0, MC_evt='200k', pm_off=0):

    # This function (MC_study) is specific to studying how the Monte Carlo (MC) statistics affects
    # the cross sections and respective errors. The more MC statistics, the smaller the variation in xsec error
    # such that if the MC --> infinity counts, xsec err -> 0 . Another point to make is that, given the same MC
    # statistics, for different charge factors (i.e., beam time, beam current), the relative xsec error remains
    # the same. This shows that the MC xsec (and its rel. error) are independent of the charge factor, which clearly
    # means that this error is not a true representation of the actual statistical error from a real experiment, but
    # is actually the MC statistics error. To calculate/estimate the 'true' experimental statistical error on the cross
    # section, one has to count the total number of weighted counts per bin, say in missing momentum Pm, then the absolute
    # statistical unc. is ~ sqrt(N) and relative stats unc. is rel_err_stats ~ 1 / sqrt(N).
    # Therefore, ideally one should reduce the MC statistics as much as possible so that it does not contribute to the
    # determination of the statistical error based on the charge factor.
    
    fname = '%s_evts/xsec_pm%d_model%s_%s_%.1fuA_%.1fhr.txt' % (MC_evt, pm_set, model, rad, Ib, time)
    fname_stats = '%s_evts/stats_pm%d_model%s_%s_%.1fuA_%.1fhr.txt' % (MC_evt, pm_set, model, rad, Ib, time)

    
    f = dfile(fname)
    fstats = dfile(fname_stats)

    #read xsec data file
    th_rq = np.array(f['x0'])
    pm    = (np.array(f['y0']))[th_rq==thrq]
    xsec  = (np.array(f['zcont']))[th_rq==thrq]
    xsec_err_MC = (np.array(f['zcont_err']))[th_rq==thrq]  # absolute MC stats error    
    rel_err_MC = (xsec_err_MC / xsec) * 100.  # realtive MC stats error [%]

    #read yield data file to get stats uncertainty based on counts
    pm_cnts = (np.array(fstats['zcont']))[th_rq==thrq]  # weighted counts
    rel_err_stats = 1. / np.sqrt(pm_cnts)      #relative statistical error  sqrt(N)/N = d_xsec/xsec  
    xsec_err_stats = xsec * rel_err_stats      #absolute statistical error on xsec
    print('rel_err_MC = ',rel_err_MC)
    print('rel_err_stats = ',rel_err_stats*100.)
    
    if(rel_err_flg==0):
        return plt.errorbar(pm+pm_off, xsec, xsec_err_MC, color=clr, linestyle='none', marker='o', label=r'MC evts = %s, $I_{beam}$=%.1f $\mu A$, time=%.1f hr'%(MC_evt,Ib,time))
    elif(rel_err_flg==1):
        return plt.errorbar(pm+pm_off, np.repeat(0, len(pm)), rel_err_MC, color=clr, linestyle='none', marker='o', label=r'MC evts = %s, $I_{beam}$=%.1f $\mu A$, time=%.1f hr'%(MC_evt,Ib,time))
    elif(rel_err_flg==2):
        return plt.errorbar(pm+pm_off, np.repeat(0, len(pm)), rel_err_stats*100, color=clr, linestyle='none', marker='o', label=r'MC evts = %s, $I_{beam}$=%.1f $\mu A$, time=%.1f hr'%(MC_evt,Ib,time))



    
def plot_yield(thrq=0, pm_set=0, model='fsi', rad='rad', Ib=1, time=1, scl_factor=1, clr='b',rel_err_flg=False):

    #User Inputs:
    # scl_factor: factor to scale beam time, assuming the time is 1 hr. e.g., to scale counts by 5 hrs, then scl_factor = 5

    fname = 'yield_pm%d_model%s_%s_%.1fuA_%.1fhr.txt' % (pm_set, model, rad, Ib, time)

    f = dfile(fname)

    #read xsec data file
    th_rq = np.array(f['x0'])
    pm    = (np.array(f['y0']))[th_rq==thrq]
    pm_bins = max(np.array(f['yb']))  #max number of pm bins
    pm_min = min(np.array(f['ylow'])[th_rq==thrq])
    pm_max = max(np.array(f['yup'])[th_rq==thrq])
    
    pm_cnts  = (np.array(f['zcont']))[th_rq==thrq] * scl_factor  # pm bin content
    MC_err = (np.array(f['zcont_err']))[th_rq==thrq] * scl_factor  #absolute error of weighted counts (MC statistics error, NOT the exp. statistical error)   
    stats_err = np.sqrt(pm_cnts) #absolute statistical errors
    print('pm = ', len(pm))
    print('pm_bins = ', pm_bins)
    print('weight = ', len(pm_cnts))
    print('pm_min = ', pm_min)
    print('pm_max = ', pm_max)
    #rel_stats_err = 1. / np.sqrt(pm_cnts) #relative statistical error
    rel_stats_err = np.divide(1, stats_err, out=np.full_like(stats_err, np.nan), where=stats_err!=0) 
    rel_stats_err_m = ma.masked_where(np.isnan(rel_stats_err), rel_stats_err)
    pm_m = ma.masked_where(np.isnan(rel_stats_err), pm)
    #print('rel_stats_err = ', rel_stats_err*100)
    rel_stats_err_m = rel_stats_err_m * 100
    #plt.hist(pm, pm_bins, weights=pm_cnts, edgecolor='k', color=clr, range=[pm_min,pm_max], alpha = 0.2)
    print(rel_stats_err_m)
    if(rel_err_flg):
        plt.ylim(-50,50)
        plt.xlim(0,1.2)

        return plt.errorbar(pm_m, np.repeat(0, len(pm)), rel_stats_err_m, color=clr, linestyle='none', marker='o', label = r'$I_{beam}$=%.1f $\mu A$, time=%.1f hr'%(Ib, scl_factor))
    else:
        return plt.errorbar(pm, pm_cnts, yerr=stats_err, linestyle='none', marker='o', color='k', markersize=3)
    

def main():
    print('Plotting xec')


    #---Study the Dependence of the MC Error on MC events----
    '''
    plt.subplots(3,1, figsize=(5,10))
    
    plt.suptitle(r'Hall C SIMC Monte Carlo Statistics Study', fontsize=18)
    
    plt.subplot(3,1,1)
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, clr='g', rel_err_flg=0, MC_evt='200k')
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, clr='b', rel_err_flg=0, MC_evt='1M', pm_off=0.005)
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, clr='r', rel_err_flg=0, MC_evt='5M', pm_off=0.01)
    plt.ylabel(r'Cross Section $\sigma$ (arb. units)', fontsize=12)
    plt.yscale('log')
    plt.legend(fontsize=12)

    plt.subplot(3,1,2)
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, clr='g', rel_err_flg=1, MC_evt='200k')
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, clr='b', rel_err_flg=1, MC_evt='1M', pm_off=0.005)
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, clr='r', rel_err_flg=1, MC_evt='5M', pm_off=0.01)
    plt.ylabel(r'MC Relative Error d$\sigma$ / $\sigma$ (\%)', fontsize=12)
    plt.ylim(-50,50)
    plt.legend(fontsize=12)

    plt.subplot(3,1,3)
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, clr='g', rel_err_flg=2, MC_evt='200k')
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, clr='b', rel_err_flg=2, MC_evt='1M', pm_off=0.005)
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, clr='r', rel_err_flg=2, MC_evt='5M', pm_off=0.01)
    plt.ylabel(r'Stat. Relative Error $\sqrt{N}$ / N (\%)', fontsize=12)
    plt.ylim(-50,50)
    plt.xlabel(r'Missing Momentum, $P_{m}$ (GeV/c)', fontsize=12)
    plt.legend(fontsize=12)
    
    plt.subplots_adjust(top=0.95)
    plt.show()
    

    #---Study the Dependence of the Stats Error on Beam Time----
    
    plt.subplots(2,1, figsize=(5,7))
    
    plt.suptitle(r'Hall C SIMC Monte Carlo Statistics Dependence on Charge Factor', fontsize=18)

    plt.subplot(2,1,1)
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, clr='g', rel_err_flg=1, MC_evt='5M')
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=5, clr='b', rel_err_flg=1, MC_evt='5M', pm_off=0.005)
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=10, clr='r', rel_err_flg=1, MC_evt='5M', pm_off=0.01)
    plt.ylabel(r'MC Relative Error d$\sigma$ / $\sigma$ (\%)', fontsize=12)
    plt.ylim(-50,50)
    plt.legend(fontsize=12)

    plt.subplot(2,1,2)
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, clr='g', rel_err_flg=2, MC_evt='5M')
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=5, clr='b', rel_err_flg=2, MC_evt='5M', pm_off=0.005)
    MC_study(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=10, clr='r', rel_err_flg=2, MC_evt='5M', pm_off=0.01)
    plt.ylabel(r'Stat. Relative Error $\sqrt{N}$ / N (\%)', fontsize=12)
    plt.ylim(-50,50)
    plt.xlabel(r'Missing Momentum, $P_{m}$ (GeV/c)', fontsize=12)
    plt.legend(fontsize=12)
    
    plt.subplots_adjust(top=0.95)
    plt.show()            
    '''

    
    plot_yield(thrq=35, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, scl_factor=1, clr='b',rel_err_flg=True)
    plt.show()
    
if __name__ == "__main__":
    main()

