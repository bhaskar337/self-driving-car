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

from mpc import MPC


sio = socketio.Server()
app = Flask(__name__)
mpc = MPC()


@sio.on('connect')
def connect(sid, environ):
	global planner
	planner = Planner()
	print("connect ", sid)
	sio.emit(
		'control',
		data={
			'steer_angle': "0.0",
			'torque': "0.0",
		},
		skip_sid=True
	)


@sio.on('telemetry')
def telemetry(sid, data):
	if data:
		print(data)
		return
		ptsx = [float(i) for i in data['ptsx']]
		ptsy = [float(i) for i in data['ptsy']]
		x = float(data['x'])
		y = float(data['y'])
		psi = float(data['psi'])
		v = float(data['v'])
		delta = float(data['delta'])
		a = float(data['a'])

		for i in range(len(ptsx)):
			shift_x = ptsx[i] - px 
			shift_y = ptsy[i] - py

			ptsx[i] = shift_x * np.cos(-psi) - shift_y * np.sin(-psi)
			ptsy[i] = shift_x * np.sin(-psi) + shift_y * np.cos(-psi)

		path = interpolate.CubicSpline(ptsx, ptsy)
		cte = path(0)
		epsi = psi - np.arctan(path(0, 1))
		delta, a = mpc.control(delta, a, 0, 0, psi, v, cte, epsi, path)

		sio.emit(
			'control',
			data={
				'steer_angle': str(delta),
				'torque': str(a),
			},
			skip_sid=True
		)

app = socketio.Middleware(sio, app)
eventlet.wsgi.server(eventlet.listen(('', 4567)), app)