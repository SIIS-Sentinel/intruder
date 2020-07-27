import time

import paho.mqtt.client as mqtt

import intruder.config_hub as cfg

from bookkeeper.sql import create_sessions, Session, Attack, Node


class IntruderHub():
    """
    This class represents the hub side of the Intruder application.

    Is uses an MQTT client to listen for incoming control messages, which it uses to determine which nodes should start which attacks.

    If no MQTT client is passed to the constructor, it will create a new one.

    If no database URL is given, it will use the one provided in the config_hub.py file
    """

    def __init__(self, name: str = "mqtt_intruder_1", client: mqtt.Client = None, debug: bool = False, db_path: str = None):
        self.name: str = name
        if db_path is None:
            self.db_path = cfg.db_path
        else:
            self.db_path = db_path
        self.session: Session = create_sessions(self.db_path)
        self.intruder_prefix: str = cfg.topic_prefix
        self.control_topic: str = cfg.topic_prefix + "control"

        self.client: mqtt.Client
        if client is None:
            self.client = mqtt.Client(self.name)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.tls_set(ca_certs=cfg.cafile,
                                certfile=cfg.certfile,
                                keyfile=cfg.keyfile)
        else:
            self.client = client

    def connect(self) -> None:
        "Connects the client to the MQTT broker."
        self.client.connect(cfg.broker_addr, cfg.broker_port)

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        "Callback method that is triggered when the client (re)connects to the broker."
        self.client.subscribe(self.control_topic)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage) -> None:
        "Callback method that is called when the client receives a message."
        if message.topic == self.control_topic:
            try:
                payload: str = message.payload.decode("utf-8")
                payload_split = payload.split("/")
                node_name: str = payload_split[0]
                attack_type: int = int(payload_split[1])
                start: int = int(payload_split[2])
                duration: int = int(payload_split[3])
                intensity: int = int(payload_split[4])
                self.start_attack(node_name, attack_type, start, duration, intensity)
                print(f"Intruder: started attack {attack_type} on {node_name}")
            except Exception as e:
                print(f"Intruder: exception '{e}' occurred during control message reception")
        else:
            print(f"Intruder: message from wrong topic received: {message.topic}")

    def get_node_id(self, name: str):
        "Helper method that queries the ID of the given node from the Sentinel database"
        node = self.session.query(Node.id).filter_by(name=name).all()
        if len(node) == 0:
            return 0
        return node[0].id

    def add_attack(self, node: int, ts: float, attack_type: int):
        "Helper method that adds a new Attack to the Sentinel database"
        newAttack: Attack = Attack(
            timestamp=ts, attack_type=attack_type, node_id=node)
        self.session.add(newAttack)
        self.session.commit()

    def start_attack(
            self,
            node_name: str,
            attack_type: int,
            start: int,
            duration: int,
            intensity: int):
        """
        Crafts and sends an MQTT message to the relevant node, with the data it needs to start an attack.
        """
        start_time: int = int(time.time() + start)
        payload: str = str(attack_type) + "/" + \
            str(start_time) + "/" + \
            str(duration) + "/" + \
            str(intensity)
        intruder_topic: str = self.intruder_prefix + node_name
        self.client.publish(intruder_topic, payload, qos=0)
        # Log the attack in the DB for plotting
        node_id: int = self.get_node_id(node_name)
        self.add_attack(node_id, start_time, attack_type)


if __name__ == "__main__":
    intr = IntruderHub(db_path="postgresql://pi:password@10.0.0.222/sentinel")
    intr.connect()
    intr.client.loop_forever()
