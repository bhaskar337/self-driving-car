#real-time server
import socketio
#concurrent networking 
import eventlet
#web server gateway interface
import eventlet.wsgi
#web framework
from flask import Flask

from planner import Planner

sio = socketio.Server()
app = Flask(__name__)
planner = Planner()


@sio.on('telemetry')
def telemetry(sid, data):
	if data:
		msg = planner.plan(data)
		sio.emit(
			'control',
			data=msg,
			skip_sid=True
		)

app = socketio.Middleware(sio, app)
eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
