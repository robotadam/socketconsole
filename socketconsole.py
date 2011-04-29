import atexit
import glob
import os
import socket
import sys
import thread
import threading
import traceback


class SocketDumper(threading.Thread):

    daemon = True

    def stacktraces(self):
        code = []
        threads = dict(
            (t.ident, t) for t in threading.enumerate())
        for thread_id, stack in sys._current_frames().items():
            # Skip the current thread; we know what it's doing
            if thread_id == thread.get_ident():
                continue
            code.append("\n# Thread Name: %s, ThreadID: %s\n" %
                (threads[thread_id].name, thread_id))
            code.extend(traceback.format_list(traceback.extract_stack(stack)))
        return code

    def run(self):
        self.name = "SocketConsole Watcher"
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        filename = '/tmp/socketdumper-%s' % os.getpid()
        try:
            os.remove(filename)
        except OSError:
            pass

        s.bind(filename)
        s.listen(1)
        
        while 1:
            conn, addr = s.accept()
            conn.sendall(''.join(self.stacktraces()))
            conn.close()


def cleanup():
    filename = '/tmp/socketdumper-%s' % os.getpid()
    try:
        os.remove(filename)
    except OSError:
        pass
            

sockthread = None

def launch():
    atexit.register(cleanup)
    global sockthread
    sockthread = SocketDumper()
    sockthread.start()


def main():
    for filename in glob.glob('/tmp/socketdumper-*'):
        try:
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
        except Exception, e:
            sys.stdout.write("Couldn't connect: %s: %s" % (type(e), str(e)))
            sys.stdout.flush()
