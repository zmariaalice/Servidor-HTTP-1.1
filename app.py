import socket
import threading
import os
import time

HOST = '0.0.0.0'  
PORT = 8080
BASE_DIR = './page'
TIMEOUT = 20

# Status HTTP 
HTTP_STATUS_CODES = {
    200: 'OK',
    404: 'Not Found',
    502: 'Bad Gateway'
}

# LOGS dos requests
def log_request(client_address, request, status_code):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'{timestamp} - {client_address} - [{request}] - {status_code}\n'
    with open('server_log.txt', 'a') as log_file:
        log_file.write(log_entry)


def handle_client(client_socket, client_address):
    request_data = client_socket.recv(1024).decode('utf-8')
    
    if request_data:
        request_lines = request_data.split('\n')
        request_line = request_lines[0].strip().split()

        if len(request_line) >= 3:
            method, path, _ = request_line
            file_path = os.path.join(BASE_DIR, path.lstrip('/'))
            print(file_path)
            if method == 'GET':
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    status_code = 200
                    response_body = open(file_path, 'rb').read()
                else:
                    status_code = 404
                    response_body = b'File Not Found'
            elif method in ('POST', 'DELETE'):
                status_code = 502
                response_body = b'Invalid Function'
            else:
                status_code = 501
                response_body = b'Not Implemented'
        else:
            status_code = 400
            response_body = b'Bad Request'
    else:
        status_code = 400
        response_body = b'Bad Request'
    
    response_headers = f'HTTP/1.1 {status_code} {HTTP_STATUS_CODES.get(status_code, "Unknown")}\r\n'
    response_headers += 'Content-Type: text/html\r\n'
    response_headers += f'Content-Length: {len(response_body)}\r\n\r\n'

    response = response_headers.encode('utf-8') + response_body
    client_socket.send(response)
    client_socket.close()

    log_request(client_address, request_line, status_code)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f'Servidor HTTP rodando em http://localhost:{PORT}/')

while True:
    client_socket, addr = server_socket.accept()
    client_socket.settimeout(TIMEOUT)
    client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()
