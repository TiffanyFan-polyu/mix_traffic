from __future__ import absolute_import
from __future__ import print_function

import sys
import math
import subprocess
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sumolib import checkBinary
import traci
from tabulate import tabulate



def run_sumo_solidline():
    sumoBinary = checkBinary('sumo')
    # sumoCmd = [sumoBinary, "-c", "scene/ramp.sumocfg"]  # "--additional-files", "scene/additional.xml"
    sumoCmd = [sumoBinary, "-c", "scene/ramp.sumocfg"]
    traci.start(sumoCmd)
    current_step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        for veh_id in traci.vehicle.getIDList():
            if traci.vehicle.getLanePosition(veh_id) < 68:
                traci.vehicle.setLaneChangeMode(veh_id, 0b001000000000)
            else:
                traci.vehicle.setLaneChangeMode(veh_id, 0b011001010101)


        current_step += 1  # Increment the current step index

    # out of while loop
    traci.close()
    sys.stdout.flush()
    # self.dump_data()

def run_sumo_changePara():
    sumoBinary = checkBinary('sumo')
    # sumoCmd = [sumoBinary, "-c", "scene/ramp.sumocfg"]  # "--additional-files", "scene/additional.xml"
    sumoCmd = [sumoBinary, "-c", "scene/ramp.sumocfg"]
    traci.start(sumoCmd)
    current_step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        for veh_id in traci.vehicle.getIDList():
            if traci.vehicle.getLanePosition(veh_id) < 68:
                traci.vehicle.setLaneChangeMode(veh_id, 0b001000000000)
            else:
                traci.vehicle.setLaneChangeMode(veh_id, 0b011001010101)
                print("ego:",traci.vehicle.getTypeID(veh_id))
                print("leader:",traci.vehicle.getLeader(veh_id))
                if traci.vehicle.getLeader(veh_id) is not None:
                    if traci.vehicle.getTypeID(traci.vehicle.getLeader(veh_id)[0])=="HDV":
                        print(traci.vehicle.getTypeID(traci.vehicle.getLeader(veh_id)[0]))




        current_step += 1  # Increment the current step index

    # out of while loop
    traci.close()
    sys.stdout.flush()
    # self.dump_data()

def get_followerHeadway(distance):
    all_followerHeadway = []
    all_followerSpeed = []
    all_learderHeadway = []
    all_learderSpeed = []
    all_position = []
    # Open the XML file and parse the root element
    tree = ET.parse('scene/output/lanechange.xml')
    root = tree.getroot()

    # Loop over all the vehicle elements in the XML file
    for change in root.iter('change'):
        # Get the vehicle position from the XML element
        from_element = change.get('from')

        # Check if the "from" element is "acc"
        if from_element == "acc_0":
            position = change.get('pos')
            position=float(position)
            all_position.append(position)
            # Add the position to the list
            followerGap = change.get('followerGap')
            leaderGap=change.get('leaderGap')
            followerSpeed = change.get('followerSpeed')
            leaderSpeed = change.get('leaderSpeed')
            if (followerGap != 'None' and leaderGap != 'None'):
              followerGap = float(followerGap)
              followerSpeed = float(followerSpeed)
              leaderGap = float(leaderGap)
              leaderSpeed = float(leaderSpeed)
              if (followerGap <= distance and leaderGap <= distance and followerSpeed > 0 and leaderSpeed>0):
                 followerHeadway = followerGap / followerSpeed
                 leaderHeadway = leaderGap/ leaderSpeed
                 all_followerHeadway.append(followerHeadway)
                 all_learderHeadway.append(leaderHeadway)
                 all_followerSpeed.append(followerSpeed)
                 all_learderSpeed.append(leaderSpeed)
    return all_followerHeadway, all_followerSpeed, all_learderHeadway, all_learderSpeed, all_position


def plot_headway(rearSpeeds, rearHeadways,leaderSpeeds,leaderHeadways,mode):

    # plot headway-speed
    fig,ax=plt.subplots(figsize=(10, 6))
    #plt.figure(figsize=(10, 6))
    plt.yticks([0,2,4,6,8,10,12,14],fontsize=14)
    plt.xticks([0, 5, 10, 15, 20, 25, 30, 35, 40],fontsize=14)
    plt.ylim([0, 14])
    plt.xlim([0, 40])
    plt.xlabel("speed(m/s)",fontsize=14)
    plt.ylabel("headway(s)",fontsize=14)
    plt.grid(ls='-', axis="both")
    plt.title(mode+ " Headway", fontsize=16)
    ax.scatter(rearSpeeds,rearHeadways,label='Rear Headway')
    ax.scatter(leaderSpeeds,leaderHeadways,label='lead Headway',color='r')
    ax.legend(fontsize=14)
    #plt.scatter(Speeds, Headways)
    plt.savefig("figure/"+mode+"_headway.png", dpi=300)
    plt.show()



def plot_flow(rearSpeeds, rearHeadways,leaderSpeeds,leaderHeadways,mode):

    rear_speed = [speed * 3.6 for speed in rearSpeeds]
    rear_flow = [3600 / headway for headway in rearHeadways]
    lead_speed = [speed * 3.6 for speed in leaderSpeeds]
    lead_flow = [3600 / headway for headway in leaderHeadways]
    fig, ax = plt.subplots(figsize=(10, 6))

    #plt.figure(figsize=(10, 6))

    plt.yticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000],fontsize=14)
    plt.xticks([0, 20, 40, 60, 80, 100, 120, 140],fontsize=14)
    plt.ylim([0, 7000])
    plt.xlim([0, 140])
    plt.xlabel("speed(km/h)",fontsize=14)
    plt.ylabel("flow(veh/h)",fontsize=14)
    plt.grid(ls='-', axis="both")
    plt.title(mode+" Flow-Speed",fontsize=16)
    #plt.scatter(speed_KM, flow)
    ax.scatter(rear_speed,rear_flow,label='Rear Flow')
    ax.scatter(lead_speed,lead_flow,label='Lead Flow',color='r')
    ax.legend(fontsize=14)
    plt.savefig("figure/"+mode+"_flow.png", dpi=300)
    plt.show()

def plot_position(positions,mode):
    # plt.figure()
    # plt.grid(linestyle="-", alpha=0.5)
    # bins = [0, 40, 80, 120, 160]
    # sns.distplot(positions, bins, hist=True, kde=True, color='royalblue')
    # plt.xticks((0,40,80,120,160), fontsize=10)
    # # 修改刻度值大小
    # plt.tick_params(labelsize=13)
    # # # 添加x, y轴描述信息
    # plt.xlabel("Merging Distance")
    # plt.show()

    plt.figure(figsize=(8, 6))
    plt.hist(positions, bins=[0, 40, 80, 120, 160], range=(0, 160), density=False,
             weights=None, cumulative=False, bottom=None,
             histtype=u'bar', align='mid', orientation=u'vertical',
             rwidth=0.8, log=False, color=None, label=None, stacked=True)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.xlabel("Merging Position")
    plt.ylabel("Number of Vehicles")
    # plt.legend(fontsize=12)
    plt.title(mode+" Merging Distribution")
    plt.savefig("figure/rear/"+mode+"_MergePos.png", dpi=300)
    plt.show()

def extract_speed(file_name):
    tree = ET.parse('scene/output/'+file_name)
    root = tree.getroot()
    speed_list = []
    for interval in root.iter('interval'):
        # Get the vehicle position from the XML element
        speed_element = float(interval.get('speed'))
        if speed_element!= -1:
            speed_list.append(speed_element)
    return speed_list

def plot_speed(mode):
    # plot speed-distance
    onramp_speed = extract_speed('onramp.xml')

    # Create a list with the same length as onramp_speed, starting from 100 and incrementing by 10
    onramp_distance = [-100 + i * 10 for i in range(len(onramp_speed))]
    #print("Onramp speed:", onramp_speed)
    #print("Onramp distance:", onramp_distance)

    mainline_speed = extract_speed('mainline.xml')
    #print("mainline speed:", mainline_speed)
    mainline_distance = [-100 + i * 10 for i in range(len(mainline_speed))]

    plt.figure(figsize=(10, 6))
    plt.yticks([0, 5, 10, 15, 20, 25, 30, 35, 40])
    plt.xticks([-100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100, 120, 140, 160])
    plt.ylim([0, 40])
    plt.xlim([-100, 160])
    plt.xlabel("position(m)")
    plt.ylabel("speed(m/s)")
    plt.grid(ls='-', axis="both")
    # plt.title("Default Follower Headway")
    plt.title( mode + " average speed")
    plt.plot(mainline_distance, mainline_speed, 's-', color='r', label="mainline")  # s-:方形
    plt.plot(onramp_distance, onramp_speed, 'o-', color='g', label="onramp")
    plt.legend()
    plt.savefig("figure/rear/"+mode+"_speed.png", dpi=300)
    plt.show()
    # plot flow(h)-speed

def main():
    parameter_mode="Calibrated"
    num_eps = 1
    distance_threshold = 100
    followerHeadway_mean = []
    followerHeadway_var = []
    followerHeadway_min = []
    leaderHeadway_mean = []
    leaderHeadway_var = []
    leaderHeadway_min = []

    for i in range(num_eps):
        # subprocess.call(
        #     ['sumo-gui', "-c", "scene/ramp.sumocfg"], stdout=sys.stdout, stderr=sys.stderr)
        # sys.stdout.flush()
        # sys.stderr.flush()

        run_sumo_changePara()
        followerHeadways, followerSpeeds, leaderHeadways, leaderSpeeds, positions = get_followerHeadway(distance_threshold)

        # print(all_followerSpeed)
        # print(all_followerHeadway)
        print("replicate", i, "followerHeadway:", np.mean(followerHeadways), "mean:", np.mean(positions))
        print("lenth of follower headway:", len(followerHeadways))
        print("lenth of leader headway:", len(leaderHeadways))
        print("lenth of positions:", len(positions))

        followerHeadway_mean.append(np.mean(followerHeadways))
        followerHeadway_var.append(np.var(followerHeadways))
        followerHeadway_min.append(np.min(followerHeadways))
        leaderHeadway_mean.append(np.mean(leaderHeadways))
        leaderHeadway_var.append(np.var(leaderHeadways))
        leaderHeadway_min.append(np.min(leaderHeadways))

    # average multiple episodes' results
    avg_followerHeadway_mean = np.mean(followerHeadway_mean)
    avg_followerHeadway_var = np.mean(followerHeadway_var)
    avg_followerHeadway_min = np.mean(followerHeadway_min)
    avg_leaderHeadway_mean = np.mean(leaderHeadway_mean)
    avg_leaderHeadway_var = np.mean(leaderHeadway_var)
    avg_leaderHeadway_min = np.mean(leaderHeadway_min)
    table = [['type', 'mean', 'var', 'minimum'], ['rear', avg_followerHeadway_mean, avg_followerHeadway_var, avg_followerHeadway_min],
             ['lead', avg_leaderHeadway_mean, avg_leaderHeadway_var, avg_leaderHeadway_min]]
    #print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
    print(tabulate(table))
    print("mean:", avg_followerHeadway_mean)
    print("var:", avg_followerHeadway_var)
    print("minimum:", avg_followerHeadway_min)
    print("leader speed mean:", np.mean(leaderSpeeds))

    plot_headway(followerSpeeds, followerHeadways,leaderSpeeds,leaderHeadways,parameter_mode)
    plot_flow(followerSpeeds, followerHeadways,leaderSpeeds,leaderHeadways,parameter_mode)
    plot_position(positions,parameter_mode)
    plot_speed(parameter_mode)

if __name__ == "__main__":
   main()

