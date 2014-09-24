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

import uuid

import ddt

from tests.api import base
from tests.api.utils.schema import response


@ddt.ddt
class TestServices(base.TestBase):

    """Tests for Services."""

    def setUp(self):
        super(TestServices, self).setUp()
        self.service_name = str(uuid.uuid1())

    @ddt.file_data('data_create_service.json')
    def test_create_service(self, test_data):

        domain_list = test_data['domain_list']
        origin_list = test_data['origin_list']
        caching_list = test_data['caching_list']
        flavor = test_data['flavorRef']

        resp = self.client.create_service(service_name=self.service_name,
                                          domain_list=domain_list,
                                          origin_list=origin_list,
                                          caching_list=caching_list,
                                          flavorRef=flavor)
        self.assertEqual(resp.status_code, 202)

        '''
        # Get on Created Service
        resp = self.client.get_service(service_name=self.service_name)
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertSchema(body, response.create_service)

        self.assertEqual(body['domains'], domain_list)
        self.assertEqual(body['origins'], origin_list)
        self.assertEqual(body['caching_list'], caching_list)
        '''

        # Verify the service is updated at all Providers for the flavor
        if self.test_config.provider_validation:
            import time; time.sleep(2)
            self.assertFlavorUpdated(flavor, self.service_name)

    def tearDown(self):
        self.client.delete_service(service_name=self.service_name)
        super(TestServices, self).tearDown()
