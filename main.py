import requests
import json
import logging
import configparser
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("logs.log", 'w', encoding="utf-8", )
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

class Keitaro:
	APIKEY = ''
	URL = ''
	def __init__(self):
		config = configparser.ConfigParser()
		if os.path.isfile('config.ini'):
			config.read('config.ini')
			self.APIKEY = config['Keitaro']['APIKEY']
			self.URL = config['Keitaro']['URL']
		else:
			log.error('Configuration file not found')


	def conversions(self, range):
		headers = {
			'Api-Key': Keitaro.APIKEY
		}
		payload = {
			'range': {'interval': range},
			'columns': ['sub_id_6', 'postback_datetime', 'status']
		}
		try:
			res = requests.post(f'{self.URL}/admin_api/v1/conversions/log', headers=headers, data=payload)
			if res.status_code == requests.codes.ok:
				return res.json()
			else:
				log.error(f'Conversions: {res.status_code}')
		except Exception as e:
			log.critical('Request conversions', exc_info=True)


	def reportfields(self):
		headers = {
			'Api-Key': self.APIKEY
		}
		return requests.get(f'{self.URL}/admin_api/v1/report/definition', headers=headers).json()


def main():
	ktr = Keitaro()
	#log.debug(f'Fields: {ktr.reportfields()}')
	scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name('sheets_secret.json', scope)
	client = gspread.authorize(creds)
	sheet = client.open('Keitaro To Ads Import').sheet1

	log.debug(f'Records:\n{sheet.get_all_records()}')

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
