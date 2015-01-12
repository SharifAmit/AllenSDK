import numpy as np
#import matplotlib.pyplot as plt
import neuron
from os import remove
import json
import copy

class GLIFExperiment( object ):
    FIT_PARAMETERS = ["coeff_th", "coeff_C", "coeff_G", "coeff_a", "coeff_b", "coeff_a_vector"]

    #If I need to get stuff from the top level script into the run functions add 
    #a thing here and remember to set it in the initialization
    def __init__(self, neuron, dt, stim_list, grid_spike_index_target_list, grid_spike_time_target_list, 
                 interpolated_spike_time_target_list, init_voltage, init_threshold, init_AScurrents, 
                 target_spike_mask, fit_names_list,
                 **kwargs):

        self.neuron = neuron
        self.dt = dt
        self.stim_list = stim_list
        self.grid_spike_index_target_list = grid_spike_index_target_list
        self.grid_spike_time_target_list = grid_spike_time_target_list
        self.interpolated_spike_time_target_list = interpolated_spike_time_target_list
        self.init_voltage = init_voltage
        self.init_threshold = init_threshold
        self.init_AScurrents = init_AScurrents
        self.target_spike_mask = target_spike_mask
        self.fit_names_list = fit_names_list
        
    def run(self, param_guess):
        '''This code will run the loaded neuron model in reference to the target neuron spikes.
        inputs:
            self: is the instance of the neuron model and parameters alone with the values of the target spikes.
                NOTE the values in each array of the self.gridSpikeIndexTarge_list and the self.interpolated_spike_time_target_list
                are in reference to the time start of of the stim in each induvidual array (not the universal time)
            param_guess: array of scalars of the values that will be inserted into the mapping function below.
        returns:
            voltage_list: list of array of voltage values. NOTE: IF THE MODEL NEURON SPIKES BEFORE THE TARGET THE VOLTAGE WILL 
                NOT BE CALCULATED THEREFORE THE RESULTING VECTOR WILL NOT BE AS LONG AS THE TARGET AND ALSO WILL NOT 
                MAKE SENSE WITH THE STIMULUS UNLEtarget_spike_maskSS YOU CUT IT AND OUTPUT IT TOO.
            gridTime_list:
            interpolatedTime_list: an array of the actual times of the spikes. NOTE: THESE TIMES ARE CALCULATED BY ADDING THE 
                TIME OF THE INDIVIDUAL SPIKE TO THE TIME OF THE LAST SPIKE.
            gridISIFromLastTargSpike_list: list of arrays of spike times of the model in reference to the last target (biological) 
                spike (not in reference to sweep start)
            interpolatedISIFromLastTargSpike_list: list of arrays of spike times of the model in reference to the last target (biological) 
                spike (not in reference to sweep start)
            voltageOfModelAtGridBioSpike_list: list of arrays of scalars that contain the voltage of the model neuron when the target or bio neuron spikes.    
            theshOfModelAtGridBioSpike_list: list of arrays of scalars that contain the threshold of the model neuron when the target or bio neuron spikes.'''

        #TODO: hmm should this really be here
        stim_list = self.stim_list
        grid_spike_index_target_list = self.grid_spike_index_target_list
        
        self.set_neuron_parameters(param_guess)    
        
#        print 'self.neuron.coeff_G', self.neuron.coeff_G
#        print 'self.neuron.coeff_a_vector', self.neuron.coeff_a_vector
        interpolatedTime_list = []
        voltage_list = []   
        threshold_list=[]   
        gridISIFromLastTargSpike_list=[]
        interpolatedISIFromLastTargSpike_list=[]      
        gridTime_list=[]                                                   
        voltageOfModelAtGridBioSpike_list=[] 
        theshOfModelAtGridBioSpike_list=[]
        AScurrentMatrix_list=[]
        voltageOfModelAtInterpolatedBioSpike_list=[]
        thresholdOfModelAtInterpolatedBioSpike_list=[]
 
 #TODO:  FIGURE OUT THE ASCURRENTS LIST VERUS MATRIX       
        for stim_list_index in range(0,len(stim_list)):
            (voltage, threshold, AScurrentMatrix, gridTime, interpolatedTime, gridISIFromLastTargSpike, interpolatedISIFromLastTargSpike, 
             voltageOfModelAtGridBioSpike_array, theshOfModelAtGridBioSpike_array, 
             voltageOfModelAtInterpolatedTargSpike_array, thresholdOfModelAtInterpolatedTargSpike_array) =  self.neuron.run_wrt_target_spike_train(
                 self.init_voltage, self.init_threshold, self.init_AScurrents, 
                 stim_list[stim_list_index], grid_spike_index_target_list[stim_list_index], 
                 self.target_spike_mask[stim_list_index], self.interpolated_spike_time_target_list[stim_list_index])
            
            interpolatedTime_list.append(interpolatedTime) 
            # changed this 5-13 refactor as TRD error function does not need to know universal time. interpolatedTime_list.append(interpolatedTime+len(stim_list[stim_list_index])*self.neuron.dt*stim_list_index) #putting things in reference to a master time
            voltage_list.append(voltage)
            threshold_list.append(threshold)
            gridTime_list.append(gridTime)
            gridISIFromLastTargSpike_list.append(gridISIFromLastTargSpike)
            interpolatedISIFromLastTargSpike_list.append(interpolatedISIFromLastTargSpike)
            voltageOfModelAtGridBioSpike_list.append(voltageOfModelAtGridBioSpike_array)
            theshOfModelAtGridBioSpike_list.append(theshOfModelAtGridBioSpike_array)
            voltageOfModelAtInterpolatedBioSpike_list.append(voltageOfModelAtInterpolatedTargSpike_array)
            thresholdOfModelAtInterpolatedBioSpike_list.append(thresholdOfModelAtInterpolatedTargSpike_array)
            AScurrentMatrix_list.append(AScurrentMatrix)
            
        return voltage_list, threshold_list, AScurrentMatrix_list, gridTime_list, interpolatedTime_list, gridISIFromLastTargSpike_list, interpolatedISIFromLastTargSpike_list, voltageOfModelAtGridBioSpike_list, theshOfModelAtGridBioSpike_list, voltageOfModelAtInterpolatedBioSpike_list, thresholdOfModelAtInterpolatedBioSpike_list  #TODO: eventually run should return all variables

    def run_base_model(self, param_guess):
        '''This code will run the loaded neuron model.
        inputs:
            self: is the instance of the neuron model and parameters alone with the values of the target spikes.
                NOTE the values in each array of the self.gridSpikeIndexTarge_list and the self.interpolated_spike_time_target_list
                are in reference to the time start of of the stim in each induvidual array (not the universal time)
            param_guess: array of scalars of the values that will be inserted into the mapping function below.
        returns:
            voltage_list: list of array of voltage values. NOTE: IF THE MODEL NEURON SPIKES BEFORE THE TARGET THE VOLTAGE WILL 
                NOT BE CALCULATED THEREFORE THE RESULTING VECTOR WILL NOT BE AS LONG AS THE TARGET AND ALSO WILL NOT 
                MAKE SENSE WITH THE STIMULUS UNLEtarget_spike_maskSS YOU CUT IT AND OUTPUT IT TOO.
            gridTime_list:
            interpolatedTime_list: an array of the actual times of the spikes. NOTE: THESE TIMES ARE CALCULATED BY ADDING THE 
                TIME OF THE INDIVIDUAL SPIKE TO THE TIME OF THE LAST SPIKE.
            gridISIFromLastTargSpike_list: list of arrays of spike times of the model in reference to the last target (biological) 
                spike (not in reference to sweep start)
            interpolatedISIFromLastTargSpike_list: list of arrays of spike times of the model in reference to the last target (biological) 
                spike (not in reference to sweep start)
            voltageOfModelAtGridBioSpike_list: list of arrays of scalars that contain the voltage of the model neuron when the target or bio neuron spikes.    
            theshOfModelAtGridBioSpike_list: list of arrays of scalars that contain the threshold of the model neuron when the target or bio neuron spikes.'''

        
        stim_list = self.stim_list
        
        self.set_neuron_parameters(param_guess)    
        
        voltage_list = []   
        threshold_list = []   
        AScurrentMatrix_list = []
        gridSpikeTime_list = []
        interpolatedSpikeTime_list = []
        gridSpikeIndex_list = []
        interpolatedSpikeVoltage_list = []
        interpolatedSpikeThreshold_list = []

        for stim_list_index in xrange(len(stim_list)):
            (voltage, threshold, AScurrentMatrix, gridSpikeTime, interpolatedSpikeTime, 
             gridSpikeIndex, interpolatedSpikeVoltage, interpolatedSpikeThreshold) = self.neuron.run(
                 self.init_voltage, self.init_threshold, self.init_AScurrents, stim_list[stim_list_index])

            voltage_list.append(voltage)
            threshold_list.append(threshold)
            AScurrentMatrix_list.append(AScurrentMatrix)
            gridSpikeTime_list.append(gridSpikeTime)
            interpolatedSpikeTime_list.append(interpolatedSpikeTime)
            gridSpikeIndex_list.append(gridSpikeIndex) 
            interpolatedSpikeVoltage_list.append(interpolatedSpikeVoltage)
            interpolatedSpikeThreshold_list.append(interpolatedSpikeVoltage)

          
        return voltage_list, threshold_list, AScurrentMatrix_list, gridSpikeTime_list, interpolatedSpikeTime_list, \
            gridSpikeIndex_list, interpolatedSpikeVoltage_list, interpolatedSpikeThreshold_list

    def set_neuron_parameters(self, param_guess): 
        '''Maps the parameter guesses to the attributes of the model.  
        input:
            param_guess is vector of values.  It is assumed that the length will be '''

        if any([param not in GLIFExperiment.FIT_PARAMETERS for param in self.fit_names_list]):
            raise Exception('you are trying to fit a variable that is not allowed')

        index = 0
        for fit_name in self.fit_names_list:
            a = getattr(self.neuron, fit_name)

            # is it a list?
            if hasattr(a, "__len__"):
                a_size = len(a)
                setattr(self.neuron, fit_name, param_guess[index:index+a_size])
                index += a_size
            else:
                setattr(self.neuron, fit_name, param_guess[index])
                index += 1

