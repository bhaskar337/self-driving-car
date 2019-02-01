#real-time server
import socketio
#concurrent networking 
import eventlet
#web server gateway interface
import eventlet.wsgi
#web framework
from flask import Flask

from pid import PIDController

sio = socketio.Server()
app = Flask(__name__)
pid = PIDController()

throttle = 0.4
@sio.on('telemetry')
def telemetry(sid, data):
    global throttle
    if data:
        cte = float(data['cte'])
        steer_value = pid.update(cte)

        if abs(cte) >= 1:
            throttle -= 0.1
            throttle = max(throttle, 0.2)
        elif abs(cte) >= 0.5:
            throttle -= 0.05
            throttle = max(throttle, 0.3)
        else:
            throttle = 0.4

        sio.emit(
            'steer',
            data={
                'steering_angle': steer_value,
                'throttle': throttle,
            },
            skip_sid=True
        )

app = socketio.Middleware(sio, app)
eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
