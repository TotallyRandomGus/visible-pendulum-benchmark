"""Controller program to manage the benchmark.

It manages the perturbation and evaluates the peformance of the user
controller.
"""

from controller import Supervisor
import math
import os
import random
import sys

def benchmarkPerformance(message, robot):
    benchmark_name = message.split(':')[1]
    benchmark_performance_string = message.split(':')[3]
    print(benchmark_name + ' Benchmark complete! Your performance was ' + benchmark_performance_string)
    if robot.getFromDef("ANIMATION_RECORDER_SUPERVISOR"):
        stop_recording(robot, message)

def stop_recording(robot, message):
    emitter = robot.getDevice('emitter')
    emitter.send(message.encode('utf-8'))

def time_convert(time):
    minutes = time / 60
    absolute_minutes =  math.floor(minutes)
    minutes_string = str(absolute_minutes).zfill(2)
    seconds = (minutes - absolute_minutes) * 60
    absolute_seconds =  math.floor(seconds)
    seconds_string = str(absolute_seconds).zfill(2)
    cs = math.floor((seconds - absolute_seconds) * 100);
    cs_string = str(cs).zfill(2)
    return minutes_string + "." + seconds_string + "." + cs_string

""" try:
    includePath = os.environ.get("WEBOTS_HOME") + "/projects/samples/robotbenchmark/include"
    includePath.replace('/', os.sep)
    sys.path.append(includePath)
    from robotbenchmark import robotbenchmarkRecord
except ImportError:
    sys.stderr.write("Warning: 'robotbenchmark' module not found.\n")
    sys.exit(0) """

# Get random generator seed value from 'controllerArgs' field
seed = 1
if len(sys.argv) > 1 and sys.argv[1].startswith('seed='):
    seed = int(sys.argv[1].split('=')[1])

robot = Supervisor()

timestep = int(robot.getBasicTimeStep())

jointParameters = robot.getFromDef("PENDULUM_PARAMETERS")
positionField = jointParameters.getField("position")

emitter = robot.getDevice("emitter")
time = 0
force = 0
forceStep = 800
random.seed(seed)
run = True

while robot.step(timestep) != -1:
    if run:
        time = robot.getTime()
        robot.wwiSendText("time:%-24.3f" % time)
        robot.wwiSendText("force:%.2f" % force)

        # Detect status of inverted pendulum
        position = positionField.getSFFloat()
        if position < -1.58 or position > 1.58:
            # stop
            run = False
            name = "Inverted Pendulum"
            performance = str(time)
            performanceString = time_convert(time)
            message = 'success:' + name + ':' + performance + ':' + performanceString
            robot.wwiSendText(message)
            benchmarkPerformance(message, robot)
        else:
            if forceStep <= 0:
                forceStep = 800 + random.randint(0, 400)
                force = force + 0.02
                toSend = "%.2lf %d" % (force, seed)
                if sys.version_info.major > 2:
                    toSend = bytes(toSend, "utf-8")
                emitter.send(toSend)
            else:
                forceStep = forceStep - 1
    else:
        # wait for record message
        message = robot.wwiReceiveText()
        while message:
            if message.startswith("confirm:"):
                print("WINDOW MESSAGE:", message)
            """ if message.startswith("success:"):
                benchmarkPerformance(message, robot)
                break """
            message = robot.wwiReceiveText()

robot.simulationSetMode(Supervisor.SIMULATION_MODE_PAUSE)
