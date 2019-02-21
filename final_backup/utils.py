import csv
import math 

lane_width = 4
safety_margin = 20
max_safe_speed = 49.5


class Vehicle:
	def __init__(self, sensor_fusion):
		self.vel_x = sensor_fusion[3]
		self.vel_y = sensor_fusion[4]
		self.s = sensor_fusion[5]
		self.d = sensor_fusion[6]
		self.speed = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2)

	def is_in_lane(self, lane):
		return (self.d > lane_width * lane) and (self.d < lane_width * lane + lane_width)


map_x, map_y, map_s = [], [], []
with open('highway_map.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=' ')
	for row in csv_reader:
		map_x.append(float(row[0]))
		map_y.append(float(row[1]))
		map_s.append(float(row[2]))


def frenet_to_cartesian(s, d):
	prev_wp = -1 

	while s > map_s[prev_wp + 1] and prev_wp < (len(map_s) - 1):
		prev_wp += 1

	wp2 = (prev_wp + 1) % len(map_x)

	heading = math.atan2(map_y[wp2] - map_y[prev_wp], map_x[wp2] - map_x[prev_wp])
	seg_s = s - map_s[prev_wp]
	seg_x = map_x[prev_wp] + seg_s * math.cos(heading)
	seg_y = map_y[prev_wp] + seg_s * math.sin(heading)

	perp_heading = heading - math.pi / 2
	x = seg_x + d * math.cos(perp_heading)
	y = seg_y + d * math.sin(perp_heading)

	return x, y