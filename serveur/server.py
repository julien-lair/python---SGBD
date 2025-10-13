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
        #while True:
        
        #pour le test, je fake un client qui arrive
        self.newClient()


    def newClient(self):
        auth = AuthManager()
        auth.new_connection()
        if not auth.isConnected:
            print("echec de connection")
        
        print("Bienvenue sur le serveur :)")



        if DEV:
            commande = [
                #ici les commandes a taper des le lancement du serveur             
                ]
            for c in commande:
                self.database.execute(c.strip())
                print("-------------")


        while True:
            request = input("\n> ").strip()
            self.database.execute(request)

    def response(self):
        print("")
    
    def request(self):
        print("")