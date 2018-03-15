#!/usr/bin/env python
# -*- coding: utf-8 -*-

from importer import Importer
from unittest import TestCase, mock
from requests.exceptions import HTTPError, Timeout
import os

fixtures_dir = os.path.abspath('tests/fixtures')


class TestClass(object):
    @classmethod
    def setup_class(cls):
        cls.actual = Importer()

    @classmethod
    def teardown_class(cls):
        del cls.actual

    def test_set_loxone_miniserver(self):
        expected = '192.168.1.2'
        self.actual.set_loxone_miniserver(expected)
        assert self.actual.loxone_miniserver == expected

    def test_set_loxone_username(self):
        expected = 'player1'
        self.actual.set_loxone_username(expected)
        assert self.actual.loxone_username == expected

    def test_set_loxone_password(self):
        expected = 'secret'
        self.actual.set_loxone_password(expected)
        assert self.actual.loxone_password == expected

    def test_set_ha_bridge_server(self):
        expected = '192.168.1.3'
        self.actual.set_ha_bridge_server(expected)
        assert self.actual.ha_bridge_server == expected

    def test_set_ha_bridge_port(self):
        expected = '8080'
        self.actual.set_ha_bridge_port(expected)
        assert self.actual.ha_bridge_port == expected


class TestGetLoxoneStructureFile(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = Importer()
        cls.actual.loxone_miniserver = '192.168.1.2'
        cls.actual.loxone_username = 'player1'
        cls.actual.loxone_password = 'secret'
        cls.actual.ha_bridge_server = '192.168.1.3'
        cls.actual.ha_bridge_port = '8080'

    @classmethod
    def tearDownClass(cls):
        del cls.actual

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
    def test_ok(self, mock_get):
        expected = '{"key": "value"}'
        mock_resp = self._mock_response(status=200, json_data=expected)
        mock_get.return_value = mock_resp

        actual = self.actual.get_loxone_structure_file()
        self.assertEqual(actual, expected)

    @mock.patch('importer.requests.get')
    def test_internal_server_error(self, mock_get):
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("ERROR"))
        mock_get.return_value = mock_resp

        self.assertRaises(HTTPError, self.actual.get_loxone_structure_file)

    @mock.patch('importer.requests.get')
    def test_timeout(self, mock_get):
        mock_resp = self._mock_response(status=None, raise_for_status=Timeout("TIMEOUT"))
        mock_get.return_value = mock_resp

        self.assertRaises(Timeout, self.actual.get_loxone_structure_file)
