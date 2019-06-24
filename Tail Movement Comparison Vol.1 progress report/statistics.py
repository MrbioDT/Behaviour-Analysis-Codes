# Mann-Whitney_U_test
# Use only when the number of observation in each sample is > 20 and you have 2 independent samples of ranks. Mann-Whitney U is significant if the u-obtained is LESS THAN or equal to the critical value of U.
# This test corrects for ties and by default uses a continuity correction.

from scipy.stats import mannwhitneyu
import csv
from dt_tools_function_vol_1 import readallfiles,readcsv_outputdict,string2number_list,mouth_movement_value, rename_csv


inputfolder = 'C:\DT files\Julie Semmelhack Lab\Code\Behavioral Analysis\Tail Movement Comparison\\results'
attack_csv = inputfolder+'\\'+'3_attack_20190611.csv'
Sstrike_csv = inputfolder+'\\'+'4_sstrike_20190611.csv'
HeadFixedStrike_csv = inputfolder+'\\'+'1_HeadFixedStrike_20190611.csv'
HeadFixedNonstrikePreycatpure_csv = inputfolder+'\\'+'2_HeadFixedNonstrikePreycatpure_20190611.csv'


csv_file_dic = readcsv_outputdict(attack_csv)  # put the csv into a dictionary
attack_tailvigour = csv_file_dic['tailvigour60']
attack_tailvigour = string2number_list(attack_tailvigour,'float')

csv_file_dic = readcsv_outputdict(Sstrike_csv)  # put the csv into a dictionary
Sstrike_tailvigour = csv_file_dic['tailvigour60']
Sstrike_tailvigour = string2number_list(Sstrike_tailvigour,'float')

csv_file_dic = readcsv_outputdict(HeadFixedStrike_csv)  # put the csv into a dictionary
HeadFixedStrike_tailvigour = csv_file_dic['tailvigour60']
HeadFixedStrike_tailvigour = string2number_list(HeadFixedStrike_tailvigour,'float')

csv_file_dic = readcsv_outputdict(HeadFixedNonstrikePreycatpure_csv)  # put the csv into a dictionary
HeadFixedNonstrikePreycatpure_tailvigour = csv_file_dic['tailvigour60']
HeadFixedNonstrikePreycatpure_tailvigour = string2number_list(HeadFixedNonstrikePreycatpure_tailvigour,'float')

x = HeadFixedNonstrikePreycatpure_tailvigour
y = HeadFixedStrike_tailvigour

result = mannwhitneyu(x,y)
print result[1], 'h-nonstrike', 'h-strike'