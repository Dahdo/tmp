import os
import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler, Application

UPLOADS_DIR = 'static/images'

class MainHandler(RequestHandler):
    def get(self):
        images = os.listdir(UPLOADS_DIR)
        self.render("index.html", images=images, current_image=None, message="")

class UploadHandler(RequestHandler):
    def post(self):
        file1 = self.request.files['file1'][0]
        filename = file1['filename']
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(file1['body'])
        self.redirect('/')

class ImageHandler(RequestHandler):
    def get(self, image_name):
        images = os.listdir(UPLOADS_DIR)
        if image_name in images:
            index = images.index(image_name)
            next_image = images[(index + 1) % len(images)]
            prev_image = images[(index - 1) % len(images)]
            self.render("index.html", images=images, current_image=image_name, next_image=next_image, prev_image=prev_image, message="")
        else:
            self.write("Image not found")

class DownloadHandler(RequestHandler):
    def get(self, image_name):
        file_path = os.path.join(UPLOADS_DIR, image_name)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=' + image_name)
            self.write(data)
        else:
            self.write("File not found")

def make_app():
    return Application([
        (r"/", MainHandler),
        (r"/upload", UploadHandler),
        (r"/image/(.*)", ImageHandler),
        (r"/download/(.*)", DownloadHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": UPLOADS_DIR}),
    ], debug=True, template_path="templates", static_path="static")

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
