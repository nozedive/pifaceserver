#!/usr/bin/python

# Python WebSocket Server for Raspberry Pi / PiFace
# by David Art [aka] adcomp <david.madbox@gmail.com>

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado import gen
import threading

from tornado.ioloop import IOLoop

import datetime
import json
import sys
import os

import time
from w1thermsensor import W1ThermSensor

# PiFace module & init
import pifacedigitalio as pfio
pfio.init()
pifacedigital = pfio.PiFaceDigital()

settemp = 72.0

temperature_in_fahrenheit = 3

class ThreadingExample(object):
    """ Threading example class

    The run() method will be started and it will run in the background
    until the application exits.
    """
 
    def __init__(self, interval=5):
        """ Constructor

        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
 
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
 
    def run(self):
        global temperature_in_fahrenheit
        """ Method that runs forever """
        while True:
            
            #this is slow need to do it less
            sensor = W1ThermSensor()  
            temperature_in_fahrenheit = sensor.get_temperature(W1ThermSensor.DEGREES_F)
            temperature_in_fahrenheit = round(temperature_in_fahrenheit,1)
            #Thermostat logic
            if temperature_in_fahrenheit<(settemp-.2):
              pfio.digital_write(2, 1) #turn heater on
       
            if temperature_in_fahrenheit>(settemp+.2):
              pfio.digital_write(2, 0) #turn heater off
 
            time.sleep(self.interval) #this is interval time for the background fn



class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")


class WebSocketHandler(tornado.websocket.WebSocketHandler):

  clients = []
  last_data = None

  def open(self):
    self.connected = True
    print("new connection")
    self.clients.append(self)
    self.timeout_loop()

  # """ Tornado 4.0 introduced an, on by default, same origin check.
  # This checks that the origin header set by the browser is the same as the host header """
  def check_origin(self, origin):
    return True

  def on_message(self, message):
    global settemp

    # message is the PIN number you want to toggle
    pin = int(message)

    if pin<8:
      # read output state
      r_output = '{0:08b}'.format(pifacedigital.output_port.value)
      # toggle output
      pin_state = int(r_output[7-pin]);
      pfio.digital_write(pin, not pin_state)
      # FIXME! I need to check with the loop so I don't send twice ?
      # I think i fixed it when I separated no_timeout_loop? -Derek
      self.no_timeout_loop()
      

    if pin==10:
      settemp = settemp - 1 #Hard coded message to lower set temp
      self.no_timeout_loop()
      

    if pin==11:
      settemp = settemp + 1 #Hard coded message to raise set temp
      self.no_timeout_loop()
      

  def on_close(self):
    self.connected = False
    print("connection closed")
    self.clients.remove(self)


  def no_timeout_loop(self):
    global temperature_in_fahrenheit
    #need to do thermostat logic here: (so that it's responsive to a click)
    if temperature_in_fahrenheit<(settemp-.2):
      pfio.digital_write(2, 1)
       
    if temperature_in_fahrenheit>(settemp+.2):
      pfio.digital_write(2, 0)

    # read PiFace input/output state
    r_input = '{0:08b}'.format(pifacedigital.input_port.value)
    r_output = '{0:08b}'.format(pifacedigital.output_port.value)
    # obj -> javascript
    data = {"in": [], "out": [], "temp": []}

    for i in range(8):
      data['in'].append(r_input[7-i])
      data['out'].append(r_output[7-i])

    data['temp'].append(temperature_in_fahrenheit)
    data['temp'].append(settemp)

    # only send message if input/output changed
    if data != self.last_data:
      for client in self.clients:
        client.write_message(json.dumps(data))
    self.last_data = data

  
   


  def timeout_loop(self):
    global temperature_in_fahrenheit

    # read PiFace input/output state
    r_input = '{0:08b}'.format(pifacedigital.input_port.value)
    r_output = '{0:08b}'.format(pifacedigital.output_port.value)
    # obj -> javascript
    data = {"in": [], "out": [], "temp": []}

    for i in range(8):
      data['in'].append(r_input[7-i])
      data['out'].append(r_output[7-i])

    data['temp'].append(temperature_in_fahrenheit)
    data['temp'].append(settemp)


    # only send message if input/output changed
    if data != self.last_data:
      for client in self.clients:
        client.write_message(json.dumps(data))
    self.last_data = data

    # here come the magic part .. loop
    # FIXME! this is going pretty bad if too many clients I think ..
    # no other way to do this ?
    if self.connected:
      tornado.ioloop.IOLoop.instance().add_timeout(datetime.timedelta(seconds=2), self.timeout_loop)
      
      


application = tornado.web.Application([
  (r'/', IndexHandler),
  (r'/piface', WebSocketHandler),
])

if __name__ == "__main__":
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8888)
  tornado.autoreload.start()
  print("Raspberry Pi - PiFace")
  print("WebSocket Server start ..")
  
  print "calling background thread"
  example = ThreadingExample()
  print "done calling background thread"
  
  try:
    #tornado.ioloop.IOLoop.instance().start()
    dioloop=tornado.ioloop.IOLoop.instance()
    dioloop.start()
  

  except KeyboardInterrupt:
    print('\nExit ..')
    sys.exit(0)
