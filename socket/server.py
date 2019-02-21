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

import cv2
import numpy as np

sio = socketio.Server()
app = Flask(__name__)
index = 0

@sio.on('connect')
def connect(sid, environ):
	global index
	index = 0
	print("connect ", sid)
	sio.emit(
		"move",
		data={
			'torque': "0.0",
			'steer_angle': "0.0",
		},
		skip_sid=True
	)


@sio.on('telemetry')
def telemetry(sid, data):
	global index
	if data:
		image = np.array(Image.open(BytesIO(base64.b64decode(data['images']['front-facing-camera']))))
		image =  cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		car_s, car_d = data['s'], data['d']
		cv2.putText(image, "d: {}".format(d), (x-20, offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

		waypoints = data['waypoints']
		prev_lanes, lanes = [0] * 3, [0] * 3
		for j in range(3):
			prev_lanes[j] = (int(waypoints[0][j][2]), int(waypoints[0][j][3]))

		for i in range(1, len(waypoints)):
			for j in range(3):
				lanes[j] = (int(waypoints[i][j][2]), int(waypoints[i][j][3]))
				cv2.line(image, prev_lanes[j], lanes[j], (0, 255, 0), 2)

			prev_lanes = lanes[:]

		traffic_cars = data['traffic-cars']
		count = 0
		for car in traffic_cars:
			s, d, x, y, z = round(car[0], 2), round(car[1], 2), int(car[2]), int(car[3]), int(car[4])
			if x > 0 and y > 0 and z > 0 and s - car_s <= 60:
				offset = 30
				cv2.putText(image, "Car: {}".format(count), (x-20, offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
				cv2.putText(image, "x: {}, y: {}".format(x, y), (x-20, offset+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
				cv2.putText(image, "Depth: {}".format(z), (x-20, offset+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
				cv2.putText(image, "s: {}, d: {}".format(s, d), (x-20, offset+45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
				cv2.line(image, (x, offset+45), (x, y), (255, 0, 0), 1)

				count += 1

		cv2.imshow("Self-Driving Car's View", image)
		key = cv2.waitKey(1) & 0xFF

		index += 1
		sio.emit(
			"move",
			data={
				'torque': "0.0",
				'steer_angle': "0.0",
			},
			skip_sid=True
		)

app = socketio.Middleware(sio, app)
eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
