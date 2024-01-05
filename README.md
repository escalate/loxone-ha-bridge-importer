[![Tests](https://github.com/escalate/loxone-ha-bridge-importer/actions/workflows/tests.yml/badge.svg?branch=master&event=push)](https://github.com/escalate/loxone-ha-bridge-importer/actions/workflows/tests.yml)

# Loxone / HA-Bridge Importer

A commandline tool to import [Loxone](https://www.loxone.com) controls into [HA-Bridge](https://github.com/bwssytems/ha-bridge).

**ATTENTION** It is recommended to create an backup of the current HA-Bridge configuration before using this tool.

## Supported Loxone control types and actions
This is just the list of already implemented control types with there meaningful actions.

Loxone offers many more control types and if you are missing one please create a Pull Request or open an Issue on Github.

| Control type      | On        | Dim | Off       |
| ----------------- | --------- | --- | --------- |
| Alarm             | delayedon | -   | off       |
| CentralAlarm      | delayedon | -   | off       |
| CentralGate       | open      | -   | close     |
| CentralJalousie   | fulldown  | -   | fullup    |
| Daytimer          | -         | -   | -         |
| Dimmer            | on        | -   | off       |
| Gate              | open      | -   | close     |
| InfoOnlyAnalog    | -         | -   | -         |
| InfoOnlyDigital   | -         | -   | -         |
| IRoomController   | -         | -   | -         |
| IRoomControllerV2 | -         | -   | -         |
| Jalousie          | fulldown  | -   | fullup    |
| LightController   | on        | -   | off       |
| LightControllerV2 | plus      | -   | minus     |
| Meter             | -         | -   | -         |
| Presence          | -         | -   | -         |
| Pushbutton        | on        | -   | off       |
| Radio             | -         | -   | -         |
| Switch            | pulse     | -   | pulse     |
| TextState         | -         | -   | -         |
| TimedSwitch       | pulse     | -   | off       |
| Tracker           | -         | -   | -         |
| UpDownDigital     | pulseup   | -   | pulsedown |
| Webpage           | -         | -   | -         |
| WindowMonitor     | -         | -   | -         |

## Installation
Tested with Python 3.12 on Ubuntu 22.04

If you encounter issues with 3.12.x patch versions of Python, please open a Github issue.

### Requirements
Install needed requirements via pip

```
$ pip install -r requirements.txt
```

### Run
Run tool from commandline
```
$ ./importer.py
```

## Usage
```
$ ./importer.py --help

Usage: importer.py [OPTIONS]

    Commandline interface for Loxone / HA-Bridge Importer

Options:
    --loxone-miniserver-host TEXT    Set IP address / hostname of Loxone MiniServer  [required]
    --loxone-miniserver-port INTEGER Set port of Loxone MiniServer (Default: 80) [required]
    --loxone-username TEXT           Set username for Loxone MiniServer login [required]
    --loxone-password TEXT           Set password for Loxone MiniServer login [required]
    --ha-bridge-host TEXT            Set IP address / hostname of HA-Bridge server (Default: localhost) [required]
    --ha-bridge-port INTEGER         Set port of HA-Bridge server (Default: 8080) [required]
    --verbose                        Enable verbose logging output
    --help                           Show this message and exit.
```

## Docker
Build Docker image
```
$ docker build \
    --tag=importer \
    .
```

Run Docker container from built image to print help
```
$ docker run \
    importer

Usage: importer.py [OPTIONS]

    Commandline interface for Loxone / HA-Bridge Importer

Options:
...
```

Run Docker container from built image with additional arguments
```
$ docker run \
    importer \
    --loxone-miniserver-host="192.168.1.2" \
    --loxone-username="alexa" \
    --loxone-password="AmAz0n" \
    --verbose
```

## Dependencies
* [click](https://pypi.python.org/pypi/click)
* [requests](https://pypi.python.org/pypi/requests)

## Contribute
Please note the separate [contributing guide](https://github.com/escalate/loxone-ha-bridge-importer/blob/master/CONTRIBUTING.md).

## License
MIT
