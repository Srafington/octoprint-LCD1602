# coding=utf-8

"""
  LCD1602 Plugin for Octoprint
"""

from __future__ import absolute_import
from octoprint.printer.estimation import PrintTimeEstimator
import octoprint.plugin
import octoprint.events
import time
import datetime
import os
import sys
from fake_rpi import printf
import fake_rpi
from dot3k import backlight
from dot3k import lcd


class OPDOT3kPlugin(octoprint.plugin.StartupPlugin,
                    octoprint.plugin.EventHandlerPlugin,
                    octoprint.plugin.ProgressPlugin):

  def __init__(self):
    if (os.getenv('LCD1602_DOCKER')):
      print('We are running in test environnement, no i2c device attached.')
      try:
        print('Loading fake_rpi instead of smbus2')
        sys.modules['smbus2'] = fake_rpi.smbus
        self.mylcd = fake_rpi.smbus.SMBus(1)
      except:
        print('Cannot load fake_rpi !')
    else:
      self.mylcd = lcd
      
      # create block for progress bar
      self.block = bytearray(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF')
      self.block.append(255)
      self.mylcd.create_char(1,self.block)
    
    # init vars
    self.start_date = 0

    # create block for progress bar
    #self.mylcd.create_char(1,self.block)

  def JobIsDone(self,lcd):

    # create final anim
    self.birdy = [ '^_-' , '^_^', '-_^' , '^_^', '0_0', '-_-', '^_-', '^_^','@_@','*_*','$_$','<_<','>_>']

    for pos in range(0,13):
      lcd.set_cursor_position = (1,pos)
      lcd.write(self.birdy[pos])
      time.sleep(0.5)
      lcd.clear()
    lcd.write('Job is Done    \,,/(^_^)\,,/')

      
  def on_after_startup(self):
    mylcd = self.mylcd
    self._logger.info("plugin initialized !")

  
  def on_print_progress(self,storage,path,progress):
    mylcd = self.mylcd
    # percent = int(progress/6.25)+1
    # completed = '\x01'*percent
    mylcd.clear()
    mylcd.write('Completed: '+str(progress)+'%')
    mylcd.set_cursor_position = (1,0)
    # mylcd.write(completed)
    backlight.set_graph(progress/100.0)
    backlight.update()

    if progress==1 :
      self.start_date=time.time()
  
    if progress>10 and progress<100:
      now=time.time()
      elapsed=now-self.start_date
      average=elapsed/(progress-1)
      remaining=int((100-progress)*average)
      remaining=str(datetime.timedelta(seconds=remaining))
      mylcd.set_cursor_position = (1,3)
      mylcd.write(remaining)

    if progress==100 :
      self.JobIsDone(mylcd)



  def on_event(self,event,payload):
    mylcd = self.mylcd
      
    if event in "Connected":
      mylcd.clear()
      mylcd.write('Connected to:')
      mylcd.set_cursor_position = (1,0)
      mylcd.write(payload["port"])

    if event in "Shutdown":
      mylcd.clear()
      mylcd.write('Bye bye ^_^')
      time.sleep(1)
      backlight.off()
      backlight.update()
      mylcd.close()
    
    
    if event in "PrinterStateChanged":
      
      if payload["state_string"] in "Offline":
        mylcd.clear()
        mylcd.write('Octoprint is not connected')
        time.sleep(2)
        mylcd.clear()
        mylcd.write('saving a polar bear, eco mode ON')
        time.sleep(5)
        backlight.off()
        backlight.update()
      
      if payload["state_string"] in "Operational":
        backlight.sweep(0.8)
        backlight.update()
        mylcd.clear()
        mylcd.write('Printer is       Operational')
      
      if payload["state_string"] in "Cancelling":
        backlight.sweep(0.2)
        backlight.update()
        mylcd.clear()
        mylcd.write('Printer  is Cancelling job') 
        time.sleep(0.2)
      
      if payload["state_string"] in "PrintCancelled":
        mylcd.clear()
        backlight.sweep(0.0)
        backlight.update()
        time.sleep(0.5)
        mylcd.write(' Job has been Cancelled (0_0) ' ) 
        time.sleep(2)
      
      if payload["state_string"] in "Paused":
        backlight.sweep(0.5)
        backlight.update()
        mylcd.clear()
        time.sleep(0.5)
        mylcd.write('Printer is  Paused') 

      if payload["state_string"] in "Resuming":
        backlight.sweep(0.8)
        backlight.update()
        mylcd.clear()
        mylcd.write('Printer is Resuming its job') 
        time.sleep(0.2)

  def get_update_information(self):
      return dict(
          OPDOT3kPlugin=dict(
              displayName="LCD1602 display",
              displayVersion=self._plugin_version,

              type="github_release",
              current=self._plugin_version,
              user="n3bojs4",
              repo="OctoPrint-Lcd1602",

              pip="https://github.com/Srafington/octoprint-LCD1602/archive/{target}.zip"
          )
      )

__plugin_name__ = "Display-O-Tron 3000"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = OPDOT3kPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
