#!/usr/bin/env python3
"""
Servidor HTTP simple para pruebas
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

# Forzar puerto 8000
PORT = 8000
HOST = '0.0.0.0'

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='application/json'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
    
    def do_GET(self):
        self._set_headers()
        response = {
            'status': 'ok',
            'message': 'Servidor funcionando correctamente',
            'port': PORT,
            'path': self.path
        }
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self._set_headers()
        response = {
            'status': 'ok',
            'message': 'Datos recibidos correctamente',
            'received_data': post_data.decode(),
            'path': self.path
        }
        self.wfile.write(json.dumps(response).encode())

def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"🚀 Servidor iniciado en http://{HOST}:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server() 