#!/bin/bash

if [ $(cat /proc/1/cgroup | grep -c -i docker) -gt 0 ] ; then export OPDOT3k_DOCKER=1; fi

source /opt/octoprint/venv/bin/activate 
python setup.py install || echo "Error: Cannot install OPDOT3k Plugin"

echo "Starting octoprint server"
/opt/octoprint/venv/bin/octoprint serve --iknowwhatimdoing >/tmp/logs &

echo "Checking octoprint is running"
sleep 3
RUNNING=$(pgrep -c octoprint)


if [ $RUNNING -eq 0 ]
then
  echo 'Octoprint failed to start' && exit 1
else
  echo 'Octoprint is started'
fi

echo "Looking for errors on logs"
sleep 10
ERRORS=$(grep -c "^| \!OPDOT3k I2c display" /tmp/logs )

if [ $ERRORS -gt 0 ]
then
  echo 'Plugin errors detected, check logs below :'
  grep -A 100 -B 20 'OPDOT3k' /tmp/logs
  exit 1
else
  echo "Plugin is installed and loaded"
fi
