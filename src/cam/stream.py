import pickle

from flask import Flask, Response, render_template_string, make_response
from picamera import PiCamera
import time
import io

class App(Flask):
    def __init__(self, server_obj= {}, import_name=__name__, **kwargs):
        self.server_obj = server_obj
        super().__init__(import_name, **kwargs)
        self.route('/')(self.index)
        self.route('/stream')(self.stream)
        self.route('/<func_name>')(self.call_method)
        self.route('/favicon.ico')(lambda *a,**kw: '')
        
    def index(self):
        html = """
                <html>
                  <head>
                    <title>Delta Cambot</title>
                  </head>
                  <body>
                    <h1>Video Streaming Demonstration</h1>
                    <img src="{{url_for('stream')}}">
                  </body>
                </html>
                """
        return render_template_string(html)
    
    @staticmethod
    def frames():
        with PiCamera() as camera:
            # let camera warm up
            time.sleep(2)

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

    
    def gen_frame(self):
        while True:
            frame = self.camera.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
    def stream(self):
        return Response(self.frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    def wrap(self, func):
        kwargs = {k: v for k, v in request.args.items()}
        pickled = kwargs.get('pickled', False)
        if 'pickled' in kwargs:
            del kwargs['pickled']
        r = func(**kwargs)
        if pickled:
            try:
                r = make_response(pickle.dumps(r))
                r.headers['Content-Type'] = 'application/python-pickle'
            except:
                pass
        return r
    
    def call_method(self, func_name):
        print('here')
        print(func_name)
        return self.wrap(getattr(self.server_obj, func_name))
    

if __name__ == '__main__':
    #cam = PiCamera()
    app = App()
    #app = App()
    app.run(host='0.0.0.0', debug=True)