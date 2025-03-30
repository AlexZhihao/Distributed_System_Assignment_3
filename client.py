import socket
import threading

nickname = ""
current_channel = "#general"

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print("\n" + msg.strip())
            print(f"\n[{nickname} @ {current_channel}] >> ", end="", flush=True)
        except:
            break

def print_help():
    print("\n[System] Available commands:")
    print("  #channel_name message    — Switch to a channel and send message")
    print("  /msg nickname message     — Send a private message")
    print("  /quit                     — Quit the chat")
    print("  /help                     — Show this help message\n")

def main():
    global nickname, current_channel

    server_ip = input("Enter server IP address (e.g., 127.0.0.1): ").strip()
    port = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, port))

    while not nickname:
        nickname_input = input("Enter your nickname: ").strip()
        if nickname_input:
            nickname = nickname_input
            sock.sendall(nickname.encode())
        else:
            print("[System] Nickname cannot be empty.")

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    print(f"\n[System] You joined channel #general as {nickname}.\n")
    print_help()

    while True:
        try:
            msg = input(f"[{nickname} @ {current_channel}] >> ").strip()
            if not msg:
                continue
            if msg.lower() == "/quit":
                print("[System] Disconnecting...")
                break
            elif msg.lower() == "/help":
                print_help()
                continue
            elif msg.startswith('#'):
                parts = msg.split(' ', 1)
                if len(parts) == 2:
                    current_channel = parts[0]
                else:
                    print("[System] Invalid format. Example: #music Hello!")
            sock.sendall(msg.encode())
        except KeyboardInterrupt:
            break
        except:
            print("[System] Error occurred. Closing connection...")
            break

    sock.close()
    print("[System] Disconnected.")

if __name__ == "__main__":
    main()
