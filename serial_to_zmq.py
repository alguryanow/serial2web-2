# -*- coding: utf-8 -*-

import zmq
import time
import serial

_SERIAL_PORT_NAME = 'COM7'
_SERIAL_PORT_SPEED = 115200

_ZMQ_PUB_ADDR = 'tcp://*:12345'
_ZMQ_REP_ADDR = 'tcp://*:12346'

def work( serial_port_name, serial_port_speed, zmq_pub_addr, zmq_rep_addr = _ZMQ_REP_ADDR ):

    context = zmq.Context.instance()

    pub_sock = context.socket(zmq.PUB)
    pub_sock.bind( zmq_pub_addr )
    
    #-- ZMQ-socket for receiving data that should be sent to COM-port
    zmq_rep_sock = context.socket(zmq.REP)
    zmq_rep_sock.bind( zmq_rep_addr )
   
    #-- for nonblocking check of data for COM-port
    poller = zmq.Poller()
    poller.register( zmq_rep_sock, zmq.POLLIN ) 
    
    ser = serial.Serial(serial_port_name, serial_port_speed, timeout=0.03)
    
    count=0
    while True:
        line = get_full_line_from_serial(ser)
        if line is not None:
            count += 1
            print line.decode('utf-8')
            pub_sock.send( time.strftime( '%Y.%m.%d %H:%M:%S' ) + ': строка № %d' % count + '<br>' +  line )
            
        #-- checking if data for COM-port arrived thr ZMQ
        socks = dict(poller.poll(timeout=0))    #-- "timeout=0" means "just check, don't wait"
        if zmq_rep_sock in socks:
            data = zmq_rep_sock.recv()
            ser.write(data)
            zmq_rep_sock.send("OK")


_captured = ''
def get_full_line_from_serial(ser):
    """ returns full line from serial or None 
        Uses global variable '_captured'
    """
    global _captured
    part = ser.readline()
    if part:
        _captured += part
        parts = _captured.split('\n', 1);
        if len(parts) == 2:
            _captured = parts[1]
            return parts[0]
            
    return None
    

if __name__ == '__main__':
    work( _SERIAL_PORT_NAME, _SERIAL_PORT_SPEED, _ZMQ_PUB_ADDR )