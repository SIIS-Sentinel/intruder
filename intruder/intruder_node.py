import socket
import string
import time
import nmap
import dns.resolver
import random as rd
import threading

from typing import List, Callable, Tuple

import paho.mqtt.client as mqtt

import intruder.config_node as cfg


class IntruderNode():
    def __init__(self, name: str = "mqtt_intruder_1", client: mqtt.Client = None):
        self.name = name
        self.intruder_topic: str = cfg.topic_prefix + self.name

        if client is None:
            self.client: mqtt.Client = mqtt.Client(self.name)
            self.client.tls_set(ca_certs=cfg.cafile,
                                certfile=cfg.certfile,
                                keyfile=cfg.keyfile)
            self.client.on_message = self.on_message
            self.client.on_connect = self.on_connect
        else:
            self.client = client

    def connect(self) -> None:
        self.client.connect(cfg.broker_addr, cfg.broker_port)
        self.client.loop_start()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        self.client.subscribe(self.intruder_topic)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage) -> None:
        if message.topic == self.intruder_topic:
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
        print("Attack completed")

    def exfiltration_attack(self, duration: int, intensity: int) -> None:
        # Simulates an attacker exfiltrating data
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        start_time: int = int(time.time())
        port = rd.randint(cfg.exfil_port_min, cfg.exfil_port_max)
        while (time.time() - start_time < duration):
            message: bytes = self.random_message()
            sock.sendto(message, (cfg.exfil_addr, port))
        print("Attack completed")

    def pivot_attack(self, duration: int, intensity: int) -> None:
        # This simulates the side effects of a corrupted node used as an Nmap scanner
        nm = nmap.PortScanner()
        start_time = int(time.time())
        while (time.time() - start_time < duration):
            nm.scan(cfg.pivot_addr, arguments="-sn")
        print("Attack completed")

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
        attack: Callable
        args: Tuple
        if attack_type == cfg.PIVOT_NMAP:
            attack = self.pivot_attack
            args = (duration, intensity)
            # self.pivot_attack(duration, intensity)
        elif attack_type == cfg.EXFILTRATION:
            attack = self.exfiltration_attack
            args = (duration, intensity)
            # self.exfiltration_attack(duration, intensity)
        elif attack_type == cfg.BLACK_HOLE:
            attack = self.routing_attack
            args = (duration, intensity)
            # self.routing_attack(duration, intensity)
        elif attack_type == cfg.GREY_HOLE:
            attack = self.routing_attack
            args = (duration, intensity)
            # self.routing_attack(duration, intensity, 0.4)
        th: threading.Thread = threading.Thread(target=attack, args=args)
        th.start()
        print("Attack started")
