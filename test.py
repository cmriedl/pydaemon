#!/usr/bin/env python

import os
import sys
import syslog
import time

import daemon


class Daemon(daemon.Daemon):
    def _run(self):
        while True:
            # Just write some crap to the syslog...
            syslog.syslog(syslog.LOG_INFO, 'doing daemon things ...')
            time.sleep(5)


if __name__ == '__main__':
    d = Daemon('/home/wrwlf/derp')

    pid = os.fork()

    # Child starts the daemon and exits
    if pid == 0:
        d.start()
        sys.exit(0)
    else:
        time.sleep(23)
        d.stop()
        sys.exit(0)
