"""
Timbl client
"""

# TODO:
# - doc strings
# - is socket closed after fatal exception?

import logging
import socket

from tt.exception import TimblClientError


class TimblClient(object):
    
    welcome_msg = "welcome to the timbl server.\n"
    
    def __init__(self, port, host="localhost", bufsize=2048, timeout=60,
                 logger=None, log_tag=None):
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.socket = None
        self.timeout = timeout
        self.last_command = None

        if logger:
            self.log = logger
        else:
            self.log = logging.getLogger(
                "{0}.{1}.{2}".format(__name__,
                                     self.__class__.__name__,
                                     log_tag or id(self)))
        self.log.info(
            "Creating new TimblClient instance {0}".format(log_tag or id(self)))
        self.log.info(
            "server host={0.host}, server port={0.port}".format(self))     
        self.log.info(
            "bufsize={0.bufsize} bytes, timeout={0.timeout} sec".format(self))
        
    def connect(self):
        self.log.debug("Connecting socket")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.connect((self.host, self.port))
        reply = ""
        
        while reply.lower() != self.welcome_msg:
            reply += self._recv()
            self.log.debug("Server reply is " + repr(reply))
            
        self.log.info("Connection to server established")
                
    def disconnect(self):
        # sockets are automatically closed when they are garbage-collected,
        # so there is no need to call disconnect from __del__
        if self.socket:
            self.log.debug("Disconnecting socket")
            self._send("exit")
            self.socket.close()
            self.socket = None
            
        self.log.info("Connection to server terminated")
            
    def reconnect(self):
        self.disconnect()
        self.connect()
        
    def classify(self, instance):
        self._send("classify " + instance)
        reply = self._recv()
        
        # Reply may be received in arbitrary chunks.
        # Handling is clumsy/inefficient, because Timbl server protocol 
        # lacks something like an "ENDCLASSIFY" flag.
        # Hence we do not know if "{\n" ends a field like "CATEGORY" 
        # or a neighbor, so we have to check if "NEIGHBORS" is in the reply.   
        while True:
            if ( reply.endswith("}\n") and
                 "NEIGHBORS" not in reply ):
                break
            elif reply.endswith("ENDNEIGHBORS\n"):
                break
            else:
                reply += self._recv()
                
        if reply.startswith("ERROR {"): 
            self.log.error("Received " + repr(reply))
            raise TimblClientError(reply)
            
        lines = reply.split("\n")
        result = {}
        
        # FIXME: parsing will fail if accolades are used as classes!
        for part in lines[0].split("}"):
            try:
                key, val = part.split(" {")
                result[key.strip()] = val.strip()
            except ValueError:
                # trailing empty string or "NEIGHBOURS"
                pass
            
        if len(lines) > 2:
            result["NEIGHBOURS"] = lines[1:-2]
        
        self.log.debug("Result = " + repr(result))
        return result
        
    def query(self):
        self._send("query")
        
        reply = self._recv()   
        # reply may be incomplete        
        while not reply.endswith("ENDSTATUS\n"):
            reply += self._recv()     
        
        if not reply.startswith("STATUS\n"):
            self.log.error("Query received ill-formed reply: " + repr(reply))
            raise TimblClientError("Ill-formed reply: " + repr(reply))
            
        status = dict()
        
        for record in reply.split("\n"):
            try:
                key, value = record.split(":")
            except ValueError:
                # STATUS, ENDSTATUS or empty line
                continue
            else:
                status[key.strip()] = value.strip()
        
        self.log.debug("Status = " + repr(status))
        return status
    
    def set(self, options):
        # the +vk seems to be unsupported in server-mode
        self._send("set " + options + "\n")
        
        reply = self._recv()
        
        # reply may be incomplete        
        while not reply.endswith("OK\n"):
            reply += self._recv()
        
        if not reply.strip() == "OK":
            # this will probably never happen as the server always replies
            # "OK", even with ill-formed input
            msg = "Set options received ill-formed reply " + str(reply)
            self.log.error(msg)
            raise TimblClientError(msg)
        
        self.log.info("Set options " + repr(options))
    
    exit = disconnect
    
    # private
        
    def _send(self, command):
        if not command.endswith("\n"):
            command += "\n"
        self.last_command = command
        self.log.debug("Sending " + repr(command))
            
        try:
            self.socket.send(command)
        except AttributeError:
            msg = "Cannot send because Timbl client is not connected"
            self.log.error(msg)
            raise TimblClientError(msg)
        except socket.timeout:
            msg = "Connection timed out while sending command: " + repr(command)
            self.log.error(msg)
            raise TimblClientError(msg)
            
    def _recv(self):  
        try:
            reply = self.socket.recv(self.bufsize)
        except AttributeError:
            msg = "Cannot receive because Timbl client is not connected"
            self.log.error(msg)
            raise TimblClientError(msg)
        except socket.timeout:
            msg = ( "Connection timed out while receiving reply for command: " + 
                    repr(self.last_command) )
            self.log.error(msg)
            raise TimblClientError(msg)

        self.log.debug("Received " + repr(reply))
        return reply
            
