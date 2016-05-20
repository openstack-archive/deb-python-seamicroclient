import json

from seamicroclient.v2 import client

seamicro = client.Client("admin", "seamicro", "http://172.16.0.25/v2.0")

servers = seamicro.servers.list()

for server in servers:
    print(json.dumps(server))
    print("\n\n")
