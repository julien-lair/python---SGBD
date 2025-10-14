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
                    # création de la table
                    "DROP TABLE test;",
                    "CREATE TABLE test (_id SERIAL, name TEXT, age INT, score FLOAT, active BOOL);",

                    # insert avec toutes les colonnes (y compris _id)
                    "INSERT INTO test VALUES  (NULL,'Alice', 25, 85.5, true);",
                    "INSERT INTO test VALUES (NULL, 'Bob', 30, 90.0, false);",

                    # insert sans spécifier le champ SERIAL (_id auto-incrémenté)
                    "INSERT INTO test VALUES ('Charlie', 22, 72.0, true);",
                    "INSERT INTO test VALUES ('Diana', 27, 88.8, false);",

                    # insert avec noms de colonnes explicites (sans _id)
                    "INSERT INTO test (name, age, score, active) VALUES ('Eve', 29, 91.5, true);",

                    # selects
                    "SELECT * FROM test;",
                    "SELECT * FROM test WHERE name='Alice' OR age=30 OR active=True;",

                    # "SELECT * FROM test WHERE age > 25;",
                    # "SELECT * FROM test WHERE age > 25 AND active = true;",
                     #'SELECT * FROM test WHERE name = "Bob";',
                     #"SELECT * FROM test WHERE score >= 88.8;",

                    # # order by / limit / offset
                     #"SELECT * FROM test ORDER BY age ASC;",
                     #"SELECT * FROM test ORDER BY score DESC LIMIT 2;", 
                    #  "SELECT * FROM test ORDER BY _id DESC ;", 

                    # # updates
                    #"UPDATE test SET score = 95.0 WHERE name = 'Alice';", 
                    #  "UPDATE test SET age = 35, active = false WHERE name = 'Bob';", 
                    # # deletes
                     #"DELETE FROM test WHERE name = 'Charlie';", #fonctionne pas
                    #  "DELETE FROM test WHERE score < 80 AND active = true;", #fonctionne pas
                    # "SELECT * FROM test;",
                    # # drop table (ou suppression finale)
                    # "DROP TABLE test;"
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