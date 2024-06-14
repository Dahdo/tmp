import os
import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler, Application
import gpiod
import threading

UPLOADS_DIR = 'static/images'
current_image_index = 0

# GPIO setup
chip = gpiod.Chip('gpiochip0')
led_next = chip.get_line(27)
led_prev = chip.get_line(23)
button_next = chip.get_line(18)
button_prev = chip.get_line(10)

led_next.request(consumer='led_next', type=gpiod.LINE_REQ_DIR_OUT)
led_prev.request(consumer='led_prev', type=gpiod.LINE_REQ_DIR_OUT)
button_next.request(consumer='button_next', type=gpiod.LINE_REQ_EV_FALLING_EDGE)
button_prev.request(consumer='button_prev', type=gpiod.LINE_REQ_EV_FALLING_EDGE)

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
    def get(self, image_name=None):
        global current_image_index
        images = os.listdir(UPLOADS_DIR)
        if images:
            if image_name:
                current_image_index = images.index(image_name)
            image_name = images[current_image_index]
            next_image = images[(current_image_index + 1) % len(images)]
            prev_image = images[(current_image_index - 1) % len(images)]
            self.render("index.html", images=images, current_image=image_name, next_image=next_image, prev_image=prev_image, message="")
        else:
            self.write("No images found")

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
        (r"/image/?(.*)", ImageHandler),
        (r"/download/(.*)", DownloadHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": UPLOADS_DIR}),
    ], debug=True, template_path="templates", static_path="static")

def button_callback(line, event):
    global current_image_index
    images = os.listdir(UPLOADS_DIR)
    if not images:
        return
    
    if line == button_next:
        current_image_index = (current_image_index + 1) % len(images)
        led_next.set_value(1)
        tornado.ioloop.IOLoop.current().add_callback(navigate_image, images[current_image_index])
        led_next.set_value(0)
    
    elif line == button_prev:
        current_image_index = (current_image_index - 1) % len(images)
        led_prev.set_value(1)
        tornado.ioloop.IOLoop.current().add_callback(navigate_image, images[current_image_index])
        led_prev.set_value(0)

def navigate_image(image_name):
    app.reverse_url("image", image_name)
    tornado.ioloop.IOLoop.current().add_callback(lambda: tornado.ioloop.IOLoop.current().add_future(
        tornado.web.Application.reverse_url(app, "image", image_name),
        lambda x: None
    ))

def watch_buttons():
    while True:
        event_next = button_next.event_wait(timeout=10)
        event_prev = button_prev.event_wait(timeout=10)
        
        if event_next:
            button_callback(button_next, event_next)
        if event_prev:
            button_callback(button_prev, event_prev)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    threading.Thread(target=watch_buttons, daemon=True).start()
    tornado.ioloop.IOLoop.current().start()
