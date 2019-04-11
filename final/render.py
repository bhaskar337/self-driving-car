#decoding camera images
import base64
#image manipulation
from PIL import Image
#input output
from io import BytesIO

import cv2
import numpy as np


def render(data):
	image = np.array(Image.open(BytesIO(base64.b64decode(data['images']['front-facing-camera']))))
	image =  cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	car_s, car_d = data['s'], data['d']

	waypoints = data['waypoints']
	prev_lanes, lanes = [0] * 4, [0] * 4
	x, y = [], []
	for wp in waypoints:
		x.append(wp[0][0])
		y.append(wp[0][1])

	for j in range(4):
		prev_lanes[j] = (int(waypoints[0][j][2]), int(waypoints[0][j][3]))

	for i in range(1, len(waypoints)):
		for j in range(4):
			lanes[j] = (int(waypoints[i][j][2]), int(waypoints[i][j][3]))
			if lanes[j][0] > 0 and lanes[j][1] > 0 and lanes[j][0] < 640 and lanes[j][1] < 320:
				cv2.line(image, prev_lanes[j], lanes[j], (0, 255, 0), 2)

		prev_lanes = lanes[:]

	traffic_cars = data['traffic-cars']
	count = 0
	for i, car in enumerate(traffic_cars):
		s, d, x, y, z = round(car[0], 2), round(car[1], 2), int(car[2]), int(car[3]), int(car[4])
		if x > 0 and y > 0 and z > 0 and 0 <= s - car_s <= 60:
			offset = 30
			cv2.putText(image, "Car: {}".format(count), (x-20, offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
			cv2.putText(image, "x: {}, y: {}".format(x, y), (x-20, offset+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
			cv2.putText(image, "Depth (z): {}".format(z), (x-20, offset+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
			cv2.putText(image, "s: {}, d: {}".format(round(s - car_s, 2), d), (x-20, offset+45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
			cv2.line(image, (x, offset+45), (x, y), (255, 0, 0), 1)

			count += 1

	cv2.imshow("Self-Driving Car's View", image)
	key = cv2.waitKey(1) & 0xFF