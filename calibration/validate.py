# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2008-2023 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    validate.py
# @author  Michael Behrisch
# @date    2012-01-21

from __future__ import absolute_import
from __future__ import print_function

import sys
import math
import subprocess
import xml.etree.ElementTree as ET
import numpy as np
import run_sumo


dDay = 1
obsTimes = {}
verbose = False
DatasetRearHeadway_mean=1.67
DatasetRearHeadway_min=0.58
DatasetLeadHeadway_mean=2.41
DatasetLeadHeadway_min=0.38
DatasetMergingPosition=61



def readTimes(obsfile): # convert timelist file into sencond list
    times = []
    with open(obsfile) as ifile:
        for line in ifile:
            ll = line.split(':')
            if ll:
                times.append(
                    3600 * int(ll[0]) + 60 * int(ll[1]) + int(float(ll[2]))) #转化成秒
    return times


def parseObsTimes():
    for i in range(0, 9):
        obsTimes[i] = []
    for i in range(1, 8):
        if dDay == 1 and i == 5:
            continue
        if dDay == 2 and i == 6:
            continue
        obsTimes[i] = readTimes('data/obstimes_%s_%s.txt' % (dDay, i))

    # convert obsTimes[][] into travel-times:
    for i in range(1, 8):
        ni = len(obsTimes[i])
        if ni == len(obsTimes[i + 1]) and ni > 100:
            for j in range(ni):
                obsTimes[i][j] = obsTimes[i + 1][j] - obsTimes[i][j]


def validate(sumoBinary):
    all_error=[]
    for i in range(1):
        # subprocess.call(
        #     [sumoBinary, "-c", "scene/ramp.sumocfg"], stdout=sys.stdout, stderr=sys.stderr)
        # sys.stdout.flush()
        # sys.stderr.flush()

        run_sumo.run_sumo_solidline()
        followerHeadways, followerSpeeds,leaderHeadways,leaderSpeeds, positions = run_sumo.get_followerHeadway(100)
        print("replicate",i,"rear length:",len(followerHeadways),"mean:", np.mean(followerHeadways),"min",np.min(followerHeadways),"pos",np.mean(positions))
        print("replicate", i, "lead length:",len(leaderHeadways), "mean:", np.mean(leaderHeadways), "min",np.min(leaderHeadways), "pos", np.mean(positions))

        error_rear_mean=abs(np.mean(followerHeadways)-DatasetRearHeadway_mean)
        error_rear_min=abs(np.min(followerHeadways)-DatasetRearHeadway_min)
        error_lead_mean=abs(np.mean(leaderHeadways)-DatasetLeadHeadway_mean)
        error_lead_min=abs(np.min(leaderHeadways)-DatasetLeadHeadway_min)
        error3=abs(np.mean(positions)-DatasetMergingPosition)
        error=0.3*error_rear_mean+0.3*error_rear_min*20+0.3*error_lead_mean+0.3*error_lead_min*20

        all_error.append(error)
        print("all_error",all_error)
    avg_error = np.mean(all_error)
    print(f"Average error: {avg_error}")

    return avg_error
