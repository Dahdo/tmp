import tornado.ioloop
import tornado.web
import os
from mpd import MPDClient
client = MPDClient()

path = "/var/lib/mpd/music/"
        
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        connect()
        global dir_list
        global path
        songs_list = client.playlistinfo()
        self.render("/opt/design.html", songs = songs_list, current_song = client.currentsong())
        
    def post(self):
        global dir_list
        global path
        
        if self.get_argument("upload", None) != None:
            connect()
            print("post")
            file = self.request.files['filearg'][0]
            original_fname = file['filename']
            output_file = open(music_path + original_fname, 'wb')
            output_file.write(file['body'])
            os.system("mpc update")
            client.add(original_fname)
            songs_list = client.playlistinfo()
            self.render("design.html", songs = songs_list, current_song = client.currentsong())
            
        if self.get_argument("toggle", None) != None:
            connect()
            if not client.currentsong():
                client.play()
            else:
                client.pause()
            songs_list = client.playlistinfo()
            self.render("/opt/design.html", songs = songs_list, current_song = client.currentsong())
            
        if self.get_argument("prev", None) != None:
            connect()
            client.previous()
            songs_list = client.playlistinfo()
            self.render("design.html", songs = songs_list, current_song = client.currentsong())
        
        if self.get_argument("next", None) != None:
            connect()
            client.next()
            songs_list = client.playlistinfo()
            self.render("/opt/design.html", songs = songs_list, current_song = client.currentsong())
            

class DownloadHandler(tornado.web.RequestHandler):
    def get(self, file):
        connect()
        print('downloading file : ',file)
        ifile  = open(music_path + file, "rb")
        self.set_header ('Content-Type', 'application/octet-stream')
        self.set_header ("Content-Disposition", f"attachment; filename={file}")
        self.write (ifile.read())

class DeleteHandler(tornado.web.RequestHandler):
    def get(self, song):
        connect()
        client.delete(song[-1])
        os.system('rm ' + music_path + song[:-1])
        client.update()
        self.redirect('/')
        
        
def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/download/(.*)",  DownloadHandler),
        (r"/delete/(.*)",  DeleteHandler)
    ])
    
def connect():
    try:
        client.ping()
    except Exception:
        client.connect("127.0.0.1", 6600)
        client.update()
        
    
if __name__ == "__main__":
    client.idletimeout = None
    client.connect("127.0.0.1", 6600)
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()