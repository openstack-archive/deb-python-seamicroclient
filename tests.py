import unittest
import sys
import pprint
import time
import requests
from seamicro_api import SeaMicroAPI, SeaMicroAPIError

SERVER_TO_POWER_TEST = "3/0"
CHASSIS_HOSTNAME = "192.168.142.10"
CHASSIS_USERNAME = "admin"
CHASSIS_PASSWORD = "seamicro"

class SeaMicroAPITestCase(unittest.TestCase):
	def setUp(self):
		self.api = SeaMicroAPI(hostname=CHASSIS_HOSTNAME, use_ssl=True, verify_ssl=False)

	def tearDown(self):
		self.api.logout()

	def do_good_login(self):
		self.api.login(username=CHASSIS_USERNAME, password=CHASSIS_PASSWORD)

	def check_download_file(self, url, content_type='application/x-tgz'):
		r = requests.get(url)
		self.assertEqual(r.status_code, 200)
		self.assertEqual(r.headers['content-type'], content_type)


class TestCardsAll(SeaMicroAPITestCase):
	def runTest(self):
		self.do_good_login()
		cards_all = self.api.cards_all()

		pprint.pprint(cards_all, stream=sys.stderr)


class TestServersAll(SeaMicroAPITestCase):
	def runTest(self):
		self.do_good_login()
		servers = self.api.servers_all()

		def func(x,y):
			return int(x['serverId'].split('/')[0]) - int(y['serverId'].split('/')[0])

		pprint.pprint([(s['serverId'], s['serverMacAddr']) for s in sorted(servers.values(), cmp=func)  if s['serverNIC'] == '0'], stream=sys.stderr)


class TestSeaMicroAPIAuthentication(SeaMicroAPITestCase):
	def runTest(self):
		self.do_good_login()


class TestBadSeaMicroLogin(SeaMicroAPITestCase):
	def tearDown(self):
		"""Since this is by definition a bad login, logout will make no sense.
		"""

		pass

	def runTest(self):
		self.assertRaises(SeaMicroAPIError, self.api.login, username='admin', password='badpass')


class TestLogs(SeaMicroAPITestCase):
	def runTest(self):
		self.do_good_login()
		log_download_url = self.api.logs()
		self.check_download_file(log_download_url)


class TestTechSupport(SeaMicroAPITestCase):
	def runTest(self):
		self.do_good_login()
		tech_support_url = self.api.tech_support()
		self.check_download_file(tech_support_url)


class TestServerPower(SeaMicroAPITestCase):
	def get_server_state(self, server_name):
		server = self.api.get_server_by_name(server_name)
		return server['serverOpStatus']


	def runTest(self):
		func = None
		server_state_before = None
		server_state_after = None

		server_name = SERVER_TO_POWER_TEST
		self.do_good_login()

		server_state_before = self.get_server_state(server_name)
		if server_state_before == 'Down':
			func = self.api.server_power_on
			kwargs = { }
		else:
			func = self.api.server_power_off
			kwargs = { 'force': True }

		result = func(server_name, **kwargs)
		self.assertTrue(result)

		retries = range(5)
		while retries > 0:
			time.sleep(0.2)
			server_state_after = self.get_server_state(server_name)
			if server_state_before != server_state_after:
				break

		self.assertNotEqual(server_state_before, server_state_after)


if __name__ == '__main__':
	unittest.main()
