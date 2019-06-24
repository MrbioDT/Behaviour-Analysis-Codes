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


def HeadFixedStrike(input_folder,direction = 'down'):
    ### generate intermediate variable for processing
    tailfit_list = [] #each item contains tailfit of certain video from certain shv
    strike_frames_list = [] #each item contains strike_frames of certain video from certain csv

    ### read csvs and shvs and tailfit
    filenames = os.listdir(input_folder)
    shvs = [filename for filename in filenames if os.path.splitext(filename)[1] == '.shv']
    csvs = [filename for filename in filenames if os.path.splitext(filename)[1] == '.csv']

    for i in range(len(shvs)):
        csv_file_dic = readcsv_outputdict(input_folder + '\\' + csvs[i])  # put the csv into a dictionary
        final_strike = csv_file_dic['final_striking']

        # read final strike
        # string into number
        strike_frames = []  # a list contains all the striking frames in certain videos
        number = ''
        for item in final_strike[0]:
            try:
                n = int(item)
                number = number + item
            except:
                if item == ',' and number != '':
                    strike_frames.append(int(number))
                else:
                    number = ''

        t = shelve.open(input_folder + '\\' + shvs[i])
        for key in t.keys():  # There's only one key in each shv!
            t = t[key].tailfit  # (x,y), fitting tail point, frame

        tailfit_list.append(t)
        strike_frames_list.append(strike_frames)

    ### detect strike bouts
    strike_bout = []
    for i in range(len(tailfit_list)):
        angles = tail2angles(tailfit_list[i],direction=direction)
        boutedges, var = extractbouts(angles)

        for frame in strike_frames_list[i]:
            for bout in boutedges:
                if bout[0] <= frame <= bout[1]:
                    strike_bout.append(tailfit_list[i][bout[0]:bout[1]])
                    boutedges.remove(bout)
                    break

    print '++++++++++++++++'
    return strike_bout


def HeadFixedNonstrikePreycatpure(input_folder,direction = 'down'):
    ###Quite similar to HeadFixedStrike

    ### generate intermediate variable for processing
    tailfit_list = []  # each item contains tailfit of certain video from certain shv
    strike_frames_list = []  # each item contains strike_frames of certain video from certain csv
    convergence_list = []

    ### read csvs and shvs and tailfit
    filenames = os.listdir(input_folder)
    plot_filenames = os.listdir(input_folder+'\\plot')
    shvs = [filename for filename in filenames if os.path.splitext(filename)[1] == '.shv']
    csvs = [filename for filename in filenames if os.path.splitext(filename)[1] == '.csv']
    plot_csvs = [filename for filename in plot_filenames if os.path.splitext(filename)[1] == '.csv']


    for i in range(len(shvs)):
        csv_file_dic = readcsv_outputdict(input_folder + '\\' + csvs[i])  # put the csv into a dictionary
        final_strike = csv_file_dic['final_striking']

        plot_csv_file_dic = readcsv_outputdict(input_folder + '\\plot\\' + plot_csvs[i])  # put the csv into a dictionary
        convergence = plot_csv_file_dic['convergence']

        # read final strike
        # string into number
        strike_frames = []  # a list contains all the striking frames in certain videos
        number = ''
        for item in final_strike[0]:
            try:
                n = int(item)
                number = number + item
            except:
                if item == ',' and number != '':
                    strike_frames.append(int(number))
                else:
                    number = ''

        t = shelve.open(input_folder + '\\' + shvs[i])
        for key in t.keys():  # There's only one key in each shv!
            t = t[key].tailfit  # (x,y), fitting tail point, frame

        tailfit_list.append(t)
        strike_frames_list.append(strike_frames)
        convergence_list.append(convergence)

    ### detect strike bouts
    nonstrike_bout = []
    for i in range(len(tailfit_list)):
        angles = tail2angles(tailfit_list[i], direction=direction)
        boutedges, var = extractbouts(angles)

        for frame in strike_frames_list[i]:
            for bout in boutedges:
                if bout[0] <= frame <= bout[1]:
                    boutedges.remove(bout)

        for bout in boutedges:
            if convergence_list[i][bout[1]] >= 30 and convergence_list[i][bout[0]] >= 30:
                nonstrike_bout.append(tailfit_list[i][bout[0]:bout[1]])
    return nonstrike_bout

def tailamplitude_max_function(tailbout, direction = 'down'):
    tailamplitude_max= []

    for bout in tailbout:
        boutangle = tail2angles(bout, direction=direction)  # extract the tailfits of the bout frames

        if abs(max(boutangle)) <= abs(min(boutangle)):
            tailamplitude_max.append(abs(min(boutangle)))
        else:
            tailamplitude_max.append(abs(max(boutangle)))

    return tailamplitude_max

def tailvigour_function(tailbout, direction = 'down', time = 120, sampling_rate = 500):

    tailvigour = []

    for bout in tailbout:
        boutangle = tail2angles(bout, direction = direction)  # extract the tailfits of the bout frames
        velocity = np.diff(boutangle)

        vigour = 0
        for i in range(int(time/(1000/float(sampling_rate)))):
            try:
                vigour = vigour + abs(velocity[i])*float(1000/float(sampling_rate))
            except:
                print i,len(velocity)
                break
        tailvigour.append(vigour)

    return tailvigour

def tailfreq_mean_function(tailbout, direction = 'down', sampling_rate = 500):
    tailfreq_mean = []

    for bout in tailbout:
        nFrames = len(bout)
        Fs = 1 / float(sampling_rate)
        boutangle = tail2angles(bout, direction = direction)  # extract the tailfits of the bout frames
        peak = peakdetector.peakdetold(boutangle, 4) ### parameters!!!
        tailfreq_mean.append((len(peak[0])+len(peak[1])) / float((2*Fs * nFrames)))

    return tailfreq_mean

def detect_firstbeat(tailbout,direction=10,thresh=10):
    #detect the frame where the fish carry the first tail beat
    frame_list = []

    for bout in tailbout:
        frame = 0
        boutangle = tail2angles(bout, direction = direction)  # extract the tailfits of the bout frames
        peaks = peakdetector.peakdetold(boutangle, 4) ### parameters!!!

        for p in peaks[0]:
            if abs(p[1]) >= thresh:
                frame = p[0]
                break

        for p in peaks[1]:
            if abs(p[1]) >= thresh:
                if frame > p[0]:
                   frame = p[0]
                break

        frame_list.append(frame)

    return frame_list

def tailcurvature_proximal_function(tailbout,firstbeat_frame,direction='down'):

    tailcurvature_proximal = []

    for i in range(len(tailbout)):
        boutangle = tail2angles(tailbout[i], fraction= 0.6, direction=direction)  # extract the tailfits of the bout frames
        tailcurvature_proximal.append(abs(boutangle[firstbeat_frame[i]]))

    return tailcurvature_proximal

def tailcurvature_distal_function(tailbout,firstbeat_frame,direction='down'):
    tailcurvature_distal = []

    for i in range(len(tailbout)):
        boutangle = tail2angles(tailbout[i], direction=direction)  # extract the tailfits of the bout frames
        tailcurvature_distal.append(abs(boutangle[firstbeat_frame[i]]))

    return tailcurvature_distal

def tailcurvature_distal_function_new(tailbout,firstbeat_frame,direction='down'):
    tailcurvature_distal = []

    for i in range(len(tailbout)):
        boutangle = tail2angles(tailbout[i], direction=direction)  # extract the tailfits of the bout frames
        tailcurvature_distal.append(abs(boutangle[firstbeat_frame[i]]))

    return tailcurvature_distal