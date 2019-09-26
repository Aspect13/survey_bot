import math
from pathlib import Path
from uuid import uuid4


def get_unique_file_name(directory, extension, uuid_length=8):
	generate = lambda: '{}.{}'.format(str(uuid4())[:uuid_length], extension)
	file_name = generate()
	while Path.exists(Path(directory, file_name)):
		file_name = generate()
	return file_name


def get_distance(lat1, lon1, lat2=55.751244, lon2=37.618423):
	# Haversine formula
	lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
	delta_lon = lon2 - lon1
	delta_lat = lat2 - lat1
	ssq_delta_lat = math.pow(math.sin(delta_lat / 2), 2)
	ssq_delta_lon = math.pow(math.sin(delta_lon / 2), 2)
	# a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
	a = ssq_delta_lat + math.cos(lat1) * math.cos(lat2) * ssq_delta_lon
	c = 2 * math.asin(math.sqrt(a))
	earth_radius = 6371  # 3956 miles
	return earth_radius * c
