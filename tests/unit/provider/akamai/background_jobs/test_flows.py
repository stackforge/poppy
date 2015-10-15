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
from taskflow import engines

from poppy.provider.akamai.background_jobs.check_cert_status_and_update \
    import check_cert_status_and_update_flow
from poppy.provider.akamai.background_jobs.update_property import (
    update_property_flow)
from tests.unit import base
from tests.unit.provider.akamai.background_jobs import akamai_mocks


class TestAkamaiBJFlowRuns(base.TestCase):

    def setUp(self):
        super(TestAkamaiBJFlowRuns, self).setUp()

        bootstrap_patcher = mock.patch(
            'poppy.bootstrap.Bootstrap',
            new=akamai_mocks.MockBootStrap
        )
        bootstrap_patcher.start()
        self.addCleanup(bootstrap_patcher.stop)

    def test_check_cert_status_and_udate_flow(self):
        kwargs = {
            'domain_name': "blog.testabc.com",
            'cert_type': "san",
            'flavor_id': "premium",
            'project_id': "000"
        }
        engines.run(check_cert_status_and_update_flow.
                    check_cert_status_and_update_flow(),
                    store=kwargs)

    def test_update_papi_flow(self):
        kwargs = {
            "property_spec": "akamai_https_san_config_numbers",
            "update_type": "hostnames",
            "update_info_list": json.dumps([
                (
                    "add",
                    {
                        "cnameFrome": "blog.testabc.com",
                        "cnameTo": 'secure2.san1.altcdn.com',
                        "cnameType": "EDGE_HOSTNAME"
                    }
                )])
        }
        engines.run(update_property_flow.update_property_flow(),
                    store=kwargs)
