import re

blacklistWord  = ["CREATE","TABLE","DROP","INSERT","INTO",
                  "VALUES","SELECT","FROM","WHERE","ORDER",
                  "BY","ASC","DESC","LIMIT","OFFSET","UPDATE",
                  "SET","DELETE","DESCRIBE","AND","OR","NOT"]    

authorizedType =["INT","FLOAT","TEXT","BOOL","SERIAL"]
class Parser:

    def __init__(self):
        self.expressionValide = False
        self.action = ""
        self.table = ""
        self.columns_name = []
        self.columns_type = []

    def parse(self,string):
       
        """
        CREATE TABLE users (id SERIAL, firstname TEXT, age INT, salary FLOAT, disabled BOOL);
        
        DROP TABLE users;
        """
        
        
        if string[-1] != ";":
            print("L'expréssion doit finir par un ;")
            self.expressionValide = False
            return
        

        stringElement = string[:-1].split() #on supprime le ;
        #On regarde l'action 
        action = stringElement[0]
        if action == "CREATE":
            self.create(string[:-1])
        elif action == "DROP":
            self.drop(stringElement)
        else:
            print(f"{action} n'est pas reconnue")
            self.expressionValide = False




    def create(self, string):
        #   CREATE TABLE users (id SERIAL, firstname TEXT, age INT, salary FLOAT, disabled BOOL);
        # CREATE TABLE sjs (dhjsgsdg TEXT,              hdhdhdhdhdhdhd                ZFTYFZFZYGFZF        );   test avec des espaces
        self.action = "CREATE"
        expressionFirstPart = string.strip().split("(")[0].split()
        try:
            if expressionFirstPart[1] == "TABLE":
                if len(expressionFirstPart) == 3:
                    if self.verify_table_name(expressionFirstPart[2].strip()):
                        #CREATE TABLE name est OK
                        self.table = expressionFirstPart[2].strip()
                        
                        #on recupere les nom de colones et type 
                        colonnesNameAndType = string.strip().split("(")[1].split(")")[0].split(",")

                        #on vérifie si les colonnes et types sont valide
                        for value in colonnesNameAndType:
                            
                            valueWithoutSpace = value.strip()
                            col = valueWithoutSpace.split()[0]
                            type = valueWithoutSpace.split()[1]

                            if self.verify_colomn_name(col.strip()):
                                self.columns_name.append(col.strip())
                            else:
                                print(f"Erreur : le nom {col} n'est pas valide")


                            if self.verify_type(type.strip()):
                                self.columns_type.append(type.strip())
                            else:
                                print(f"Erreur : le type {type} n'est pas valide")
                        

                else:
                    print("Erreur : expréssion invalide")
            else:
                print(f"Erreur : expréssion invalide ")
        except IndexError:
            print("Erreur : expréssion invalide")



    def drop(self,expression):
        #   DROP TABLE users
        self.action = "DROP"

        try:
            if expression[1] == "TABLE":
                if len(expression) == 3:
                    if self.verify_table_name(expression[2].strip()):
                        #Tous est OK 
                        self.table = expression[2].strip()
                        self.expressionValide = True
                else:
                    print("Erreur : expréssion invalide")
            else:
                print("Erreur : expréssion invalide")
        except IndexError:
            print("Erreur : expréssion invalide")

    def verify_table_name(self,name)->bool:
        if not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", name):
            print(f"Erreur : nom de table '{name}' invalide. Il doit commencer par une lettre et ne contenir que des caractères alphanumériques ou '_'.")
            return False
        
        if name in blacklistWord:
            print(f"Erreur : le nom de table {name}, porte un nom interdit.")
            return False
        
        return True
        
    def verify_colomn_name(self,name)->bool:
        if not re.match(r"[A-Za-z0-9_]+$", name):
            print(f"Erreur : nom de colonne '{name}' invalide. il doit contenir seulement des lettre min maj, et _")
            return False
        
        if name in blacklistWord:
            print(f"Erreur : le nom de colonne {name}, porte un nom interdit.")
            return False

        return True
    
    def verify_type(self,type)->bool:
        if type in authorizedType:
            return True
        print(f"Le type {type} n'est pas valide vous devez choisir : INT,FLOAT,TEXT,BOOL,SERIAL")
        return False
    