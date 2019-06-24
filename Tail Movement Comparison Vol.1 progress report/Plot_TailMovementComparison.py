import seaborn as sns
import matplotlib.pyplot as plt
from dt_tools_function_vol_1 import readallfiles,readcsv_outputdict,string2number_list,mouth_movement_value, rename_csv
import pandas as pd
import os

###Give the inputs
parameter = 'tailcurvature_distal30'
analysis = ['HeadFixedStrike','HeadFixedNonstrikePreycatpure','attack','sstrike','prey_capture','spontaneous']
analysis2 = []
output_disc = {}

big_list = []

input_folder = 'C:\DT files\Julie Semmelhack Lab\Code\Behavioral Analysis\Tail Movement Comparison\\results'
filenames = os.listdir(input_folder)
csvs = [filename for filename in filenames if os.path.splitext(filename)[1] == '.csv']

for csv in csvs:

    for type in analysis:
        if type in csv and '20190611_curvature' in csv:
            csv_file_dic = readcsv_outputdict(input_folder + '\\' + csv)  # put the csv into a dictionary
            output_disc[type] = csv_file_dic[parameter]
            big_list.append(csv_file_dic[parameter])
            print csv

    # for type in analysis2:
    #     if type in csv:
    #         csv_file_dic = readcsv_outputdict(input_folder + '\\' + csv)  # put the csv into a dictionary
    #         output_disc2[type] = csv_file_dic[parameter]
    #         big_list.append(csv_file_dic[parameter])


# attack_csv = inputfolder+'\\'+'attack_20190611.csv'
# Sstrike_csv = inputfolder+'\\'+'sstrike_20190611.csv'
#
# csv_file_dic = readcsv_outputdict(attack_csv)  # put the csv into a dictionary
# attack_tailvigour = csv_file_dic['tailvigour']
# attack_tailvigour = string2number_list(attack_tailvigour,'float')
# output_disc['attack_tailvigour'] = attack_tailvigour
#
# csv_file_dic = readcsv_outputdict(Sstrike_csv)  # put the csv into a dictionary
# Sstrike_tailvigour = csv_file_dic['tailvigour']
# Sstrike_tailvigour = string2number_list(Sstrike_tailvigour,'float')
# output_disc['Sstrike_tailvigour'] = Sstrike_tailvigour

tips = big_list
# tips = pd.DataFrame(output_disc, columns=analysis)
# tips2 = pd.DataFrame(output_disc2, columns=analysis2)
#print tips

# s = pd.Series(output_disc,index = analysis)
# print s

sns.set(style="whitegrid")
#tips = sns.load_dataset("tips")

ax = sns.boxplot(data=tips, showfliers = False)
ax = sns.swarmplot(data=tips, color=".25")

plt.title(parameter)
plt.show()