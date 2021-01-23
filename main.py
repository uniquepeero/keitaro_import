import configparser
import json
import logging
import os
from time import sleep

import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
fh = logging.FileHandler('logs.log', 'w', encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


config = configparser.ConfigParser()


class Keitaro:
	APIKEY = ''
	URL = ''

	def __init__(self):
		if os.path.isfile('config.ini'):
			config.read('config.ini')
			self.APIKEY = config['Keitaro']['APIKEY']
			self.URL = config['Keitaro']['URL']
		else:
			log.error('Configuration file not found')

	def conversions(self, interval):
		headers = {
			'Api-Key': self.APIKEY
		}
		payload = {
			'range': {'interval': interval},
			'columns': ['sub_id_6', 'postback_datetime', 'status']
		}
		try:
			res = requests.post(f'{self.URL}/admin_api/v1/conversions/log', headers=headers, data=json.dumps(payload))
			if res.status_code == requests.codes.ok:
				return res.json()
			else:
				log.error(f'Conversions error code: {res.status_code} / Message: {res.json()}')
		except Exception:
			log.critical('Request conversions', exc_info=True)

	def reportfields(self):
		headers = {
			'Api-Key': self.APIKEY
		}
		return requests.get(f'{self.URL}/admin_api/v1/report/definition', headers=headers).json()


def _find_json():
	for file in os.listdir('.'):
		if file.endswith('.json'):
			return file
	return None


def main():
	ktr = Keitaro()

	leads = ktr.conversions("today")['rows']
	log.info(f'Found {len(leads)} conversions')

	try:
		scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
		creds = ServiceAccountCredentials.from_json_keyfile_name(_find_json(), scope)
		client = gspread.authorize(creds)
		sheet = client.open(config['Google']['SHEET_NAME']).sheet1
		sleep(2)
	except Exception:
		log.error(f'Google Sheets opening: ', exc_info=True)
		exit()

	sheet.clear()
	sleep(1)
	sheet.update_cell(6, 1, 'Parameters:TimeZone=+0000;')
	sleep(1)
	sheet.insert_row(['Google Click ID', 'Conversion Name', 'Conversion Time', 'Conversion Value', 'Conversion Currency'], 7)
	sleep(1)

	index = 8
	for lead in leads:
		if lead['sub_id_6'] is not None:
			row = [lead['sub_id_6'], 'sell', lead['postback_datetime']]
			sheet.insert_row(row, index)
			log.debug(f'Row {index} inserted')
			index += 1
			sleep(2)
	log.info(f'Inserted {index - 8} rows')


if __name__ == '__main__':
	try:
		log.info('Started')
		main()
	except (SystemExit, KeyboardInterrupt):
		raise
	except Exception:
		log.critical('Main proccess error', exc_info=True)
	finally:
		log.info('Finished')
