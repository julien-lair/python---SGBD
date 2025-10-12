import re
from node_condition import NodeCondition
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
        self.where : NodeCondition = None
        self.orderBy = None
        self.limit = None
        self.offset = None

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

                        if string.strip().split("(")[1].split(")")[1].strip() != "":
                            print("Erreur : argument indésirable")
                            return
                        
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
                            if(caractere == " "):
                                continue
                            if(caractere!="," and ouvertureParenthese == False):
                                print("Erreur : Commandes mal formaté")
                                return
                        for line in lines:
                            #print("-->.  ",end="")
                            valueLine = []
                            for elem in line.split(","):
                                #print(elem + "  -  ",end="")
                                valueLine.append(elem.strip())
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
        self.action = "SELECT"

        #On récupère les colonnes à selectionner 
        if " FROM " not in string:
            print("Erreur : Il manque le FROM")
            return

        colonneSelectionner = string.split("FROM")[0].split("SELECT")[1].strip().split(",")
        for col in colonneSelectionner:
            if self.verify_colomn_name_select(col.strip()):
                self.columns_name.append(col.strip())

        tableName = string.split("FROM")[1].strip().split()[0].strip()
        if self.verify_table_name(tableName.strip()):
            self.table = tableName.strip()
        
        #Si un mot est présent après FROM table, ça doit être : WHERE,ORDER BY, LIMIT
        if len(string.split("FROM")[1].strip().split()) > 1:
            if string.split("FROM")[1].strip().split()[1] not in "WHERE ORDER BY LIMIT":
                #On a des mot inconnues à la fin de l'expression, exemple :  SELECT * FROM users where ..; (where en minuscule)
                print("Erreur : expréssion invalide")
                return

        """
        Règle : (tous les champs optionel)
        WHERE après le FROM
        WHERE avant ORDER BY
        LIMIT peut être spécifier sant les autres (WHERE,ORDER BY), mais si ils sont présent doit être en dernier
        OFFSET doit être après LIMIT
        """
        if "WHERE" in string: 
            if string.split("FROM")[1].strip().split()[1].strip() == "WHERE":
                self.whereCondition(string)
            else:
                print("Erruer : La condition WHERE doit se trouvé après la table sélectionner dans le FROM")
                return
            
            #Si un mot est présent après expréssion de WHERE, ça doit être : WHERE,ORDER BY, LIMIT
            if len(string.split("FROM")[1].strip().split()) > 0:
                if string.split("FROM")[1].strip().split()[1] not in "WHERE ORDER BY LIMIT":
                    #On a des mot inconnues à la fin de l'expression, exemple :  SELECT * FROM users where ..; (where en minuscule)
                    print("Erreur : expréssion invalide")
                    return
                
        if "ORDER BY" in string:
            #vérifie si après WHERE (si WHERE existe)
            if "WHERE" in string:
                if "ORDER BY" in string.split("WHERE")[1]:
                    #ORDER BY est bien après WHERE si il existe
                    self.orderByCondition(string)
                    return
                else:
                    print("Erreur: Le ORDER BY doit être après le WHERE")
                    return
            else:
                self.orderByCondition(string)
            
        if "LIMIT" in string:
            if "WHERE" in string:
                if "LIMIT" in string.split("WHERE")[1]:
                    #LIMIT après WHERE (si WHERE présent)
                    self.limitCondition(string)
                    return
                else:
                    print("Erreur: Le LIMIT doit être après le WHERE")
                    return 
                
            if "ORDER BY" in string:
                if "LIMIT" in string.split("ORDER BY")[1]:
                    #LIMIT après ORDER BY (si ORDER BY présent)
                    self.limitCondition(string)
                    return
                else:
                    print("Erreur: Le LIMIT doit être après le ORDER BY")
                    return 
            self.limitCondition(string)
            

        if "OFFSET" in string:
            if "LIMIT" in string:
                if "OFFSET" in string.split("LIMIT")[1]:
                    #OFFSET après LIMIT (LIMIT obligatoire pour OFFSET)
                    self.limitCondition(string)
                    return
            print("Erreur: OFFSET doit être après le LIMIT")
            return         
        
        if self.where != None:
            if self.where.verify_condition() == False:
                print(f"Erreur: condition invalide passer dans le paramètre WHERE")
                return
        self.expressionValide = True

    def whereCondition(self,string):
        # WHERE (age > 25 and age <= 30) or disabled=false
        # WHERE age < 30
        # WHERE id = "h6avqpgxow6hggx0"

        whereCondition = string.split("WHERE")[1].strip()
        
        #On enleve tous ce qui pourrait être après le WHERE : 
        wordlist = ["ORDER BY","LIMIT"] 
        for word in wordlist:
            whereCondition = whereCondition.split(word)[0].strip()

        # Pré-traitement 

        whereCondition = whereCondition.replace("("," ( ")
        whereCondition = whereCondition.replace(")"," ) ")
        whereCondition = whereCondition.replace("<="," <= ")
        whereCondition = whereCondition.replace(">="," >= ")
        whereCondition = re.sub(r'<(?![=])', ' < ', whereCondition)
        whereCondition = re.sub(r'>(?![=])', ' > ', whereCondition)
        whereCondition = re.sub(r'(?<![><!])=', ' = ', whereCondition)
        whereCondition = whereCondition.replace("!="," != ")
        whereCondition = whereCondition.replace(" and "," AND ")
        whereCondition = whereCondition.replace(" or "," OR ")
        whereCondition = whereCondition.replace(" not "," NOT ")

        # On sépare chaque mot 
        whereDecoupe = whereCondition.split()


        #On créer un tableau avec les condition selon leur logique 
        #priorité des parenthèse

        condition = []
        for _ in whereDecoupe:
            condition.append("")
        whereFinish = False
        compteur = 0

        parentheseOuverte = 0
        
        position = 0
        for elem in whereDecoupe:
            if elem == "(":
                if condition[position] != "":
                    position += 1
                parentheseOuverte += 1
                condition[position] = condition[position] + " " + elem
            elif elem == ")" and parentheseOuverte >= 1:
                parentheseOuverte -= 1
                condition[position] = condition[position] + " " + elem
                position += 1
            else:
                condition[position] = condition[position] + " " + elem
            

        #On supprime les valeurs null
        conditionSecondpart = []
        for elem in condition:
            if elem != '':
                conditionSecondpart.append(elem.strip())

        #Création de l'arbre de décision 
        #Règle:
        #Si j'ai une parenthèse ouvrante : Je créer deux fils, et si gauche libre alors je met la parenthèse au gauche, sinon a celui de droite
        #Si j'ai parenthèse qui ferme je remonte au parent et je la ferme
        #Si mon expression contient un mot spécial (and,or,not) je la coupe en deux et j'ajoute la condition au noeud actuellle et les condition au enfant a gauche et droite
        
        rootNode = NodeCondition(None,None,None,None)
        actualNode = rootNode
        specialWords = ["AND","OR","NOT"]
        
        for elem in conditionSecondpart:
            modify = False
            if elem[0] == "(":
                if actualNode.child_left_free():
                    actualNode.new_child_left()
                    actualNode = actualNode.left
                    actualNode.openCondition = True
                elif actualNode.child_right_free():
                    actualNode.new_child_right()
                    actualNode = actualNode.right
                    actualNode.openCondition = True
                modify = True
            
            specialWordDetected = False    
            for specialWord in specialWords:
                if specialWord in elem and len(elem) > len(specialWord): #si "condition1 AND|OR|NOT condition2"
                    specialWordDetected = True
                    restart = True
                    while restart:
                        if actualNode.child_left_free():
                            actualNode.new_child_left()
                            actualNode.operateur = specialWord
                            actualNode.left.condition = elem.split(specialWord)[0]
                            restart=False
                        if actualNode.child_right_free():
                            actualNode.new_child_right()
                            actualNode.operateur = specialWord
                            actualNode.right.condition = elem.split(specialWord)[1]
                            restart = False
                        if (not actualNode.child_left_free() and not actualNode.child_right_free()) and restart:
                            actualNode = actualNode.parent
                        
                    modify = True
                if specialWord in elem and len(elem) == len(specialWord): #si "AND|OR|NOT"
                    #on remonte  et on ecrit la condition 
                    specialWordDetected = True
                    actualNode = actualNode.parent
                    actualNode.operateur = specialWord
                    modify = True
            #Si on a (age > 25) 
            if modify and specialWordDetected == False and len(elem) > 2: #si != '()'
                actualNode.condition = elem


            if modify == False and elem != ")":
                #on ajoute elem au noeud actuelle 
                actualNode.condition = elem
            if elem[-1] == ")":
                if actualNode.openCondition == True:
                    actualNode.openCondition = False
                elif actualNode.parent.right == actualNode and actualNode.parent.operateur != '' and actualNode.parent.openCondition == True:
                    actualNode = actualNode.parent
                    actualNode.openCondition = False
                else:
                    print("Une erreur")
                    return 

        #rootNode.draw()
        
        self.where = rootNode   



        """
        print(f"WHERE CONDITION : {whereCondition}")
        print(f"Decoupé : {whereDecoupe}")
        print(f"Condition : {conditionSecondpart}")
        """

    def orderByCondition(self,string):
        orderByCondition = string.split("ORDER BY")[1].strip()
        
        #On enleve tous ce qui pourrait être après le WHERE : 
        wordlist = ["WHERE","LIMIT","OFFSET"] 
        for word in wordlist:
            orderByCondition = orderByCondition.split(word)[0].strip()
        orderByConditionSplit = orderByCondition.split()
        if(len(orderByConditionSplit)) == 2:
            if self.verify_colomn_name(orderByConditionSplit[0].strip()):
                if orderByConditionSplit[1].strip() == "ASC" or orderByConditionSplit[1].strip() == "DESC":
                    self.orderBy = {"colonne":orderByConditionSplit[0].strip(),"order":orderByConditionSplit[1].strip()}
                    return
        print("Erreur : mauvaise condition dans le ORDER BY")
        

    def limitCondition(self,string):
        limitCondition = string.split("LIMIT")[1].strip()
        wordlist = ["WHERE","LIMIT","OFFSET"] 
        for word in wordlist:
            limitCondition = limitCondition.split(word)[0].strip()
        limitConditionSplit = limitCondition.split()
        if(len(limitConditionSplit)) == 1:
            try:
                valeur = int(limitConditionSplit[0].strip())
                self.limit = valeur
                return
            except (ValueError, TypeError):
                print("Erreur : Veuillez précisez un entier valide pour LIMIT")
                return
        print("Erreur : mauvaise condition dans le LIMIT")
        
    def offsetCondition(self,string):
        offsetCondition = string.split("OFFSET")[1].strip()
        wordlist = ["WHERE","LIMIT"] 
        for word in wordlist:
            offsetCondition = offsetCondition.split(word)[0].strip()
        offsetConditionSplit = offsetCondition.split()
        if(len(offsetConditionSplit)) == 1:
            try:
                valeur = int(offsetConditionSplit[0].strip())
                self.offset = valeur
                return
            except (ValueError, TypeError):
                print("Erreur : Veuillez précisez un entier valide pour OFFSET")
                return
        print("Erreur : mauvaise condition dans le OFFSET")

    def describe(self,string):
        self.action = "DESCRIBE"
        if len(string.strip().split()) == 2: #Vérifie qu'il y a seulement 2 arguments
            tableName = string.strip().split()[1]
            if self.verify_table_name(tableName.strip()):
                self.table = tableName.strip()
                self.expressionValide = True
        else:
            print("Erreur : Argument indésirable")
            return

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
    
    def verify_colomn_name_select(self,name)->bool:
        if name in ["*"]:
            return True
        return self.verify_colomn_name(name)

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
