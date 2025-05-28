#!/usr/bin/env python3
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

# Configurar el puerto
PORT = 8000

class SimpleHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><head><title>Prueba Puerto 8000</title></head><body><h1>Servidor de prueba funcionando en puerto 8000</h1><p>Esta es una pagina de prueba para verificar que el puerto 8000 funciona correctamente.</p></body></html>")
        else:
            super().do_GET()

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"🚀 Servidor iniciado en http://localhost:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server() 