from auth_manager import AuthManager
from database import Database
DEV = True
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
                "SELECT age FROM users WHERE (age > 25 and age <= 30) or disabled=false; ",
                "SELECT age FROM users WHERE ((age > 25) and (age <= 30)) or disabled=false; ",
                "SELECT age FROM users WHERE age < 30; ",
                'SELECT age FROM users WHERE id="h6avqpgxow6hggx0";',
                                'SELECT * FROM users WHERE (((age >= 25) AND (age < 40)) OR ((francais = false) AND (age > 50))) AND (name != "julien");'                
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