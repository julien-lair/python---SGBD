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
        self.values = []

    def parse(self,string): 

        if self.verify_pointVirgule(string):
            stringElement = string[:-1].split() #on supprime le ;
        else:
                return
        

        #On regarde l'action 
        action = stringElement[0]
        if action == "CREATE":
            self.create(string[:-1])
        elif action == "DROP":
            self.drop(stringElement)
        elif action == "INSERT":
            self.insert(string[:-1])
        elif action == "SELECT":
            self.select(string[:-1])
        elif action == "DESCRIBE":
            self.describe(string[:-1])
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
                                if col.strip() in self.columns_name:
                                    print("Erreur : deux colonnes portent le même nom")
                                    return
                                self.columns_name.append(col.strip())
                            else:
                                print(f"Erreur : le nom {col} n'est pas valide")


                            if self.verify_type(type.strip()):
                                self.columns_type.append(type.strip())
                            else:
                                print(f"Erreur : le type {type} n'est pas valide")
                        
                       
                        self.expressionValide = True

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

    def insert(self,string):
        """
        INSERT INTO users VALUES ('Richard', 25, 20000, false);
        INSERT INTO users (firstname, age, salary, disabled) VALUES ('Richard', 25, 20000, false);
        """
        self.action = "INSERT"
        expressionFirstPart = string.strip().split("(")[0].split()
        try:
            if expressionFirstPart[1] == "INTO":
                if len(expressionFirstPart) == 3 or len(expressionFirstPart) == 4:
                    
                    if self.verify_table_name(expressionFirstPart[2].strip()):
                        #CREATE TABLE name est OK
                        self.table = expressionFirstPart[2].strip()
                        
                        expressionIsWithColumnsName = False
                        if(len(expressionFirstPart) == 4):
                            if expressionFirstPart[3] == "VALUES":
                                #expression de type : INSERT INTO users VALUES ('Richard', 25, 20000, false);
                                expressionIsWithColumnsName = False
                            else:
                                print("Erreur: L'expression n'est pas valide")
                                return
                        else:
                            #expression de type : INSERT INTO users (firstname, age, salary, disabled) VALUES ('Richard', 25, 20000, false);
                            expressionIsWithColumnsName = True


                        if expressionIsWithColumnsName:
                            #On récupère le nom des colonnes 
                            colonnes = string.strip().split("(")[1].split(")")[0].strip().split(",")
                            for col in colonnes:
                                if self.verify_colomn_name(col.strip()):
                                    self.columns_name.append(col.strip())
                                else:
                                    print("Erreur : un nom de colonne ne convient pas.")
                                    return

                            if string.strip().split(")")[1].strip().split()[0] != "VALUES":
                                print("Erreur: le mot clé VALUES est manquant")
                                return
                        
                        #on réucpère les valeurs à insérer après le VALUES
                        #il peux il y avoir plusieurs lignes à ajouter en une fois
                        partAfterVALUES = string.strip().split("VALUES")[1].strip()

                        ouvertureParenthese = False 
                        ouvertureQuoteSimple = False  # ' 
                        ouvertureQuoteDouble = False  # "

                        lines = []
                        lineStart = 0
                        compteur = 0
                        for caractere in partAfterVALUES:
                            #on parcour chaque caratere récupérer les X lignes à ajouter 
                            compteur += 1
                            if(caractere == "(" and ouvertureParenthese == False and ouvertureQuoteSimple == False and ouvertureQuoteDouble == False):
                                #début d'une lignes
                                lineStart = compteur
                                ouvertureParenthese = True
                                continue
                            if(caractere == "'" and  ouvertureParenthese and ouvertureQuoteSimple == False and ouvertureQuoteDouble == False):
                                ouvertureQuoteSimple = True
                                continue
                            if(caractere == '"' and  ouvertureParenthese and ouvertureQuoteSimple == False and ouvertureQuoteDouble == False):
                                ouvertureQuoteDouble = True
                                continue
                            if(caractere == "'" and  ouvertureParenthese and ouvertureQuoteSimple and ouvertureQuoteDouble == False):
                                ouvertureQuoteSimple = False
                                continue
                            if(caractere == '"' and  ouvertureParenthese and ouvertureQuoteSimple == False and ouvertureQuoteDouble):
                                ouvertureQuoteDouble = False
                                continue
                            if(caractere == ")" and ouvertureParenthese == True and ouvertureQuoteSimple == False and ouvertureQuoteDouble == False):
                                #fin d'une lignes
                                lines.append(partAfterVALUES[lineStart:compteur-1])
                                ouvertureParenthese = False
                                continue
                            
                        for line in lines:
                            #print("-->.  ",end="")
                            valueLine = []
                            for elem in line.split(","):
                                #print(elem + "  -  ",end="")
                                valueLine.append(elem)
                            self.values.append(valueLine)
                        
                        if len(lines) == 0:
                            print("Erreur : Veuillez spécifier des valeurs")
                            return
                        self.expressionValide = True

                else:
                    print("Erreur : expréssion invalide")
            else:
                print(f"Erreur : expréssion invalide ")
        except IndexError:
            print("Erreur : expréssion invalide")

    def select(self,string):
        return 
    
    def describe(self,string):
        self.action = "DESCRIBE"
        if len(string.strip().split()) == 2: #Vérifie qu'il y a seulement 2 arguments
            tableName = string.strip().split()[1]
            if self.verify_table_name(tableName.strip()):
                self.table = tableName.strip()
                self.expressionValide = True

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
    
    def verify_pointVirgule(self,string)->bool:
        if string[-1] != ";":
            print("L'expréssion doit finir par un ;")
            self.expressionValide = False
            return False
        return True
