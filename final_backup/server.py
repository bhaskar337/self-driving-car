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
index = 0

@sio.on('connect')
def connect(sid, environ):
	planner = Planner()
	print("connect ", sid)
	sio.emit(
		"move",
		data={
			'steer_angle': "0.0",
			'torque': "1.0",
		},
		skip_sid=True
	)


@sio.on('telemetry')
def telemetry(sid, data):
	global index
	if data:
		msg = planner.plan(data)
		# image = Image.open(BytesIO(base64.b64decode(data['image'])))
		# image.save('images/{}.jpg'.format(index))
		index += 1
		sio.emit(
			"move",
			data={
				'steer_angle': str(msg[0]),
				'torque': str(msg[1]),
				# 'd': str(msg[2]),
			},
			skip_sid=True
		)

app = socketio.Middleware(sio, app)
eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
