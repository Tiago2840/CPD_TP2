"""
 Simple JSON-RPC Client

"""

import json
import socket


class JSONRPCClient:
    """The JSON-RPC client."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.request_id = 0
        self._connect()

    def _connect(self):
        """Establish a new connection to the server."""
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))

    def close(self):
        """Closes the connection."""
        if self.sock:
            self.sock.close()
            self.sock = None

    def send(self, msg):
        """Sends a message to the server."""
        try:
            self.sock.sendall(msg.encode())
            return self.sock.recv(1024).decode()
        except (socket.error, OSError):
            self._connect()  # Reconnect if the connection was closed
            self.sock.sendall(msg.encode())
            return self.sock.recv(1024).decode()

    def invoke(self, method, params=None):
        """Invokes a remote function."""
        self.request_id += 1
        req = {
            'jsonrpc': '2.0',
            'id': self.request_id,
            'method': method,
            'params': params or []
        }
        msg = self.send(json.dumps(req))
        res = json.loads(msg)

        if 'error' in res:
            code = res['error']['code']
            message = res['error']['message']
            if code == -32601:
                raise AttributeError(message)
            elif code == -32602:
                raise TypeError(message)
            elif code == -32700:
                raise ParseError(message)
            elif code == -32600:
                raise InvalidRequestError(message)
            else:
                raise ServerError(message)

        return res['result']

    def __getattr__(self, name):
        """Invokes a generic function."""

        def inner(*args, **kwargs):
            if kwargs:
                return self.invoke(name, kwargs)
            return self.invoke(name, args)

        return inner


if __name__ == "__main__":
    # Test the JSONRPCClient class
    client = JSONRPCClient('127.0.0.1', 8000)

    try:
        print(client.hello())
        print(client.greet(name="John Doe"))
        print(client.add(a=2, b=3))
        print(client.sub(a=5, b=3))
        print(client.mul(a=3, b=4))
        print(client.div(a=10, b=2))
    except Exception as e:
        print(f"Error: {e}")

    client.close()


## CUSTOM EXCEPTIONS
class JSONRPCError(Exception):
    """Base class for JSON-RPC errors."""
    pass


class ParseError(JSONRPCError):
    """Raised when there is a parse error in the JSON-RPC request."""
    pass


class InvalidRequestError(JSONRPCError):
    """Raised when the request is invalid."""
    pass


class ServerError(JSONRPCError):
    """Raised when the server encounters an error."""
    pass
