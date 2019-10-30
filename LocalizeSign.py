"""
Dependencies:
- opencv
- utm (https://pypi.org/project/utm/)
- pandas
- numpy
- matplotlib

Input args:
	- file_object
	- file_trajectory
	- file_annotations
	- file_vehicle_coord

Usage:
python LocalizeSign.py Saving/ObjectMapSP1_2.txt Saving/KeyFrameTrajectorySP1_2.txt ../Desktop/SmartCityAI/SignLocalization/SmartPhone/1/sign_annotations.json ../Desktop/SmartCityAI/SignLocalization/SmartPhone/1/coords.csv

run LocalizeSign --sequence_folder Datasets/all_gather/interstate/curve/i75_ramp_1
run LocalizeSign --sequence_folder Datasets/all_gather/interstate/curve/i75_ramp_2

run LocalizeSign --sequence_folder Datasets/all_gather/interstate/straight/i75_1
run LocalizeSign --sequence_folder Datasets/all_gather/interstate/straight/i75_2
run LocalizeSign --sequence_folder Datasets/all_gather/interstate/straight/i75_3

run LocalizeSign --sequence_folder Datasets/all_gather/non-interstate/curve/northside_i75
run LocalizeSign --sequence_folder Datasets/all_gather/non-interstate/curve/techwood_10th
run LocalizeSign --sequence_folder Datasets/all_gather/non-interstate/curve/west_wesley

Note:
1. KeyframeTrajectory.txt format:
	trajectory_cols = ['ts', 't1', 't2', 't3', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9']

2. kf is pulled from df_objectMap

3. PlotImage() will fail if annotations.json is not synced with the images in the images/ folder


"""
import cv2
import utm
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json, sys, os
import argparse
# print(pd.__version__)

def LoadORBSLAMResults(file_object, file_trajectory):
	""" load vehicle trajectory and map points corresponding to traffic sign """
	with open(file_object) as f:
		if not f.read():
			print("Empty keyframe trajectory and object map. Re-run sequence?")
			return

	with open(file_object) as f:
		max_num_cols = max(len(line.split(" ")) for line in f)
	max_num_points = (max_num_cols - 2) / 3

	objectMap_cols = []
	objectMap_cols.append("ts")
	objectMap_cols.append("img")
	for i in range(max_num_points):
		objectMap_cols.append("x" + str(i + 1))
		objectMap_cols.append("y" + str(i + 1))
		objectMap_cols.append("z" + str(i + 1))

	trajectory_cols = ['ts', 't1', 't2', 't3', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9']

	df_objectMap = pd.read_csv(file_object, sep='\s+', header=None, names = objectMap_cols)
	df_trajectory = pd.read_csv(file_trajectory, sep='\s+', header=None, names = trajectory_cols)

	return df_objectMap, df_trajectory

def LoadAnnotations(file_annotations):
	""" load json annotations """
	with open(file_annotations) as f:
		d = json.load(f)
		annotations = d["output"]["frames"]
	return annotations

def LoadVehicleCoord(file_vehicle_coord):
	""" load vehicle trajectory (m) """
	## interstate/straight/i75_2
	# df_vehicle_coord = pd.read_csv(file_vehicle_coord,
	# 								sep='\t',
	# 								names=['image_name', 'lat', 'lon', 'x', 'y'],
	# 								skiprows=1)

	df_vehicle_coord = pd.read_csv(file_vehicle_coord,
									sep=',',
									names=['image_name', 'lat', 'lon', 'x', 'y'],
									skiprows=1)
	return df_vehicle_coord

def GetBoundingBox(annotations, kf_image):
	"""
	args:
		annotations: annotation list from the json file
		imagename: image filename, e.g. 001875.jpg
	returns:
		x, y, w, h : bounding box top left coordinates (x,y), width and height
	"""
	for ant in annotations:
		if ant["frame_number"] == kf_image:
			rois = ant["RoIs"].split(',')
			x = int(rois[1])
			y = int(rois[2])
			w = int(rois[3])
			h = int(rois[4])
			return x,y,w,h
	print("Warning: Image annotation not in annotations file.")
	return None

def PlotImage(annotations, imagename, kf_image):
	""" Plots bounding box in image """
	img = cv2.imread(imagename)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	x, y, w, h = GetBoundingBox(annotations, kf_image)
	cv2.rectangle(img, (x, y), (x+w, y+h), (0,255,0), 3)
	cv2.circle(img, (int(x+w/2), int(y+h/2)), int(max(h/2, w/2)), (255,0,0), 3)
	plt.rcParams['figure.figsize'] = (16, 8)
	plt.imshow(img)
	plt.show()

def main(file_object, file_trajectory, file_annotations, file_vehicle_coord):
	"""
	Main pipeline to localize traffic sign using the results from ORB-SLAM.
	"""

	print("file_object: %s" % file_object)
	print("file_trajectory: %s" % file_trajectory)
	print("file_annotations: %s" % file_annotations)
	print("file_vehicle_coord: %s" % file_vehicle_coord)


	## Load Data
	orbslam_result = LoadORBSLAMResults(file_object, file_trajectory)
	if orbslam_result is None:
		return
	else:
		df_objectMap = orbslam_result[0]
		df_trajectory = orbslam_result[1]
	annotations = LoadAnnotations(file_annotations)
	df_vehicle_coord  = LoadVehicleCoord(file_vehicle_coord)


	## Get candidate key-frame (closest to sign)
	kf_image = df_objectMap.iloc[-1].img
	kf_timestamp = df_objectMap.loc[df_objectMap.img == kf_image].ts
	kf_timestamp = kf_timestamp.values[0]
	imagename = os.path.join(os.path.split(file_vehicle_coord)[0] + "/images", kf_image)
	print("imagename: %s" % imagename)


	PlotImage(annotations, imagename, kf_image)


	## Get scale factor (use first two key-frames)
	kf_1 = df_objectMap["img"][0]
	kf_2 = df_objectMap["img"][1]



	## Compute baseline in metres
	x_v_kf1 = float(df_vehicle_coord[df_vehicle_coord["image_name"] == kf_1].x)
	y_v_kf1 = float(df_vehicle_coord[df_vehicle_coord["image_name"] == kf_1].y)
	x_v_kf2 = float(df_vehicle_coord[df_vehicle_coord["image_name"] == kf_2].x)
	y_v_kf2 = float(df_vehicle_coord[df_vehicle_coord["image_name"] == kf_2].y)
	baseline_m = np.linalg.norm(np.array([x_v_kf1, y_v_kf1]) - np.array([x_v_kf2, y_v_kf2]))



	## Compute baseline in ORB-SLAM units
	t = np.array([df_trajectory.iloc[1].t1, df_trajectory.iloc[1].t2, df_trajectory.iloc[1].t3 ])
	baseline_slam = np.linalg.norm(t)
	scale_factor = baseline_m / baseline_slam
	print("baseline (m): %f" % baseline_m)
	print("baseline (orbslam): %f" % baseline_slam)
	print("scale factor: %f" % scale_factor)



	## Get object points with respect to chosen key-frame (average over all points)
	p_object_avg = df_objectMap.loc[df_objectMap.ts == kf_timestamp, 'x1': df_objectMap.columns[-1]].values.reshape(-1, 3)
	p_object_avg = np.nanmean(p_object_avg, axis=0)


	## Extract camera pose of chosen key-frame
	t_kf_wc = np.hstack([df_trajectory[df_trajectory.ts == kf_timestamp].t1.values,
                         df_trajectory[df_trajectory.ts == kf_timestamp].t2.values,
                         df_trajectory[df_trajectory.ts == kf_timestamp].t3.values])
	R_kf_wc = df_trajectory.loc[df_trajectory.ts == kf_timestamp, 'R1':'R9'].values.reshape(3,3)
	# print("t_kf_wc: ", t_kf_wc)
	print("R_kf_wc: ", R_kf_wc)

	p1_m = scale_factor * (np.dot(np.linalg.inv(R_kf_wc), p_object_avg) - t_kf_wc)
	print("p_object_avg: ", p_object_avg)
	print("p1_m: ", p1_m)



	## Get gps coordinates of vehicle at keyframe timestamp
	p_v_locate = np.hstack([df_vehicle_coord[df_vehicle_coord.image_name == kf_image].x.values,
	                        df_vehicle_coord[df_vehicle_coord.image_name == kf_image].y.values])
	sign_x_coord = p_v_locate[0] + p1_m[0]
	sign_y_coord = p_v_locate[1] + p1_m[2]

	print("Vehicle UTM16N: (%f, %f)" % (p_v_locate[0], p_v_locate[1]))
	print("Sign UTM16N: (%f, %f)"  % (sign_x_coord, sign_y_coord))
	sign_latlon = utm.to_latlon(sign_x_coord, sign_y_coord, 16, 'S')
	print("Sign LAT-LON: (%f, %f)" % (sign_latlon[0], sign_latlon[1]))

	# todo: write to .csv file
	# image_name | sign_id | x | y | width | height | lat | lon | method | comments | side | lat_pred | lon_pred | error (meters)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--sequence_folder", help="path_to_sequence_folder")
	args = parser.parse_args()
	if len(sys.argv) < 2:
		raise ValueError("Usage: python LocalizeSign path_to_sequence_folder")
	else:
		file_object = os.path.join(args.sequence_folder, "ObjectMap.txt")
		file_trajectory = os.path.join(args.sequence_folder, "KeyFrameTrajectory.txt")
		file_annotations = os.path.join(args.sequence_folder, "sign_annotations.json")
		file_vehicle_coord = os.path.join(args.sequence_folder, "coords.csv")
		main(file_object, file_trajectory, file_annotations, file_vehicle_coord)
