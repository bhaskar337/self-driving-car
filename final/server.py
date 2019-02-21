#real-time server
import socketio
#concurrent networking 
import eventlet
#web server gateway interface
import eventlet.wsgi
#web framework
from flask import Flask
#decoding camera images
import base64
#image manipulation
from PIL import Image
#input output
from io import BytesIO

from planner import Planner

sio = socketio.Server()
app = Flask(__name__)
planner = Planner()

@sio.on('connect')
def connect(sid, environ):
	global planner
	planner = Planner()
	print("connect ", sid)
	sio.emit(
		"move",
		data={
			'steer_angle': "0.0",
			'torque': "0.0",
		},
		skip_sid=True
	)


@sio.on('telemetry')
def telemetry(sid, data):
	global index
	if data:
		msg = planner.plan(data)
		sio.emit(
			"move",
			data={
				'steer_angle': str(msg[0]),
				'torque': str(msg[1]),
			},
			skip_sid=True
		)

app = socketio.Middleware(sio, app)
eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
