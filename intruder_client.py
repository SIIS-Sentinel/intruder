#!/usr/bin/env python3

import socket
import time
import config as cfg


def start_attack(attack_type: int, start: int, duration: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((cfg.server_addr, cfg.server_port))
        payload = str(attack_type) + "/" + str(int(time.time()) +
                                               start) + "/" + str(duration)
        s.sendall(payload.encode("utf-8"))
        data = s.recv(1024)

    print('Received', data.decode())


if __name__ == "__main__":
    start_attack(0, 1, 10)
