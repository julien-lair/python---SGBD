import struct
from sql_parser import Parser
import copy 
from node_condition import NodeCondition

TAILLE_MAX_TEXT = 1000 #équivaut à 1000 caractere ASCII
class Table:
    def __init__(self,path):
        self.path = path
        self.name = ""
        self.columns= []
        self.serialColumns = []
        self.lines = []
        self.header_decoder()
        self.load_raw()
        
    def insert(self,parser : Parser):
        if parser.table != self.name:
            print("Erreur : erreur nom de table non correspondante")
            return 
        
        newLines = []
        
       

    
        
        for line in parser.values:
            

            newLine = copy.deepcopy(self.columns)
            for col in newLine:
                col["value"] = None


            if len(line) == len(self.columns) and len(parser.columns_name) == 0:
                """
                Ici l'utilisateur fait une requête du style : INSERT INTO table VALUES (..),(..);
                l'utilisateur à spécifier un champ pour toutes les colonnes (même _id)
                """
                for value in line:
                    if self.verify_type_is_correct(value,self.columns[line.index(value)]["type"]):
                        if self.columns[line.index(value)]["type"] == "TEXT":
                            newLine[line.index(value)]["value"] = value[1:-1]
                        else:
                            newLine[line.index(value)]["value"] = value
                    else:
                        print(f'Erreur : {value} n\'est pas de type {self.columns[line.index(value)]["type"]}')
                        return
            elif len(line) == len(self.columns) - 1 and self.columns[0]["colonne"] == "_id" and self.columns[0]["type"] == "SERIAL" and len(parser.columns_name) == 0:
                """
                Ici l'utilisateur fait une requête du style : INSERT INTO table VALUES (..),(..);
                l'utilisateur n'a pas spécifier le champ _ID de type SERIAL
                """
                for value in line:
                    if self.verify_type_is_correct(value,self.columns[line.index(value) + 1]["type"]):
                        if self.columns[line.index(value) + 1]["type"] == "TEXT":
                                newLine[line.index(value) + 1]["value"] = value[1:-1]
                        else:
                            newLine[line.index(value) + 1]["value"] = value
                    else:
                        print(f'Erreur : {value} n\'est pas de type {self.columns[line.index(value) + 1]["type"]}')
                        return
            elif len(parser.columns_name) != 0:
                """
                Ici l'utilisateur fait une requête du style : INSERT INTO table (col,col...) VALUES (..),(..);
                """
                if self.verify_missing_colonne(parser.columns_name) == False:
                    print("Vous devez spécifier toutes les colonnes dans votre INSERT, seul les colonne de type SERIAL sont optionel à spécifier")
                    return 
                
                for i in range(len(line)):
                    valeur = line[i]
                    colToAdd = parser.columns_name[i]
                    typeCol = "" 
                    for col in self.columns:
                        if col["colonne"] == colToAdd:
                            typeCol = col["type"]
                            break
                    if typeCol == "":
                        print(f"Erreur : La colonne {colToAdd} est inconnue")
                        return
                    if self.verify_type_is_correct(valeur, typeCol):
                        for elem in newLine:
                            if elem["colonne"] == colToAdd:
                                if elem["type"] == "TEXT":
                                    elem["value"] = valeur[1:-1]
                                else:
                                    elem["value"] = valeur
                                break

            else:
                if self.columns[0]["colonne"] == "_id" and self.columns[0]["type"] == "SERIAL":
                    print("Erreur: Vous devez spécifier un champs pour chaques colonnes (vous pouvez ne pas spécifier pour _id)")
                else:
                    print("Erreur: Vous devez spécifier un champs pour chaques colonnes")
                return
            
            #auto incrmeent sur les champs de type serial : 

            for serialCol in self.serialColumns:
                for col in newLine:
                    if col["colonne"] == serialCol["colonne"]:
                        col["value"] = serialCol["value"]
                        serialCol["value"] = int(serialCol["value"]) + 1
                        break
                                 
            newLines.append(newLine)
            self.lines.append(newLine) #on ajoute à notre mémoire



      

        self.write_line(newLines)

    def select(self,parser : Parser):
        #PARTIE 1 : SELECT [*|col] FROM table

        whereCondition = parser.where != None
        result = []
        for line in self.lines: 
            if len(parser.columns_name) == 1 and parser.columns_name[0] == "*": # cas où SELECT *
                if whereCondition:
                    try :
                        if self.select_where(line,parser.where):
                            result.append(line)
                            
                    except Exception as e:
                        print(e)
                        return
                else:
                    result.append(line)
            else:
                lineSelect = []
                for colChoice in parser.columns_name:
                    for col in line:
                        if col["colonne"] == colChoice:
                            lineSelect.append(col)
                            break
                if len(lineSelect)> 0:
                    if whereCondition:
                        try :
                            if self.select_where(line,parser.where):
                                result.append(line)
                        except Exception as e:
                            print(e)
                            return
                    else:
                        result.append(lineSelect)
        

        # On regarde si ORDER BY est spécifié 
        if parser.orderBy != None:
            colNeedToBeOrder = parser.orderBy["colonne"]
            order = parser.orderBy["order"]
            if order == "ASC":
                result = sorted(result, key=lambda row: self.get_value_of_col_in_row(row, 'age'))
            elif order == "DESC":
                result = sorted(result, key=lambda row: self.get_value_of_col_in_row(row, 'age'),reverse=True)
            else:
                print("Erreur: Une erreur c'est produite lors du ORDER BY")
                return

        #on regarde si on à une LIMIT et par la suite un OFFSET 
        if parser.limit != None:
            print(parser.offset)
            #On vérifie directement si il y a un décalage avec OFFSET
            if parser.offset != None:
                result = result[parser.offset:parser.limit + parser.offset]
            if len(result) > parser.limit and parser.offset == None:
                result = result[:parser.limit]
            
        #PARTIE N : affichage résultat 
        if len(result) > 0:
            tailleColonne = 12

            print("-" * (len(result[0]) * (tailleColonne+2) +1))
            for _ in result[0]:
                print(f'|{" "*(tailleColonne+1)}',end="")
            print("|")
            for col in result[0]:
                print(f'| {col["colonne"]}{" "*(tailleColonne-len(str(col["colonne"])))}',end="")
            print("|")
            for _ in result[0]:
                print(f'|{" "*(tailleColonne + 1)}',end="")
            print("|")
            print("-" * (len(result[0]) * (tailleColonne+2) +1))
            for line in result:
                for col in line:
                    print(f'| {col["value"]}{" "*(tailleColonne-len(str(col["value"])))}',end="")
                print("|")
                print("-" * (len(result[0]) * (tailleColonne+2) +1))

    def get_value_of_col_in_row(self, row, colName):
        for col in row:
            if col["colonne"] == colName:
                return col["value"]
    def update(self,parser : Parser):
        
        for row in self.lines:
            for colData in row:
                for colUpdate in parser.update:
                    if colData["colonne"] == colUpdate["colonne"]:
                        if self.verify_type_is_correct(colUpdate["value"],colData["type"]):
                            #On modifie cette colonne
                            updateValue = colUpdate["value"]
                            if colData["type"] == "TEXT":
                                updateValue = colUpdate["value"][1:-1]

                            if parser.where != None:
                                if self.select_where(row,parser.where):
                                    #la condition est respecter on modifie la colonne
                                    colData["value"] = updateValue
                            else:
                                #On modifie pour toutes les colonnes
                                colData["value"] = updateValue
                            
                        else:
                            print(f'Erreur: Le type de {colUpdate["value"]} n\'est pas le bon.')
                            return
            self.write_updateLine(row)

        #On met à jour le fichier 
        
    
    def delete(self, parser : Parser):
        for line in self.lines:
            if parser.where != None:
                if self.select_where(line,parser.where):
                    #la condition est respecter on supprime la ligne
                    self.write_updateLine(line,delete=True)
            else:
                #On supprime la ligne
                self.write_updateLine(line,delete=True)
                
                """
                TODO
                ici pour la supprésion : ajouter dans l'encodage un flag delete 
                et dans la ligne du .db mettre le flag a jour, mettre tous les X caracteres suivant sur null " "b
                """

    
    def describe(self):
        print(f"Nom de la table : {self.name}\n")

        print("Colonnes :")
        for col in self.columns:
            print(f'  - {col["colonne"]} ({col["type"]})')

        if self.serialColumns:
            print("\nColonnes de type SERIAL :")
            for serial in self.serialColumns:
                print(f'  - {serial["colonne"]} (compteur = {serial["value"]})')
        else:
            print("\nAucune colonne de type SERIAL.")

    def write_line(self,lines):
        self.update_serial()
        for line in lines:
            rowBytes = self.encode_row(line)

            file = open(self.path, "ab")
            file.write(rowBytes)
            file.close()
    def write_updateLine(self,line,delete = False):
        #On réucpère d'abord l'id de la colonne (nous permettera de se déplacer plus rapidement dans le fichier)
        id = None 
        for col in line:
            if col["colonne"] == "_id":
                id = col["value"]
                break
                   
        rowBytes = self.encode_row(line)
        file = open(self.path, "r+b")
        #Il va falloir passer le header et avancer de id ligne
        #on passe le header 
        sizeName = struct.unpack("I", file.read(4))[0]
        file.seek(sizeName,1)

        totalCol = struct.unpack("I", file.read(4))[0]

        for _ in range(totalCol):
            sizeNameCol = struct.unpack("I",file.read(4))[0]
            file.seek(sizeNameCol,1)
            file.seek(4,1)
        
        totalSerial = struct.unpack("I", file.read(4))[0]

        for _ in range(totalSerial):
            sizeColName = struct.unpack("I", file.read(4))[0]
            file.seek(sizeColName,1)
            file.seek(4,1)

        #fin du header

        #On passe id fois les parametre pour modifier ce qui nous intérèsse 
        for _ in range(int(id)):
            for col in self.columns:
                if col["type"] == "INT":
                    file.seek(4,1)
                elif col["type"] == "FLOAT":
                    file.seek(4,1)
                elif col["type"] == "TEXT":
                    file.seek(TAILLE_MAX_TEXT,1)
                elif col["type"] == "BOOL":
                    file.seek(1,1)
                elif col["type"] == "SERIAL":
                    file.seek(4,1)
        
        #Le curseur est sur notre ligne, on la récrit
        if delete == False:
            file.write(rowBytes)
        if delete == True:
            #On écrit que des 0
            nbr_zero = len(rowBytes)

        file.close()

    def update_serial(self):
        """
        Objectif : mettre à jour l'incrémentation des type SERIAL
        Encodage du header : [size_name]name[number_col][size_colX]colX[encode_type_colX][number_serial][size_colSerialX]colSerialX[valeur_serial]
        """ 
        try:
            file = open(self.path, "r+b")

            sizeName = struct.unpack("I", file.read(4))[0]
            file.seek(sizeName,1)

            totalCol = struct.unpack("I", file.read(4))[0]

            for _ in range(totalCol):
                sizeNameCol = struct.unpack("I",file.read(4))[0]
                file.seek(sizeNameCol,1)
                file.seek(4,1)
            
            totalSerial = struct.unpack("I", file.read(4))[0]

            for _ in range(totalSerial):
                sizeColName = struct.unpack("I", file.read(4))[0]
                serialColName = file.read(sizeColName).decode("utf-8")
                for serialCol in self.serialColumns:
                    if serialColName == serialCol["colonne"]:
                        file.write(struct.pack("I",int(serialCol["value"])))
                        break
            file.close()
        except Exception as e:
            print("Erreur : une erreur lors de la mise à jour de l'entête de la table.")
            print(e)

    def encode_row(self,line):
        #Encodage : on écrit en bytes diretement les valeurs, pour le text on ecrit sur TAILLE_MAX_TEXT
        #Exemple de line reçu : [{'colonne': '_id', 'type': 'SERIAL', 'value': '0'}, {'colonne': 'age', 'type': 'INT', 'value': '6'}]
        rowBytes = b""
        for col in line:
            if col["type"] == "INT":
                rowBytes += struct.pack("i", int(col["value"]))
            elif col["type"] == "FLOAT":
                rowBytes += struct.pack("f", float(col["value"]))
            elif col["type"] == "TEXT":
                textBytes = col["value"].encode("utf-8")
                rowBytes += textBytes + b' ' * (TAILLE_MAX_TEXT - len(textBytes)) #On complète pour obtenir TAILLE_MAX_TEXT
            elif col["type"] == "BOOL":
                rowBytes += struct.pack("?", bool(col["value"]))
            elif col["type"] == "SERIAL":
                rowBytes += struct.pack("I", int(col["value"]))
        
        return rowBytes

    def load_raw(self):
        #on charge les lignes 

       

        try:
            file = open(self.path, "rb")

                #Premier temps on va après le header

            sizeName = struct.unpack("I", file.read(4))[0]
            file.seek(sizeName,1)

            totalCol = struct.unpack("I", file.read(4))[0]

            for _ in range(totalCol):
                sizeNameCol = struct.unpack("I",file.read(4))[0]
                file.seek(sizeNameCol,1)
                file.seek(4,1)
            
            totalSerial = struct.unpack("I", file.read(4))[0]

            compteurSerial = 0
            for _ in range(totalSerial):
                sizeColName = struct.unpack("I", file.read(4))[0]
                file.seek(sizeColName,1)
                #On récupère le compteur serial pour parcourir par la suite les n lignes
                compteurSerial = struct.unpack("I", file.read(4))[0]

            #fin du header
            # On récupère les données 
            for _ in range(compteurSerial):
                line = copy.deepcopy(self.columns)
                for col in line:
                    col["value"] = None

                for col in line:
                    typeCol = col["type"]

                    if typeCol == "INT":
                        col["value"] = struct.unpack("i",file.read(4))[0]
                    elif typeCol == "FLOAT":
                        col["value"] = struct.unpack("f",file.read(4))[0]
                    elif typeCol == "TEXT":
                        col["value"] = file.read(TAILLE_MAX_TEXT).decode("utf-8").strip()
                    elif typeCol == "BOOL":
                        col["value"] = struct.unpack("?",file.read(1))[0]
                    elif typeCol == "SERIAL":
                        col["value"] = struct.unpack("I",file.read(4))[0]
                self.lines.append(line)
            
            file.close()
        except Exception as e:
            print("Erreur : une erreur lors de la lecture des donnée de la table.")
            print(e)




    def header_decoder(self):
        """
        Pour rappel l'encodage de l'header est de la forme suivante : 
        [size_name]name[number_col][size_colX]colX[encode_type_colX][number_serial][size_colSerialX]colSerialX[valeur_serial]

        encode_type_colX : 
        "INT"     1
        "FLOAT"   2
        "TEXT"    3
        "BOOL"    4
        "SERIAL"  5
        """
        try:
            file = open(self.path,"rb")
            
            nameSize = struct.unpack("I",file.read(4))[0]
            self.name = file.read(nameSize).decode("utf-8")
            
            numberCol = struct.unpack("I",file.read(4))[0]
            for _ in range(numberCol):
                sizeNameCol = struct.unpack("I",file.read(4))[0]
                colName = file.read(sizeNameCol).decode("utf-8")
                encodeType = int(struct.unpack("I", file.read(4))[0])
                colType = ""
                if encodeType == 1:
                    colType = "INT"
                elif encodeType == 2:
                    colType = "FLOAT"
                elif encodeType == 3:
                    colType = "TEXT"
                elif encodeType == 4:
                    colType = "BOOL"
                elif encodeType == 5:
                    colType = "SERIAL"
                self.columns.append({"colonne":colName,"type":colType})

            numSerialCol = struct.unpack("I",file.read(4))[0]
            for _ in range(numSerialCol):
                sizeNameCol = struct.unpack("I",file.read(4))[0]
                colName = file.read(sizeNameCol).decode("utf-8")
                value = int(struct.unpack("I", file.read(4))[0])
                self.serialColumns.append({"colonne":colName,"value":value})
            file.close()

        except Exception as e:
            print(f"Erreur : Le fichier {self.path} est mal formatté")


    def verify_type_is_correct(self,value,value_type)->bool:
        #les type pris en charge "INT","FLOAT","TEXT","BOOL","SERIAL"
        if value_type == "INT":
            try:
                int(value)
                return True
            except (ValueError, TypeError):
                return False
            
        elif value_type == "FLOAT":
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False
            
        elif value_type == "TEXT":
            conditionA = isinstance(value, str) and value[0] == value[-1] and value[0] in ("'",'"')
            conditionB = len(value.encode("utf-8")) <= TAILLE_MAX_TEXT
            if conditionB == False:
                print("Le champ de type TEXT est trop long ", end="")
            return conditionA and conditionB
        
        elif value_type == "BOOL":
            return value.lower() == "true" or value.lower() == "false"
        
        elif value_type == "SERIAL":
            if value == "NULL":
                return True
            else:
                return False
    def verify_missing_colonne(self,colonneInput)->bool:
        #On vérifie si l'utilisateur à spécifier tous les colonnes non SERIAL
        #Je part du principe que toutes les colonnes sont NOT NULL
        for col in self.columns:
            if col["type"] != "SERIAL":
                #si la colonne non serial est pas dans l'entré de l'user
                if col["colonne"] not in colonneInput :
                    return False
        return True
    
    def select_where(self, line, node: NodeCondition)->bool:
        """
        Si la condition est respecter on return True sinon False
        
        Il faut parcourir l'arbre binaire (node) en parcour POSTFIXE
        appliqué les condition et inscrire le résultat node.resultCondition avec True ou False
        
        PSEUDO-CODE POSTFIXE:
        ParcoursPostfixe ( Arbre binaire T de racine r )
            ParcoursPostfixe ( Arbre de racine fils_gauche [ r ] )
            ParcoursPostfixe ( Arbre de racine f i l s _ d r o i t [ r ] )
            A f f i c h e r  c l e f  [ r ]
        """
        
        if self.parcour_postfixe(node, line):
            #node.draw()
            return node.resultCondition
        return False
    
    def parcour_postfixe(self, node : NodeCondition, line) -> bool:
        if node.left != None:
            self.parcour_postfixe(node.left, line)
        if node.right != None:
            self.parcour_postfixe(node.right, line)

        if node.left == None and node.right == None:        
            #Si feuille de l'arbre
            #On check si les conditions sont respecter pour chaques feuilles
            self.test_condition_where_leaf(node, line)
        else:                                               #Noeud avec opérateur
            #print(f"Checker l'opérateur {node.operateur} par rapport au résultat des deux enfants")
            return self.test_condition_where_parent_node(node)
        #si on a seulement 1 noeud et qu'il est déjà évaluer 
        if node.left == None and node.right == None and node.resultCondition != None:
            return node.resultCondition
            
    
    def test_condition_where_leaf(self,node : NodeCondition, line):
        condition = node.condition
        condition = condition.replace("(","")
        condition = condition.replace(")","")
        condition = condition.strip()
        #on split sois-même car si j'ai une chaine de ractere avec des espaces erreur : "ceci est un exemple" serait split en plusieurs morceaux

        parts = []
        quoteOppen = False
        strToAdd = ""
        typeQuote = ""
        for i in condition:
            if i in "'" or i in '"' and quoteOppen == False: #début chaine de carcateres entre "" 
                quoteOppen = True 
                typeQuote = i
                strToAdd = i
            elif i in typeQuote and quoteOppen:  # find de la chaine de caracteres
                quoteOppen = False
                strToAdd += i
            elif i == " " and quoteOppen == False:
                parts.append(strToAdd)
                strToAdd = ""
            else:
                strToAdd += i

        if strToAdd != "":
            parts.append(strToAdd)


        #véirfié si parts[0] est une colonnes existantes et que parts[2] est bien du bon type
        coloneOK = False
        typeOK = False
        for col in self.columns:
            if parts[0] == col["colonne"]:
                coloneOK = True
                if col["type"] == "SERIAL":
                    typeOK = self.verify_type_is_correct(parts[2], "INT")
                else:
                    typeOK = self.verify_type_is_correct(parts[2], col["type"])
        
                    
        
        if coloneOK == False:
            if parts[0] not in "()":
                raise Exception(f"Erreur: la colonne {parts[0]} n'est pas dans la table") 
            return False
        if typeOK == False:
            raise Exception(f"Erreur: dans le WHERE, le type de la colone {parts[0]} n'est pas le bon.")
        
            
        
        for col in line:
            value = col["value"]
            name = col["colonne"]
            typeCol = col["type"]
            if name == parts[0]:
                if parts[1] == "<":
                    node.resultCondition = (self.string_to_type(value,typeCol) < self.string_to_type(parts[2],typeCol))
                elif parts[1] == ">":
                    node.resultCondition = (self.string_to_type(value,typeCol) > self.string_to_type(parts[2],typeCol))
                elif parts[1] == "<=":
                    node.resultCondition = (self.string_to_type(value,typeCol) <= self.string_to_type(parts[2],typeCol))
                elif parts[1] == ">=":
                    node.resultCondition = (self.string_to_type(value,typeCol) >= self.string_to_type(parts[2],typeCol))
                elif parts[1] == "=":
                        node.resultCondition = self.string_to_type(value,typeCol) == self.string_to_type(parts[2],typeCol)
                elif parts[1] == "!=":
                    node.resultCondition = self.string_to_type(value,typeCol) != self.string_to_type(parts[2],typeCol)
                    
                else:
                    print(f"Erreur: L'opérateur {parts[1]} n'est pas reconnue")
       
    def test_condition_where_parent_node(self,node : NodeCondition)->bool:
        if node.operateur == "AND":
            node.resultCondition = node.left.resultCondition and node.right.resultCondition
        elif node.operateur == "OR":
            node.resultCondition = node.left.resultCondition or node.right.resultCondition
        elif node.operateur == "":
            #pas d'opérateur préciser, on retourne le résultat de l'enfant
            # Ce cas se produit lorsque la condition where comportent des parenthèse en trop, exemple: WHERE (_id = 2) 
            if node.left != None and node.right == None:
                node.resultCondition = node.left.resultCondition #tester dans le left icizZ
            if node.right != None and node.left == None:
                node.resultCondition = node.right.resultCondition
        else: #Si l'opérateur est inconnue
            return False
        return True
    
    def string_to_type(self,value,type):
        if type == "INT":
            return int(value)
        elif type == "FLOAT":
            return float(value)
        elif type == "TEXT":
            return str(value[1:-1]) #On suppirme les "" du text
        elif type == "BOOL":
            return bool(value)
        elif type == "SERIAL":
            return int(value)