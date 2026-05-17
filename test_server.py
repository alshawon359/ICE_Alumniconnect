#!/usr/bin/env python3
"""
Simple HTTP server to test React routing with /iceaa base path
Serves the dist folder from /iceaa/ path
"""

import http.server
import socketserver
import os
import json
import urllib.parse
from pathlib import Path

PORT = 8000
DIST_DIR = Path(__file__).parent / 'react-app' / 'dist'

class IceaaHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the request path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Handle /iceaa/* paths
        if path.startswith('/iceaa/'):
            # Remove /iceaa prefix to find the file
            file_path = path[7:]  # Remove '/iceaa/'
        else:
            # Redirect root to /iceaa/
            if path == '/' or path == '':
                self.send_response(301)
                self.send_header('Location', '/iceaa/')
                self.end_headers()
                return
            file_path = path
        
        # Handle /iceaa/api/* requests (mock API responses)
        if file_path.startswith('api/'):
            api_endpoint = file_path[len('api/'):]
            self.handle_api_request(api_endpoint)
            return
        
        # Try to serve files from dist
        if not file_path or file_path.endswith('/'):
            # Try to serve index.html for SPA routing
            file_path_obj = DIST_DIR / (file_path if file_path else 'index.html')
            if not file_path_obj.exists() or file_path_obj.is_dir():
                file_path_obj = DIST_DIR / 'index.html'
        else:
            file_path_obj = DIST_DIR / file_path
        
        try:
            if file_path_obj.exists() and file_path_obj.is_file():
                self.send_response(200)
                if str(file_path).endswith('.html'):
                    self.send_header('Content-type', 'text/html')
                elif str(file_path).endswith('.js'):
                    self.send_header('Content-type', 'application/javascript')
                elif str(file_path).endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                elif str(file_path).endswith('.json'):
                    self.send_header('Content-type', 'application/json')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                with open(file_path_obj, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                # SPA fallback - serve index.html for any non-file request
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open(DIST_DIR / 'index.html', 'rb') as f:
                    self.wfile.write(f.read())
        except Exception as e:
            self.send_error(404, str(e))
    
    def do_POST(self):
        # Handle POST requests for /iceaa/api/* (mock API)
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/iceaa/'):
            file_path = path[7:]
        else:
            file_path = path

        if file_path.startswith('api/'):
            api_endpoint = file_path[len('api/'):]
            # Read request body (but mock handler currently ignores body content)
            content_length = int(self.headers.get('Content-Length') or 0)
            if content_length:
                _ = self.rfile.read(content_length)
            self.handle_api_request(api_endpoint)
            return

        # For non-API POSTs, return 404
        self.send_error(404, 'Not Found')
    
    def handle_api_request(self, api_path):
        """Mock API responses for testing"""
        # Mock responses for login endpoints
        if api_path == 'admin-login' and self.command == 'POST':
            response = {
                'success': True,
                'message': 'Admin login successful',
                'admin': True,
                'admin_user': {
                    'id': 1,
                    'username': 'admin',
                    'role': 'super_admin'
                },
                'token': 'test-token-12345',
                'role': 'super_admin',
                'username': 'admin'
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, f'API endpoint {api_path} not implemented in test server')
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        print(f"[{self.client_address[0]}] {format % args}")

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), IceaaHandler) as httpd:
        print(f"Test server running at http://localhost:{PORT}/iceaa/")
        print(f"Serving dist from: {DIST_DIR}")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()
