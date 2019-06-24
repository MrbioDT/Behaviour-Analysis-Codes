import os
import csv
import peakdetector
from matplotlib import pyplot as plt



def readallfiles(filetype, folder):
    # function: read all the file in the folder and stores the filename into a list as strings
    # filetype should be a string specify the type of files eg. '.csv'
    # folder is the folder(full directory) that contains the files to read
    # return of this function is a list, that each item is the string of corresponding files(only the filenames)

    filenames = os.listdir(folder)
    files = [filename for filename in filenames if os.path.splitext(filename)[1] == filetype]

    return files

def readcsv_outputdict(filelocation):
    # fuction: read the single one csv files and output the content in directionary
    # filelocation should be a string contains the folder+'\\'+filename
    # output a directionary that contains all the content, each pair is each row, key is the heading(1st row/string), value is a list of rest

    csv_dic = {} # storing all the content of this csv
    with open(filelocation) as f:
        f_csv = csv.reader(f)
        headers = next(f_csv) # a list, each item string

        # filling the keys
        for head in headers:
            csv_dic[head] = []

        # filling the values to each keys
        for row in f_csv:
            i = 0
            for head in headers:
                csv_dic[head].append(row[i])
                i += 1

    return csv_dic

def rename_csv(first_x,folder):
    # function: rename all the csv files in the folder and shorten the filename based on first x character
    # first_x should be an interger specify first x character
    # folder should be the folder that contains the files
    # Note. rely on the funtcion readallfiles

    csv_list = readallfiles('.csv',folder)
    for csv_file in csv_list:
        print csv_file
        first_x_c = csv_file[:first_x]
        os.rename(folder + '\\' + csv_file, folder + '\\' + first_x_c + '.csv')
    return 0

def string2number_list(old_list,type):
    # convert a string list into a number list
    new_list = []
    if type == 'float':
        for item in old_list:
            new_list.append(float(item))
    elif type == 'int':
        for item in old_list:
            new_list.append(int(item))
    return new_list

def mouth_movement_value(data_list, frame, time_window, logic = 'mouth', t_sb_slider = 10):
    # calculate the value in specific time windoes based on the frame and requirement
    # data_list is a list of value
    # frame is the specific frame
    # time_window is the frame range before and after the frame, has to be even
    # logic means processing either mouth_cr or sb_cr data, which has slightly different in algorithm

    if logic == 'mouth':
        ### new way to calcualte the value
        value = max(data_list[frame-time_window/2:frame])-min(data_list[frame:frame+time_window/2])
        plt.subplot(2,1,1)
        plt.title('mouth_cr')
        plt.plot(frame,max(data_list[frame-time_window/2:frame]),'ro')
        plt.plot(frame,min(data_list[frame:frame+time_window/2]),'ro')
        return value

        # Logic. directly get it from a very small time windows

        ### old way for calculating the value
        # peakind = peakdetector.peakdetold(new_list,0.5)  # Parameters! the second number is the threshold, it compares the peaks with neighbor value
        # # Parameters! Trying to use a very small delta here! Notice the delta for mouth and swim bladder are different!!!
        # p_p = peakind[0]  # positive peaks
        # n_p = peakind[1]  # negative peaks
        #
        # value = 0
        # for pp in p_p:
        #     for np in n_p:
        #         if 0< np[0]-pp[0] <30: #positive peak has to be before negative peak and within 30 frames #Parameters!!! should be more strict!
        #             temp_value = pp[1]-np[1]
        #             value = max(temp_value, value)

    if logic == 'swimbladder':

        new_list = data_list[frame - time_window / 2:frame + time_window / 2]  # Task... there could be problems here...

        peakind = peakdetector.peakdetold(new_list,0.1)  # Parameter! the second number is the threshold, it compares the peaks with neighbor value
        # Parameters! Trying to use a very small delta here! Notice the delta for mouth and swimbladder are different!!!
        p_p = peakind[0]  # positive peaks
        n_p = peakind[1]  # negative peaks

        value = 0
        condition = False
        for np in n_p:
            for pp in p_p:
                if 0< pp[0]-np[0] <t_sb_slider: #positive peak has to be after negative peak and within 30 frames
                    temp_value = pp[1]-np[1]
                    if temp_value > value:
                       value = temp_value
                       npeak = np[0]
                       ppeak = pp[0]
        return value



if __name__ == '__main__':

    rename_csv(35,'D:\\temp')
