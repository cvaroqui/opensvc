from __future__ import print_function

import sys
import os
mod_d = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, mod_d)

import json
import rcAsset
from node import Node
node = Node()

class TestAsset:
    def test_011_get_connect_to(self):
        """
        asset connect_to on GCE, valid data
        """
        data_s = json.dumps({
            "networkInterfaces": [
                {
                    "accessConfigs": [
                        {
                            "kind": "compute#accessConfig",
                            "name": "external-nat",
                            "natIP": "23.251.137.71",
                            "type": "ONE_TO_ONE_NAT"
                        }
                    ],
                    "name": "nic0",
                    "networkIP": "10.132.0.2",
                }
            ]
        })
        asset = rcAsset.Asset(node)
        ret = asset._parse_connect_to(data_s)
        assert ret == "23.251.137.71"

    def test_012_get_connect_to(self):
        """
        asset connect_to on GCE, empty data
        """
        data_s = json.dumps({
            "networkInterfaces": [
            ]
        })
        asset = rcAsset.Asset(node)
        ret = asset._parse_connect_to(data_s)
        assert ret is None

    def test_013_get_connect_to(self):
        """
        asset connect_to on GCE, corrupt data
        """
        data_s = "{corrupted}"
        asset = rcAsset.Asset(node)
        ret = asset._parse_connect_to(data_s)
        assert ret is None

