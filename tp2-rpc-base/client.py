"""
 Simple JSON-RPC Client

"""

import json
import socket


class JSONRPCClient:
    """The JSON-RPC client."""

    def __init__(self, host, port):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.request_id = 0

    def close(self):
        """Closes the connection."""
        self.sock.close()

    def send(self, msg):
        """Sends a message to the server."""
        self.sock.sendall(msg.encode())
        return self.sock.recv(1024).decode()

    def invoke(self, method, params):
        """Invokes a remote function."""
        self.request_id += 1
        req = {
            'jsonrpc': '2.0',
            'id': self.request_id,
            'method': method,
            'params': params
        }
        msg = self.send(json.dumps(req))
        res = json.loads(msg)

        if 'error' in res:
            if res['error']['code'] == -32601:
                raise AttributeError(res['error']['message'])
            elif res['error']['code'] == -32602:
                raise TypeError(res['error']['message'])
            else:
                raise Exception(res['error']['message'])

        return res['result']

    def __getattr__(self, name):
        """Invokes a generic function."""
        def inner(*params):
            return self.invoke(name, params)
        return inner


if __name__ == "__main__":

    # Test the JSONRPCClient class
    client = JSONRPCClient('127.0.0.1', 8000)

    try:
        print(client.hello())
        print(client.greet("John Doe"))
        print(client.add(2, 3))
        print(client.sub(5, 3))
        print(client.mul(3, 4))
        print(client.div(10, 2))
    except Exception as e:
        print(f"Error: {e}")

    client.close()
