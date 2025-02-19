import http.server
import ssl
import os

# Katalog, w którym znajduje się index.html
web_dir = os.path.expanduser("~/.config/browser/")
os.chdir(web_dir)

# Parametry serwera
PORT = 1337
server_address = ('localhost', PORT)
handler = http.server.SimpleHTTPRequestHandler

# Tworzenie serwera HTTP
httpd = http.server.HTTPServer(server_address, handler)

# Konfiguracja SSL
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")  # Ścieżka do certyfikatu i klucza
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

# Uruchomienie serwera
print(f"Serwer HTTPS działa na https://localhost:{PORT}")
httpd.serve_forever()
