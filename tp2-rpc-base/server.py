"""
 Simple JSON-RPC Server

"""

import json
import socket

import functions


class JSONRPCServer:
    """The JSON-RPC server."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.funcs = {}
        self.shutdown_flag = False

    def register(self, name, function):
        """Registers a function."""
        self.funcs[name] = function

    def start(self):
        """Starts the server."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f"Listening on port {self.port} ...")

        try:
            while not self.shutdown_flag:
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
        self.shutdown_flag = True
        if self.sock:
            self.sock.close()

    def handle_client(self, conn):
        """Handles the client connection."""
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                return
            print('Received:', msg)

            _, res = self.process_request(msg)
            if res is not None:
                conn.sendall(json.dumps(res).encode())

        except socket.error as e:
            print(f"Socket error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def process_request(self, msg):
        try:
            req = json.loads(msg)
            if 'jsonrpc' not in req or 'method' not in req:
                raise ValueError('Invalid Request')

            method = req['method']
            params = req.get('params', [])
            request_id = req.get('id')

            if method in self.funcs:
                return req, self.execute_method(method, params, request_id)
            else:
                return req, self.method_not_found(request_id)

        except json.JSONDecodeError:
            return None, self.json_parse_error()
        except ValueError as e:
            return None, self.invalid_request(str(e))

    def execute_method(self, method, params, request_id):
        try:
            func = self.funcs[method]
            if isinstance(params, dict):
                result = func(**params)
            else:
                result = func(*params)
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            } if request_id is not None else None
        except TypeError:
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32602,
                    'message': 'Invalid params'
                }
            } if request_id is not None else None

    def method_not_found(self, request_id):
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': -32601,
                'message': 'Method not found'
            }
        } if request_id is not None else None

    def json_parse_error(self):
        return {
            'jsonrpc': '2.0',
            'id': None,
            'error': {
                'code': -32700,
                'message': 'Parse error'
            }
        }

    def invalid_request(self, message):
        return {
            'jsonrpc': '2.0',
            'id': None,
            'error': {
                'code': -32600,
                'message': message
            }
        }


if __name__ == "__main__":
    server = JSONRPCServer('0.0.0.0', 8000)

    server.register('hello', functions.hello)
    server.register('greet', functions.greet)
    server.register('add', functions.add)
    server.register('sub', functions.sub)
    server.register('mul', functions.mul)
    server.register('div', functions.div)

    server.start()
