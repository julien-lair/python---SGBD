import getpass
import hashlib
import os
from result import resultAPI
from database import Database
import json
DEV=False
class AuthManager():
    
    def __init__(self):
        self.isConnected = False
        self.database = Database()
    def new_connection(self,user,password):
        if DEV:
            self.isConnected = True
        else:
            if self.secure_File_exist():#si une table avec les creds existe (si il a déjà créer son compte)
                self.login(user,password)
            else:
                self.register()
            

    def register(self):
        print("Créer votre compte")
        user = input("User : ").strip()
        password_match = False
        while not(password_match):
            password = getpass.getpass("Mot de passe : ")
            password_verify = getpass.getpass("Confirmer le mot de passe : ")
            if password == password_verify:
                password_match = True
            else:
                resultAPI.unauthorized("Erreur : les mots de passe ne correspondent pas.")

        #on créer la table et on ajoute les nouvelles informations 
        sql = "CREATE TABLE secure (username TEXT, password TEXT);"
        self.database.execute(sql)

        sql2 = f"INSERT INTO secure (username, password) VALUES ('{user}', '{self.hash(password)}');"
        self.database.execute(sql2)
        password = None
        password_verify = None


    def login(self,user,password):
        self.database.execute(f"SELECT password FROM secure WHERE username = '{user}';")
        reusltData = resultAPI.show()["data"]
        try:
            storePass = json.loads(reusltData)["data"][0][0]
            if password == storePass: #si les usernma eosnt équiavlent et les deux hash sont équiavalent
                self.isConnected = True
                resultAPI.sucess("Vous êtes connecté.",None)
            else:
                resultAPI.unauthorized("Erreur : identifiant incorrect.")
        except IndexError:
            #si l'index est une erreur, c'est que aucun retour dans le select
            #donc l'username est faux
            resultAPI.unauthorized("Erreur : identifiant incorrect.")

       

    

    def hash(self,value):
        return hashlib.sha512(value.encode('utf-8')).hexdigest()

    def secure_File_exist(self)->bool:
        sql = "DESCRIBE secure;"
        self.database.execute(sql)
        if resultAPI.show()["statut"] == "sucess":
            #la table exist
            return True
        else:
            return False

        

