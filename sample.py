#!/usr/bin/env python
import json
import logging
from nxos_grpc import Client
import secrets

logging.basicConfig(level=logging.DEBUG)

client = Client(secrets.hostname, secrets.username, secrets.password)
print(
    json.dumps(
        client.get_oper(
            'Cisco-NX-OS-device:System/nd-items/inst-items/dom-items/Dom-list/if-items/If-list/vaddrstat-items/VaddrStat-list',
            namespace='http://cisco.com/ns/yang/cisco-nx-os-device'
        ).as_dict(),
        sort_keys=True,
        indent=4
    )
)
print(
    json.dumps(
        client.get(
            'Cisco-NX-OS-device:System/nd-items/inst-items/dom-items/Dom-list/if-items/If-list/vaddrstat-items/VaddrStat-list',
            namespace='http://cisco.com/ns/yang/cisco-nx-os-device',
            request_id=1
        ).as_dict(),
        sort_keys=True,
        indent=4
    )
)
print(
    json.dumps(
        client.get_config(
            'Cisco-NX-OS-device:System/nd-items/inst-items/dom-items/Dom-list/if-items/If-list/vaddrstat-items/VaddrStat-list',
            namespace='http://cisco.com/ns/yang/cisco-nx-os-device',
            request_id=2
        ).as_dict(),
        sort_keys=True,
        indent=4
    )
)
