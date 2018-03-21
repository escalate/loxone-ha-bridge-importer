#!/usr/bin/env python
# -*- coding: utf-8 -*-

from importer import Importer

import pytest
from unittest import mock
from requests.exceptions import HTTPError, Timeout
import json
import os
from pathlib import Path

FIXTURES_DIR = os.path.abspath('tests/fixtures')


@pytest.fixture(scope='function')
def unconfigured_importer():
    return Importer()


@pytest.fixture(scope='function')
def configured_importer():
    importer = Importer()
    importer.loxone_miniserver = '192.168.1.2'
    importer.loxone_username = 'player1'
    importer.loxone_password = 'secret'
    importer.ha_bridge_server = '192.168.1.3'
    importer.ha_bridge_port = '8080'
    return importer


@pytest.mark.usefixtures('unconfigured_importer')
class TestSetter(object):
    def test_set_loxone_miniserver(self, configured_importer):
        expected = '192.168.1.2'
        configured_importer.set_loxone_miniserver(expected)
        assert configured_importer.loxone_miniserver == expected

    def test_set_loxone_username(self, configured_importer):
        expected = 'player1'
        configured_importer.set_loxone_username(expected)
        assert configured_importer.loxone_username == expected

    def test_set_loxone_password(self, configured_importer):
        expected = 'secret'
        configured_importer.set_loxone_password(expected)
        assert configured_importer.loxone_password == expected

    def test_set_ha_bridge_server(self, configured_importer):
        expected = '192.168.1.3'
        configured_importer.set_ha_bridge_server(expected)
        assert configured_importer.ha_bridge_server == expected

    def test_set_ha_bridge_port(self, configured_importer):
        expected = '8080'
        configured_importer.set_ha_bridge_port(expected)
        assert configured_importer.ha_bridge_port == expected


@pytest.mark.usefixtures('configured_importer')
class TestGetLoxoneStructureFile(object):
    def _mock_response(
            self,
            status=200,
            content="CONTENT",
            json_data=None,
            raise_for_status=None):
        mock_resp = mock.Mock()
        mock_resp.raise_for_status = mock.Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        mock_resp.status_code = status
        mock_resp.content = content
        if json_data:
            mock_resp.json = mock.Mock(
                return_value=json_data
            )
        return mock_resp

    @mock.patch('importer.requests.get')
    def test_ok(self, mock_get, configured_importer):
        expected = '{"key": "value"}'
        mock_resp = self._mock_response(status=200, json_data=expected)
        mock_get.return_value = mock_resp
        actual = configured_importer.get_loxone_structure_file()
        assert actual == expected

    @mock.patch('importer.requests.get')
    def test_internal_server_error(self, mock_get, configured_importer):
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("ERROR"))
        mock_get.return_value = mock_resp
        with pytest.raises(HTTPError):
            configured_importer.get_loxone_structure_file()

    @mock.patch('importer.requests.get')
    def test_timeout(self, mock_get, configured_importer):
        mock_resp = self._mock_response(status=None, raise_for_status=Timeout("TIMEOUT"))
        mock_get.return_value = mock_resp
        with pytest.raises(Timeout):
            configured_importer.get_loxone_structure_file()
