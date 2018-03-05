#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Commandline interface
to control Importer class"""

import json
import requests
import logging
import click
from collections import OrderedDict


class Importer(object):
    """Class to retrieve all controls from Loxone MiniServer
    and send them to HA-Bridge server"""

    def __init__(self):
        """Constructor"""

        # Declare variables
        self.loxone_miniserver = None
        self.loxone_username = None
        self.loxone_password = None
        self.ha_bridge_server = None
        self.ha_bridge_port = None

    def set_loxone_miniserver(self, loxone_miniserver):
        """Sets the IP address of Loxone MiniServer"""
        self.loxone_miniserver = loxone_miniserver
        logging.debug('Loxone MiniServer is set to "{host}"'.format(host=loxone_miniserver))

    def set_loxone_username(self, loxone_username):
        """Sets the username for Loxone MiniServer login"""
        self.loxone_username = loxone_username
        logging.debug('Loxone username is set to "{username}"'.format(username=loxone_username))

    def set_loxone_password(self, loxone_password):
        """Sets the password for Loxone MiniServer login"""
        self.loxone_password = loxone_password
        logging.debug('Loxone password is set to "{password}"'.format(password=loxone_password))

    def set_ha_bridge_server(self, ha_bridge_server):
        """Sets the IP address of HA-Bridge server"""
        self.ha_bridge_server = ha_bridge_server
        logging.debug('HA-Bridge server is set to "{host}"'.format(host=ha_bridge_server))

    def set_ha_bridge_port(self, ha_bridge_port):
        """Sets the port of HA-Bridge server"""
        self.ha_bridge_port = ha_bridge_port
        logging.debug('HA-Bridge port is set to "{port}"'.format(port=ha_bridge_port))

    def get_loxone_structure_file(self):
        """Retrieves visualisation structure file from Loxone MiniServer"""
        url = 'http://{host}/data/LoxAPP3.json'.format(host=self.loxone_miniserver)
        r = requests.get(url, auth=(self.loxone_username, self.loxone_password), timeout=5)

        if r.status_code != 200:
            r.raise_for_status()

        loxone_structure_file = r.json()
        logging.debug(loxone_structure_file)

        return loxone_structure_file

    def generate_ha_bridge_devices_configuration(self, loxone_structure_file):
        """Generates HA-Bridge devices configruation
        from visualisation structure file"""
        ha_bridge_devices_configuration = []
        loxone_url_schema = 'http://{username}:{password}@{miniserver}/dev/sps/io/{control}/{action}'
        loxone_rooms = loxone_structure_file['rooms']
        loxone_controls = loxone_structure_file['controls']

        control_actions_mapping = {
            'CentralGate': {'on': 'Open', 'off': 'Close'},
            'CentralJalousie': {'on': 'FullDown', 'off': 'FullUp'},
            'Daytimer': None,
            'Dimmer': {'on': 'On', 'off': 'Off'},
            'Gate': {'on': 'Open', 'off': 'Close'},
            'InfoOnlyAnalog': None,
            'InfoOnlyDigital': None,
            'IRoomController': None,
            'Jalousie': {'on': 'FullDown', 'off': 'FullUp'},
            'Meter': None,
            'Presence': None,
            'Pushbutton': {'on': 'On', 'off': 'Off'},
            'Switch': {'on': 'Pulse', 'off': 'Pulse'},
            'TimedSwitch': {'on': 'Pulse', 'off': 'Off'},
            'Webpage': None
        }

        for uuid, control in sorted(loxone_controls.items()):
            control_type = control['type']
            room_uuid = control['room']
            device_name = '{control_name} {room_name}'.format(control_name=control['name'],
                                                              room_name=loxone_rooms[room_uuid]['name'])
            ha_bridge_device = {
                'name': device_name,
                'targetDevice': 'Loxone',
                'deviceType': 'custom',
                'mapType': 'httpDevice',
                'mapId': uuid
            }

            item = OrderedDict()
            item['item'] = ''
            item['type'] = 'httpDevice'
            item['httpVerb'] = 'GET'
            item['contentType'] = 'text/html'

            ha_bridge_on = []
            ha_bridge_on.append(item)
            ha_bridge_dim = []
            ha_bridge_dim.append(item)
            ha_bridge_off = []
            ha_bridge_off.append(item)

            if control_type in control_actions_mapping:
                if control_actions_mapping[control_type] is not None:
                    if 'on' in control_actions_mapping[control_type]:
                        url = loxone_url_schema.format(username=self.loxone_username,
                                                          password=self.loxone_password,
                                                          miniserver=self.loxone_miniserver,
                                                          control=uuid,
                                                          action=control_actions_mapping[control_type]['on'])
                        ha_bridge_on[0]['item'] = url
                        ha_bridge_device['onUrl'] = json.dumps(ha_bridge_on)
                    if 'dim' in control_actions_mapping[control_type]:
                        url = loxone_url_schema.format(username=self.loxone_username,
                                                           password=self.loxone_password,
                                                           miniserver=self.loxone_miniserver,
                                                           control=uuid,
                                                           action=control_actions_mapping[control_type]['dim'])
                        ha_bridge_dim[0]['item'] = url
                        ha_bridge_device['dimUrl'] = json.dumps(ha_bridge_dim)
                    if 'off' in control_actions_mapping[control_type]:
                        url = loxone_url_schema.format(username=self.loxone_username,
                                                           password=self.loxone_password,
                                                           miniserver=self.loxone_miniserver,
                                                           control=uuid,
                                                           action=control_actions_mapping[control_type]['off'])
                        ha_bridge_off[0]['item'] = url
                        ha_bridge_device['offUrl'] = json.dumps(ha_bridge_off)
                    ha_bridge_devices_configuration.append(ha_bridge_device)
            else:
                logging.warn('Control type "' + control_type + '" is not supported at the moment.')

        return ha_bridge_devices_configuration

    def add_devices_into_ha_bridge(self, ha_bridge_devices_configuration):
        """Adds devices over REST API into HA-Bridge"""
        url = 'http://{host}:{port}/api/devices'.format(host=self.ha_bridge_server, port=self.ha_bridge_port)

        for device_configuration in ha_bridge_devices_configuration:
            r = requests.post(url, json=device_configuration, timeout=5)
            logging.debug(r.text)

            if r.status_code != 201:
                r.raise_for_status()


@click.command()
@click.option('--loxone-miniserver',
              required=True,
              help='Set IP address of Loxone MiniServer')
@click.option('--loxone-username',
              required=True,
              help='Set username for Loxone MiniServer login')
@click.option('--loxone-password',
              required=True,
              help='Set password for Loxone MiniServer login')
@click.option('--ha-bridge-server',
              required=True,
              default='localhost',
              help='Set IP address of HA-Bridge server (Default: localhost)')
@click.option('--ha-bridge-port',
              required=True,
              default=8080,
              help='Set port of HA-Bridge server (Default: 8080)')
@click.option('--verbose',
              is_flag=True,
              help='Enable verbose logging output')
def cli(*args, **kwargs):
    """Commandline interface for Loxone / HA-Bridge Importer"""

    # Configure logging
    log_format = '%(levelname)s: %(message)s'
    if kwargs['verbose']:
        logging.basicConfig(format=log_format, level=logging.DEBUG)
    else:
        logging.basicConfig(format=log_format)

    # Instantiate Importer
    importer = Importer()

    # Handle required options
    importer.set_loxone_miniserver(kwargs['loxone_miniserver'])
    importer.set_loxone_username(kwargs['loxone_username'])
    importer.set_loxone_password(kwargs['loxone_password'])
    importer.set_ha_bridge_server(kwargs['ha_bridge_server'])
    importer.set_ha_bridge_port(kwargs['ha_bridge_port'])

    # Run Importer
    click.echo('Retrieve visualisation structure file from Loxone MiniServer')
    loxone_structure_file = importer.get_loxone_structure_file()
    click.echo('Generate HA-Bridge devices configruation from visualisation structure file')
    ha_bridge_devices_configuration = importer.generate_ha_bridge_devices_configuration(loxone_structure_file)
    click.echo('Add devices over REST API into HA-Bridge')
    importer.add_devices_into_ha_bridge(ha_bridge_devices_configuration)


if __name__ == '__main__':
    cli()
