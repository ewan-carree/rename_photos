from PIL import Image, ExifTags
import os
import os.path
import platform
import sys
import geopy
from geopy.geocoders import Nominatim
import time
from termcolor import colored
import shutil



set_path = lambda fileName : os.chdir(fileName) #va dans le dossier de travail
get_path = lambda : os.getcwd() #répertoire actuel
create_folder = lambda folderName : os.mkdir(folderName) #créer le dossier de travail
get_pictures = lambda folderName : os.listdir(folderName)


def parseArguments():
  import argparse

  parser = argparse.ArgumentParser(description='Extract the necessary names to create c++ files')

  parser.add_argument("path", type = str , help = "This argument represents the path where you want to sort your pictures.")

  return parser.parse_args()

def detect_OS(path):
	"""
	Verifier OS pour faire tourner le programme
	"""
	OS = platform.system()
	if OS == "Linux":
		set_path(path)
	else:
		print("This program isn't built to run on this OS")
		sys.exit(0)


class GPS(object):
	@staticmethod
	def DMS_to_DD(data):
		for x in ['N', 'W','S','E']:
			try:
				if data[x] != '':
					data[x] = (data[x][1]*60+data[x][2])/3600.0 + data[x][0]
					if x == 'W' or x == 'S':
						data[x] = round(-data[x],5) # 5 chiffres après la virgule
					else:
						data[x] = round(data[x],5) # 5 chiffres après la virgule
				else:
					data[x] = ""
			except Exception as e:
				data[x] = ""
				print("Unable to convert " + data["name"] + " :" + e)
		return data		

	@staticmethod
	def locate(coordinates):
		try:
			locator = Nominatim(user_agent="openmapquest")
			location = locator.reverse(coordinates)
			location = location.raw["display_name"]
			print(colored(location + " found","blue"))
		except Exception as e:
			location = ""
			print(colored((location + f" not found : {e}"),"red"))
		return location

	def sort_invalid_char(func):
		invalid_char = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
		def wrapper(*args, **kwargs):
			rv = func(*args, **kwargs)
			for char in invalid_char:
				if char in rv:
					rv = rv.replace(char, "")
			return rv
		return wrapper

	@sort_invalid_char
	def get_GPS_info(data):
		if data["N"] != "" and data["W"] != "" and data["S"] == "" and data["E"] == "":
			coordinates = "{}, {}".format(data["N"],data["W"])
			location = GPS.locate(coordinates)

		elif data["N"] == "" and data["W"] == "" and data["S"] != "" and data["E"] != "":
			coordinates = "{}, {}".format(data["S"],data["E"])
			location = GPS.locate(coordinates)

		elif data["N"] == "" and data["W"] != "" and data["S"] != "" and data["E"] == "":
			coordinates = "{}, {}".format(data["S"],data["W"])
			location = GPS.locate(coordinates)

		elif data["N"] != "" and data["W"] == "" and data["S"] == "" and data["E"] != "":
			coordinates = "{}, {}".format(data["N"],data["E"])
			location = GPS.locate(coordinates)

		else:
			location = ""
		return location



def extract_data(file):
	data = {"date": "", "heure": "", "N": "", "W": "", "S": "", "E": "", "name": "", "ext": ""}

	name, ext = os.path.splitext(file)

	data["ext"] = ext.lower()
	
	data["name"] = name

	if data["ext"] == ".jpg":
		try:
			exif = { ExifTags.TAGS[k]: v for k, v in Image.open(file)._getexif().items() if k in ExifTags.TAGS }
			
			if "GPSInfo" in exif.keys(): 
				for key, value in exif.items():
					if key == "GPSInfo":
						if len(value.keys())>=4:
							if value[1] == 'N':
								data["N"] = value[2]
								data["S"] = ""
							else:
								data["S"] = value[2]
								data["N"] = ""
							if value[3] == 'W':
								data["W"] = value[4]
								data["E"] = ""
							else:
								data["E"] = value[4]
								data["W"] = ""
						else:
							for x in ['N', 'W', 'S', 'E']:
								data[x] = ""
			else:
				print("No GPS")
				for x in ['N', 'W','S','E']:
					data[x] = ""
			
			if "DateTimeOriginal" in exif.keys():
				for key, value in exif.items():
					if key == "DateTimeOriginal":
						datetime = value.split(' ')
						hour = list(datetime[1])
						hour[2] = "'"
						hour[5] = "''"
						datetime[1]=''.join(hour)
						data["heure"] = datetime[1]
						data["date"] = datetime[0].replace(':','-')
			else:
				print("No date")
				for x in ["heure", "date"]:
					data[x] = ""
		except Exception as e:
			print(f"Bad image : {e}")

	else:
		for x in ["date", "heure", "N", "W", "S", "E"]:
			data[x] = ""

	return data


def rename_file(location, data, file, path, new_folder, i):
	try:
		if data["date"] != "":
			if location != "": #si la localisation a fonctionné
				if data["ext"] == ".jpg":
					shutil.move(path + "/" + file, path + "/" + new_folder + '/' + data["date"] + '_' +data["heure"] + "_" + location + "_" + str(i) + ".jpg") #deux disques différent fonctionnent aussi
				else:
					pass
			else: #si la localisation n'a pas fonctionné
				if data["ext"] == ".jpg":
					shutil.move(path + "/" + file, path + "/" + new_folder + '/' + data["date"] +'_'+data["heure"] + "_" + str(i) +  ".jpg") #deux disques différent fonctionnent aussi
				else:
					pass
		else:
			if location != "": #si la localisation a fonctionné
				if data["ext"] == ".jpg":
					shutil.move(path + "/" + file, path + "/" + new_folder + '/' + location + "_" + str(i) +  ".jpg") #deux disques différent fonctionnent aussi
				else:
					pass
			else: #si la localisation n'a pas fonctionné
				if data["ext"] == ".jpg":
					shutil.move(path + "/" + file, path + "/" + new_folder + '/' + file) #deux disques différent fonctionnent aussi
				else:
					pass

	except Exception as e:
		print(f"{file} couldn't have been renamed : {e}")




def timer(func):
	def wrapper(*args, **kwargs):
		start = time.time()
		rv = func(*args, **kwargs)
		total = time.time() - start
		minutes = total//60
		seconds = total%60
		print("Time to execute : " + "%.0f" % minutes + "min "+ "%.2f" % seconds + "sec")
		return rv
	return wrapper

@timer
def main():
	#extraire path
	args = parseArguments()
	#set path
	detect_OS(args.path)
	#faire un fichier pour déplacer les photos
	new_folder = "Sorted_pictures"
	create_folder(new_folder)
	#recuperer images
	files = get_pictures(args.path)

	i = 1
	for file in files:
		data = extract_data(file)
		data = GPS.DMS_to_DD(data)
		location = GPS.get_GPS_info(data)
		rename_file(location, data, file, args.path, new_folder, i) 
		time.sleep(0.5) # evite surcharge et erreur
		i += 1


if __name__ == "__main__":
	main()