import atexit
import glob
import os
import socket
import sys
import tempfile
import thread
import threading
import traceback


class SocketDumper(threading.Thread):

    daemon = True

    locals_limit = 20

    def stacktraces(self):
        code = []
        threads = dict(
            (t.ident, t) for t in threading.enumerate())
        for thread_id, stack in sys._current_frames().items():
            # Skip the current thread; we know what it's doing
            if thread_id == thread.get_ident():
                continue
            try:
                name = threads[thread_id].name
            except KeyError:
                name = 'Unknown (see Python issue #5632)'
            code.append("\n# Thread Name: %s, ThreadID: %s\n" %
                (name, thread_id))
            code.extend(traceback.format_list(traceback.extract_stack(stack)))
            stack_locals = stack.f_locals.items()[:self.locals_limit]
            code.append("\n# Locals:\n")
            for i, (var, val) in enumerate(stack_locals):
                if i == self.locals_limit:
                    break
                code.append("  %s: %r\n" % (var, val))
        return code

    def run(self):
        self.name = "SocketConsole Watcher"
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        filename = os.path.join(sockpath, 'socketdumper-%s' % os.getpid())
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
    filename = os.path.join(sockpath, 'socketdumper-%s' % os.getpid())
    try:
        os.remove(filename)
    except OSError:
        pass


sockpath = tempfile.gettempdir()
sockthread = None

def launch(path=None):
    global sockpath, sockthread
    if path is not None and os.path.exists(path) and os.path.isdir(path):
        sockpath = path
    atexit.register(cleanup)
    sockthread = SocketDumper()
    sockthread.start()


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = sockpath

    socket_glob = os.path.join(path, 'socketdumper-*')
    for filename in glob.glob(socket_glob):
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(filename)
            print "**** %s" % filename
            sys.stdout.flush()
            buf = s.recv(1024)
            while buf:
                sys.stdout.write(buf)
                buf = s.recv(1024)
            sys.stdout.write('\n')
            sys.stdout.flush()
            s.close()
        except Exception as e:
            sys.stdout.write("Couldn't connect: %s: %s" % (type(e), str(e)))
            sys.stdout.flush()


if __name__ == '__main__':
    main()
