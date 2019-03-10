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
        self.control_actions_map = {
            'Alarm': {'on': 'delayedon', 'off': 'off'},
            'CentralAlarm': {'on': 'delayedon', 'off': 'off'},
            'CentralGate': {'on': 'open', 'off': 'close'},
            'CentralJalousie': {'on': 'fulldown', 'off': 'fullup'},
            'Daytimer': None,
            'Dimmer': {'on': 'on', 'off': 'off'},
            'Gate': {'on': 'open', 'off': 'close'},
            'InfoOnlyAnalog': None,
            'InfoOnlyDigital': None,
            'IRoomController': None,
            'IRoomControllerV2': None,
            'Jalousie': {'on': 'fulldown', 'off': 'fullup'},
            'Meter': None,
            'Presence': None,
            'Pushbutton': {'on': 'on', 'off': 'off'},
            'Radio': None,
            'Switch': {'on': 'pulse', 'off': 'pulse'},
            'TextState': None,
            'TimedSwitch': {'on': 'pulse', 'off': 'off'},
            'UpDownDigital': {'on': 'pulseup', 'off': 'pulsedown'},
            'Webpage': None,
            'WindowMonitor': None
        }

    def print_configuration(self):
        """Prints configuration of Importer"""
        logging.debug('Loxone MiniServer is set to "{host}"'.format(
            host=self.loxone_miniserver))
        logging.debug('Loxone username is set to "{username}"'.format(
            username=self.loxone_username))
        logging.debug('Loxone password is set to "{password}"'.format(
            password=self.loxone_password))
        logging.debug('HA-Bridge server is set to "{host}"'.format(
            host=self.ha_bridge_server))
        logging.debug('HA-Bridge port is set to "{port}"'.format(
            port=self.ha_bridge_port))

    def get_loxone_structure_file(self):
        """Retrieves visualisation structure file from Loxone MiniServer"""
        url = 'http://{host}/data/LoxAPP3.json'.format(
              host=self.loxone_miniserver)
        r = requests.get(
            url,
            auth=(self.loxone_username, self.loxone_password),
            timeout=5)

        if r.status_code != requests.codes.ok:
            r.raise_for_status()

        loxone_structure_file = r.json()
        logging.debug(loxone_structure_file)

        return loxone_structure_file

    def get_loxone_controls(self, loxone_structure_file):
        """Extracts controls from Loxone structure file"""
        loxone_controls = loxone_structure_file.get('controls')
        return loxone_controls

    def get_loxone_rooms(self, loxone_structure_file):
        """Extracts rooms from Loxone structure file
        and adds a blank room definition"""
        loxone_rooms = loxone_structure_file.get('rooms')
        loxone_rooms['00000000-0000-0000-0000000000000000'] = {
            'uuid': '00000000-0000-0000-0000000000000000',
            'name': ''
        }
        return loxone_rooms

    def get_loxone_categories(self, loxone_structure_file):
        """Extracts categories from Loxone structure file
        and adds a blank category definition"""
        loxone_categories = loxone_structure_file.get('cats')
        loxone_categories['00000000-0000-0000-0000000000000000'] = {
            'uuid': '00000000-0000-0000-0000000000000000',
            'name': 'undefined',
            'type': 'undefined'
        }
        return loxone_categories

    def generate_ha_bridge_devices_configuration(self, loxone_structure_file):
        """Generates HA-Bridge devices configruation
        from visualisation structure file"""
        ha_bridge_devices_configuration = []
        loxone_url_schema = 'http://{username}:{password}@{miniserver}/dev/sps/io/{control}/{action}'
        loxone_controls = self.get_loxone_controls(loxone_structure_file)
        loxone_rooms = self.get_loxone_rooms(loxone_structure_file)
        loxone_categories = self.get_loxone_categories(loxone_structure_file)

        for uuid, control in sorted(loxone_controls.items()):
            control_name = control.get('name')
            control_type = control.get('type')
            room_uuid = control.get('room', '00000000-0000-0000-0000000000000000')
            category_uuid = control.get('cat', '00000000-0000-0000-0000000000000000')
            device_name = '{control_name} {room_name}'.format(
                control_name=control_name,
                room_name=loxone_rooms[room_uuid]['name'])
            device_name = device_name.strip()
            device_description = 'Control-Type: {control_type}, Category: {category}'.format(
                control_type=control_type,
                category=loxone_categories[category_uuid]['name'])
            ha_bridge_device = {
                'name': device_name,
                'description': device_description,
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

            if control_type in self.control_actions_map:
                if self.control_actions_map[control_type] is not None:
                    if 'on' in self.control_actions_map[control_type]:
                        url = loxone_url_schema.format(
                            username=self.loxone_username,
                            password=self.loxone_password,
                            miniserver=self.loxone_miniserver,
                            control=uuid,
                            action=self.control_actions_map[control_type]['on'])
                        ha_bridge_on[0]['item'] = url
                        ha_bridge_device['onUrl'] = json.dumps(ha_bridge_on)
                    if 'dim' in self.control_actions_map[control_type]:
                        url = loxone_url_schema.format(
                            username=self.loxone_username,
                            password=self.loxone_password,
                            miniserver=self.loxone_miniserver,
                            control=uuid,
                            action=self.control_actions_map[control_type]['dim'])
                        ha_bridge_dim[0]['item'] = url
                        ha_bridge_device['dimUrl'] = json.dumps(ha_bridge_dim)
                    if 'off' in self.control_actions_map[control_type]:
                        url = loxone_url_schema.format(
                            username=self.loxone_username,
                            password=self.loxone_password,
                            miniserver=self.loxone_miniserver,
                            control=uuid,
                            action=self.control_actions_map[control_type]['off'])
                        ha_bridge_off[0]['item'] = url
                        ha_bridge_device['offUrl'] = json.dumps(ha_bridge_off)
                    ha_bridge_devices_configuration.append(ha_bridge_device)
            else:
                logging.warn('Control type "{control_type}" is not supported at the moment.'.format(
                    control_type=control_type))

        return ha_bridge_devices_configuration

    def add_devices_into_ha_bridge(self, ha_bridge_devices_configuration):
        """Adds devices over REST API into HA-Bridge"""
        url = 'http://{host}:{port}/api/devices'.format(
              host=self.ha_bridge_server,
              port=self.ha_bridge_port)

        for device_configuration in ha_bridge_devices_configuration:
            r = requests.post(url, json=device_configuration, timeout=5)
            logging.debug(r.text)

            if r.status_code != requests.codes.created:
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
    importer.loxone_miniserver = kwargs['loxone_miniserver']
    importer.loxone_username = kwargs['loxone_username']
    importer.loxone_password = kwargs['loxone_password']
    importer.ha_bridge_server = kwargs['ha_bridge_server']
    importer.ha_bridge_port = kwargs['ha_bridge_port']
    importer.print_configuration()

    # Run Importer
    click.echo('Retrieve visualisation structure file from Loxone MiniServer')
    loxone_structure_file = importer.get_loxone_structure_file()
    click.echo('Generate HA-Bridge devices configruation from visualisation structure file')
    ha_bridge_devices_configuration = importer.generate_ha_bridge_devices_configuration(loxone_structure_file)
    click.echo('Add devices over REST API into HA-Bridge')
    importer.add_devices_into_ha_bridge(ha_bridge_devices_configuration)


if __name__ == '__main__':
    cli()
