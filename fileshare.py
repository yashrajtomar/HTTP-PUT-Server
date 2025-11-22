#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8000

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>File Share</title>
<style>
body {{ font-family: Arial; margin: 40px; }}
.container {{ width: 500px; margin: auto; }}
.error {{ color: red; font-weight: bold; }}
</style>
</head>
<body>
<div class="container">
<h2>Simple File Upload / Download</h2>

<form method="POST" enctype="multipart/form-data">
<label>Select file to upload:</label><br><br>
<input type="file" name="file"><br><br>
<input type="submit" value="Upload">
</form>

{error_msg}

<h3>Files:</h3>
<ul>
{files}
</ul>

</div>
</body>
</html>
"""

class Handler(http.server.SimpleHTTPRequestHandler):

    def send_html(self, error_message=""):
        file_list = ""

        for f in os.listdir('.'):
            if os.path.isfile(f):
                file_list += f"<li><a href='/{f}' download>{f}</a></li>"

        page = HTML_TEMPLATE.format(
            files=file_list,
            error_msg=f"<p class='error'>{error_message}</p>" if error_message else ""
        )

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(page.encode())

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_html()
        else:
            super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        content_type = self.headers.get("Content-Type", "")

        if "multipart/form-data" not in content_type:
            self.send_html("Invalid form submission.")
            return

        boundary = content_type.split("boundary=")[1].encode()
        data = self.rfile.read(content_length).split(boundary)

        # Extract file header block
        file_block = [b for b in data if b'filename="' in b]
        if not file_block:
            self.send_html("No file selected! Please choose a file.")
            return

        header, file_data = file_block[0].split(b"\r\n\r\n", 1)
        header_str = header.decode(errors="ignore")

        # Extract filename
        filename_line = [line for line in header_str.split("\r\n") if "filename=" in line][0]
        filename = filename_line.split("filename=")[1].strip('"')

        if filename == "":
            self.send_html("No file selected! Please choose a file.")
            return

        # Remove footer
        file_data = file_data.rstrip(b"\r\n--")

        # Save the uploaded file
        with open(filename, "wb") as f:
            f.write(file_data)

        # Redirect back to homepage
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Server running on http://localhost:{PORT}")
        print("📁 Upload + Download through browser")
        httpd.serve_forever()
