#!/usr/bin/env python
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

# @file    runner.py
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @date    2007-10-25

from __future__ import absolute_import
from __future__ import print_function

import os
import subprocess
import sys
import shutil
from scipy.optimize import fmin_cobyla
from scipy.optimize import minimize

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
from sumolib import checkBinary  # noqa
import validate  # noqa


def buildVSS(obs7file, obs8file, vss):
    t7Times = validate.readTimes(obs7file)
    t8Times = validate.readTimes(obs8file)
    print('data read: ', len(t7Times), len(t8Times))

    fp = open(vss, 'w')
    lObs8 = 337.5
    print('<vss>', file=fp)
    for i, t7 in enumerate(t7Times):
        v = lObs8 / (t8Times[i] - t7)
        if i != len(t7Times) - 1 and t7 != t7Times[i + 1]:
            print('    <step time ="%s" speed="%s"/>' % (t7, v), file=fp)
    print('</vss>', file=fp)
    fp.close()


def genDemand(inputFile, outputFile):
    t1Times = validate.readTimes(inputFile)
    fRou = open(outputFile, 'w')
    fRou.write('<routes>\n')
    fRou.write('    <route id="route01" edges="1to7 7to8"/>\n')
    for vehID, t in enumerate(t1Times):
        print('    <vehicle depart="%s" arrivalPos="-1" id="%s" route="route01" type="pass" departSpeed="max" />' % (
            t, vehID), file=fRou)
    print('</routes>', file=fRou)
    fRou.close()

# definition of gof() function to be given to fmin_cobyla() or fmin()

min_result=1000

def gof(p):
    global min_result
    para = [('tTau', p[0]),
            ('lcAssertive', p[1]),
            ('minGap', p[2]),
            ('accel', p[3]),
            ('decel', p[4])]
    print('# simulation with:', *["%s:%.3f" % i for i in para])
    fType = open('scene/input_types.add.xml', 'w')
    fType.write(('<routes>\n   <vType id="HDV" tau="%(tTau)s" lcAssertive="%(lcAssertive)s"'
                 ' minGap="%(minGap)s" accel="%(accel)s" decel="%(decel)s"/>\n</routes>') % dict(para))

    # para = [('tTau', p[0]),
    #         ('lcStrategic', p[1]),
    #         ('lcAssertive', p[2]),
    #         ('minGap', p[3]),
    #         ('cc1', p[4]),
    #         ('cc3', p[5])]
    # print('# simulation with:', *["%s:%.3f" % i for i in para])
    # fType = open('scene/input_types.add.xml', 'w')
    # fType.write(('<routes>\n   <vType id="HDV" tau="%(tTau)s" lcStrategic="%(lcStrategic)s" lcAssertive="%(lcAssertive)s"'
    #              ' minGap="%(minGap)s" accel="%(accel)s" decel="%(decel)s"/>\n</routes>') % dict(para))

    fType.close()
    result = validate.validate(checkBinary('sumo'))


    print('#### yields rmse: %.4f' % result)
    if result<min_result:
        min_result=result
        optimize_para=para
        print('************************************************')
        print('min_rmse', min_result, 'at para', optimize_para)

    print("%s %s" % (" ".join(["%.3f" % pe for pe in p]), result), file=fpLog)
    fpLog.flush()
    return result

# defining all the constraints



def conTtau(params):  # tTau > 1.0
    return params[0] - 1.0

# def conlcStra(params):  # lcStrategic > 1
#     return params[1] - 1

def conlcAss(params):  # lcAssertive > 0
    return params[1]-0.1

# def conlcCooperative(params):  # lcCooperative > 0
#     return params[3]-0.01

# def conlcSpeedGain(params):  # lcSpeedGain > 0
#     return params[4]-0.01

# def conspeedDev(params):  # lcSpeedGain > 0
#     return params[4]-0.1

def conminGap(params):
    return params[2]-0.01

def conaccel(params):
    return params[3]-0.01

def condecel(params):
    return params[4]-0.01


def __init__(self):
    self.max_result = 0



# perform calibration
fpLog = open('results.csv', 'w')
#params = [3, 0.1, 0.1, 4, 0.8, 4.5]
params = [3, 1, 4, 0.8, 4.5]

# call to (unconstrained) Nelder Mead; does not work correctly, because
# method very often stumples over unrealistic input parameterss (like tTau<1),
# which causes SUMO to behave strangely.
# fmin(gof, params)
fmin_cobyla(
    gof, params, [conTtau, conlcAss, conminGap, conaccel, condecel], rhoend=1.0e-4)

fpLog.close()

