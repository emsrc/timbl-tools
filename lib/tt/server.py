"""
TimblServer wrapper
"""

# When debugging with Wing IDE om Mac OS X, extend the PATH with the directory
# of the Timbl binary in the project's Environment settings

# TODO:
# - docstrings

import atexit
import logging
import os
import socket
import signal
import subprocess
import tempfile
import time

from tt.exception import TimblServerError

# Logging to "tt.server". In order to see log messages, importer must add
# handlers and formaters
log = logging.getLogger(__name__)


class TimblServer(object):
    """
    Wrapper class for managing a TimblServer. The main advantage is that it
    records the server's pid, so stopping the server is easy.
    """
    
    # pids of all TimblServer processes that must be killed at exit
    kill_pids = [] 
    
    def __init__(self,
                 timbl_opts,
                 exec_fname="TimblServer",
                 port=0,
                 max_connect=None,
                 pid_fname=None,
                 server_log_fname=None,
                 kill_at_exit=True,
                 wait_for_dead=True,
                 wait_time=30,
                 logger=None,
                 log_tag=None):
        self.timbl_opts = timbl_opts
        self.exec_fname = exec_fname
        self.port = port
        self.max_connect = max_connect
        self.pid_fname = pid_fname
        self.server_log_fname = server_log_fname
        self.kill_at_exit = kill_at_exit
        self.wait_for_dead = wait_for_dead
        self.wait_time = wait_time
        self.pid = None
        
        if logger:
            self.log = logger
        else:
            self.log = logging.getLogger(
                "{0}.{1}.{2}".format(__name__,
                                     self.__class__.__name__,
                                     log_tag or id(self)))
        
    def start(self):   
        if not self.port:
            self.port = self._get_free_port()
            
        # running as daemon requires storing pid
        if not self.pid_fname:
            # tmp file to store pid of Timbl server,
            # will be automatically deleted after pid is read
            tmpf = tempfile.NamedTemporaryFile(mode="rb", bufsize=0)
            self.pid_fname = tmpf.name
            
        cmd_str = ( '{exec_fname} {timbl_opts} -S {port} '
                    '--daemonize=yes --pidfile="{pid_fname}" ' )
        
        if self.max_connect:
            cmd_str += "-C {max_connect} "     
            
        if self.server_log_fname:
            cmd_str += '--logfile="{server_log_fname}" '
         
        # For some unkown reason, I cannot make Popen.communicate() work
        # reliably with TimblServer, so I resort to piping stdout and stderr
        # to a temporary file, which is read afterwards
        outf = tempfile.NamedTemporaryFile(mode="rb", bufsize=0)
        out_fname = outf.name
        cmd_str += ' >"{0}" 2>&1 '.format(out_fname)
            
        command = cmd_str.format(**self.__dict__)
        
        self.log.info("command = \n" + command)

        # TimblServer will fork and background automatically when started in
        # daemon mode
        exit_code = subprocess.call(command, shell=True)
        
        if exit_code == 0:
            self._wait_for_pid_file()
            self.log.info("pid = {0}".format(self.pid))
        else:
            # a Timbl error such as an invalid option
            time.sleep(3)
            msg = "\n" + open(out_fname).read()
            self.log.critical(msg)
            raise TimblServerError(msg)
            
        out = open(out_fname).read()
        self.log.info("startup trace:\n" + out)
        
        if self.kill_at_exit:
            self.kill_pids.append(self.pid)
            
    def stop(self):
        if self.pid:
            os.kill(self.pid, signal.SIGHUP)
            if self.wait_for_dead:
                self._wait_until_server_dead()
            if self.kill_at_exit:
                self.kill_pids.remove(self.pid)
            self.pid = None
            
    def restart(self):
        self.stop()
        self.port = self._get_free_port()
        self.start()
            
    def _wait_for_pid_file(self):
        # wait until pid can be read from pid file
        for i in range(self.wait_time):
            try:
                self.pid = int(open(self.pid_fname).read())
                break
            except (OSError, ValueError):
                self.log.debug("waiting {0} seconds for pid file".format(i+1))
                time.sleep(1)
        else:
            msg = "cannot open pidfile {0}".format(self.pid_fname)()
            self.log.critical(msg)
            raise TimblServerError(msg)
            
    def _wait_until_server_dead(self):
        # now wait until TimblServer is really dead
        for i in range(self.wait_time):
            try:
                # this might not be 100% reliable, because in principle
                # another process may have received this pid in the meantime
                os.getpgid(self.pid)
                self.log.debug("waiting {0} seconds for server to die".format(i+1))
                time.sleep(1)
            except OSError:
                break
        else:
            msg = "cannot kill TimblServer with pid {0}".format(self.pid)
            self.log.critical(msg)
            raise TimblServerError(msg)
            
    def _get_free_port(self):
        # bind to port 0 and the OS will pick an available port
        s = socket.socket()
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        return port
        
    @atexit.register
    def kill_all():
        # Called by atexit module upon program termination. 
        for pid in TimblServer.kill_pids:
            log.info(
                "killing at exit server with pid {0}".format(pid))
            os.kill(pid, signal.SIGHUP)
    
           
            
# --- Old code ---------------------------------------------------------------                   
        

class _TimblServer(object):
    """
    NOTE: this class worked with old versions of Timbl (<6.3)
    
    Wrapper class for managing a Timbl server. The main advantage is that it
    keeps the server's pid, so stopping the server is easy.
    """
    
    def __init__(self,
                 timbl_exec="Timbl",
                 port=5555,
                 options="",
                 stop_at_exit=True):
        self.timbl_exec = timbl_exec
        self.port = port
        self.options = options
        self.stop_at_exit = stop_at_exit
        self.pid = None
        self.pid_file = None
        
        # **************************************
        # temporary hack to use Timbl 6.1.5 --
        # later version use "--pidfile" 
        self.command_str = ( "{timbl_exec} "
                             "{options} " 
                             "-S {port} "
                             '-pidfile="{pid_file}" ')
        # ***************************************
        

    def __del__(self):
        if self.stop_at_exit and self.pid:
            self.stop()
           
 
    def start(self):
        # tmp file to store pid of Timbl server,
        # will be automatically deleted
        tmpf = tempfile.NamedTemporaryFile(mode="rb", bufsize=0)
        self.pid_file = tmpf.name
        
        command = self.command_str.format(**self.__dict__)
        print command
        # Timbl will fork and background automatically when started in server
        # mode
        subprocess.call(command, shell=True)
        
        # wait until Timbl has written pid to file
        for i in range(30):
            try:
                self.pid = int(open(self.pid_file).read())
                break
            except:
                time.sleep(1)
        else:
            msg = "cannot open pidfile " + repr(self.pid_file)
            self.log.critical(msg)
            raise TimblServerError(msg)
        
        
    def stop(self):
        if not self.pid:
            msg = "No Timbl server pid. Server not started?"
            self.log.critical(msg)
            raise TimblServerError(msg)
        
        os.kill(self.pid, signal.SIGHUP)
        self.pid = None
        self.pid_file = None
        

        
        
        
        