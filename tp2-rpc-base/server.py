"""
Simple JSON-RPC Server
"""

import functions
import json
import socket


class JSONRPCServer:
    """The JSON-RPC server."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.funcs = {}

    def register(self, name, function):
        """Registers a function."""
        self.funcs[name] = function

    def start(self):
        """Starts the server."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print('Listening on port %s ...' % self.port)

        try:
            while True:
                conn, addr = self.sock.accept()
                print(f"Connection from {addr}")
                self.handle_client(conn)
                conn.close()

        except ConnectionAbortedError:
            pass
        except OSError:
            pass

    def stop(self):
        """Stops the server."""
        if self.sock:
            self.sock.close()

    def handle_client(self, conn):
        """Handles the client connection."""
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                return
            print('Received:', msg)

            try:
                req = json.loads(msg)
                if 'jsonrpc' not in req or 'method' not in req:
                    raise ValueError('Invalid Request')

                method = req['method']
                params = req.get('params', [])
                request_id = req.get('id')

                if method in self.funcs:
                    try:
                        result = self.funcs[method](*params)
                        res = {
                            'jsonrpc': '2.0',
                            'id': request_id,
                            'result': result
                        } if request_id is not None else None
                    except TypeError:
                        res = {
                            'jsonrpc': '2.0',
                            'id': request_id,
                            'error': {
                                'code': -32602,
                                'message': 'Invalid params'
                            }
                        } if request_id is not None else None
                else:
                    res = {
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'error': {
                            'code': -32601,
                            'message': 'Method not found'
                        }
                    } if request_id is not None else None

            except json.JSONDecodeError:
                res = {
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32700,
                        'message': 'Parse error'
                    }
                }
            except ValueError as e:
                res = {
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32600,
                        'message': str(e)
                    }
                }

            if res is not None:
                res = json.dumps(res)
                conn.sendall(res.encode())

        except socket.error as e:
            print(f"Socket error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    server = JSONRPCServer('0.0.0.0', 8000)

    server.register('hello', functions.hello)
    server.register('greet', functions.greet)
    server.register('add', functions.add)
    server.register('sub', functions.sub)
    server.register('mul', functions.mul)
    server.register('div', functions.div)

    server.start()