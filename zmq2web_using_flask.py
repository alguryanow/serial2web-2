from flask import Flask
from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime
import zmq

_ZMQ_SUB_ADDR = 'tcp://localhost:12345'
_ZMQ_REP_ADDR = 'tcp://localhost:12346'

app = Flask(__name__)

@app.route('/')
def index():
    return open('index.html').read()

@app.route('/get_serial')
def get_serial():
    context = zmq.Context.instance()
    zmq_sub_sock = context.socket(zmq.SUB)
    zmq_sub_sock.setsockopt(zmq.SUBSCRIBE, '')
    zmq_sub_sock.connect( _ZMQ_SUB_ADDR )
       
    poller = zmq.Poller()
    poller.register( zmq_sub_sock, zmq.POLLIN )

    socks = dict(poller.poll(timeout=5000))
    if zmq_sub_sock in socks:
        return zmq_sub_sock.recv()
    else:
        return 'flask.py: No data within 5 sec'

        
@app.route('/send_to_serial/<offset>')
def send_to_serial(offset):
    context = zmq.Context.instance()
    zmq_req_sock = context.socket(zmq.REQ)
    zmq_req_sock.connect( _ZMQ_REP_ADDR )
    
    zmq_req_sock.send(bytes(offset+'\r'))
    print zmq_req_sock.recv()
    
    return 'OK'

    
    

def work(zmq_sub_addr):
    _ZMQ_SUB_ADDR = zmq_sub_addr
    app.run(host='0.0.0.0', debug=False, threaded=True)
    
    
if __name__ == '__main__':
    work(_ZMQ_SUB_ADDR)