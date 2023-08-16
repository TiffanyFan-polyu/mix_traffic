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

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.path.append('/usr/share/sumo/tools')

from sumolib import checkBinary
import traci

random.seed(1)
np.random.seed(1)


class Color(Enum):
    MAIN_INIT = (0, 255, 0)
    RAMP_INIT = (0, 0, 255)


class Flag(Enum):
    Initial = 0
    Controlled = 1
    LC = 2
    DONE = 3


class Lane(Enum):
    RAMP = 0
    MAIN = 1


def vehicles_ngsim():
    dataset = pd.read_csv('cleaned.csv')
    init_time = dataset.Global_Time.min()

    main_vehicles_ = []
    ramp_vehicles_ = []

    id_sets = set(dataset.Vehicle_ID.values)
    for ID in id_sets:
        one_id_vehicles = dataset[dataset.Vehicle_ID == ID]
        one_id_vehicles = one_id_vehicles.sort_values(by='Global_Time', ascending=True)

        time_frames = list(one_id_vehicles['Global_Time'])
        # check data
        for frame1, frame2 in zip(time_frames[:-1], time_frames[1:]):
            if frame2 - frame1 > 100:
                raise ValueError('not continuous trj')

        if one_id_vehicles.Lane_ID.values[0] == 6:
            main_vehicles_.append(one_id_vehicles)
        elif one_id_vehicles.Lane_ID.values[0] == 7:
            ramp_vehicles_.append(one_id_vehicles)
        else:
            raise ValueError('Lane ID is not 6 or 7')

    min_speed, max_speed = dataset.v_Vel.values.min(), dataset.v_Vel.values.max()  # 0, 30
    min_acc, max_acc = dataset.v_Acc.values.min(), dataset.v_Acc.values.max()     # +- 11.2

    # t_min = []
    # t_max = []
    # for main in main_vehicles_:
    #     t_min.append(main.Time_Headway.min())
    #     t_max.append(main.Time_Headway.max())

    return main_vehicles_, ramp_vehicles_, init_time



class SumoEnv:
    def __init__(self):
        # SUMO setting
        self.main_veh_list = []; self.ramp_veh_list = []  # all coming vehicles name

        self.hw_detector_pos: list = []
        self.hw_data = defaultdict(list)

        self.group_time_summary = []
        self.time_log = []
        self.travel_time = defaultdict(lambda: int)
        self.travel_time_0 = defaultdict(lambda: int)

        self.loop_main_pos = None
        self.loop_ramp_pos = None
        return

    @staticmethod
    def setup_vehicles():
        vehicle_departures = {}  # Dictionary to store vehicle names and departure times
        for route_id, depart_lane_, color_, vehicles in [('route0', Lane.MAIN.value, Color.MAIN_INIT.value, main_vehicles),
                                                         ('route1', Lane.RAMP.value, Color.RAMP_INIT.value, ramp_vehicles)]:
            for v_ in vehicles:
                name = 'main_veh' if route_id == 'route0' else 'ramp_veh'
                veh_name_ = name + str((v_.Vehicle_ID.values[0]).item())
                depart_pos_ = (v_.Local_Y.values[0]).item()
                depart_time_ = (v_.Global_Time.values[0] - start_time) / 1000  # to second
                depart_speed_ = (v_.v_Vel.values[0]).item()
                # depart_speed_ = random.randint(150, 300) * 0.1
                traci.vehicle.add(veh_name_,
                                  route_id,
                                  typeID="Car",
                                  depart=depart_time_,
                                  departPos=depart_pos_,
                                  departSpeed=depart_speed_,
                                  departLane=depart_lane_)
                # Store vehicle name and departure time in the dictionary
                vehicle_departures[veh_name_] = depart_time_

                print(veh_name_,"depart at", depart_time_ ,"departPos",depart_pos_,"departSpeed",depart_speed_)
                traci.vehicle.setSpeedFactor(veh_name_, 1)
                traci.vehicle.setColor(veh_name_, color_)
                SumoEnv.disable_auto_lane_change(veh_name_)
                # SumoEnv.manual_drive_mode(veh_name_)
                # traci.vehicle.setSpeed(veh_name_, depart_speed_)
                # cnt += 1
        return vehicle_departures

    # def setup_vehicles(vehicles):
    #     # Sort the list of vehicles by their departure time
    #     sorted_vehicles = vehicles.sort_values(by='Global_Time')
    #
    #     # Add vehicles to SUMO in order
    #     for index, vehicle in sorted_vehicles.iterrows():
    #         name = 'main_veh' if vehicle['RouteID'] == 'route0' else 'ramp_veh'
    #         veh_name = f"{name}{vehicle['Vehicle_ID']}"
    #         depart_pos = vehicle['Local_Y']
    #         depart_time = (vehicle['Global_Time'] - start_time) / 1000  # to seconds
    #         depart_speed = vehicle['v_Vel']
    #         depart_lane = Lane.MAIN.value if vehicle['RouteID'] == 'route0' else Lane.RAMP.value
    #
    #         traci.vehicle.add(veh_name,
    #                           vehicle['RouteID'],
    #                           typeID="Car",
    #                           depart=depart_time,
    #                           departPos=depart_pos,
    #                           departSpeed=depart_speed,
    #                           departLane=depart_lane)
    #
    #         traci.vehicle.setSpeedFactor(veh_name, 1)
    #         traci.vehicle.setColor(veh_name,
    #                                Color.MAIN_INIT.value if vehicle['RouteID'] == 'route0' else Color.RAMP_INIT.value)
    #         SumoEnv.disable_auto_lane_change(veh_name)



    @staticmethod
    def get_vehicle_speed_from_trajectory(veh_id, current_step, departure_time):
        veh_num_id = int(veh_id[8:])  # Extract numerical ID from veh_id
        next_state = int(current_step-departure_time*10 + 1)

        for v_ in main_vehicles:
            if v_.Vehicle_ID.values[0] == veh_num_id:
                try:
                    #print(f"main vehicle {veh_id}, {v_.v_Vel.values[current_step + 1].item(), v_.Lane_ID.values[current_step + 1].item()}")
                    return v_.v_Vel.values[next_state].item(), v_.Lane_ID.values[next_state].item()
                except IndexError:
                    print(f"IndexError: skipping vehicle {veh_id}")
                    return None,None
        for v_ in ramp_vehicles:
            if v_.Vehicle_ID.values[0] == veh_num_id:
                try:
                    #print(f"ramp vehicle {veh_id}, {v_.v_Vel.values[current_step + 1].item(), v_.Lane_ID.values[current_step + 1].item()}")
                    return v_.v_Vel.values[next_state].item(), v_.Lane_ID.values[next_state].item()
                except IndexError:
                    print(f"IndexError: skipping vehicle {veh_id}")
                    return None,None
        raise ValueError(f"Vehicle {veh_id} not found in any trajectory.")


    def main(self):
        vehicle_departures = self.setup_vehicles()
        current_step = 0
        changed_lane_vehicles = set()  # Initialize an empty set to keep track of vehicles that have already changed lanes

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            print("current_step:",current_step)
            print(traci.vehicle.getIDList())

            #Update each vehicle's speed and lane
            for veh_id in traci.vehicle.getIDList():
                veh_speed, lane_id = self.get_vehicle_speed_from_trajectory(veh_id, current_step,vehicle_departures.get(veh_id))
                if veh_speed is not None:
                    traci.vehicle.setSpeed(veh_id, veh_speed)
                    print(veh_id,veh_speed)
                    if veh_id.startswith("ramp_veh") and lane_id == 6 and veh_id not in changed_lane_vehicles:
                        print(f"Vehicle {veh_id} is changing lane")
                        traci.vehicle.changeLane(veh_id, 1, 1)
                        changed_lane_vehicles.add(veh_id)  # Add the vehicle ID to the set of changed lane vehicles
                else:
                    print(f"Skipping vehicle {veh_id} due to missing or invalid speed value")
            current_step += 1  # Increment the current step index


            duration = self.get_sim_time()
            if self.collide():
                print('collision happens at %.3f' % duration)
                break

        # out of while loop
        traci.close()
        print(sum(self.time_log), len(self.time_log), sum(self.time_log) / len(self.time_log))
        sys.stdout.flush()
        # self.dump_data()


    @staticmethod
    def launch_sumo():
        sumoBinary = checkBinary('sumo-gui')
        # sumoCmd = [sumoBinary, "-c", "scene/ramp.sumocfg"]  # "--additional-files", "scene/additional.xml"
        sumoCmd = [sumoBinary, "-c", "scene/ramp.sumocfg",
                   "--additional-files", "scene/additional.xml",
                   "--tripinfo-output", "nocontrol_output.xml"]
        traci.start(sumoCmd)
        return

    # ---- Todo: ----
    def record_headway(self):
        detector_name = ['l5.2', 'l5.5', 'l6', 'l7', 'l8', 'l9', 'l10', 'l11', 'l12', 'l13', 'l14', 'l15',  'l16', 'l17', 'l18']
        for _i, detector in enumerate(detector_name):
            who = traci.inductionloop.getLastStepVehicleIDs(detector)
            if len(who) > 0:
                _veh = who[0]
                lead_info = traci.vehicle.getLeader(_veh, 500)
                if lead_info is not None:
                    headway = lead_info[1] / traci.vehicle.getSpeed(_veh)
                else:
                    headway = 1000
            else:
                headway = 1000
            self.hw_data[self.get_sim_time()].append(headway)
        return

    # -------------------------

    @staticmethod
    def collide():
        colliding_vehs = traci.simulation.getCollidingVehiclesIDList()
        if len(colliding_vehs) > 0:
            print(colliding_vehs)
            set_trace()
        return len(colliding_vehs) > 0

    @staticmethod
    def manual_drive_mode(veh_id):
        traci.vehicle.setSpeedMode(veh_id, 31)  # for manual control

    @staticmethod
    def set_car_following_mode(veh_name):
        traci.vehicle.setSpeedMode(veh_name, 31)  # default https://sumo.dlr.de/docs/TraCI/Change_Vehicle_State.html#speed_mode_0xb3
        traci.vehicle.setSpeed(veh_name, -1)
        return

    @staticmethod
    def get_lane_position(veh_name):
        return traci.vehicle.getLanePosition(veh_name)

    @staticmethod
    def get_sim_time():
        return traci.simulation.getTime()

    @staticmethod
    def get_veh_number(veh_name):
        # return int(veh_name)
        return int(veh_name[8:])

    @staticmethod
    def disable_auto_lane_change(veh_name):
        traci.vehicle.setLaneChangeMode(veh_name, 0)
        return

    @staticmethod
    def release_to_sumo(veh_name):
        if str(Lane.RAMP.value) in traci.vehicle.getLaneID(veh_name):
            traci.vehicle.setLaneChangeMode(veh_name, 1621)  # 1621 513
        traci.vehicle.setSpeed(veh_name, -1)
        traci.vehicle.setColor(veh_name, Color.RAMP_INIT.value)
        traci.vehicle.setSpeedFactor(veh_name, 1)
        return

    def setup_sensors(self):
        # self.loop_main_pos = traci.inductionloop.getPosition('loop_main')
        # self.hw_detector_pos = [500, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3300, 4300, 5300]
        self.loop_ramp_pos = traci.inductionloop.getPosition('loop_ramp')
        return


if __name__ == '__main__':
    main_vehicles, ramp_vehicles, start_time = vehicles_ngsim()
    env = SumoEnv()
    SumoEnv.launch_sumo()
    env.main()

