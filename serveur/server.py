from auth_manager import AuthManager
from database import Database
from result import resultAPI
import socket
import threading
import json
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
            #On récupère les id que le client à envoyer sous la forme {"user":xxx,"password":hash}
            creds = json.loads(client.recv(4096).decode().strip())
            
            auth.new_connection(creds["user"],creds["password"])
            client.send(json.dumps(resultAPI.show()).encode() + b"\n") #on revoit le résultat de l'auth
            
            while True and auth.isConnected:
                request = client.recv(4096).decode().strip()
                self.database.execute(request)
                client.send(json.dumps(resultAPI.show()).encode() + b"\n")
                resultAPI.reset()
        except ConnectionResetError:
            print("Client déconnecté")
        except BrokenPipeError:
            print("Client déconnecté")

