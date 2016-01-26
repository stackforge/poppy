# Copyright (c) 2016 Rackspace, Inc.
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

import ddt
from hypothesis import given
from hypothesis import strategies

from tests.api import base
from tests.api.utils.schema import san_retry


@ddt.ddt
class TestGetSanRetryList(base.TestBase):

    def setUp(self):
        super(TestGetSanRetryList, self).setUp()

        if self.test_config.run_operator_tests is False:
            self.skipTest(
                'Test Operator Functions is disabled in configuration')

        self.service_name = self.generate_random_string(prefix='api-test')
        self.flavor_id = self.test_flavor

        self.domain1 = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'
        self.domain2 = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'
        self.domain3 = self.generate_random_string(
            prefix='www.api-test-domain') + '.com'

        self.domain_list = [
            {"domain": self.domain1, "protocol": "https",
             "certificate": "san"},
            {"domain": self.domain2, "protocol": "https",
             "certificate": "san"},
            {"domain": self.domain3, "protocol": "https",
             "certificate": "san"}
        ]

        origin = self.generate_random_string(
            prefix='api-test-origin') + u'.com'
        self.origin_list = [
            {
                u"origin": origin,
                u"port": 443,
                u"ssl": True,
                u"rules": [{
                    u"name": u"default",
                    u"request_url": u"/*"
                }]
            }
        ]

        self.caching_list = [
            {
                u"name": u"default",
                u"ttl": 3600,
                u"rules": [{
                    u"name": "default",
                    u"request_url": "/*"
                }]
            },
            {
                u"name": u"home",
                u"ttl": 1200,
                u"rules": [{
                    u"name": u"index",
                    u"request_url": u"/index.htm"
                }]
            }
        ]

        self.restrictions_list = [
            {
                u"name": u"website only",
                u"access": u"whitelist",
                u"rules": [
                    {
                        u"name": self.domain1,
                        u"referrer": self.domain1,
                        u"request_url": "/*"
                    }
                ]
            }
        ]

        resp = self.setup_service(
            service_name=self.service_name,
            domain_list=self.domain_list,
            origin_list=self.origin_list,
            caching_list=self.caching_list,
            restrictions_list=self.restrictions_list,
            flavor_id=self.flavor_id)

        self.assertEqual(resp.status_code, 202)
        self.assertEqual(resp.text, '')
        self.service_url = resp.headers['location']

        self.client.wait_for_service_status(
            location=self.service_url,
            status='deployed',
            abort_on_status='failed',
            retry_interval=self.test_config.status_check_retry_interval,
            retry_timeout=self.test_config.status_check_retry_timeout)

    @ddt.file_data('data_put_san_retry_list_negative.json')
    def test_put_san_retry_list_negative(self, san_retry_list):
        resp = self.operator_client.put_san_retry_list(san_list=san_retry_list)
        self.assertEqual(resp.status_code, 400)

    @given(strategies.text(), strategies.text(), strategies.text(),
           strategies.booleans)
    def test_put_san_retry_list_quickcheck(
            self, project, domain, flavor_id, validate_service):
        san_retry_list = [{
            "project_id": self.user_project_id,
            "domain_name": self.domain1,
            "flavor_id": self.flavor_id,
            "validate_service": validate_service}]

        resp = self.operator_client.put_san_retry_list(san_list=san_retry_list)
        self.assertEqual(resp.status_code, 400)

    def test_san_retry_list(self):
        san_list = [
            {
                "project_id": self.user_project_id,
                "domain_name": self.domain1,
                "flavor_id": self.flavor_id,
            },
            {
                "project_id": self.user_project_id,
                "domain_name": self.domain2,
                "flavor_id": self.flavor_id
            }
        ]
        self.operator_client.put_san_retry_list(san_list=san_list)

        resp = self.operator_client.admin_get_san_retry_list()

        self.assertEqual(resp.status_code, 200)
        san_retry_list = resp.json()
        self.assertSchema(san_retry_list, san_retry.retry_list)

        for item in san_retry_list:
            # Verify matches the data created in test set up.
            # Verify Order
            pass

    def test_san_retry_empty_list(self):
        san_list = []
        self.operator_client.put_san_retry_list(san_list=san_list)

        resp = self.operator_client.admin_get_san_retry_list()

        self.assertEqual(resp.status_code, 200)
        san_retry_list = resp.json()
        self.assertSchema(san_retry_list, san_retry.retry_list)
        self.assertEqual(san_retry_list, [])

    def test_san_retry_list_update_order(self):
        san_list = [
            {
                "project_id": self.user_project_id,
                "domain_name": self.domain1,
                "flavor_id": self.flavor_id,
            },
            {
                "project_id": self.user_project_id,
                "domain_name": self.domain2,
                "flavor_id": self.flavor_id
            }
        ]
        self.operator_client.put_san_retry_list(san_list=san_list)

        resp = self.operator_client.admin_get_san_retry_list()
        self.assertEqual(resp.status_code, 200)
        san_retry_list = resp.json()
        self.assertSchema(san_retry_list, san_retry.retry_list)
        self.assertEqual(san_retry_list, san_list)

        san_list_updated = [
            {
                "project_id": self.user_project_id,
                "domain_name": self.domain2,
                "flavor_id": self.flavor_id,
            },
            {
                "project_id": self.user_project_id,
                "domain_name": self.domain1,
                "flavor_id": self.flavor_id
            }
        ]
        self.operator_client.put_san_retry_list(san_list=san_list)
        resp = self.operator_client.admin_get_san_retry_list()
        self.assertEqual(resp.status_code, 200)
        san_retry_list = resp.json()
        self.assertSchema(san_retry_list, san_retry.retry_list)
        self.assertEqual(san_retry_list, san_list_updated)

        san_list_updated_again = [
            {
                "project_id": self.user_project_id,
                "domain_name": self.domain2,
                "flavor_id": self.flavor_id,
            }
        ]
        self.operator_client.put_san_retry_list(san_list=san_list)
        resp = self.operator_client.admin_get_san_retry_list()
        self.assertEqual(resp.status_code, 200)
        san_retry_list = resp.json()
        self.assertSchema(san_retry_list, san_retry.retry_list)
        self.assertEqual(san_retry_list, san_list_updated_again)

    def test_san_retry_list_validate_service_false(self):
        san_list = [
            {
                "project_id": self.user_project_id,
                "domain_name": "api-test.cannotbetrue.com",
                "flavor_id": self.flavor_id,
                "validate_service": False
            }
        ]
        self.operator_client.put_san_retry_list(san_list=san_list)

        resp = self.operator_client.admin_get_san_retry_list()

        self.assertEqual(resp.status_code, 200)
        san_retry_list = resp.json()
        self.assertSchema(san_retry_list, san_retry.retry_list)

        for item in san_retry_list:
            # Verify matches the data created in test set up.
            # Verify Order
            pass

    def tearDown(self):
        self.client.delete_service(location=self.service_url)
        if self.test_config.generate_flavors:
            self.client.delete_flavor(flavor_id=self.flavor_id)
        self.operator_client.put_san_retry_list(san_list=[])
        super(TestGetSanRetryList, self).tearDown()
