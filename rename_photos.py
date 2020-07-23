# Permet de renommer chaque fichier photo avec un nom explicit à partir de la métadonnée du fichier

# année/mois/jour-heure/minute/seconde-gps

# Objectifs : 
# récupérer répertoire en argument
# Aller dans la métadonnée de chaque fichier et en extraire les infos
# obtenir données gps
# Renommer les fichiers avec les métadonnées extraites


from PIL import Image, ExifTags
import os
import platform
from selenium import webdriver
import sys
import googlemaps
import geopy
from geopy.geocoders import Nominatim
import time
from termcolor import colored

def detect_OS(path):
	"""
	Verifier OS pour faire tourner le programme
	"""
	OS = platform.system()
	if OS == "Linux" or "Linux":
		set_path(path)
	else:
		print("This program isn't built to run on this OS")
		sys.exit(0)

def extract_args():
	"""
	Cette fonction permet de récupérer répertoire pour trier les photos 
	"""
	arguments = sys.argv
	assert isinstance(arguments, list)
	if len(arguments) > 1:
		return arguments[1]
	else:
		while len(arguments) <= 1:
			arguments = input("Entrez le répertoire à trier : ")
		return arguments


def get_data(): 
	files = os.listdir(get_path())
	data = {"date": [], "heure": [], "N": [], "W": [], "S": [], "E": [], "name": []}
	for file in files:
		name, ext = os.path.splitext(file)
		data["name"].append(name)
		if ext.lower() == ".jpg":
			img = Image.open(file)
			exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS }
			for key, value in exif.items():
				if key=="DateTimeOriginal":
				    	datetime = value.split(' ')
				    	hour = list(datetime[1])
				    	hour[2] = "'"
				    	hour[5] = "''"
				    	datetime[1]=''.join(hour)
				    	data["heure"].append(datetime[1])
				    	data["date"].append(datetime[0].replace(':','-'))
				elif key=="GPSInfo":
			    		if len(value.keys())>=4:
			    			if value[1] == 'N':
			    				data["N"].append(value[2])
			    				data["S"].append("")
			    			else:
			    				data["S"].append(value[2])
			    				data["N"].append("")
			    			if value[3] == 'W':
			    				data["W"].append(value[4])
			    				data["E"].append("")
			    			else:
			    				data["E"].append(value[4])
			    				data["W"].append("")
			    		else:
			    			data["N"].append("")
			    			data["W"].append("")
			    			data["S"].append("")
			    			data["E"].append("")
		else:
			data["heure"].append("")
			data["date"].append(name)
			data["N"].append("") 
			data["W"].append("") 
			data["S"].append("")
			data["E"].append("")
	return data 

def DMStoDD(data):
	i=0
	for coordonnee in data["N"]:
		if coordonnee != '':
			coordonnee = (coordonnee[1]*60+coordonnee[2])/3600.0 + coordonnee[0]
			data["N"][i] = round(coordonnee,3) # 3 chiffres après la virgule
		else:
			data["N"][i] = ""
		i+=1
	
	i=0
	for coordonnee in data["W"]:
		if coordonnee != '':
			coordonnee = (coordonnee[1]*60+coordonnee[2])/3600.0 + coordonnee[0]
			data["W"][i] = round(-coordonnee,3)
		else:
			data["W"][i] = ""
		i+=1

	i=0
	for coordonnee in data["S"]:
		if coordonnee != '':
			coordonnee = (coordonnee[1]*60+coordonnee[2])/3600.0 + coordonnee[0]
			data["S"][i] = round(-coordonnee,3)
		else:
			data["S"][i] = ""
		i+=1

	i=0
	for coordonnee in data["E"]:
		if coordonnee != '':
			coordonnee = (coordonnee[1]*60+coordonnee[2])/3600.0 + coordonnee[0]
			data["E"][i] = round(coordonnee,3)
		else:
			data["E"][i] = ""
		i+=1



def get_GPS_info(data):

	# méthode avec google API mais payant
	"""reverse_geocode_result = []
	for i in range(len(data["N"])):
		if data["N"][i] and data["W"][i] != "":
			gmaps = googlemaps.Client(key="AIzaSyCPBHixn5tuWM84MC8Mpk-5TeIgsWKMWHE")
			reverse_geocode_result.append(gmaps.reverse_geocode((data["N"], data["W"]))) 
		else:
			reverse_geocode_result.append("")
	return reverse_geocode_result"""

	# méthode avec geopy 
	reverse_geocode_result = []
	for i in range(len(data["N"])):
		if data["N"][i] != "" and data["W"][i] != "" and data["S"][i] == "" and data["E"][i] == "":
			locator = Nominatim(user_agent="openmapquest")
			coordinates = "{}, {}".format(data["N"][i],data["W"][i])
			try:
				location = locator.reverse(coordinates)
				reverse_geocode_result.append(location.raw["display_name"])
				print(data["name"][i] + " accepted...")
			except Exception:
				reverse_geocode_result.append("")
				print(colored((data["name"][i] + " refused..."),"red"))
		elif data["N"][i] == "" and data["W"][i] == "" and data["S"][i] != "" and data["E"][i] != "":
			locator = Nominatim(user_agent="openmapquest")
			coordinates = "{}, {}".format(data["S"][i],data["E"][i])
			try:
				location = locator.reverse(coordinates)
				reverse_geocode_result.append(location.raw["display_name"])
				print(data["name"][i] + " accepted...")
			except Exception:
				reverse_geocode_result.append("")
				print(colored((data["name"][i] + " refused..."),"red"))
		elif data["N"][i] == "" and data["W"][i] != "" and data["S"][i] != "" and data["E"][i] == "":
			locator = Nominatim(user_agent="openmapquest")
			coordinates = "{}, {}".format(data["S"][i],data["W"][i])
			try:
				location = locator.reverse(coordinates)
				reverse_geocode_result.append(location.raw["display_name"])
				print(data["name"][i] + " accepted...")
			except Exception:
				reverse_geocode_result.append("")
				print(colored((data["name"][i] + " refused..."),"red"))
		elif data["N"][i] != "" and data["W"][i] == "" and data["S"][i] == "" and data["E"][i] != "":
			locator = Nominatim(user_agent="openmapquest")
			coordinates = "{}, {}".format(data["N"][i],data["E"][i])
			try:
				location = locator.reverse(coordinates)
				reverse_geocode_result.append(location.raw["display_name"])
				print(data["name"][i] + " accepted...")
			except Exception:
				reverse_geocode_result.append("")
				print(colored((data["name"][i] + " refused..."),"red"))
		else:
			reverse_geocode_result.append("")
		time.sleep(0.5)
	return sort_invalid_char(reverse_geocode_result)

def sort_invalid_char(reverse_geocode_result,invalid_char = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):#variable par défaut toujours après variable non connue
	for i in range(len(reverse_geocode_result)):
		for char in invalid_char:
			if char not in reverse_geocode_result[i]:
				continue
			else:
				reverse_geocode_result[i] = reverse_geocode_result[i].replace(char, '-')
	return reverse_geocode_result


def rename_photos(data, reverse_geocode_result):
	i=0
	files = os.listdir(get_path())
	for file in files:
		name, ext = os.path.splitext(file)
		if data["N"][i] and data["W"][i] != "":
			if ext.lower() == ".jpg":
				os.rename(get_path()+'/'+file, get_path()+'/'+data["date"][i]+'_'+data["heure"][i]+"_"+reverse_geocode_result[i]+".jpg")
			else:
				continue
		else:
			if ext.lower() == ".jpg":
				os.rename(get_path()+'/'+file, get_path()+'/'+data["date"][i]+'_'+data["heure"][i]+".jpg")
			else:
				continue			
		i+=1

set_path = lambda fileName : os.chdir(fileName) #va dans le dossier de travail
get_path = lambda : os.getcwd() #répertoire actuel



def main():
	path = extract_args()
	detect_OS(path)
	data = get_data()
	DMStoDD(data)
	#print(data)
	reverse_geocode_result = get_GPS_info(data)
	#print(reverse_geocode_result)
	rename_photos(data, reverse_geocode_result)


if __name__ == '__main__':
	main()