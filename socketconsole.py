from __future__ import print_function
import atexit
import errno
import glob
import os
import socket
import sys
import tempfile
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
            if thread_id == self.ident:
                continue
            try:
                name = threads[thread_id].name
            except KeyError:
                name = 'Unknown (see Python issue #5632)'
            code.append("\n# Thread Name: %s, ThreadID: %s\n" %
                (name, thread_id))
            code.extend(traceback.format_list(traceback.extract_stack(stack)))
            stack_locals = list(stack.f_locals.items())[:self.locals_limit]
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
            try:
                conn, addr = s.accept()
                conn.sendall(''.join(self.stacktraces()).encode('utf8'))
                conn.close()
            except socket.error as e:
                if e[0] == errno.EINTR:
                    # EINTR is ignorable
                    continue
                else:
                    raise


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


def clean_socket_files(socket_glob):
    alive = 0
    removed = 0
    for filename in glob.glob(socket_glob):
        sys.stdout.flush()
        try:
            _, pid = filename.split('-')
            pid = int(pid)
        except ValueError:
            print('Invalid filename: %s' % filename)
            continue

        try:
            os.kill(pid, 0)
        except OSError as e:
            if e.errno == errno.EPERM:
                print('PID %d is alive but owned by another user, skipping.'
                        % pid)
                continue
            elif e.errno != errno.ESRCH:
                # 'No such process' means we can safely delete this stale pid
                print('PID %d not found. Deleting %s' % (pid, filename))
            else:
                # Don't assume it's safe to continue after other OSErrors
                raise
        else:
            # PID is alive and well, leave it alone
            alive += 1
            continue

        try:
            os.remove(filename)
            removed += 1
        except OSError as e:
            print('Could not remove %s: %s' % (filename, str(e)))
    return alive, removed


def main():
    """socketreader"""
    usage = 'socketreader [path] <clean>'

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = sockpath

    socket_glob = os.path.join(path, 'socketdumper-*')

    if len(sys.argv) > 2:
        if sys.argv[2] == 'clean':
            print('Cleaning stale socketdumper files in %s' % path)
            alive, removed = clean_socket_files(socket_glob)
            print('Removed %d stale files and found %s active.' % (
                removed, alive))
        else:
            print(usage)
            sys.exit(1)
    else:
        for filename in glob.glob(socket_glob):
            try:
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.connect(filename)
                print("**** %s" % filename)
                sys.stdout.flush()
                buf = s.recv(1024)
                while buf:
                    #FIXME I suppose the buffer may split a multibyte character
                    sys.stdout.write(buf.decode('utf8', 'replace'))
                    buf = s.recv(1024)
                sys.stdout.write('\n')
                sys.stdout.flush()
                s.close()
            except Exception as e:
                sys.stdout.write(
                        "Couldn't connect: %s: %s" % (type(e), str(e)))
                sys.stdout.flush()


if __name__ == '__main__':
    main()
