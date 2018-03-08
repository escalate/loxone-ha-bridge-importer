#!/usr/bin/env python
# -*- coding: utf-8 -*-

from importer import Importer

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
