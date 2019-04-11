import numpy as np
from scipy import interpolate, optimize
import time

ref_v = 70

N = 10
dt = 0.1
Lf = 2.67

# cost weights
cte_weight = 2000
epsi_weight = 2000
v_weight = 100
actuator_cost_weight = 10
change_steer_cost_weight = 100000
change_acc_cost_weight = 10000


class MPC:

	def objective(self, vars):
	    cost = 0
	    for i in range(N):
	        if i == 0:
	        	# intialize variables
	            path = self.path
	            x = self.x
	            y = self.y
	            psi = self.psi
	            v = self.v
	            cte = self.cte
	            epsi = self.epsi
	          
	        # direct actuator_cost_weight
	        cost += cte_weight * (cte) ** 2
	        cost += epsi_weight * (epsi) ** 2
	        cost += v_weight * (v - ref_v) ** 2

	        # since there are N - 1 acctuators
	        if i == N - 1:
	            return cost
	        
	        delta = vars[i]
	        a = vars[i + N - 1]

	        # cost due to magnitude of actuators
	        cost += actuator_cost_weight * (delta) ** 2
	        cost += actuator_cost_weight * (a) ** 2

	        if i != 0:
	        	# cost due to change in magnitude of actuators
	            cost += change_steer_cost_weight * (delta - prev_delta) ** 2
	            cost += change_acc_cost_weight * (a - prev_a) ** 2

	        prev_delta = delta
	        prev_a = a

	        # calculate values for next iteration
	        f = path(x)
	        psides = np.arctan(path(x, 1))

	        # kinematic bicycle model
	        x = x + v * np.cos(psi) * dt
	        y = y + v * np.sin(psi) * dt
	        psi = psi - v * delta / Lf * dt
	        v = v + a * dt
	        cte = f - y + v * np.sin(epsi) * dt
	       	epsi = psi - psides - v * delta / Lf * dt


	def control(self, delta, a, x, y, psi, v, cte, epsi, path):
		self.x = x 
		self.y = y
		self.psi = psi
		self.v = v
		self.cte = cte
		self.epsi = epsi
		self.path = path

		n_vars = (N - 1) * 2
		bounds = [None] * n_vars
		vars = [0] * n_vars

		bounds[0] = (delta, delta)
		max_radians = 25 * np.pi / 180
		for i in range(1, N - 1):
		    bounds[i] = (-max_radians, max_radians)

		bounds[N-1] = (a, a)
		max_acc_value = 1.0
		for i in range(N, n_vars):
		    bounds[i] = (-max_acc_value, max_acc_value)

		solution = optimize.minimize(self.objective, vars, bounds=bounds)
		return solution.x[1], solution.x[N]




# ptsx = [float(i) for i in data['ptsx']]
# ptsy = [float(i) for i in data['ptsy']]
# x = float(data['x'])
# y = float(data['y'])
# psi = float(data['psi'])
# v = float(data['v'])
# delta = float(data['delta'])
# a = float(data['a'])

# for i in range(len(ptsx)):
# 	shift_x = ptsx[i] - px 
# 	shift_y = ptsy[i] - py

# 	ptsx[i] = shift_x * np.cos(-psi) - shift_y * np.sin(-psi)
# 	ptsy[i] = shift_x * np.sin(-psi) + shift_y * np.cos(-psi)


# path = interpolate.CubicSpline(ptsx, ptsy)
# cte = path(0)
# epsi = psi - np.arctan(path(0, 1))

# mpc = MPC()
# mpc.control(delta, a, 0, 0, psi, v, cte, epsi, path)

