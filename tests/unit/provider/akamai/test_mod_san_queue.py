# Copyright (c) 2015 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import mock
from oslo_config import cfg
from zake import fake_client

from poppy.provider.akamai.mod_san_queue import zookeeper_queue
from tests.unit import base


AKAMAI_OPTIONS = [
    # queue backend configs
    cfg.StrOpt(
        'queue_backend_type',
        help='SAN Cert Queueing backend'),
    cfg.ListOpt('queue_backend_host', default=['localhost'],
                help='default queue backend server hosts'),
    cfg.IntOpt('queue_backend_port', default=2181, help='default'
               ' default queue backend server port (e.g: 2181)'),
    cfg.StrOpt(
        'mod_san_queue_path', default='/mod_san_queue', help='Zookeeper path '
        'for mod_san_queue'),
]

AKAMAI_GROUP = 'drivers:provider:akamai'


class TestModSanQueue(base.TestCase):

    def setUp(self):
        super(TestModSanQueue, self).setUp()
        self.cert_obj_json = {
            "cert_type": "san",
            "domain_name": "www.abc.com",
            "flavor_id": "premium"
        }

        # Need this fake class bc zake's fake client
        # does not take any host parameters
        class fake_kz_client(fake_client.FakeClient):
            def __init__(self, hosts):
                super(self.__class__, self).__init__()

        zookeeper_client_patcher = mock.patch(
            'kazoo.client.KazooClient',
            fake_kz_client
        )
        zookeeper_client_patcher.start()
        self.addCleanup(zookeeper_client_patcher.stop)

        self.conf = cfg.ConfigOpts()
        self.zk_queue = zookeeper_queue.ZookeeperModSanQueue(self.conf)

    def test_enqueue_mod_san_request(self):
        self.zk_queue.enqueue_mod_san_request(
            json.dumps(self.cert_obj_json).encode('utf-8'))
        self.assertTrue(len(self.zk_queue.mod_san_queue_backend) == 1)
        self.assertTrue(
            json.loads(self.zk_queue.mod_san_queue_backend.get().
                       decode('utf-8')) == self.cert_obj_json)

    def test_dequeue_mod_san_request(self):
        self.zk_queue.enqueue_mod_san_request(
            json.dumps(self.cert_obj_json).encode('utf-8'))
        res = self.zk_queue.dequeue_mod_san_request(False).decode('utf-8')
        self.assertTrue(len(self.zk_queue.mod_san_queue_backend) == 1)
        self.assertTrue(json.loads(res) == self.cert_obj_json)

        res = self.zk_queue.dequeue_mod_san_request().decode('utf-8')
        self.assertTrue(len(self.zk_queue.mod_san_queue_backend) == 0)
        self.assertTrue(json.loads(res) == self.cert_obj_json)

    def test_traverse_queue(self):
        self.zk_queue.enqueue_mod_san_request(
            json.dumps(self.cert_obj_json).encode('utf-8'))
        res = self.zk_queue.traverse_queue()
        self.assertTrue(len(res) == 1)
        res = [json.loads(r.decode('utf-8')) for r in res]
        self.assertTrue(res == [self.cert_obj_json])
