# Copyright (c) 2014 Rackspace, Inc.
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

import cassandra
import mock
from oslo.config import cfg

from poppy.storage.cassandra import driver
from poppy.storage.cassandra import flavors
from poppy.storage.cassandra import services
from tests.unit import base


CASSANDRA_OPTIONS = [
    cfg.ListOpt('cluster', default='mock_ip',
                help='Cassandra Cluster contact points'),
    cfg.StrOpt('keyspace', default='mock_poppy',
               help='Keyspace for all queries made in session'),
]


class CassandraStorageDriverTests(base.TestCase):

    @mock.patch.object(driver, 'CASSANDRA_OPTIONS', new=CASSANDRA_OPTIONS)
    def setUp(self):
        super(CassandraStorageDriverTests, self).setUp()

        conf = cfg.ConfigOpts()
        self.cassandra_driver = driver.CassandraStorageDriver(conf)

    def test_storage_driver(self):
        # assert that the configs are set up based on what was passed in
        self.assertEqual(self.cassandra_driver.cassandra_conf['cluster'],
                         ['mock_ip'])
        self.assertEqual(self.cassandra_driver.cassandra_conf.keyspace,
                         'mock_poppy')

    def test_storage_name(self):
        self.assertEqual('Cassandra', self.cassandra_driver.storage_name)

    def test_is_alive(self):
        self.assertTrue(self.cassandra_driver.is_alive())

    def test_connect(self):
        self.cassandra_driver.session = None
        self.cassandra_driver.connect = mock.Mock()
        self.cassandra_driver.database
        self.cassandra_driver.connect.assert_called_once_with()
        # reset session to not None value
        self.cassandra_driver.session = mock.Mock(is_shutdown=False)
        # 2nd time should get a not-none session
        self.assertTrue(self.cassandra_driver.database is not None)

    def test_close_connection(self):
        self.cassandra_driver.session = mock.Mock()
        self.cassandra_driver.close_connection()

        self.cassandra_driver.session.cluster.shutdown.assert_called_once_with(
        )
        self.cassandra_driver.session.shutdown.assert_called_once_with(
        )

    def test_service_controller(self):
        sc = self.cassandra_driver.services_controller

        self.assertEqual(
            isinstance(sc, services.ServicesController),
            True)

    def test_flavor_controller(self):
        sc = self.cassandra_driver.flavors_controller

        self.assertEqual(
            isinstance(sc, flavors.FlavorsController),
            True)

    @mock.patch.object(cassandra.cluster.Cluster, 'connect')
    def test_database(self, mock_cluster):
        self.cassandra_driver.database
        mock_cluster.assert_called_with('mock_poppy')
