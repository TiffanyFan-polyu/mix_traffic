import os
import sys

from pdb import set_trace
import random
from collections import defaultdict
import copy
import numpy as np
from matplotlib import pyplot as plt
import time
import pandas as pd
from enum import Enum
from sumolib import checkBinary
import traci



def get_recording_duration():
    recordingMeta=pd.read_csv('../data/39_recordingMeta.csv')
    duration_set=recordingMeta['duration (s)'].values
    return duration_set


def get_flow(i):

    # store the track Id of car using trackMeta file
    dataMeta=pd.read_csv('../data/%s_tracksMeta.csv' % i)
    # filtered_data = dataMeta[dataMeta["class"] == "car"]
    # track_id_set = filtered_data["trackId"].values
    track_id_set = dataMeta["trackId"].values


    #read 39_tracks.csv
    dataset = pd.read_csv('../data/%s_tracks.csv' % i)
    #init_time = dataset.Global_Time.min()

    mainInner_vehicles_ = []
    mainOuter_vehicles_ = []
    ramp_vehicles_ = []
    other_route=[]

    #id_sets = set(dataset.trackId.values)

    for ID in track_id_set:
        one_id_vehicles = dataset[dataset.trackId == ID]
        one_id_vehicles = one_id_vehicles.sort_values(by='frame', ascending=True)

        if one_id_vehicles.laneletId.values[0] in ['1488', '1492', '1498', '1501', '1504', '1508']:
            mainInner_vehicles_.append(one_id_vehicles)
        elif one_id_vehicles.laneletId.values[0] in ['1489', '1493', '1499', '1502', '1574', '1509','1574;1567']:
            mainOuter_vehicles_.append(one_id_vehicles)
        elif one_id_vehicles.laneletId.values[0] in ['1494', '1495','1496', '1500', '1503', '1566']:
            ramp_vehicles_.append(one_id_vehicles)
        else:
            other_route.append(one_id_vehicles)

    return len(mainInner_vehicles_), len(mainOuter_vehicles_), len(ramp_vehicles_)



pene_cav=0.1
pene_hdv=1-pene_cav

with open('scene/veh.rou.xml', 'w') as fType:
    pass  # Simply doing nothing to clear the file content

fType = open('scene/veh.rou.xml', 'a')
fType.write('<routes>\n')

for record_id in range(39,53):
    flow_mainInner, flow_mainOuter, flow_ramp = get_flow(record_id)
    duration_second = get_recording_duration()
    duration_hour = duration_second/3600
    time_step = np.cumsum([0] + duration_second)
    time_step = np.insert(time_step, 0, 0)


    fType.write(
        f'  <flow id="main_inner_{record_id}" type="HDV" color="green" begin="{time_step[record_id-39]}" end="{time_step[record_id-38]}" departLane="1" departSpeed="30" from="upstream" to="downstream" vehsPerHour="{flow_mainInner/duration_hour[record_id-39]}"/> \n')
    fType.write(
        f'  <flow id="main_outer_{record_id}" type="HDV" color="yellow" begin="{time_step[record_id-39]}" end="{time_step[record_id-38]}" departLane="0" departSpeed="30" from="upstream" to="downstream" vehsPerHour="{flow_mainOuter/duration_hour[record_id-39]}"/> \n')
    fType.write(
        f'  <flow id="ramp_{record_id}" type="HDV" color="red" begin="{time_step[record_id-39]}" end="{time_step[record_id-38]}" departLane="0" departSpeed="30" from="onramp" to="downstream" vehsPerHour="{flow_ramp/duration_hour[record_id-39]}"/> \n')
    print("recording:",record_id, flow_mainInner, flow_mainOuter, flow_ramp)
    #print("recording:", record_id, flow_mainInner/duration_hour[record_id-39],flow_mainOuter/duration_hour[record_id-39],flow_ramp/duration_hour[record_id-39])
    fType.write( '\n')


fType.write('</routes>\n')
fType.close()