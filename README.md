# Intruder

Intruder is a small library that simulates IoT attacks, designed to help evaluate Sentinel. It uses MQTT to signal a node what attack it should run.

## Installing

While `Intruder` can be installed as a standalone application, it is recommended it to instead use it as part of the [Scheduler](https://github.com/SIIS-Sentinel/scheduler) application for the hub, and [IoT handlers](https://github.com/SIIS-Sentinel/iot-integrations) for the nodes.

To install it as standalone, follow these steps:

* Create a new virtual environment: `virtualenv venv`
* Activate it: `source venv/bin/activate`
* Install the dependencies: `pip install -e .`

## Usage

Intruder is designed to run on both the hub (where it orchestrates attacks, and stores the relevant information in the Sentinel SQL database, using [bookkeeper](https://github.com/SIIS-Sentinel/bookkeeper)) and the nodes (where the attacks are run).

Intruder is configured using the `config_node.py` and `config_hub.py` files. 

For a node:
* Import `intruder.intruder_node` 
* Create an intruder handler: `intr = IntruderNode($MQTT_TOPIC, $MQTT_CLIENT)`
* Whenever an MQTT message is sent to `intruder/$MQTT_TOPIC`, the intruder handler will decode it and execute the correct attack

**Note:** The attack messages are slash-separated string, with the following fields:
1. Attack type (`int`): the type of attack to run (between 0 and 4)
2. Start (`int`): delay (in seconds) before the start of the attack
3. Duration (`int`): duration of the attack (in seconds)
4. Intensity (`int`): attack intensity, between 0 and 100 (not implemented for all attacks yet)

For the hub:
* Import `intruder.intruder_hub` 
* Create an intruder handler: `intr = IntruderNode($MQTT_CLIENT_NAME, $MQTT_CLIENT, $DEBUG, $DB_URL)`
* Whenever an MQTT message is sent to `intruder/control`, the intruder handler will decode it, and send a new message to the corresponding node to trigger an attack

**Note:** The control messages are slash-separated string, with the following fields:
1. Node topic (`str`): the topic suffix to which the message will be sent
2. Attack type (`int`): the type of attack to run (between 0 and 4)
3. Start (`int`): delay (in seconds) before the start of the attack
4. Duration (`int`): duration of the attack (in seconds)
5. Intensity (`int`): attack intensity, between 0 and 100 (not implemented for all attacks yet)