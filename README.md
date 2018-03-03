# Loxone / HA-Bridge Importer
A commandline tool to import [Loxone](https://www.loxone.com) controls into [HA-Bridge](https://github.com/bwssytems/ha-bridge).

**ATTENTION** It is recommended to create an backup of the current HA-Bridge configuration before using this tool.

## Supported Loxone control types and actions
This is just the list of already implemented control types with there meaningful actions.
Loxone offers many more control types and if you are missing one please create a Pull Request or open an Issue on Github.

| Control type    | On     | Dim | Off      |
| --------------- | ------ | --- | -------- |
| CentralGate     | Open   | -   | Close    |
| CentralJalousie | FullUp | -   | FullDown |
| Daytimer        | -      | -   | -        |
| Dimmer          | On     | -   | Off      |
| Gate            | Open   | -   | Close    |
| InfoOnlyAnalog  | -      | -   | -        |
| InfoOnlyDigital | -      | -   | -        |
| IRoomController | -      | -   | -        |
| Jalousie        | FullUp | -   | FullDown |
| Meter           | -      | -   | -        |
| Presence        | -      | -   | -        |
|'Pushbutton      | On     | -   | Off      |
| Switch          | Pulse  | -   | Pulse    |
| TimedSwitch     | Pulse  | -   | Off      |
| Webpage         | -      | -   | -        |

## Installation
Tested with Python 3.6.x on Ubuntu 16.04

If you encounter issues with 3.6.x patch versions of Python, please open a Github issue.

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
  --loxone-miniserver TEXT  Set IP address of Loxone MiniServer  [required]
  --loxone-username TEXT    Set username for Loxone MiniServer login
                            [required]
  --loxone-password TEXT    Set password for Loxone MiniServer login
                            [required]
  --ha-bridge-server TEXT   Set IP address of HA-Bridge server (Default:
                            localhost)  [required]
  --ha-bridge-port INTEGER  Set port of HA-Bridge server (Default: 8080)
                            [required]
  --verbose                 Enable verbose logging output
  --help                    Show this message and exit.
```

## Dependencies
* [click](https://pypi.python.org/pypi/click)
* [requests](https://pypi.python.org/pypi/requests)

## License
MIT
