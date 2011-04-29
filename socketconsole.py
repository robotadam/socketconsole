import atexit
import os
import socket
import sys
import threading
import traceback


class SocketDumper(threading.Thread):

    daemon = True

    def stacktraces(self):
        code = []
        threads = dict(
            (t.ident, t) for t in threading.enumerate())
        for thread_id, stack in sys._current_frames().items():
            code.append("\n# Thread Name: %s, ThreadID: %s\n" %
                (threads[thread_id].name, thread_id))
            code.extend(traceback.format_list(traceback.extract_stack(stack)))
        return code

    def run(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        filename = '/tmp/socketdumper-%s' % os.getpid()
        try:
            os.remove(filename)
        except OSError:
            pass

        s.bind(filename)
        s.listen(1)
        print "Serving on %s" % filename
        
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
