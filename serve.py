import http.server, socketserver, os, webbrowser, threading

PORT = 8080
os.chdir(os.path.dirname(os.path.abspath(__file__)))

handler = http.server.SimpleHTTPRequestHandler
handler.log_message = lambda *a: None  # silence request logs

def open_browser():
    webbrowser.open(f'http://localhost:{PORT}')

threading.Timer(0.5, open_browser).start()
print(f'Serving at http://localhost:{PORT}  (Ctrl+C to stop)')
with socketserver.TCPServer(('', PORT), handler) as httpd:
    httpd.serve_forever()
