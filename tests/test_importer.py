#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path
from unittest import mock

import pytest
import requests
from click.testing import CliRunner
from requests.exceptions import HTTPError, Timeout

from importer import Importer, cli


FIXTURES_DIR = os.path.abspath('tests/fixtures')


def mock_requests_response(
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


def load_json_fixture_file(file_name):
    json_file = '{fixtures_dir}/{file_name}'.format(
        fixtures_dir=FIXTURES_DIR,
        file_name=file_name)
    return json.loads(Path(json_file).read_text())


@pytest.fixture(scope='function')
def unconfigured_importer():
    return Importer()


@pytest.fixture(scope='function')
def configured_importer():
    importer = Importer()
    importer.loxone_miniserver_host = '192.168.1.2'
    importer.loxone_miniserver_port = '80'
    importer.loxone_username = 'player1'
    importer.loxone_password = 'secret'
    importer.ha_bridge_host = '192.168.1.3'
    importer.ha_bridge_port = '8080'
    return importer


@pytest.fixture(scope='function')
def cli_runner():
    return CliRunner()


@pytest.mark.usefixtures('configured_importer')
class TestGetLoxoneStructureFile(object):

    @mock.patch('importer.requests.get')
    def test_ok(self, mock_get, configured_importer):
        expected = '{"key": "value"}'
        mock_resp = mock_requests_response(status=requests.codes.ok, json_data=expected)
        mock_get.return_value = mock_resp
        actual = configured_importer.get_loxone_structure_file()
        assert actual == expected

    @mock.patch('importer.requests.get')
    def test_internal_server_error(self, mock_get, configured_importer):
        mock_resp = mock_requests_response(status=requests.codes.internal_server_error, raise_for_status=HTTPError("ERROR"))
        mock_get.return_value = mock_resp
        with pytest.raises(HTTPError):
            configured_importer.get_loxone_structure_file()

    @mock.patch('importer.requests.get')
    def test_timeout(self, mock_get, configured_importer):
        mock_resp = mock_requests_response(status=None, raise_for_status=Timeout("TIMEOUT"))
        mock_get.return_value = mock_resp
        with pytest.raises(Timeout):
            configured_importer.get_loxone_structure_file()


@pytest.mark.parametrize('loxone_structure_file,loxone_controls', [
    ('{ "controls": { "99999999-9999-9999-9999999999999999": {"name": "test"} } }', '{ "99999999-9999-9999-9999999999999999": {"name": "test"} }'),
    ('{ "controls": { } }', '{}'),
])
@pytest.mark.usefixtures('unconfigured_importer')
def test_get_loxone_controls(loxone_structure_file, loxone_controls, unconfigured_importer):
    expected = json.loads(loxone_controls)
    actual = unconfigured_importer.get_loxone_controls(json.loads(loxone_structure_file))
    assert actual == expected


@pytest.mark.parametrize('loxone_structure_file,loxone_rooms', [
    ('{ "rooms": { "99999999-9999-9999-9999999999999999": {"name": "test"} } }', '{ "99999999-9999-9999-9999999999999999": {"name": "test"}, "00000000-0000-0000-0000000000000000": {"uuid": "00000000-0000-0000-0000000000000000", "name": ""} }'),
    ('{ "rooms": { } }', '{ "00000000-0000-0000-0000000000000000": {"uuid": "00000000-0000-0000-0000000000000000", "name": ""} }'),
])
@pytest.mark.usefixtures('unconfigured_importer')
def test_get_loxone_rooms(loxone_structure_file, loxone_rooms, unconfigured_importer):
    expected = json.loads(loxone_rooms)
    actual = unconfigured_importer.get_loxone_rooms(json.loads(loxone_structure_file))
    assert actual == expected


@pytest.mark.parametrize('loxone_structure_file,loxone_categories', [
    ('{ "cats": { "99999999-9999-9999-9999999999999999": {"name": "test"} } }', '{ "99999999-9999-9999-9999999999999999": {"name": "test"}, "00000000-0000-0000-0000000000000000": {"uuid": "00000000-0000-0000-0000000000000000", "name": "undefined", "type": "undefined"} }'),
    ('{ "cats": { } }', '{ "00000000-0000-0000-0000000000000000": {"uuid": "00000000-0000-0000-0000000000000000", "name": "undefined", "type": "undefined"} }'),
])
@pytest.mark.usefixtures('unconfigured_importer')
def test_get_loxone_categories(loxone_structure_file, loxone_categories, unconfigured_importer):
    expected = json.loads(loxone_categories)
    actual = unconfigured_importer.get_loxone_categories(json.loads(loxone_structure_file))
    assert actual == expected


@pytest.mark.usefixtures('configured_importer')
class TestGenerateHaBridgeDevicesConfiguration(object):

    @pytest.mark.parametrize('loxone_structure_file,ha_bridge_devices_configuration', [
        ('LoxAPP3_1.json', 'LoxAPP3_1_ha_bridge.json'),
        ('LoxAPP3_2.json', 'LoxAPP3_2_ha_bridge.json'),
    ])
    def test_generate_ha_bridge_devices_configuration(self, loxone_structure_file, ha_bridge_devices_configuration, configured_importer):
        actual = configured_importer.generate_ha_bridge_devices_configuration(load_json_fixture_file(loxone_structure_file))
        expected = load_json_fixture_file(ha_bridge_devices_configuration)
        assert actual == expected


@pytest.mark.usefixtures('configured_importer')
class TestAddDevicesIntoHaBridge(object):

    @mock.patch('importer.requests.post')
    def test_ok(self, mock_post, configured_importer):
        ha_bridge_devices_configuration = [{'key': 'value'}]
        device_configuration = {'key': 'value'}
        mock_resp = mock_requests_response(status=requests.codes.created, json_data='{"key": "value"}')
        mock_post.return_value = mock_resp
        configured_importer.add_devices_into_ha_bridge(ha_bridge_devices_configuration)
        url = 'http://192.168.1.3:8080/api/devices'
        mock_post.assert_called_once_with(url, json=device_configuration, timeout=5)

    @mock.patch('importer.requests.post')
    def test_internal_server_error(self, mock_post, configured_importer):
        ha_bridge_devices_configuration = {'key': 'value'}
        mock_resp = mock_requests_response(status=requests.codes.internal_server_error, raise_for_status=HTTPError("ERROR"))
        mock_post.return_value = mock_resp
        with pytest.raises(HTTPError):
            configured_importer.add_devices_into_ha_bridge(ha_bridge_devices_configuration)

    @mock.patch('importer.requests.post')
    def test_timeout(self, mock_post, configured_importer):
        ha_bridge_devices_configuration = {'key': 'value'}
        mock_resp = mock_requests_response(status=None, raise_for_status=Timeout("TIMEOUT"))
        mock_post.return_value = mock_resp
        with pytest.raises(Timeout):
            configured_importer.add_devices_into_ha_bridge(ha_bridge_devices_configuration)


@pytest.mark.usefixtures('cli_runner')
class TestCommandLineInterface(object):

    def test_no_parameter(self, cli_runner):
        actual = cli_runner.invoke(cli, [])
        assert actual.exit_code == 2
        assert 'Usage: cli [OPTIONS]' in actual.output
        assert "Error: Missing option '--loxone-miniserver-host'." in actual.output

    def test_help(self, cli_runner):
        actual = cli_runner.invoke(cli, ['--help'])
        assert actual.exit_code == 0
        assert 'Usage: cli [OPTIONS]' in actual.output

    @mock.patch('importer.Importer', autospec=True)
    def test_with_mandatory_parameter(self, mock_importer, cli_runner):
        actual = cli_runner.invoke(cli, ['--loxone-miniserver-host=192.168.1.2', '--loxone-username=player1', '--loxone-password=secret'])
        assert actual.exit_code == 0
        assert 'Retrieve visualisation structure file from Loxone MiniServer' in actual.output
        assert 'Generate HA-Bridge devices configruation from visualisation structure file' in actual.output
        assert 'Add devices over REST API into HA-Bridge' in actual.output
