from scipy import interpolate
# from utils import *
import matplotlib.pyplot as plt
from plot import *


class PIDController:
    def __init__(self):
    	self.kp = 0.05
    	self.ki = 0.0001
    	self.kd = 1.5

    	self.p_error = 0
    	self.i_error = 0
    	self.d_error = 0


    def update(self, cte):
    	self.i_error += cte
    	self.d_error = cte - self.p_error
    	self.p_error = cte

    	return -(self.kp * self.p_error + self.ki * self.i_error + self.kd * self.d_error)


lane = 1
ref_vel = 0
lane_width = 4
safety_margin = 20
max_safe_speed = 49.5
d = 6
is_channging_lanes = False
last_s = None
tck = None


class Vehicle:
	def __init__(self, vehicle_arr):
		self.s = vehicle_arr[0]
		self.d = vehicle_arr[1]
		self.lane = int(self.d / lane_width)
		# self.speed = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2)


throttle = 0.4
class Planner:
	def __init__(self):
		self.pid = PIDController()
		self.pid_speed = PIDController()
		self.i = 0
		self.speed = 0


	def plan(self, data):
		global tck, lane, ref_vel, throttle, d, is_channging_lanes, last_s
		car_x, car_y = float(data['x']), float(data['y'])
		car_s, car_d = float(data['s']), float(data['d'])
		speed = float(data['speed'])
		traffic_cars = data['traffic-cars']

		# lane = int(d / lane_width)
	
		# wp0_x, wp0_y = data['wp0_x'], data['wp0_y']
		# wp1_x, wp1_y = data['wp1_x'], data['wp1_y']
		# wp2_x, wp2_y = data['wp2_x'], data['wp2_y']

		# pts_x = [car_x, wp0_x, wp1_x, wp2_x]
		# pts_y = [car_y, wp0_x]

		is_too_close = False
		prepare_for_lane_change = False
		ready_for_lane_change = False
		is_left_lane_free = True
		is_right_lane_free = True

		for i in traffic_cars:
			vehicle = Vehicle(i)
			if vehicle.lane == lane:
				# vehicle.s += prev_size * 0.02 * vehicle.speed
				is_in_front_of_us = vehicle.s > car_s
				is_closer_than_safety_margin = vehicle.s - car_s < safety_margin
		
				if is_in_front_of_us and is_closer_than_safety_margin:
					is_too_close = True
					prepare_for_lane_change = True
					# break


		if prepare_for_lane_change:
			num_vehicles_left, num_vehicles_right = 0, 0
			for i in traffic_cars:
				vehicle = Vehicle(i)
				if vehicle.lane == lane + 1:
					# vehicle.s = prev_size * 0.02 * vehicle.speed
					too_close_to_change = (vehicle.s < car_s + safety_margin / 2) and (vehicle.s > car_s + 5)
					if too_close_to_change:
						is_left_lane_free = False

				elif vehicle.lane == lane - 1:
					# vehicle.s = prev_size * 0.02 * vehicle.speed
					too_close_to_change = (vehicle.s < car_s + safety_margin / 2) and (vehicle.s > car_s + 5)
					if too_close_to_change:
						is_right_lane_free = False


				if is_left_lane_free or is_right_lane_free:
					ready_for_lane_change = True
					# break

		if not is_channging_lanes:
			if ready_for_lane_change and is_right_lane_free and lane > 0:
				lane -= 1
				pts_x = [d, d-4, d-4, d-4]
				pts_y = [0, 20, 40, 60,]
				tck = interpolate.splrep(pts_y, pts_x)
				last_s = car_s
				is_channging_lanes = True

			elif ready_for_lane_change and is_left_lane_free and lane < 2:
				lane += 1
				pts_x = [d, d+4, d+4, d+4]
				pts_y = [0, 20, 40, 60,]
				tck = interpolate.splrep(pts_y, pts_x)
				last_s = car_s
				is_channging_lanes = True
		else:
			if last_s > car_s:
				dist = 509 - last_s + car_s 
			else:
				dist = car_s - last_s
			if dist >= 90:
				is_channging_lanes = False

			d = interpolate.splev(dist, tck)

		if is_channging_lanes:
			 with open('points.txt', 'w') as f:
			 	for x, y in zip(pts_x, pts_y):
			 		f.write('{},{}\n'.format(x, y))


		max_speed = 39.5
		if speed >= max_speed:
			throttle = 0
		elif 30 <= speed < 40:
			throttle = 0.4	
		elif 20 <= speed < 30:
			throttle = 0.6
		else:
		 	throttle = 0.8

		if is_too_close:
			throttle = 0
			if lane == 0:
				if self.speed > 50:
					self.speed -= 1
				elif self.speed < 50:
					self.speed += 1
				self.speed = 50
			elif lane == 1:
				if self.speed > 40:
					self.speed -= 1
				elif self.speed < 40:
					self.speed += 1
			else:
				if self.speed > 30:
					self.speed -= 1

		elif self.speed < 80:
			self.speed += 1


		cte = d - car_d
		steer_val = self.pid.update(cte)


		

		# if lane == 0:
		# 	if d >= 2:
		# 		d -= 0.1
		# elif lane == 1:
		# 	if d > 6:
		# 		d -= 0.1
		# 	elif d < 6:
		# 		d += 0.1
		# elif lane == 2:
		# 	if d <= 10:
		# 		d += 0.1

		# wp0 = frenet_to_cartesian(car_s + 30, lane_width * lane + lane_width / 2)
		# wp1 = frenet_to_cartesian(car_s + 60, lane_width * lane + lane_width / 2)
		# wp2 = frenet_to_cartesian(car_s + 90, lane_width * lane + lane_width / 2)


		# print(lane)
		# if is_too_close:
		# 	d += 0.1
		# 	steer_val = -1
		# throttle = 0.5 #self.speed
		return steer_val, throttle, d

		# print(car_d)
		# car_yaw = data['yaw']
		# car_speed = data['speed']

		# previous_path_x = data['previous_path_x']
		# previous_path_y = data['previous_path_y']

		# end_path_s = data['end_path_s']
		# end_path_y = data['end_path_d']

		# sensor_fusion = data['sensor_fusion']

		# prev_size = len(previous_path_x)
		# if prev_size > 0:
		# 	car_s = end_path_s
		
		# is_too_close = False
		# prepare_for_lane_change = False
		# ready_for_lane_change = False
		# is_left_lane_free = True
		# is_right_lane_free = True
		# for i in sensor_fusion:
		# 	vehicle = Vehicle(i)
		# 	if vehicle.is_in_lane(lane):
		# 		vehicle.s += prev_size * 0.02 * vehicle.speed
		# 		is_in_front_of_us = vehicle.s > car_s
		# 		is_closer_than_safety_margin = vehicle.s - car_s < safety_margin
		
		# 		if is_in_front_of_us and is_closer_than_safety_margin:
		# 			is_too_close = True
		# 			prepare_for_lane_change = True
		# 			# break

		# if prepare_for_lane_change:
		# 	num_vehicles_left, num_vehicles_right = 0, 0
		# 	for i in sensor_fusion:
		# 		vehicle = Vehicle(i)
		# 		if vehicle.is_in_lane(lane - 1):
		# 			num_vehicles_left += 1
		# 			vehicle.s = prev_size * 0.02 * vehicle.speed
		# 			too_close_to_change = (vehicle.s > car_s - safety_margin / 2) and (vehicle.s < car_s + safety_margin / 2)
		# 			if too_close_to_change:
		# 				is_left_lane_free = False

		# 		elif vehicle.is_in_lane(lane + 1):
		# 			num_vehicles_right += 1
		# 			vehicle.s = prev_size * 0.02 * vehicle.speed
		# 			too_close_to_change = (vehicle.s > car_s - safety_margin / 2) and (vehicle.s < car_s + safety_margin / 2)
		# 			if too_close_to_change:
		# 				is_right_lane_free = True

		# 		if is_left_lane_free or is_right_lane_free:
		# 			ready_for_lane_change = True
		# 			# break

		# if ready_for_lane_change and is_left_lane_free and lane > 0:
		# 	lane -= 1
		# elif ready_for_lane_change and is_right_lane_free and lane < 2:
		# 	lane += 1

		# if is_too_close:
		# 	ref_vel -= 0.224
		# elif ref_vel < max_safe_speed:
		# 	ref_vel += 0.224

		# pts_x, pts_y = [], []
		# ref_x, ref_y = car_x, car_y
		# ref_yaw = math.radians(car_yaw)

		# if prev_size < 2:
		# 	prev_car_x = car_x - math.cos(ref_yaw)
		# 	prev_car_y = car_y - math.sin(ref_yaw)

		# 	pts_x += [prev_car_x, car_x]
		# 	pts_y += [prev_car_y, car_y]
		# else:
		# 	ref_x = previous_path_x[prev_size - 1]
		# 	ref_y = previous_path_y[prev_size - 1]

		# 	ref_x_prev = previous_path_x[prev_size - 2]
		# 	ref_y_prev = previous_path_y[prev_size - 2]
		# 	ref_yaw = math.atan2(ref_y - ref_y_prev, ref_x - ref_x_prev)

		# 	pts_x += [ref_x_prev, ref_x]
		# 	pts_y += [ref_y_prev, ref_y]

		# wp0 = frenet_to_cartesian(car_s + 30, lane_width * lane + lane_width / 2)
		# wp1 = frenet_to_cartesian(car_s + 60, lane_width * lane + lane_width / 2)
		# wp2 = frenet_to_cartesian(car_s + 90, lane_width * lane + lane_width / 2)

		# pts_x += [wp0[0], wp1[0], wp2[0]]
		# pts_y += [wp0[1], wp1[1], wp2[1]]

		# for i in range(len(pts_x)):
		# 	shift_x = pts_x[i] - ref_x
		# 	shift_y = pts_y[i] - ref_y
		# 	pts_x[i] = shift_x * math.cos(-ref_yaw) - shift_y * math.sin(-ref_yaw)
		# 	pts_y[i] = shift_x * math.sin(-ref_yaw) + shift_y * math.cos(-ref_yaw)

		# tck = interpolate.splrep(pts_x, pts_y)
		# next_x_vals = previous_path_x[:]
		# next_y_vals = previous_path_y[:]

		# target_x = 30
		# target_y = interpolate.splev(target_x, tck)
		# target_dist = math.sqrt(target_x ** 2 + target_y ** 2)
		# x_add_on = 0
		
		# for i in range(1, 51 - len(previous_path_x)):
		# 	n = target_dist / (0.02 * ref_vel / 2.24)
		# 	x_point = x_add_on + target_x / n 
		# 	y_point = interpolate.splev(x_point, tck)

		# 	x_add_on = x_point
		# 	x_ref, y_ref = x_point, y_point

		# 	x_point = x_ref * math.cos(ref_yaw) - y_ref * math.sin(ref_yaw)
		# 	y_point = x_ref * math.sin(ref_yaw) + y_ref * math.cos(ref_yaw)

		# 	x_point += ref_x
		# 	y_point += ref_y

		# 	next_x_vals.append(x_point)
		# 	next_y_vals.append(y_point)

		# msg = {
		# 	'next_x': next_x_vals,
		# 	'next_y': next_y_vals
		# }
		# return msg


	def change_lane(self):
		pass