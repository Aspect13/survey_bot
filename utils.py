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
	earth_radius = 6371
	delta_lat = math.radians(lat2 - lat1)
	delta_lon = math.radians(lon2 - lon1)
	ssq_delta_lat = math.pow(math.sin(delta_lat / 2), 2)
	ssq_delta_lon = math.pow(math.sin(delta_lon / 2), 2)
	a = ssq_delta_lat + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * ssq_delta_lon
	# c = math.atan2(math.sqrt(a), math.sqrt(1-a))
	# print('c1 ', c)
	c = math.asin(math.sqrt(a))
	# print('c2 ', c)
	return earth_radius * c