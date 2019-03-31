# coding=utf-8

"""
  OPDOT3k Plugin for Octoprint
"""

from __future__ import absolute_import
from octoprint.printer.estimation import PrintTimeEstimator
import octoprint.plugin
import octoprint.events
import time
import datetime
import os
import sys
from dot3k import backlight
from dot3k import lcd


class OPDOT3kPlugin(octoprint.plugin.StartupPlugin,
                    octoprint.plugin.EventHandlerPlugin,
                    octoprint.plugin.ProgressPlugin):

  def __init__(self):
    # init vars
    self.start_date = 0

    # create block for progress bar
    #self.lcd.create_char(1,self.block)

  def JobIsDone(self,localLcd):

    # create final anim
    self.birdy = [ '^_-' , '^_^', '-_^' , '^_^', '0_0', '-_-', '^_-', '^_^','@_@','*_*','$_$','<_<','>_>']

    for pos in range(0,13):
      localLcd.set_cursor_position = (1,pos)
      localLcd.write(self.birdy[pos])
      time.sleep(0.5)
      localLcd.clear()
    localLcd.write('Job is Done')
    backlight.rgb(255,255,255)
    backlight.update();
    for i in range(0,100):
      backlight.set_graph((100-i)/100.0)
      time.sleep(0.05)

      
  def on_after_startup(self):
    self._logger.info("plugin initialized !")

  
  def on_print_progress(self,storage,path,progress):
    # percent = int(progress/6.25)+1
    # completed = '\x01'*percent
    lcd.clear()
    lcd.write('Completed: '+str(progress)+'%')
    lcd.set_cursor_position = (1,0)
    # lcd.write(completed)
    backlight.set_graph(progress/100.0)
    backlight.sweep(progress/100.0)
    backlight.update()

    if progress==1 :
      self.start_date=time.time()
  
    if progress>10 and progress<100:
      now=time.time()
      elapsed=now-self.start_date
      average=elapsed/(progress-1)
      remaining=int((100-progress)*average)
      remaining=str(datetime.timedelta(seconds=remaining))
      lcd.set_cursor_position = (1,2)
      lcd.write('ETC: ')
      lcd.write(remaining)

    if progress==100 :
      self.JobIsDone(lcd)



  def on_event(self,event,payload):
      
    if event in "Connected":
      lcd.clear()
      lcd.write('Connected to:')
      lcd.set_cursor_position = (1,0)
      lcd.write(payload["port"])

    if event in "Shutdown":
      lcd.clear()
      lcd.write('Bye bye ^_^')
      time.sleep(1)
      backlight.off()
      backlight.update()
      lcd.exit()
    
    
    if event in "PrinterStateChanged":
      
      if payload["state_string"] in "Offline":
        lcd.clear()
        lcd.write('Octoprint is not connected')
        time.sleep(2)
        lcd.clear()
        lcd.write('saving a polar bear, eco mode ON')
        time.sleep(5)
        backlight.off()
        backlight.update()
      
      if payload["state_string"] in "Operational":
        backlight.rgb(255,255,255)
        backlight.update()
        lcd.clear()
        lcd.write('Printer is       Operational')
      
      if payload["state_string"] in "Cancelling":
        backlight.rgb(255,0,255)
        backlight.update()
        lcd.clear()
        lcd.write('Printer  is Cancelling job') 
        time.sleep(0.2)
      
      if payload["state_string"] in "PrintCancelled":
        lcd.clear()
        backlight.rgb(255,0,0)
        backlight.update()
        time.sleep(0.5)
        lcd.write(' Job has been Cancelled (0_0) ' ) 
        time.sleep(2)
      
      if payload["state_string"] in "Paused":
        backlight.rgb(255,255,0)
        backlight.update()
        lcd.clear()
        time.sleep(0.5)
        lcd.write('Printer is  Paused') 

      if payload["state_string"] in "Resuming":
        backlight.rgb(0,255,255)
        backlight.update()
        lcd.clear()
        lcd.write('Printer is Resuming its job') 
        time.sleep(0.2)

  def get_update_information(self):
      return dict(
          OPDOT3kPlugin=dict(
              displayName="Display-O-Tron-3000",
              displayVersion=self._plugin_version,

              type="github_release",
              current=self._plugin_version,
              user="Srafington",
              repo="OctoPrint-Lcd1602",

              pip="https://github.com/Srafington/octoprint-Lcd1602/archive/{target}.zip"
          )
      )

__plugin_name__ = "Display-O-Tron-3000"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = OPDOT3kPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}