import socket
import asyncore
import asynchat

class EchoClient(asynchat.async_chat):
    """Sends messages to the server and receives responses.
    """

    # Artificially reduce buffer sizes to illustrate
    # sending and receiving partial messages.
    ac_in_buffer_size = 64
    ac_out_buffer_size = 64
    
    def __init__(self, host, port, message):
        self.message = message.encode('utf-8')
        print(self.message)
        self.received_data = []
        #self.logger = logging.getLogger('EchoClient')
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        print('connecting to %s', (host, port))
        self.connect((host, port))
        return
        
    def handle_connect(self):
        print('handle_connect()')
        # Send the command
        self.push(b'%d\n' % len(self.message))
        # Send the data
        self.push_with_producer(EchoProducer(self.message, buffer_size=self.ac_out_buffer_size))
        # We expect the data to come back as-is, 
        # so set a length-based terminator
        self.set_terminator(len(self.message))
    
    def collect_incoming_data(self, data):
        """Read an incoming message from the client and put it into our outgoing queue."""
        print('collect_incoming_data() -> (%d)\n"""%s"""', len(data), data)
        self.received_data.append(data)

    def found_terminator(self):
        print('found_terminator()')
        received_message = ''.join(self.received_data)
        if received_message == self.message:
            print('RECEIVED COPY OF MESSAGE')
        else:
            print('ERROR IN TRANSMISSION')
            print('EXPECTED "%s"', self.message)
            print('RECEIVED "%s"', received_message)
        return

class EchoProducer(asynchat.simple_producer):

    #logger = logging.getLogger('EchoProducer')

    def more(self):
        response = asynchat.simple_producer.more(self)
        #self.logger.debug('more() -> (%s bytes)\n"""%s"""', len(response), response)
        return response

client = EchoClient('', 50007, message="message_data")
asyncore.loop()

#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect(('localhost', 50007))
#print ("Connected to server")
#data = """A few lines of data
#to test the operation
#of both server and client."""
#for line in data.splitlines(  ):
#    sock.sendall(line.encode('utf-8'))
#    #sock.sendall('123;456')
#    print ("Sent:", line)
#    response = sock.recv(8192)
#    print ("Received:", response)
#sock.close(  )
