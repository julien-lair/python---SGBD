from auth_manager import AuthManager
from database import Database
from result import resultAPI
import socket
import threading
from result import resultAPI
DEV = False
class Server:

    def __init__(self, host,port,database : Database):
        self.host = host 
        self.port = port 
        self.database = database
    def start(self):
        print(f"Serveur lancer sur {self.host}:{self.port}")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        while True:
            client_socket, adresse = server_socket.accept()
            print(f"Connexion entrante de {adresse}")
            client_thread = threading.Thread(target=self.newClient, args=(client_socket,))
            client_thread.start()


    def newClient(self,client):
        try:
            auth = AuthManager()
            auth.new_connection()
            if not auth.isConnected:
                resultAPI.unauthorized("Échec de connexion : authentification requise ou invalide")
                client.send(str("error").encode())
                client.close()
                return
            
            while True:
                request = client.recv(5000).decode().strip()
                self.database.execute(request)
                client.send(str(resultAPI.show()).encode() + b"\n")
                resultAPI.reset()
        except ConnectionResetError:
            print("Client déconnecter")

