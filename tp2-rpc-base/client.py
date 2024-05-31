"""
 JSON-RPC Client
"""

import json
import socket


class JSONRPCClient:
    """The JSON-RPC client."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.request_id = 0  # Inicializa request_id corretamente

    def call(self, method, *params):
        """Calls a JSON-RPC method."""
        self.request_id += 1
        req = {
            'jsonrpc': '2.0',
            'id': self.request_id,
            'method': method,
            'params': params
        }
        msg = json.dumps(req)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.sendall(msg.encode())

            response = b""
            while True:
                part = sock.recv(4096)
                response += part
                if len(part) < 4096:
                    break

        res = json.loads(response.decode())

        if 'error' in res:
            if res['error']['code'] == -32601:
                raise AttributeError(res['error']['message'])
            elif res['error']['code'] == -32602:
                raise TypeError(res['error']['message'])
            else:
                raise Exception(res['error']['message'])

        return res['result']

    def __getattr__(self, name):
        def method(*params):
            return self.call(name, *params)

        return method


if __name__ == "__main__":
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
