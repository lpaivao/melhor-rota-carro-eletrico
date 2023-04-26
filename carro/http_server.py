from http.server import BaseHTTPRequestHandler,HTTPServer

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'Amg,estou funcionando')
                elif self.path == '/about':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<html><body><h1>About Us</h1><p>We are a small company.</p></body></html>')
                else:
                    self.send_error(404)
