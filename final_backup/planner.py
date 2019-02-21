from scipy import interpolate
from pid import PIDController

lane_width = 4
max_safe_speed = 39.5
safety_margin = 20


class Vehicle:
	def __init__(self, vehicle_arr):
		self.s = vehicle_arr[0]
		self.d = vehicle_arr[1]
		self.lane = int(self.d / lane_width)

	def is_too_close(self, m_car_s):
		# if vehicle is front of main m_car and is within safety margin
		return (self.s > m_car_s) and (self.s - m_car_s < safety_margin)

	def is_too_close_to_change(self, m_car_s):
		return (self.s > m_car_s - safety_margin / 2) and (self.s < m_car_s + safety_margin / 2)

	def is_on_same_lane(self, m_car_lane):
		return self.lane == m_car_lane

	def is_on_left_lane(self, m_car_lane):
		return self.lane == m_car_lane + 1

	def is_on_right_lane(self, m_car_lane):
		return self.lane == m_car_lane - 1


class Planner:
	def __init__(self):
		self.pid = PIDController()
		self.tck = None
		self.lane = 1
		self.prev_s = 0
		self.d = 6
		self.is_changing_lanes = False


	def plan(self, data):
		# getting data from socket
		car_x, car_y = float(data['x']), float(data['y'])
		car_s, car_d = float(data['s']), float(data['d'])
		speed = float(data['speed'])
		traffic_cars = [Vehicle(i) for i in data['traffic-cars']]

		is_too_close = False
		prepare_for_lane_change = False
		ready_for_lane_change = False
		is_left_lane_free = self.lane < 2
		is_right_lane_free = self.lane > 0
		left_lane_clearance = 0 
		right_lane_clearance = 0

		# check if lane change is needed
		for vehicle in traffic_cars:
			if vehicle.is_on_same_lane(self.lane) and vehicle.is_too_close(car_s):
				is_too_close = True
				prepare_for_lane_change = True
				break

		# check which adjacent lane (left / right) is free for lane change
		if not self.is_changing_lanes and prepare_for_lane_change:
			for vehicle in traffic_cars:
				if is_left_lane_free and vehicle.is_on_left_lane(self.lane):
					is_left_lane_free = not vehicle.is_too_close_to_change(car_s)
					left_lane_clearance = min(left_lane_clearance, vehicle.s - car_s)

				elif is_right_lane_free and vehicle.is_on_right_lane(self.lane):
					is_right_lane_free = not vehicle.is_too_close_to_change(car_s)
					right_lane_clearance = min(right_lane_clearance, vehicle.s - car_s)	

				if is_left_lane_free or is_right_lane_free:
					ready_for_lane_change = True

		# initialize change of lanes if ready for lane change and if any adjancent lane is free
		if not self.is_changing_lanes:
			if ready_for_lane_change:
				print(left_lane_clearance, right_lane_clearance)
				if is_right_lane_free and (is_left_lane_free and right_lane_clearance >= left_lane_clearance):
					self.lane -= 1
					pts_d = [car_d] + [car_d - lane_width] * 3
					self.is_changing_lanes = True

				elif is_left_lane_free:
					self.lane += 1
					pts_d = [car_d] + [car_d + lane_width] * 3
					self.is_changing_lanes = True

			if self.is_changing_lanes:
				self.tck = interpolate.splrep([0, 30, 60, 90], pts_d)
				self.prev_s = car_s
				print('New Lane: ', self.lane)

		else:
			if self.prev_s > car_s:
				dist = 509 - self.prev_s + car_s 
			else:
				dist = car_s - self.prev_s

			# if car has reached sufficiently close to target d, we stop
			if abs(self.lane * lane_width + 2 - car_d) <= 0.2:
				print('Reached lane ', self.lane)
				self.is_changing_lanes = False   

			else:
				self.d = interpolate.splev(dist, self.tck)


		# calculate steer angle with pid controller
		cte = self.d - car_d
		steer_val = self.pid.update(cte)


		# regulate throttle based on speed
		if speed >= max_safe_speed:
			torque = 0
		elif 30 <= speed < 40:
			torque = 0.4	
		elif 20 <= speed < 30:
			torque = 0.6
		else:
		 	torque = 0.8

		torque -= cte / 4

		if is_too_close:
		 	torque = 0

		# print(self.lane, self.is_changing_lanes, self.d, car_d, abs(self.lane * lane_width + 2 - car_d))
		# print(is_too_close, is_left_lane_free, is_right_lane_free, '\n')
		return steer_val, torque