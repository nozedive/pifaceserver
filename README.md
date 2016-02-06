piface-python-websocket-server

This code modified from https://github.com/adcomp/piface-python-websocket-server 

I have added thermostat logic and second thread to check a one-wire temperature sensor.

View my blog post here: https://medium.com/@derek_seaton/piface-thermostat-server-a7a60d974e32#.xsl6qw2d1
==============================
- Hardware Prerequisites:
  * PiFace: http://www.piface.org.uk/

- Software Prerequisites:
-  Tornado:
  * $> sudo apt-get install python-tornado 
-  JSON:
  * $> sudo apt-get install python-simplejson

- PiFace server:
  * $> git clone https://github.com/adcomp/piface-python-websocket-server.git
  * $> cd piface-python-websocket-server
  * $> python server.py

- Browser: 
  * http//[your_raspberrypi_IP]:8888

- Video:
  * https://www.youtube.com/watch?v=eJpGfqwGr08

- References:
  * http://www.piface.org.uk/guides/Install_PiFace_Software/
  * https://piface.github.io/pifacedigitalio/
