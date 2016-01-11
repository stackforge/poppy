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

import logging

from oslo_config import cfg

from poppy.metrics import base
from poppy.metrics.blueflood import controllers


LOG = logging.getLogger(__name__)

BLUEFLOOD_OPTIONS = [
    cfg.StrOpt('blueflood_url',
               default='https://www.metrics.com',
               help='Metrics url for retrieving cached content'),
]

BLUEFLOOD_GROUP = 'drivers:metrics:blueflood'


class BlueFloodMetricsDriver(base.Driver):
    """Blue Flood Metrics Driver."""

    def __init__(self, conf):
        super(BlueFloodMetricsDriver, self).__init__(conf)
        conf.register_opts(BLUEFLOOD_OPTIONS, group=BLUEFLOOD_GROUP)
        self.metrics_conf = conf[BLUEFLOOD_GROUP]

    def is_alive(self):
        """Health check for Blue Flood Metrics driver."""
        return True

    @property
    def metrics_driver_name(self):
        """metrics driver name.

        :returns 'BlueFlood'
        """
        return 'BlueFlood'

    @property
    def services_controller(self):
        """services_controller.

        :returns service controller
        """
        return controllers.ServicesController(self)
