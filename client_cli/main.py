import socket

HOST = "127.0.0.1"
PORT = 1234

def main():
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    serveur.connect((HOST, PORT))
    print("Connecté au serveur !")

    connected = True
    while connected:
        cmd = input("> ").strip()
        if cmd.strip() == "exit":
            print("Déconnexion")
            serveur.close()
            connected = False

        if len(cmd) > 0 and cmd.strip() != "exit":
            serveur.send(cmd.encode())
            data = serveur.recv(4096).decode()
            print(data)

if __name__ == "__main__":
    main()
