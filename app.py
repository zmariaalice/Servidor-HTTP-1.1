import socket
import threading
import time
import os
import datetime
import queue

# Função para lidar com uma conexão de cliente
def serve_client(client_socket, base_dir):
    # Define o timeout para 20 segundos
    client_socket.settimeout(20)
    
    # Parse da requisição HTTP
    request = client_socket.recv(1024)
    request_str = request.decode('utf-8')
    request_parts = request_str.split()
    
    # Obtenha o endereço IP do cliente
    client_ip = client_socket.getpeername()[0]
    
    # Verifica se a requisição possui o método GET
    if len(request_parts) >= 2 and request_parts[0] == 'GET':
        file_path = os.path.join(base_dir, request_parts[1][1:])
        
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
            
            # Envia a resposta com sucesso (200 OK)
            response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(content)}\r\n\r\n"
            client_socket.send(response.encode('utf-8') + content)
            
            # Registra um log de sucesso
            log_entry = f"{datetime.datetime.now()} - {client_ip} - [{request_str}] - 200 OK\n"
            log_queue.put(log_entry)
        
        except FileNotFoundError:
            # Arquivo não encontrado (404 Not Found)
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
            client_socket.send(response.encode('utf-8'))
            
            # Registra um log de erro
            log_entry = f"{datetime.datetime.now()} - {client_ip} - [{request_str}] - 404 Not Found\n"
            log_queue.put(log_entry)
    
    else:
        # Método HTTP não suportado (502 Bad Gateway)
        response = "HTTP/1.1 502 Bad Gateway\r\n\r\n"
        client_socket.send(response.encode('utf-8'))
        
        # Registra um log de erro
        log_entry = f"{datetime.datetime.now()} - {client_ip} - [{request_str}] - 502 Bad Gateway\n"
        log_queue.put(log_entry)
    
    # Fecha o socket do cliente
    client_socket.close()

# Função para registrar logs em uma thread exclusiva
def log_worker(log_file):
    while True:
        log_entry = log_queue.get()
        with open(log_file, 'a') as log:
            log.write(log_entry)
        log_queue.task_done()

def main():
    base_dir = '/temp'  # Substitua pelo diretório base desejado
    log_file = 'server.log'
    
    # Inicia a thread de registro de log
    log_thread = threading.Thread(target=log_worker, args=(log_file,))
    log_thread.daemon = True
    log_thread.start()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8080))
    server.listen(5)
    print(f"[*] Servidor HTTP 1.1 iniciado na porta 8080, servindo arquivos de {base_dir}")
    
    while True:
        client_socket, addr = server.accept()
        print(f"[*] Aceitando conexão de {addr[0]}:{addr[1]}")
        
        # Inicia uma nova thread para lidar com a conexão
        client_handler = threading.Thread(target=serve_client, args=(client_socket, base_dir))
        client_handler.start()

if __name__ == '__main__':
    log_queue = queue.Queue()
    main()
