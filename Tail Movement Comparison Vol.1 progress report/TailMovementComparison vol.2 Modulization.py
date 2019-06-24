# This version is the modulization version for both shv and Duncan's data

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import shelve
import os
from framemetrics import *
import peakdetector
from bouts import *
from dt_tools_function_vol_1 import readallfiles,readcsv_outputdict,string2number_list,mouth_movement_value, rename_csv
from TailMovementComparison_functions import HeadFixedStrike,HeadFixedNonstrikePreycatpure,tailamplitude_max_function,tailvigour_function,tailfreq_mean_function,detect_firstbeat,tailcurvature_distal_function,tailcurvature_proximal_function

if __name__ == "__main__":

    ### INPUT SESSION ###
    bout_type = 'HeadFixedNonstrikePreycatpure' #
    input_folder = 'C:\DT files\Julie Semmelhack Lab\Code\Behavioral Analysis\Tail Movement Comparison\Head-fixed strike'
    #input_folder = 'C:\DT files\Julie Semmelhack Lab\Code\Behavioral Analysis\Tail Movement Comparison\Duncan_data'
    direction = 'down'
    sampling_rate = 300 #300Hz for DT's data, 500Hz for Duncan's data
    analysis = ['tailamplitude_max','tailvigour','tailfreq_mean','tailcurvature_distal','tailcurvature_proximal','tailvigour60','tailvigour_alltrial','tailcurvature_distal30']

    ### PART-1. PROCESS RAW INPUTS INTO LIST
    if bout_type == 'HeadFixedStrike':
        # shv and csv of same video should be put into the same folder, with same name
        tailbout = HeadFixedStrike(input_folder, direction=direction)
    elif bout_type == 'HeadFixedNonstrikePreycatpure':
        tailbout = HeadFixedNonstrikePreycatpure(input_folder,direction)
    else:
        tail_points = np.load('C:\DT files\Julie Semmelhack Lab\Code\Behavioral Analysis\Tail Movement Comparison\Duncan_data\\'+ bout_type + '_points.npy')  # file containing tail points for each bout
        indexer = np.load('C:\DT files\Julie Semmelhack Lab\Code\Behavioral Analysis\Tail Movement Comparison\Duncan_data\\'+ bout_type + '_indexer.npy')  # file containing indices of the first and last frames for each bout
        tailbout = []
        for i, j in zip(indexer, indexer[1:]):
            tailbout.append(tail_points[i:j])

    ### PART-2 parameters calculation!
    output_disc = {}

    if 'tailcurvature_distal' in analysis:
        firstbeat_frame = detect_firstbeat(tailbout, direction=direction, thresh = 10)
        print firstbeat_frame

        tailcurvature_distal = []
        for i in range(len(tailbout)):
            tailcurvature_distal.append(abs(tail2sumangles(tailbout[i],direction=direction)[firstbeat_frame[i]]))
        output_disc['tailcurvature_distal'] = tailcurvature_distal

    if 'tailcurvature_distal30' in analysis:
        firstbeat_frame = detect_firstbeat(tailbout, direction=direction, thresh = 10)
        print firstbeat_frame

        tailcurvature_distal30 = []
        for i in range(len(tailbout)):
            tailcurvature_distal30.append(abs(tail2sumangles_distal30(tailbout[i],direction=direction)[firstbeat_frame[i]]))
        output_disc['tailcurvature_distal30'] = tailcurvature_distal30

    if 'tailcurvature_proximal' in analysis:
        firstbeat_frame = detect_firstbeat(tailbout, direction=direction, thresh = 10)
        tailcurvature_proximal = []

        for i in range(len(tailbout)):
            tailcurvature_proximal.append(abs(tail2sumangles_proximal(tailbout[i],direction=direction)[firstbeat_frame[i]]))

        output_disc['tailcurvature_proximal'] = tailcurvature_proximal

    # old version for back-up
    # if 'tailcurvature_distal' in analysis:
    #     firstbeat_frame = detect_firstbeat(tailbout, direction=direction, thresh = 10)
    #     tailcurvature_distal = tailcurvature_distal_function(tailbout, firstbeat_frame, direction=direction)
    #     output_disc['tailcurvature_distal'] = tailcurvature_distal
    #
    # if 'tailcurvature_proximal' in analysis:
    #     firstbeat_frame = detect_firstbeat(tailbout, direction=direction, thresh = 10)
    #     tailcurvature_proximal = tailcurvature_proximal_function(tailbout, firstbeat_frame, direction=direction)
    #     output_disc['tailcurvature_proximal'] = tailcurvature_proximal

    if 'tailamplitude_max' in analysis:
        tailamplitude_max = tailamplitude_max_function(tailbout,direction=direction)
        output_disc['tailamplitude_max'] = tailamplitude_max

    if 'tailvigour' in analysis:
        tailvigour = tailvigour_function(tailbout,direction=direction,time=120,sampling_rate=sampling_rate)
        output_disc['tailvigour'] = tailvigour

    if 'tailvigour60' in analysis:
        tailvigour60 = tailvigour_function(tailbout,direction=direction,time=60,sampling_rate=sampling_rate)
        output_disc['tailvigour60'] = tailvigour60

    if 'tailvigour_alltrial' in analysis:
        tailvigour_alltrial = tailvigour_function(tailbout,direction=direction,time=10000,sampling_rate=sampling_rate)
        output_disc['tailvigour_alltrial'] = tailvigour_alltrial

    if 'tailfreq_mean' in analysis:
        tailfreq_mean = tailfreq_mean_function(tailbout,direction=direction,sampling_rate=sampling_rate)
        output_disc['tailfreq_mean'] = tailfreq_mean

    data = pd.DataFrame(output_disc,index=range(0, len(tailamplitude_max)),columns=analysis)
    csv_name = bout_type + '_20190611_curvature.csv'
    output_path = os.path.join('results\\'+csv_name)
    data.to_csv(output_path)

    # for bout in tailbout:
    #     nFrames = len(bout)
    #     Fs = 1 / float(500)  ### parameters!!! 500 for duncan, 300 for dt
    #     boutangle = tail2angles(bout, direction = direction)  # extract the tailfits of the bout frames
    #     velocity = np.diff(boutangle)
    #     peak = peakdetector.peakdetold(boutangle, 4) ### parameters!!!
    #     tailfreq_mean.append((len(peak[0])+len(peak[1])) / float((2*Fs * nFrames)))
    #
    #     tailfreq_mean = [];
    #     tailamplitude_mean = [];
    #     tailamplitude_max = [];
    #     boutduration = [];
    #     tailasymmetry = [];
    #     tailvigour = [];
    #
    #     p = 0; n = 0
    #     for angle in boutangle:
    #         if angle >= 0:
    #             p += 1
    #         else:
    #             n += 1
    #
    #     if abs(max(boutangle))<= abs(min(boutangle)):
    #         tailamplitude_max.append(abs(min(boutangle)))
    #     else:
    #         tailamplitude_max.append(abs(max(boutangle)))
    #
    #     tailamplitude_mean.append(sum(boutangle)/float(len(boutangle)))
    #     tailfreq_mean.append((len(peak[0])+len(peak[1])) / float((2*Fs * nFrames)))
    #     boutduration.append(float((Fs * nFrames)))
    #     tailasymmetry.append(p/float(n+p))  ### Question. maybe want to refine this?
    #
    #     time = 120
    #     vigour = 0
    #     for i in range(int(time/(1000/500))):
    #         try:
    #             vigour = vigour + abs(velocity[i])*2
    #         except:
    #             print i,len(velocity)
    #             break
    #
    #     tailvigour.append(vigour)
    #
    #     # # plot and validation session
    #     # plt.plot(boutangle)
    #     # for p in peak[1]:
    #     #     plt.plot(p[0],p[1],'ro')
    #     # for p in peak[0]:
    #     #     plt.plot(p[0],p[1],'ro')
    #     # plt.show()
    #     # plt.plot(velocity)
    #     # plt.show()

