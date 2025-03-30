import socket
import threading
import time

HOST = '0.0.0.0'
PORT = 12345

clients = {}
lock = threading.Lock()

def timestamp():
    return time.strftime("[%H:%M:%S]")

def broadcast(message, exclude_conn = None, channel=None):
    with lock:
        for conn, info in clients.items():
            if conn != exclude_conn and (channel == '#general' or info['channel'] == channel):
                try:
                    conn.sendall(message.encode())
                except:
                    conn.close()
                    del clients[conn]

def handle_client(conn, addr):
    try:
        nickname = conn.recv(1024).decode().strip()
        with lock:
            clients[conn] = {'nickname': nickname, 'channel': '#general'}

        join_msg = f"{timestamp()} [System] {nickname} joined #general\n"
        broadcast(join_msg, exclude_conn=conn, channel='#general')
        conn.sendall(f"{timestamp()} [System] You joined #general. Use #channel_name to switch channels or /msg user message to private chat.\n".encode())

        while True:
            msg = conn.recv(1024).decode().strip()
            if not msg:
                break

            with lock:
                sender = clients[conn]['nickname']
                current_channel = clients[conn]['channel']

            if msg.startswith('#'):
                parts = msg.split(' ', 1)
                new_channel = parts[0]
                message = parts[1] if len(parts) > 1 else ''
                with lock:
                    clients[conn]['channel'] = new_channel
                broadcast(f"{timestamp()} [System] {sender} joined {new_channel}\n", exclude_conn=conn, channel=new_channel)
                if message:
                    broadcast(f"{timestamp()} [{new_channel}] {sender}: {message}\n", exclude_conn=conn, channel=new_channel)
            elif msg.startswith('/msg'):
                parts = msg.split(' ', 2)
                if len(parts) >= 3:
                    target_nick = parts[1]
                    message = parts[2]
                    found = False
                    with lock:
                        for c, info in clients.items():
                            if info['nickname'] == target_nick:
                                c.sendall(f"{timestamp()} [Private] {sender}: {message}\n".encode())
                                found = True
                                break
                    if not found:
                        conn.sendall(f"{timestamp()} [System] User '{target_nick}' not found.\n".encode())
                else:
                    conn.sendall(f"{timestamp()} [System] Invalid format. Use: /msg nickname message\n".encode())
            else:
                broadcast(f"{timestamp()} [{current_channel}] {sender}: {msg}\n", exclude_conn=conn, channel=current_channel)
    except:
        pass
    finally:
        with lock:
            if conn in clients:
                nickname = clients[conn]['nickname']
                channel = clients[conn]['channel']
                del clients[conn]
                broadcast(f"{timestamp()} [System] {nickname} left {channel}\n", exclude_conn=conn, channel=channel)
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"{timestamp()} Server started on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
