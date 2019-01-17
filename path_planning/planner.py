from scipy import interpolate
from utils import *

lane = 1
ref_vel = 0

class Planner:
	def __init__(self):
		pass

	def plan(self, data):
		global lane, ref_vel

		car_x, car_y = data['x'], data['y']
		car_s, car_d = data['s'], data['d']
		car_yaw = data['yaw']
		car_speed = data['speed']

		previous_path_x = data['previous_path_x']
		previous_path_y = data['previous_path_y']

		end_path_s = data['end_path_s']
		end_path_y = data['end_path_d']

		sensor_fusion = data['sensor_fusion']

		prev_size = len(previous_path_x)
		if prev_size > 0:
			car_s = end_path_s
		
		is_too_close = False
		prepare_for_lane_change = False
		ready_for_lane_change = False
		is_left_lane_free = True
		is_right_lane_free = True

		for i in sensor_fusion:
			vehicle = Vehicle(i)
			if vehicle.is_in_lane(lane):
				vehicle.s = prev_size * 0.02 * vehicle.speed
				is_in_front_of_us = vehicle.s > car_s
				is_closer_than_safety_margin = vehicle.s - car_s < safety_margin

				if is_in_front_of_us and is_closer_than_safety_margin:
					is_too_close = True
					prepare_for_lane_change = True
					# break

		if prepare_for_lane_change:
			num_vehicles_left, num_vehicles_right = 0, 0
			for i in sensor_fusion:
				vehicle = Vehicle(i)
				if vehicle.is_in_lane(lane - 1):
					num_vehicles_left += 1
					vehicle.s = prev_size * 0.02 * vehicle.speed
					too_close_to_change = (vehicle.s > car_s - safety_margin / 2) and (vehicle.s < car_s + safety_margin / 2)
					if too_close_to_change:
						is_left_lane_free = False

				elif vehicle.is_in_lane(lane + 1):
					num_vehicles_right += 1
					vehicle.s = prev_size * 0.02 * vehicle.speed
					too_close_to_change = (vehicle.s > car_s - safety_margin / 2) and (vehicle.s < car_s + safety_margin / 2)
					if too_close_to_change:
						is_right_lane_free = True

				if is_left_lane_free or is_right_lane_free:
					ready_for_lane_change = False
					# break

		if ready_for_lane_change and is_left_lane_free and lane > 0:
			lane -= 1
		elif ready_for_lane_change and is_right_lane_free and lane < 2:
			lane += 1

		if is_too_close:
			ref_vel -= 0.224
		elif ref_vel < max_safe_speed:
			ref_vel += 0.224

		pts_x, pts_y = [], []
		ref_x, ref_y = car_x, car_y
		ref_yaw = math.radians(car_yaw)

		if prev_size < 2:
			prev_car_x = car_x - math.cos(car_yaw)
			prev_car_y = car_y - math.sin(car_yaw)

			pts_x += [prev_car_x, car_x]
			pts_y += [prev_car_y, car_y]
		else:
			ref_x = previous_path_x[prev_size - 1]
			ref_y = previous_path_y[prev_size - 1]

			ref_x_prev = previous_path_x[prev_size - 2]
			ref_y_prev = previous_path_y[prev_size - 2]
			ref_yaw = math.atan2(ref_y - ref_y_prev, ref_x - ref_x_prev)

			pts_x += [ref_x_prev, ref_x]
			pts_y += [ref_y_prev, ref_y]

		wp0 = frenet_to_cartesian(car_s + 30, lane_width * lane + lane_width / 2)
		wp1 = frenet_to_cartesian(car_s + 60, lane_width * lane + lane_width / 2)
		wp2 = frenet_to_cartesian(car_s + 90, lane_width * lane + lane_width / 2)

		pts_x += [wp0[0], wp1[0], wp2[0]]
		pts_y += [wp0[1], wp1[1], wp2[1]]

		for i in range(len(pts_x)):
			shift_x = pts_x[i] - ref_x
			shift_y = pts_y[i] - ref_y
			pts_x[i] = shift_x * math.cos(0-ref_yaw) - shift_y * math.sin(0-ref_yaw)
			pts_y[i] = shift_y * math.sin(0-ref_yaw) + shift_y * math.cos(0-ref_yaw)

		tck = interpolate.splrep(pts_x, pts_y)
		next_x_vals = previous_path_x[:]
		next_y_vals = previous_path_y[:]

		target_x = 30
		target_y = interpolate.splev(target_x, tck)
		target_dist = math.sqrt(target_x ** 2 + target_y ** 2)
		x_add_on = 0
		
		for i in range(1, 51 - len(previous_path_x)):
			n = target_dist / (0.02 * ref_vel / 2.24)
			x_point = x_add_on + target_x / n 
			y_point = interpolate.splev(x_point, tck)

			x_add_on = x_point
			x_ref, y_ref = x_point, y_point

			x_point = x_ref * math.cos(ref_yaw) - y_ref * math.sin(ref_yaw)
			y_point = x_ref * math.sin(ref_yaw) + y_ref * math.cos(ref_yaw)

			x_point += ref_x
			y_point += ref_y

			next_x_vals.append(x_point)
			next_y_vals.append(y_point)

		print(next_x_vals)
		print(next_y_vals)
		print()

		msg = {
			'next_x': next_x_vals,
			'next_y': next_y_vals
		}
		return msg


	def change_lane(self):
		pass



# pl = Planner()
# data = {
#   "s": 124.8336,
#   "y": 1128.67,
#   "end_path_s": 0,
#   "end_path_d": 0,
#   "previous_path_y": [],
#   "sensor_fusion": [
#     [
#       0,
#       817.6062,
#       1132.905,
#       23.5875,
#       -0.2455978,
#       33.01413,
#       2.023479
#     ],
#     [
#       1,
#       1029.072,
#       1152.99,
#       17.08941,
#       7.069682,
#       245.8449,
#       5.990943
#     ],
#     [
#       2,
#       775.8,
#       1429,
#       0,
#       0,
#       6716.599,
#       -282.9019
#     ],
#     [
#       3,
#       775.8,
#       1432.9,
#       0,
#       0,
#       6713.911,
#       -285.7268
#     ],
#     [
#       4,
#       775.8,
#       1436.3,
#       0,
#       0,
#       6711.566,
#       -288.1896
#     ],
#     [
#       5,
#       775.8,
#       1441.7,
#       0,
#       0,
#       6661.772,
#       -291.7797
#     ],
#     [
#       6,
#       762.1,
#       1421.6,
#       0,
#       0,
#       6711.778,
#       -268.0964
#     ],
#     [
#       7,
#       762.1,
#       1425.2,
#       0,
#       0,
#       6709.296,
#       -270.7039
#     ],
#     [
#       8,
#       762.1,
#       1429,
#       0,
#       0,
#       6663.543,
#       -273.1828
#     ],
#     [
#       9,
#       762.1,
#       1432.9,
#       0,
#       0,
#       6660.444,
#       -275.5511
#     ],
#     [
#       10,
#       762.1,
#       1436.3,
#       0,
#       0,
#       6657.743,
#       -277.6157
#     ],
#     [
#       11,
#       762.1,
#       1441.7,
#       0,
#       0,
#       6653.453,
#       -280.8947
#     ]
#   ],
#   "previous_path_x": [],
#   "speed": 0,
#   "yaw": 0,
#   "x": 909.48,
#   "d": 6.164833
# }
# print(pl.plan(data))