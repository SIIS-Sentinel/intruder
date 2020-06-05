#!/usr/bin/env python3

import time
import config_hub as cfg
import argparse
import paho.mqtt.client as mqtt

from sql import session, Attack, Node


class IntruderHub():
    def __init__(self, name="hub"):
        self.name = name
        self.topic_base: str = cfg.topic_prefix
        self.client: mqtt.Client = mqtt.Client(self.name)

    def connect(self) -> None:
        self.client.tls_set(
            ca_certs=cfg.ca_file,
            certfile=cfg.cert_file,
            keyfile=cfg.key_file
        )
        self.client.on_connect = self.on_connect
        self.client.connect(cfg.broker_addr, cfg.broker_port)

    def on_connect(self, client: mqtt.Client, userdata, flags, rc) -> None:
        print("Connected to MQTT broker")

    @staticmethod
    def get_node_id(name: str):
        node = session.query(Node.id).filter_by(name=name).all()
        if len(node) == 0:
            return 0
        return node[0].id

    @staticmethod
    def add_attack(node: int, ts: float, attack_type: int):
        newAttack: Attack = Attack(
            timestamp=ts, attack_type=attack_type, node_id=node)
        session.add(newAttack)
        session.commit()

    def start_attack(
            self,
            attack_type: int,
            start: int,
            duration: int,
            node_name: str,
            intensity: int):
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        start_time: int = int(time.time() + start)
        payload: str = str(attack_type) + "/" + \
            str(start_time) + "/" + \
            str(duration) + "/" + \
            str(intensity)
        topic_set: str = self.topic_base + node_name + "/set"
        self.client.publish(topic_set, payload, qos=1)
        # Log the attack in the DB for plotting
        node_id: int = self.get_node_id(node_name)
        self.add_attack(node_id, start_time, attack_type)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Details of the attack to start')
    parser.add_argument('-t', type=int, default=0, dest="attack_type",
                        help="Attack type (defaults to 0)")
    parser.add_argument('-s', type=int, default=0, dest="start",
                        help="Start time offet (defaults to 0)")
    parser.add_argument('-d', type=int, default=60, dest="duration",
                        help='Attack duration (defaults to 60s)')
    parser.add_argument('-a', type=str, default=cfg.default_node, dest="node_name",
                        help='Node IP address (defaults to cfg.node_addr)')
    parser.add_argument('-i', type=int, default=100, dest="intensity",
                        help="Attack intensity (between 0 and 100, defaults to 100")

    args = parser.parse_args()
    intruder = IntruderHub()
    intruder.connect()
    intruder.start_attack(args.attack_type,
                          args.start,
                          args.duration,
                          args.node_name,
                          args.intensity)
