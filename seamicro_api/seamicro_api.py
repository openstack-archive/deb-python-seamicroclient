import requests
import json
import logging

from enum import Enum

class SeaMicroAPIError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

LOGGER = logging.getLogger('SeaMicroAPI')
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.INFO)

SERVER_POWER_STATES = Enum('on', 'off', 'reset')

class SeaMicroAPI:
    RESPONSE_CODES = {
        200: 'OK',
        202: 'Accepted',
        304: 'Not Modified',
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        500: 'Internal Server Error',
        501: 'Internal Server Error (not implemented)'
    }

    def __init__(self, hostname='seamicro', use_ssl=True, verify_ssl=True, api_version='v0.9', debug=False):
        self.hostname = hostname
        self.protocol = "http"
        self.api_version = api_version
        self.verify_ssl = verify_ssl
        self.token = ""
        if use_ssl:
                self.protocol = "https"

        self.base_uri = "%s://%s/%s" % (self.protocol, self.hostname, self.api_version)
        if debug:
            LOGGER.setLevel(logging.DEBUG)

    # the v0.9 resources, except for techsupport, do not accept key/value pairs, 
    # so the below function builds them manually
    def assemble_url_legacy(self, location, params={ }):
        param_string = "&".join(filter(None, params.values()))
        uri = "%s?%s" % (location, param_string)
        url = "/".join([ self.base_uri, uri ])
        
        return url

    def decode_response(self, response):
        """
        Handle the response object, and raise exceptions if errors are found.
        """
        url = response.url
        if response.status_code not in (200, 202, 304):
                http_status_code = response.status_code
                raise SeaMicroAPIError('Got HTTP response code %d - %s for %s' %
                    (http_status_code, self.RESPONSE_CODES.get(http_status_code, 'Unknown!'), url))

        LOGGER.debug(response.text)        
        json_data = json.loads(response.text)

        if not json_data:
            raise SeaMicroAPIError('No JSON Data Found from %s: just got %s' % (url, response.text))

        json_rpc_code = int(json_data['error']['code'])

        if json_rpc_code not in (200, 202, 304):
                raise SeaMicroAPIError('Got JSON RPC error code %d: %s for %s' %
                    (json_rpc_code, self.RESPONSE_CODES.get(json_rpc_code, 'Unknown!'), url))

        LOGGER.debug(json_data)
        return json_data

    def send_get(self, location, params):
        params.update({ 'token': self.token })
        url = "/".join([ self.base_uri, location ])
        r = requests.get(url, verify=self.verify_ssl, params=params)
        return self.decode_response(r)

    def send_get_legacy(self, location, params):
        params.update({ 'token': self.token })
        url = self.assemble_url_legacy(location, params)
        LOGGER.debug('GET: %s' % url)

        r = requests.get(url, verify=self.verify_ssl)
        return self.decode_response(r)
    
    def send_put_legacy(self, location, params):
        #removed the line below since the only current PUT command
        #serverPowerByName adds the token info manually because
        #the arguments are order-dependant
        #params.update({ 'token': self.token })
        
        url = self.assemble_url_legacy(location, params)
        LOGGER.debug('PUT: %s' % url)
        headers = {'content-type': 'text/json'}

        r = requests.put(url, headers=headers, verify=self.verify_ssl)
        return self.decode_response(r)

    def login(self, username=None, password=None):
        self.username = username
        location = "login"
        decoded_json_response = self.send_get_legacy(location, params={ 'username': username, 'password': password })
        self.token = decoded_json_response['result']

    def logout(self):
        location = "logout"
        decoded_json_response = self.send_get_legacy(location, params={ })
        return decoded_json_response['result']

    def cards(self):
        location = "cards"
        decoded_json_response = self.send_get_legacy(location, params={ })

        return decoded_json_response['result']

    def cards_all(self):
        location = "cards/all"
        decoded_json_response = self.send_get_legacy(location, params={ })

        return decoded_json_response['result']
        
    def servers(self):
        location = "servers"
        decoded_json_response = self.send_get_legacy(location, params={ })

        return decoded_json_response['result']

    def servers_all(self):
        location = "servers/all"
        decoded_json_response = self.send_get_legacy(location, params={ })

        return decoded_json_response['result']


    def get_server_by_name(self, server_name):
    	"""Wrapper for camel case serverByName.
    	"""
    	return self.serverByName(server_name)


    def serverByName(self, serverName):
    	"""
    	Get detailed server info based on server name. For example, "17/0".
    	"""
        serverIndex = self.indexForServer(serverName)    
        location = "servers/%s" % (serverIndex)

        return self.send_get_legacy(location, params={ })['result']
    

    # wrapping the below commands to be consistent with the function names created
    # previously, and also to allow the user not to worry about magic strings like
    # "Power-On"

    def server_power_on(self, server_name, using_pxe=False):
    	"""Power-on - wrapper around serverPowerByName
    	"""
    	
    	return self.serverPowerByName(server_name, 'Power-On', doPxe=using_pxe)


    def server_power_off(self, server_name, force=False):
    	"""Power-off - wrapper around serverPowerByName"""

    	return self.serverPowerByName(server_name, 'Power-Off', force=force)


    def server_reset(self, server_name, using_pxe=False):
    	"""Reset - wrapper around serverPowerByName"""

    	return self.serverPowerByName(server_name, 'Reset', doPxe=using_pxe)


    def index_for_server(self, server_name):
    	"""
    	Wrapper for camel case
    	"""
    	return self.indexForServer(server_name)


    # XXX: arguments are order-dependant at the system,
    # XXX: so we're manually creating post string here
    def serverPowerByName(self, serverName, newStatus, doPxe=False, force=False):
    	"""Issue power on, power off, reset commands.
    		newStatus must be one of "Power-On", "Power-Off", or "Reset". 
    		The keyword argument doPxe may be True or False, and governs whether a power-on or reset
    		action will include a PXE attempt.
    		The keyword argument force may be True or False, and governs whether a power-off will
    		use ACPI to power down gracefully (force=False) or force the server off un-gracefully
    		(force=True).
    	"""
        serverIndex = self.indexForServer(serverName)
        location = "servers/%s" % (serverIndex)
        
        params = {}
        if newStatus in ['Power-On', 'Reset']:
            if doPxe:
                params['params'] = "action=%s&using-pxe=true&%s" % (newStatus,self.token)
            else:
                params['params'] = "action=%s&using-pxe=false&%s" % (newStatus,self.token)
        elif newStatus == 'Power-Off':
            if force:
                params['params'] = "action=%s&force=true&%s" % (newStatus,self.token)
            else:
                params['params'] = "action=%s&force=false&%s" % (newStatus,self.token)
        else:
            return False
        
        result = self.send_put_legacy(location, params=params)
        LOGGER.debug(result)
        return True


    def indexForServer(self, serverName):
    	"""
    	API v0.9 uses arbitrary indexing. This function converts a server id
    	to an index that can be used for detailed outputs & commands.
    	"""

        location = "servers"
        serverDict = self.send_get_legacy(location, params={ })['result']['serverId']
        
        for serverIndex, serverId in serverDict.items():
            if serverId == serverName:
                return serverIndex
        
        return False
    
    def logs(self):
        location = "system/logs"
        decoded_json_response = self.send_get_legacy(location, params={ })
        return decoded_json_response['result']

    # this is the only command that takes a key-value pair,
    # so we'll use the proper send_get method
    def tech_support(self):
        location = "system/techsupport"
        params = { 'scope': 'scope=brief' }

        decoded_json_response = self.send_get_legacy(location, params=params)
        return decoded_json_response['result']
