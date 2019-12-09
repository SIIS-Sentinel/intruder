#!/usr/bin/env python3

import socket
import time
import config as cfg
import argparse


def start_attack(attack_type: int, start: int, duration: int, addr: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, port))
        payload = str(attack_type) + "/" + str(int(time.time()) +
                                               start) + "/" + str(duration)
        s.sendall(payload.encode("utf-8"))
        data = s.recv(1024)

    print('Received', data.decode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Details of the attack to start')
    parser.add_argument('-t', type=int, default=0, dest="attack_type",
                        help="Attack type (defaults to 0)")
    parser.add_argument('-s', type=int, default=0, dest="start",
                        help="Start time offet (defaults to 0)")
    parser.add_argument('-d', type=int, default=60, dest="duration",
                        help='Attack duration (defaults to 60s)')
    parser.add_argument('-a', type=str, default=cfg.node_addr, dest="node_addr",
                        help='Node IP address (defaults to cfg.node_addr)')
    parser.add_argument('-p', type=int, default=cfg.node_port, dest="node_port",
                        help='Attack duration (defaults to 60s)')

    args = parser.parse_args()
    start_attack(args.attack_type, args.start, args.duration, args.node_addr, args.node_port)
