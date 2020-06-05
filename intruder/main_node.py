#!/usr/bin/env python3

import socket
import time
import config_node as cfg
import nmap
import random as rd
import string
import dns.resolver
import paho.mqtt.client as mqtt

from typing import List


class IntruderNode():
    def __init__(self, name: str):
        self.name: str = name
        self.topic_base: str = cfg.topic_prefix + self.name
        self.topic_set: str = self.topic_base + "/set"
        self.topic_state: str = self.topic_base + "/state"
        self.client: mqtt.Client = mqtt.Client(self.name)

    def connect(self) -> None:
        self.client.tls_set(ca_certs=cfg.ca_file,
                            certfile=cfg.cert_file,
                            keyfile=cfg.key_file
                            )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(cfg.broker_addr, port=cfg.broker_port)

    def on_connect(self, client: mqtt.Client, userdata, flags, rc) -> None:
        print("Connected to MQTT broker")
        self.client.subscribe(self.topic_set)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage) -> None:
        if message.topic == self.topic_set:
            payload: str = message.payload.decode("utf-8")
            payload_args: List[int] = [int(i) for i in payload.split("/")]
            if len(payload_args) != 4:
                print(f"Error, wrong number of arguments received: expected 4, got {len(payload_args)}.")
            self.start_attack(
                payload_args[0],
                payload_args[1],
                payload_args[2],
                payload_args[3])

        else:
            print(f"Received message from from topic: {message.topic}")

    def loop_forever(self) -> None:
        self.client.loop_forever()

    @staticmethod
    def random_message(length: int = 1024) -> bytes:
        # Generates a random string of ASCII characters of the given length
        letters = string.ascii_letters
        message = ''.join([rd.choice(letters) for i in range(length)])
        encoded_message = message.encode("utf-8")
        return encoded_message

    def routing_attack(self, duration: int, intensity: int, drop_rate: float = 1) -> None:
        # Simulates a black/grey hole attack where all the traffic gets routed to the node
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        start_time = time.time()
        while (time.time() - start_time < duration):
            answers = dns.resolver.query(cfg.black_hole_src, "MX")
            if (rd.random() > drop_rate):
                # Route the packet to its destination
                message = (''.join(str([e for e in answers]))).encode("utf-8")
                sock.sendto(message, (cfg.black_hole_dest, cfg.black_hole_port))

    def exfiltration_attack(self, duration: int, intensity: int) -> None:
        # Simulates an attacker exfiltrating data
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        start_time: int = int(time.time())
        port = rd.randint(cfg.exfil_port_min, cfg.exfil_port_max)
        while (time.time() - start_time < duration):
            message: bytes = self.random_message()
            sock.sendto(message, (cfg.exfil_addr, port))

    def pivot_attack(self, duration: int, intensity: int) -> None:
        # This simulates the side effects of a corrupted node used as an Nmap scanner
        nm = nmap.PortScanner()
        start_time = int(time.time())
        while (time.time() - start_time < duration):
            nm.scan(cfg.pivot_addr, arguments="-sn")

    def start_attack(
            self,
            attack_type: int,
            start: int,
            duration: int,
            intensity: int) -> None:
        print("Starting attack %d, starting a time %d, lasting for %d seconds" % (
            attack_type, start, duration))
        # Wait until the start of the attack
        if (start > time.time()):
            time.sleep(start - time.time())
        if attack_type == cfg.PIVOT_NMAP:
            self.pivot_attack(duration, intensity)
        elif attack_type == cfg.EXFILTRATION:
            self.exfiltration_attack(duration, intensity)
        elif attack_type == cfg.BLACK_HOLE:
            self.routing_attack(duration, intensity)
        elif attack_type == cfg.GREY_HOLE:
            self.routing_attack(duration, intensity, 0.4)
        print("Attack completed")


# def run_server(server_addr: str, port: int) -> None:
#     # Runs an attacker server forever
#     while True:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             # Create the socket
#             s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#             s.bind((server_addr, port))
#             s.listen()
#             # Accept the connection
#             conn, addr = s.accept()
#             print('Connected by', addr)
#             data_bytes: bytes = conn.recv(1024)
#             conn.sendall(b'OK')
#             # Decode and process the request
#             data: str = data_bytes.decode()
#             data_args_str: List[str] = data.split("/")
#             data_args: List[int] = [int(i) for i in data_args_str]
#             start_attack(data_args[0], data_args[1],
#                          data_args[2], data_args[3])


if __name__ == "__main__":
    intruder = IntruderNode("node")
    intruder.connect()
    intruder.loop_forever()
    # run_server(cfg.node_addr, cfg.node_port)
