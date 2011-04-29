import glob
import socket

def main():
    for filename in glob.glob('/tmp/socketdumper-*'):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(filename)
        print "**** %s" % filename
        buf = s.recv(1024)
        while buf:
            print buf
            buf = s.recv(1024)
        s.close()
