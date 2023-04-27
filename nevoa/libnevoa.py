

class Message:
    def __init__(self, selector, sock, addr, request):
        pass

    def write(self):
        if not self._request_queued: # Because the client initiates a connection to the server and sends a request first, the state variable _request_queued is checked
            self.queue_request()
        
        self._write() # calls socket.send() if there's data in the send buffer.
        
        if self._request_queued: 
            if not self._send_buffer:
                # Set selector to listen for read events, we're done writing.
                self._set_selector_events_mask("r")