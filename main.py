import requests
import json
import logging
import configparser
import os


class Keitaro:
	APIKEY = ''
	def __init__(self):

		config = configparser.ConfigParser()
		if os.path.isfile('config.ini'):
			config.read('config.ini')
			Keitaro.APIKEY = config['Keitaro']['APIKEY']
		else:



	def getreport(self):

def main():
	log = logging.getLogger(__name__)
	log.setLevel(logging.INFO)
	fh = logging.FileHandler("logs.log", encoding="utf-8", )
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	log.addHandler(fh)


if __name__ == '__main__':
	main()