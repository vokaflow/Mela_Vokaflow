#!/usr/bin/env python3
import socket

def test_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', port))
        print(f'Puerto {port} disponible')
        s.close()
        return True
    except Exception as e:
        print(f'Error al usar puerto {port}: {e}')
        return False

if __name__ == "__main__":
    test_port(8000)
    test_port(5000) 