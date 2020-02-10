#!/usr/bin/env python3

import socket
import time
import config as cfg
import nmap
import random as rd
import string
import dns.resolver
from typing import List


def random_message(length: int = 1024) -> bytes:
    # Generates a random string of ASCII characters of the given length
    letters = string.ascii_letters
    message = ''.join([rd.choice(letters) for i in range(length)])
    encoded_message = message.encode("utf-8")
    return encoded_message


def routing_attack(duration: int, intensity: int, drop_rate: float = 1) -> None:
    # Simulates a black/grey hole attack where all the traffic gets routed to the node
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time = time.time()
    while (time.time() - start_time < duration):
        answers = dns.resolver.query(cfg.black_hole_src, "MX")
        if (rd.random() > drop_rate):
            # Route the packet to its destination
            message = (''.join(str([e for e in answers]))).encode("utf-8")
            sock.sendto(message, (cfg.black_hole_dest, cfg.black_hole_port))


def exfiltration_attack(duration: int, intensity: int) -> None:
    # Simulates an attacker exfiltrating data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_time: int = int(time.time())
    port = rd.randint(cfg.exfil_port_min, cfg.exfil_port_max)
    while (time.time() - start_time < duration):
        message: bytes = random_message()
        sock.sendto(message, (cfg.exfil_addr, port))


def pivot_attack(duration: int, intensity: int) -> None:
    # This simulates the side effects of a corrupted node used as an Nmap scanner
    nm = nmap.PortScanner()
    start_time = int(time.time())
    while (time.time() - start_time < duration):
        nm.scan(cfg.pivot_addr, arguments="-sn")


def start_attack(
        attack_type: int,
        start: int,
        duration: int,
        intensity: int) -> None:
    print("Starting attack %d, starting a time %d, lasting for %d seconds" % (
        attack_type, start, duration))
    # Wait until the start of the attack
    if (time.time() - duration > 0):
        time.sleep(time.time() - duration)
    if attack_type == cfg.PIVOT_NMAP:
        pivot_attack(duration, intensity)
    elif attack_type == cfg.EXFILTRATION:
        exfiltration_attack(duration, intensity)
    elif attack_type == cfg.BLACK_HOLE:
        routing_attack(duration, intensity)
    elif attack_type == cfg.GREY_HOLE:
        routing_attack(duration, intensity, 0.4)


def run_server(addr: str, port: int) -> None:
    # Runs an attacker server forever
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Create the socket
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((addr, port))
            s.listen()
            # Accept the connection
            conn, addr = s.accept()
            print('Connected by', addr)
            data_bytes: bytes = conn.recv(1024)
            conn.sendall(b'OK')
            # Decode and process the request
            data: str = data_bytes.decode()
            data_args_str: List[str] = data.split("/")
            data_args: List[int] = [int(i) for i in data_args_str]
            start_attack(data_args[0], data_args[1],
                         data_args[2], data_args[3])


if __name__ == "__main__":
    run_server(cfg.node_addr, cfg.node_port)
