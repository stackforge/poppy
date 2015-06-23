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

import json

import pecan
from pecan import hooks

from poppy.dns.rackspace import services as dns_services
from poppy.dns.rackspace import driver as dns_driver
from poppy.transport.pecan.controllers import base
from poppy.transport.pecan import hooks as poppy_hooks
from poppy.transport.validators import helpers
from poppy.transport.validators.schemas import san_migration
from poppy.transport.validators.schemas import service_state
from poppy.transport.validators.stoplight import decorators
from poppy.transport.validators.stoplight import helpers as stoplight_helpers
from poppy.transport.validators.stoplight import rule


class SANDomainMigrationController(base.Controller, hooks.HookController):
    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(SANDomainMigrationController, self).__init__(driver)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_service_schema(
                san_migration.SANMigrationServiceSchema.get_schema(
                    "SAN_migration", "POST")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def post(self):
        request_json = json.loads(pecan.request.body.decode('utf-8'))
        project_id = request_json.get('project_id', None)
        service_id = request_json.get('service_id', None)
        domain_name = request_json.get('domain_name', None)
        new_cert = request_json.get('new_cert', None)

        if not "edgekey.net" in new_cert:
            new_cert = new_cert + ".edgekey.net"

        services_controller = self._driver.manager.services_controller
        dns_controller = self._driver._manager.dns.services_controller
        storage_controller = self._driver._manager.storage.services_controller

        try:
            access_url = ''
            service_obj = services_controller.get(project_id, service_id)
            for provider_name in service_obj.provider_details:
                provider_detail = service_obj.provider_details[provider_name]
                access_urls = provider_detail.access_urls
                for url in access_urls:
                    if 'operator_url' in url:
                        access_url = url['operator_url']
                        dns_controller.migrate_SAN_domain(access_url, new_cert)

            # Update provider_details in cassandra
            provider_details = storage_controller.get_provider_details(
                project_id, service_id)
            for provider in provider_details:
                if str(provider_details[provider].access_urls[0][
                           'operator_url']) == access_url:
                    provider_details[provider].access_urls[0][
                        'provider_url'] = new_cert
                    storage_controller.update_provider_details(project_id,
                                                               service_id,
                                                               provider_details
                                                               )
        except ValueError:
            pecan.abort(404, detail='Service {0} could not be found'.format(
                service_id))

        return pecan.Response(None, 202)


class AkamaiController(base.Controller, hooks.HookController):
    def __init__(self, driver):
        super(AkamaiController, self).__init__(driver)
        self.__class__.service = SANDomainMigrationController(driver)


class ProviderController(base.Controller, hooks.HookController):
    def __init__(self, driver):
        super(ProviderController, self).__init__(driver)
        self.__class__.akamai = AkamaiController(driver)


class OperatorStateController(base.Controller, hooks.HookController):
    __hooks__ = [poppy_hooks.Context(), poppy_hooks.Error()]

    def __init__(self, driver):
        super(OperatorStateController, self).__init__(driver)

    @pecan.expose('json')
    @decorators.validate(
        request=rule.Rule(
            helpers.json_matches_service_schema(
                service_state.ServiceStateSchema.get_schema(
                    "service_state", "POST")),
            helpers.abort_with_message,
            stoplight_helpers.pecan_getter))
    def post(self):

        service_state_json = json.loads(pecan.request.body.decode('utf-8'))
        service_state = service_state_json.get('state', None)
        project_id = service_state_json.get('project_id', None)
        service_id = service_state_json.get('service_id', None)

        services_controller = self._driver.manager.services_controller

        try:
            services_controller.update_state(project_id,
                                             service_id,
                                             service_state)
        except ValueError:
            pecan.abort(404, detail='Service {0} could not be found'.format(
                service_id))

        return pecan.Response(None, 202)


class AdminServiceController(base.Controller, hooks.HookController):
    def __init__(self, driver):
        super(AdminServiceController, self).__init__(driver)
        self.__class__.state = OperatorStateController(driver)


class AdminController(base.Controller, hooks.HookController):
    def __init__(self, driver):
        super(AdminController, self).__init__(driver)
        self.__class__.services = AdminServiceController(driver)
        self.__class__.provider = ProviderController(driver)
