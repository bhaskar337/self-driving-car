
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