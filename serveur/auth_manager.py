import getpass
import hashlib
import os
DEV=True
class AuthManager():
    
    def __init__(self):
        self.fileName = os.path.dirname(__file__) +  "/data/secure.db"
        self.isConnected = False
        self.maxTentative = 3
    def new_connection(self):
        if DEV:
            self.isConnected = True
        else:
            if not(self.file_exist()):
                self.register()
            while self.isConnected == False and self.maxTentative > 0:
                self.login()
                print("\n")
            if self.maxTentative <= 0:
                print("Trop de tentative")

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
                print("Les mot de passe ne correspondent pas\n")
        
        self.create_file(self.hash(user),self.hash(password))

        password = None
        password_verify = None

    def create_file(self,username,password):
        file = open(self.fileName, "w", encoding="utf-8")
        file.write(f"{username}\n")
        file.write(f"{password}\n")
        file.close()

    def login(self):
        print("Veuillez vous connecter")
        user = input("User : ").strip()
        password = getpass.getpass("Mot de passe : ")

        userHash = self.hash(user)
        user = None 

        passwordHash = self.hash(password)
        password = None

        storeUser,storePass = self.get_credential()

        if(userHash == storeUser and passwordHash == storePass):
            self.isConnected = True
        else:
            print("Identifiant incorecte")
            self.maxTentative -= 1

    

    def get_credential(self):
        try:
            file = open(self.fileName, "r", encoding="utf-8")
            lines = file.readlines()
            file.close()
            user = lines[0].strip()
            password = lines[1].strip()
            return user,password
        except Exception as e:
            print("Une erreur est survenue")
            
    def hash(self,value):
        return hashlib.sha512(value.encode('utf-8')).hexdigest()

    def file_exist(self):
        return os.path.exists(self.fileName)
        
        

