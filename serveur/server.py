from auth_manager import AuthManager
from database import Database
DEV = False
class Server:

    def __init__(self, host,port,database : Database):
        self.host = host 
        self.port = port 
        self.database = database
    def start(self):
        print("Je créer le serveur, j'ouvre un port")
        self.newClient()


    def newClient(self):
        auth = AuthManager()
        auth.new_connection()
        if not auth.isConnected:
            print("echec de connection")
        
        print("Bienvenue sur le serveur :)")



        if DEV:
            commande = [
                 
                ]
            for c in commande:
                self.database.execute(c.strip())


        while True:
            request = input("\n> ").strip()
            self.database.execute(request)

    def response(self):
        print("")
    
    def request(self):
        print("")