'''
Alpha version of SeaMicro API v2.0 Client
Excuse any hacky-ness
'''
import requests
import json
import logging
import inspect

DEBUG = False

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)

class SeaMicroAPIError(Exception):
    def __init__(self, value):
	self.value = value

    def __str__(self):
	return repr(self.value)

#LOGGER = logging.getLogger('SeaMicroAPI')


class SeaMicroAPI:
    RESPONSE_CODES = {
	200: 'OK',
	202: 'Accepted',
	204: 'Deleted',
	304: 'Not Modified',
	400: 'Bad Request',
	401: 'Unauthorized',
	403: 'Forbidden',
	404: 'Not Found',
	500: 'Internal Server Error',
	501: 'Internal Server Error (not implemented)'
    }

    def __init__(self, hostname='seamicro', use_ssl=True, verify_ssl=True, api_version='v2.0',stateless=False,json=False, username='admin',password='seamicro'):
	self.hostname = hostname
	self.protocol = "http"
	self.api_version = api_version
	self.verify_ssl = verify_ssl
	self.token = ""
	self.stateless = stateless
	self.json = json
	self.username = username
	self.password = password
	if use_ssl:
		self.protocol = "https"

	self.base_uri = "%s://%s/%s" % (self.protocol, self.hostname, self.api_version)

    def decode_response(self, response):
	global DEBUG
	"""
	Handle the response object, and raise exceptions if errors are found.
	"""
	url = response.url
	if response.status_code not in (200, 201, 202, 204, 304):
		http_status_code = response.status_code
		raise SeaMicroAPIError('Got HTTP response code %d - %s for %s. Reason: %s' % (http_status_code, self.RESPONSE_CODES.get(http_status_code, 'Unknown!'), url, response.text))

	if DEBUG:
	    print response.headers
	    print response.text

	if response.headers.get('content-type') == 'text/html':
	    if response.text in ['','Done.\r\n']:
		if DEBUG:
		    print 'Valid text/html from %s: got %s' % (url, response.text)
		return True
	    else:
		raise SeaMicroAPIError('Unknown text/html received from %s: got %s' % (url, response.text))
		return False
	elif response.headers.get('content-type') == 'application/json':
	    try:
		json_response = json.loads(response.text)
		if DEBUG and json_response:
		    print 'Valid JSON from %s: got %s' % (url, response.text)
		return json_response
	    except ValueError:
		raise SeaMicroAPIError('Bad application/json received from %s: got %s' % (url, response.text))
	else:
	    raise SeaMicroAPIError('Bad content-type received from %s: got %s' % (url, response.headers.get('content-type')))

    def send_get(self, location, params):
	if self.stateless:
	    params.update({ 'username': self.username })
	    params.update({ 'password': self.password })
	elif not self.stateless and self.token != '':
	    params.update({ 'authtoken': self.token })
	else:
	    return False

	url = "/".join([ self.base_uri, location ])
	r = requests.get(url, verify=self.verify_ssl, params=params)

	return self.decode_response(r)

    def send_post(self, location, params):
	if self.json:
	    return self.send_post_json(location,params)
	else:
	    return self.send_post_form(location,params)

    def send_post_json(self, location, params):
	global DEBUG
	# the inspect statement below is a hacky way of figuring out if we're called by login
	# there should be a better way...
	if self.stateless or inspect.stack()[2][3] == "login":
	    params.update({ 'username': self.username })
	    params.update({ 'password': self.password })
	elif not self.stateless and self.token != '':
	    params.update({ 'authtoken': self.token })
	else:
	    return False
	url = "/".join([ self.base_uri, location ])
	headers = {'content-type': 'application/json'}

	if DEBUG:
	    print params

	r = requests.post(url, verify=self.verify_ssl, data=json.dumps(params), headers=headers)

	return self.decode_response(r)

    def send_post_form(self, location, params):
	if self.stateless or inspect.stack()[2][3] == "login":
	    params.update({ 'username': self.username })
	    params.update({ 'password': self.password })
	elif not self.stateless and self.token != '':
	    params.update({ 'authtoken': self.token })
	else:
	    return False
	url = "/".join([ self.base_uri, location ])
	headers = {'content-type': 'application/x-www-form-urlencoded'}

	r = requests.post(url, verify=self.verify_ssl, params=params)
	return self.decode_response(r)

    def send_put(self, location, params):
	if self.json:
	    return self.send_put_json(location,params)
	else:
	    return self.send_put_form(location,params)

    def send_put_json(self, location, params):
	global DEBUG
	if self.stateless:
	    params.update({ 'username': self.username })
	    params.update({ 'password': self.password })
	elif not self.stateless and self.token != '':
	    params.update({ 'authtoken': self.token })
	else:
	    return False
	url = "/".join([ self.base_uri, location ])
	headers = {'content-type': 'application/json'}

	if DEBUG:
	    print params
	r = requests.put(url, verify=self.verify_ssl, data=json.dumps(params), headers=headers)
	return self.decode_response(r)

    def send_put_form(self, location, params):
	if self.stateless:
	    params.update({ 'username': self.username })
	    params.update({ 'password': self.password })
	elif not self.stateless and self.token != '':
	    params.update({ 'authtoken': self.token })
	else:
	    return False
	url = "/".join([ self.base_uri, location ])
	headers = {'content-type': 'application/x-www-form-urlencoded'}

	r = requests.put(url, verify=self.verify_ssl, params=params)
	return self.decode_response(r)

    def login(self):
	if not self.stateless and self.username != '' and self.password != '':
	    location = "login"
	    decoded_json_response = self.send_post(location, {})
	    if decoded_json_response:
		self.token = decoded_json_response
		return True
	    else:
		return False
	else:
	    return False

    def logout(self):
	if self.token != '':
	    location = "logout"
	    decoded_json_response = self.send_get(location, params={ })

    def root(self):
	location = ""
	decoded_json_response = self.send_get(location, params={ })
	return decoded_json_response

    def cards(self):
	location = "cards"
	decoded_json_response = self.send_get(location, params={ })
	return decoded_json_response

    def chassis(self, section='', subsection=''):
	if section == '':
	    location = "chassis"
	elif section in ( 'system','mxcard','scard','ccard','smcard','ucard','powersupply','fantray' ):
	    if subsection == '':
		location = "chassis/%s" % section
	    else:
		location = "chassis/%s/%s" % (section,subsection)
	else:
	    return False

	decoded_json_response = self.send_get(location, params={ })
	return decoded_json_response

    def servers(self, server='', section=''):
	if server == '':
	    location = "servers"
	else:
	    if section == '':
		location = "servers/%s" % server
	    else:
		location = "servers/%s/%s" % (server,section)

	decoded_json_response = self.send_get(location, params={ })
	return decoded_json_response

    def disks(self, slot='', disk=''):
	if slot == '':
	    location = "disks"
	else:
	    if disk == '':
		location = "disks/%s" % slot
	    else:
		location = "disks/%s/%s" % (slot,disk)

	decoded_json_response = self.send_get(location, params={ })
	return decoded_json_response

    def pools(self, slot='', pool=''):
	if slot == '':
	    location = "pools"
	else:
	    if pool == '':
		location = "pools/%s" % slot
	    else:
		location = "pools/%s/%s" % (slot,pool)

	decoded_json_response = self.send_get(location, params={ })
	return decoded_json_response

    def volumes(self, slot='', pool='',volume=''):
	if slot == '':
	    location = "volumes"
	else:
	    if pool == '':
		location = "volumes/%s" % slot
	    else:
		if volume == '':
		    location = "volumes/%s/%s" % (slot,pool)
		else:
		    location = "volumes/%s/%s/%s" % (slot,pool,volume)

	decoded_json_response = self.send_get(location, params={ })
	return decoded_json_response

    def interfaces(self, interface='', section=''):
	if interface == '':
	    location = "interfaces"
	else:
	    if section == '':
		location = "interfaces/%s" % interface
	    else:
		location = "interfaces/%s/%s" % (interface,section)

	decoded_json_response = self.send_get(location, params={ })
	return decoded_json_response

    def vlans(self):
	location = "vlans"
	decoded_json_response = self.send_get(location, params={ })

	return decoded_json_response

    def system(self):
	location = "system"
	decoded_json_response = self.send_get(location, params={ })

	return decoded_json_response

    def alarms(self):
	location = "system/alarms"
	decoded_json_response = self.send_get(location, params={ })

	return decoded_json_response

    def alerts(self):
	location = "system/alerts"
	decoded_json_response = self.send_get(location, params={ })

	return decoded_json_response

    def logs(self):
	location = 'system/logs'
	decoded_json_response = self.send_get(location, params={ })

	return decoded_json_response
    '''
    # below issues power on/off/reset command
    # newStatus must be ['power-on', 'power-off', 'reset']
    # do_pxe boolean to accompany Power-On & Reset
    # force boolean to accompany Power-Off
    '''
    def server_power(self, serverid, new_status, do_pxe=False, force=False):
	location = "servers/%s" % (serverid)
	params = {}
	if new_status in ['power-on', 'power-off', 'reset']:
	    params['action'] = new_status
	else:
	    raise SeaMicroAPIError('Invalid Power Operation %s' % (new_status))
	if do_pxe:
	    params['using-pxe'] = True
	if force:
	    params['force'] = True

	decoded_json_response = self.send_put(location, params=params)
	return decoded_json_response

    def server_config(self,serverid,path,value):
	location = "servers/%s/%s" % (serverid, path)
	params = {}
	params['value'] = value

	decoded_json_response = self.send_put(location, params=params)
	return decoded_json_response

    def chassis_config(self,path,value):
	location = "chassis/%s" % (path)
	params = {}
	params['value'] = value

	decoded_json_response = self.send_put(location, params=params)
	return decoded_json_response

    def generic_get(self,path):
	if not path:
	    raise SeaMicroAPIError('Invalid GET Operation - Path missing')
	location = "%s" % (path)

	decoded_json_response = self.send_get(location, params={ })
	return decoded_json_response

    def generic_config(self,path,value,op='value'):
	if not path or not value:
	    raise SeaMicroAPIError('Invalid Config Operation - Path or Value missing')
	location = "%s" % (path)
	params = {}
	if op == 'value':
	    params['value'] = value
	elif op == 'add':
	    params['add'] = value
	elif op == 'remove':
	    params['remove'] = value
	else:
	    raise SeaMicroAPIError('Invalid Config Operation %s' % (op))

	decoded_json_response = self.send_put(location, params=params)
	return decoded_json_response

    def write_mem(self):
	location = "system"
	params = {"action":"write-memory"}

	decoded_json_response = self.send_put(location, params=params)
	return decoded_json_response
