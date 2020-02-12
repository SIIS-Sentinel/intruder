#!/usr/bin/env python3

import socket
import time
import config as cfg
import argparse

from sql import session, Attack, Node


def get_node_id(name: str):
    node = session.query(Node.id).filter_by(name=name).all()
    if len(node) == 0:
        return 0
    return node[0].id


def add_attack(node: int, ts: float, attack_type: int):
    newAttack: Attack = Attack(
        timestamp=ts, attack_type=attack_type, node_id=node)
    session.add(newAttack)
    session.commit()


def start_attack(
        attack_type: int,
        start: int,
        duration: int,
        addr: str,
        port: int,
        intensity: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        start_time: int = int(time.time() + start)
        s.connect((addr, port))
        payload: str = str(attack_type) + "/" + \
            str(start_time) + "/" + \
            str(duration) + "/" + \
            str(intensity)
        payload_bytes: bytes = payload.encode("utf-8")
        s.sendall(payload_bytes)
        data: bytes = s.recv(1024)
    print('Received', data.decode())
    # Log the attack in the DB for plotting
    # TODO: fix the name determination
    node_id: int = get_node_id("node_1")
    add_attack(node_id, start_time, attack_type)


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
                        help='Node port (defaults to cfg.node_port)')
    parser.add_argument('-i', type=int, default=100, dest="intensity",
                        help="Attack intensity (between 0 and 100, defaults to 100")

    args = parser.parse_args()
    start_attack(args.attack_type, args.start, args.duration,
                 args.node_addr, args.node_port, args.intensity)
