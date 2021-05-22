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



    
def plot_yield(thrq=0, pm_set=0, model='fsi', rad='rad', Ib=1, time=1, scl_factor=1, clr='b',rel_err_flg=False, pm_off=0):

    # Brief: this function reads a .txt file with the 2D bin information of the th_rq vs Pm histogram yield, and plots the yield and relative error.
    
    # User Inputs:
    # thrq : recoil angle central value (can be looked up in the .txt file
    # pm_set: central missing momentum setting (this is based on the .txt file name (e.g., 120, 700, 800, 900)
    # model : deuteron cross section model ("fsi" or "pwia" based on the .txt file name
    # rad: with radiative effects ("rad") or without ("norad"), based on the .txt file name
    # Ib: beam current (uA) based on the .txt file name
    # time: beam-on-target time (hrs) based on the .txt file name
    # scl_factor: factor to scale beam time, **NOTE** : this scale factor assumes the time is 1 hr. e.g., to scale counts by 5 hrs, then scl_factor = 5
    # clr: data point color
    # rel_err_flg: flag to determine whether to plot relative errors or not (if false, will plot missing momentum for the given th_rq bin)
    # pm_off : missing momentum offset (a few MeV), to slightly offset (by ~MeV/c) the overlappong relative error data points and make it easier to compare

    
    fname = 'yield_pm%d_model%s_%s_%.1fuA_%.1fhr.txt' % (pm_set, model, rad, Ib, time)

    f = dfile(fname)

    #read yield data file
    th_rq = np.array(f['x0'])
    pm    = (np.array(f['y0']))[th_rq==thrq]
    pm_bins = max(np.array(f['yb']))  #max number of pm bins
    pm_min = min(np.array(f['ylow'])[th_rq==thrq])
    pm_max = max(np.array(f['yup'])[th_rq==thrq])
    pm_cnts  = (np.array(f['zcont']))[th_rq==thrq] * scl_factor  # pm bin content
    MC_err = (np.array(f['zcont_err']))[th_rq==thrq] * scl_factor  #absolute error of weighted counts (MC statistics error, NOT the exp. statistical error)   
    stats_err = np.sqrt(pm_cnts) #absolute statistical errors

    #rel_stats_err = 1. / np.sqrt(pm_cnts) #relative statistical error
    rel_stats_err = np.divide(1, stats_err, out=np.full_like(stats_err, 0), where=stats_err!=0)    

    #mask the values if relative statistical error = 0 or > 50 % 
    rel_stats_err_m = ma.masked_where((rel_stats_err == 0) | (rel_stats_err > 0.5), rel_stats_err)
    pm_m = ma.masked_where((rel_stats_err == 0) | (rel_stats_err > 0.5), pm)

    pm_cnts_m = np.where(rel_stats_err_m.mask, 0, pm_cnts)

    #pm_cnts_m =  ma.masked_where((rel_stats_err == 0) | (rel_stats_err > 0.5), pm_cnts)
    rel_stats_err_m = rel_stats_err_m * 100
    
    print(rel_stats_err_m)
    if(rel_err_flg):
        plt.ylim(-50,80)
        plt.xlim(pm_min,pm_max)
        return plt.errorbar(pm_m+pm_off, np.repeat(0, len(pm)), rel_stats_err_m, color=clr, linestyle='none', marker='o', alpha = 0.4, label = r'%d MeV/c, $I_{\textrm{beam}}$=%.1f $\mu A$, time=%.1f hr'%(pm_set, Ib, scl_factor))
    else:
        plt.ylim(1e-3,1e5)
        plt.hist(pm_m, pm_bins, weights=pm_cnts, edgecolor='k', color=clr, range=[pm_min,pm_max], alpha = 0.1)
        plt.xlim(pm_min,pm_max)
        plt.yscale('log')
        return plt.errorbar(pm_m, pm_cnts_m, yerr=stats_err, linestyle='none', marker='o', color=clr, ecolor=clr, alpha = 0.4, markersize=3, label = r'%d MeV/c, $I_{\textrm{beam}}$=%.1f $\mu A$, time=%.1f hr'%(pm_set, Ib, scl_factor))
    

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

    
    #-------- Plot Yield and Relative Errors for Beam Time Estimates ---------

    #Make subplots
    plt.subplots(2,1, figsize=(5,10))

    #adjust margin spacing 
    plt.subplots_adjust(top=0.95)

    plt.suptitle(r'Relative Statistical Errors, $\theta_{nq}=45\pm5^{\circ}$', fontsize=18)
    
    plt.subplot(2,1,1)
    plot_yield(thrq=45, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, scl_factor=1, clr='m',rel_err_flg=False)
    plot_yield(thrq=45, pm_set=700, model='fsi', rad='rad', Ib=40, time=1, scl_factor=45, clr='b',rel_err_flg=False)
    plot_yield(thrq=45, pm_set=800, model='fsi', rad='rad', Ib=40, time=1, scl_factor=102, clr='g',rel_err_flg=False)
    plot_yield(thrq=45, pm_set=900, model='fsi', rad='rad', Ib=40, time=1, scl_factor=204, clr='r',rel_err_flg=False)

    
    plt.ylabel(r'Yield', fontsize=12)

    plt.legend(fontsize=12, loc='upper right')

    plt.subplot(2,1,2)
    plot_yield(thrq=45, pm_set=120, model='fsi', rad='rad', Ib=40, time=1, scl_factor=1, clr='m',rel_err_flg=True)
    plot_yield(thrq=45, pm_set=700, model='fsi', rad='rad', Ib=40, time=1, scl_factor=45, clr='b',rel_err_flg=True)
    plot_yield(thrq=45, pm_set=800, model='fsi', rad='rad', Ib=40, time=1, scl_factor=102, clr='g',rel_err_flg=True, pm_off=0.005)
    plot_yield(thrq=45, pm_set=900, model='fsi', rad='rad', Ib=40, time=1, scl_factor=204, clr='r',rel_err_flg=True, pm_off=0.01)


    plt.ylabel(r'Stat. Relative Error $\sqrt{N}$ / N (\%)', fontsize=12)
    plt.xlabel(r'Missing Momentum, $P_{m}$ (GeV/c)', fontsize=12)

    plt.legend(fontsize=12)
    
    plt.show()
    
if __name__ == "__main__":
    main()

