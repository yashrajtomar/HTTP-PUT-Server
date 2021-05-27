#!/usr/bin/env python3

"""
USAGE: -
    python3[ScriptName][Port]
            or
    chmod + x[ScriptName]
    ./ [ScriptName][Port]

Extend Python's built in HTTP server to save files

curl or wget
can
be
used
to
send
files
with options similar to the following

curl - X PUT --upload-file somefile.txt http://localhost:port
wget -O- --method=PUT --body-file=somefile.txt http://localhost:port/somefile.txt

__Note__: curl automatically appends the filename onto the end of the URL so the path can be omitted.
"""

import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
from sys import argv


class HTTPRequestHandler(SimpleHTTPRequestHandler):
    """Extend SimpleHTTPRequestHandler to handle PUT requests"""

    def do_PUT(self):
        """Save a file following a HTTP PUT request"""
        filename = os.path.basename(self.path)

        file_length = int(self.headers['Content-Length'])
        with open(filename, 'wb') as output_file:
            output_file.write(self.rfile.read(file_length))
        self.send_response(201, 'Created')
        self.end_headers()
        reply_body = 'Saved “ % s”\n' % filename
        self.wfile.write(reply_body.encode('utf-8'))


def run():
    if len(argv) == 2:
        port = int(argv[1])
    else:
        port = 80
    s_port = ('', port)
    serve = HTTPServer(s_port, HTTPRequestHandler)
    try:
        print(f"Serving HTTP on 0.0.0.0 port {port}")
        serve.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")


if __name__ == '__main__':
    run()
