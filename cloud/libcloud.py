import selectors


class Message:
    def __init__(self, selector, sock, addr):
        pass
    
    
    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()
            
    def read(self):
        self._read()
        
        if self._jsonheader_len is None:
            self.process_protoheader() #state check that is related to the message component "Fixed-length header" - returns self.__jsonheader_len
        
        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader() #state check that is related to the message component "JSON header" - returns self.jsonheader
        
        if self.jsonheader:
            if self.request is None:
                self.process_request() #state check that is related to the message component "contenct" - - returns self.request
                
    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response() # sets the state variable "response_created" and writes the response to the send buffer. This should be called ONCE!
        
        self._write() # calls "socket.send() if there's data in the send buffer." It's expected that this will need to be called multiple times
        
    