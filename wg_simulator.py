# -*- coding: utf-8 -*-
"""
Created on Mon Feb 01 20:49:48 2016
@author: Devin
"""
import sys
if ~(r'F:\Documents\Yale\Junior Year\HFSSpython\pyHFSS' in sys.path):
    sys.path.append(r'F:\Documents\Yale\Junior Year\HFSSpython\pyHFSS')
import hfss, numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import pandas as pd

class simulated_wg(object):
    def __init__(self):
        prefix = "../data/parameters"
        name = prefix + "capacitance" + ".npy"
        self.capacitance = np.load(name)
        name = prefix + "voltage" + ".npy"
        self.voltage = np.load(name)
        name = prefix + "inductance" + ".npy"
        self.inductance = np.load(name)
        name = prefix + "current" + ".npy"
        self.current = np.load(name)
        name = "../data/parametersangles.npy"
        self.angles = np.load(name)
        name = "../data/parameterseigenmodes.npy"
        self.eigenmodes = np.load(name)
    
    def build_L_mat(self):
        smooth_l = interpolate_outliers(self.angles, self.inductance)   
        smooth_l = interpolate_outliers(self.angles, smooth_l,plot_me = True) 
        size = len(smooth_l)
        self.L = np.zeros((size,size))
        d_l = 5.89*.001*2*np.pi/100
        for i in range(size):
            self.L[i][i] += (d_l*smooth_l[i])**-1
            self.L[(i+1)%size][i] += -(d_l*smooth_l[i])**-1
            self.L[i][(i+1)%size] += -(d_l*smooth_l[i])**-1
            self.L[(i+1)%size][(i+1)%size] += (d_l*smooth_l[i])**-1

    def build_C_mat(self):
        smooth_c = interpolate_outliers(self.angles, self.capacitance)
        smooth_c = interpolate_outliers(self.angles, smooth_c,plot_me = True)
        size = len(smooth_c)
        self.C = np.zeros((size,size))
        d_l = 5.89*.001*2*np.pi/100
        for i in range(size):
            self.C[i][i] += (d_l*smooth_c[i])
            self.C[(i+1)%size][i] += -(d_l*smooth_c[i])
            self.C[i][(i+1)%size] += -(d_l*smooth_c[i])
            self.C[(i+1)%size][(i+1)%size] += (d_l*smooth_c[i])
            
    def build_L_mat_test(self):
        smooth_l = interpolate_outliers(self.angles, self.inductance)   
        size = len(smooth_l)
        self.L = np.zeros((size,size))
        d_l = 5.89*.001*2*np.pi/100
        for i in range(size):
            self.L[i][i] += (d_l*5*10**(-8))**-1
            self.L[(i+1)%size][i] += -(d_l*5*10**(-8))**-1
            self.L[i][(i+1)%size] += -(d_l*5*10**(-8))**-1
            self.L[(i+1)%size][(i+1)%size] += (d_l*5*10**(-8))**-1
        print "L:", self.L

    def build_C_mat_test(self):
        smooth_c = interpolate_outliers(self.angles, self.capacitance)
        size = len(smooth_c)
        self.C = np.zeros((size,size))
        d_l = 5.89*.001*2*np.pi/100
        for i in range(size):
            self.C[i][i] += (d_l*2.3*10**(-10))
            self.C[(i+1)%size][i] += -(d_l*2.3*10**(-10))
            self.C[i][(i+1)%size] += -(d_l*2.3*10**(-10))
            self.C[(i+1)%size][(i+1)%size] += (d_l*2.3*10**(-10))
        print "C:", self.C

    def test_interpolate(self,plot_me = True):
        potted = self.inductance
        voltage = interpolate_outliers(self.angles,potted, plot_me = plot_me)
        plt.plot(self.angles,voltage, self.angles, potted)
        ax = plt.gca()
        ax.set_ylim(min(voltage)/1.05, max(voltage)*1.05)
        plt.show()
        
    def get_frequencies(self):
        LC = np.dot(self.L,np.linalg.inv(self.C))
        print "LC"        
        print LC
        self.evals = -np.linalg.eigvals(LC)
        self.calc_freq = np.sqrt(self.evals)/(2*np.pi)
        plt.figure()
        plt.plot(np.sort(self.calc_freq))
        plt.show()
        print np.sort(self.calc_freq)

def interpolate_outliers(angle, data, threshold=1., window = 12, plot_me = False):
    '''
    Function to smooth outliers from the data set. Applys moving
    average smoothing and cyclic boundary conditions. Threshold
    is set by:
    threshold - number of standard deviations from average which defines outliers
    window - number of points in each direction used for average
    '''
    df = pd.DataFrame({'parameter':data},index=angle)
    #mean_data = np.mean(df['parameter'])
    df['data_mean'] = pd.rolling_median(df['parameter'].copy(), window=window, center=True).fillna(method='bfill').fillna(method='ffill')
    difference = np.abs(df['parameter'] - df['data_mean'])#mean_data)#
    outlier_idx = difference > threshold*df['parameter'].std()    
    #df['data_mean'].plot()
#    s = df['parameter'].copy()
#    s[outlier_idx] = np.nan
#    s.interpolate(method='spline', order=1, inplace=True)
#    df['cleaned_parameter'] = s
    tst = np.array(outlier_idx)
    datamean= np.array(df['data_mean'])
    s = np.array(df['parameter'])
    itms = len(outlier_idx)
    for i in range(itms):
        if tst[i] == True or tst[(i-1)%itms] == True or tst[(i+1)%itms] == True or tst[(i-2)%itms] == True or tst[(i+2)%itms] == True:
            tmp =  datamean[i]
            s[i] = tmp
    #print s
    df['cleaned_parameter'] = s
    
    if (plot_me == True):
        figsize = (7, 2.75)
        fig, ax = plt.subplots(figsize=figsize)
        df['parameter'].plot()
        df['cleaned_parameter'].plot()
        ax.set_ylim(min(df['cleaned_parameter']), max(df['cleaned_parameter']))
    return np.array(df['cleaned_parameter'])


        
def main():
    sim_wg = simulated_wg()
    #sim_wg.test_interpolate()
    sim_wg.build_L_mat_test()
    sim_wg.build_C_mat_test()
    sim_wg.get_frequencies()
    
    
if __name__ == "__main__":
    main()            