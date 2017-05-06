# wrwlf.net@gmail.com

import os
import signal
import sys
import syslog
import time

class Daemon:
    def __init__(self, pidfile):
        self.pidfile = pidfile

    def start(self):
        syslog.syslog(syslog.LOG_INFO, 'starting daemon')
        if os.path.exists(self.pidfile):
            syslog.syslog(syslog.LOG_ERR,
                f'pidfile=\"{self.pidfile}\" already exists'
            )
            raise RuntimeError
        try:
            os.mknod(self.pidfile)
        except OSError:
            syslog.syslog(syslog.LOG_ERR,
                f'pidfile=\"{self.pidfile}\" could not be created'
            )
            raise RuntimeError

        pid = self._daemonize()

        try:
            with open(self.pidfile, 'w') as pidfile:
                pidfile.write(str(pid))
        except OSError:
            syslog.syslog(syslog.LOG_ERR,
                f'pidfile=\"{self.pidfile}\" could not be opened while'
                ' attempting to start daemon'
            )
            # Kill the daemon process for good measure
            os.kill(pid, signal.SIGKILL)
            raise RuntimeError
        # Run the actual daemon process
        self._run()

    def stop(self):
        syslog.syslog(syslog.LOG_INFO, 'stopping daemon')
        try:
            with open(self.pidfile, 'r') as pidfile:
                pid = int(pidfile.readline())
        except OSError:
            syslog.syslog(syslog.LOG_ERR,
                f'pidfile=\"{self.pidfile}\" could not be opened while'
                ' attempting to exit daemon'
            )
            raise RuntimeError
        os.kill(pid, signal.SIGKILL)
        os.remove(self.pidfile)

    def _run(self):
        pass

    def _daemonize(self):
        # Based on http://www.steve.org.uk/Reference/Unix/faq_2.html (wayback)

        # Fork once
        try:
            pid = os.fork()
        except OSError:
            # TODO error message
            raise RuntimeError
        # Close the parent
        if pid != 0:
            sys.exit(0)
        # Become a process group and session group leader which ensures the
        # daemon does not have a controlling terminal
        os.setsid()
        
        # Fork again
        try:
            pid = os.fork()
        except OSError:
            # TODO error message
            raise RuntimeError
        # Close the parent (session group leader), the daemon can never regain
        # a controlling terminal (daemon is now a non-session group leader)
        if pid != 0:
            sys.exit(0)
        # Prevent the daemon from keeping a a directory in use (preventing
        # said directory from being unmounted)
        os.chdir('/')
        # Daemon gets complete control of permissions for anything it writes
        os.umask(0)

        # TODO close any open fds or hope/assume parent took care of that?

        sys.stdout.flush
        sys.stderr.flush
        sys.stdout = open('/dev/null')
        sys.stdin = open('/dev/null')
        sys.sterr = open('/dev/null')

        return os.getpid()
