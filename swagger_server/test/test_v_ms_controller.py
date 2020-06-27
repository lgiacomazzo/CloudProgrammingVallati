# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.configuration import Configuration  # noqa: E501
from swagger_server.test import BaseTestCase


class TestVMsController(BaseTestCase):
    """VMsController integration test stubs"""

    def test_add_new_configuration(self):
        """Test case for add_new_configuration

        Add a new configuration
        """
        body = Configuration()
        response = self.client.open(
            '/v1/configurations',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_configuration_by_id(self):
        """Test case for delete_configuration_by_id

        Deletes a configuration via ID
        """
        response = self.client.open(
            '/v1/configurations/{configurationID}'.format(configurationID=789),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_configuration_by_id(self):
        """Test case for get_configuration_by_id

        Retrieve a configuration via ID
        """
        response = self.client.open(
            '/v1/configurations/{configurationID}'.format(configurationID=789),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_configurations(self):
        """Test case for get_configurations

        Retrieve all existing configurations
        """
        response = self.client.open(
            '/v1/configurations',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_configuration_by_id(self):
        """Test case for update_configuration_by_id

        Updates a configuration in the database via ID
        """
        body = Configuration()
        response = self.client.open(
            '/v1/configurations/{configurationID}'.format(configurationID=789),
            method='PUT',
            data=json.dumps(body),
            content_type='application/xml')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
