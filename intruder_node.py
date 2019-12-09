#!/usr/bin/env python3

import socket
import config as cfg


def start_attack(attack_type: int, start: int, duration: int):
    print("Starting attack %d, starting a time %d, lasting for %d seconds" % (
        attack_type, start, duration))
    pass


def run_server(addr: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Create the socket
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((addr, port))
        s.listen()
        # Accept the connection
        conn, addr = s.accept()
        print('Connected by', addr)
        data = conn.recv(1024)
        conn.sendall(b'OK')
        # Decode and process the request
        data = data.decode()
        data_args = data.split("/")
        data_args = [int(i) for i in data_args]
        start_attack(data_args[0], data_args[1], data_args[2])


if __name__ == "__main__":
    run_server(cfg.node_addr, cfg.node_port)
