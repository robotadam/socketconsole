import glob
import socket
import sys

def main():
    for filename in glob.glob('/tmp/socketdumper-*'):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(filename)
        print "**** %s" % filename
        buf = s.recv(1024)
        while buf:
            sys.stdout.write(buf)
            buf = s.recv(1024)
        sys.stdout.write('\n')
        sys.stdout.flush()
        s.close()
