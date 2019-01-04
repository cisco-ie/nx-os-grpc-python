#!/usr/bin/env python
"""Copyright 2019 Cisco Systems

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
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
