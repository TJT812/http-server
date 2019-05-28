import http.server
import socketserver
import os
import http
import urllib
import sys
import io
import shutil

 #  python http-server.py

PORT = 8001
SERVER_DIR = r"C:\Users\Asus\Desktop\server"

class MySimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(self.headers)
        self.directory = SERVER_DIR
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def do_PUT(self):
        print(self.headers)
        
        path =  '/server' + self.path
        path = self.translate_path(path)
        print(path)
        try:
            print(os.path.dirname(path))
            os.makedirs(os.path.dirname(path))
        except FileExistsError: pass
        length = int(self.headers['Content-Length'])
        with open(path, 'w+b') as f:
            #self.copyfile(io.BufferedIOBase.readinto(self.rfile), f)
            f.write(self.rfile.read(length))
        self.send_response(http.HTTPStatus.CREATED, "Created")
        self.end_headers()


    def do_HEAD(self):
        print(self.headers)
        path = ''
        path =  '/server' + self.path
        path = self.translate_path(path)
        if os.path.exists(path):
            if os.path.isdir(path):
                self.wfile.write("Must be file")
                self.send_error(
                    http.HTTPStatus.BAD_REQUEST,
                    "Must be file")
            else:
                info = os.stat(path)
                self.send_header("Owner", info.st_uid)
                self.send_header("Size", info.st_size)
                self.send_header("Last-modification", info.st_mtime)
                self.end_headers()

        else:
            self.send_error(
                http.HTTPStatus.NOT_FOUND,
                "File not found")



    def do_DELETE(self):
        print(self.headers)
        path = ''
        path =  '/server' + self.path
        path = self.translate_path(path)
        #print(path)
        file_dir = os.path.dirname(path)
        #print(file_dir)
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                shutil.rmtree(path, ignore_errors=True)
            finally:
                self.send_response(http.HTTPStatus.OK)
                self.end_headers()
                self.wfile.write(b"Deleted")
        else:
            self.send_error(
                http.HTTPStatus.NOT_FOUND,
                "File not found")



    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "File not found")
            return None
        list.sort(key=lambda a: a.lower())
        r = []

        enc = sys.getfilesystemencoding()
        for name in list:
            print(name)
            r.append(name)
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        if io.BytesIO.seekable(f):
            f.seek(0)
        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f




httpd = http.server.HTTPServer(('localhost', PORT), MySimpleHTTPRequestHandler)
httpd.serve_forever()
