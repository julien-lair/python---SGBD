import struct
from sql_parser import Parser
import copy 
from ShuntingYard import ShuntingYard
from result import resultAPI
import json

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
            resultAPI.notFound("Erreur : nom de table non correspondant.")
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
                        resultAPI.syntaxError(f"Erreur : {value} n'est pas de type {self.columns[line.index(value)]['type']}.")
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
                        resultAPI.syntaxError(f"Erreur : {value} n'est pas de type {self.columns[line.index(value) + 1]['type']}.")
                        return
            elif len(parser.columns_name) != 0:
                """
                Ici l'utilisateur fait une requête du style : INSERT INTO table (col,col...) VALUES (..),(..);
                """
                if self.verify_missing_colonne(parser.columns_name) == False:
                    resultAPI.syntaxError("Erreur : vous devez spécifier toutes les colonnes dans votre INSERT, seules les colonnes de type SERIAL sont optionnelles à spécifier.")
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
                        resultAPI.notFound(f"Erreur : la colonne '{colToAdd}' est inconnue.")
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
                    resultAPI.syntaxError("Erreur : vous devez spécifier un champ pour chaque colonne (vous pouvez ne pas spécifier pour _id).")
                else:
                    resultAPI.syntaxError("Erreur : vous devez spécifier un champ pour chaque colonne.")
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
        resultAPI.create(f"Les données ont bien été ajoutées.")

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
                    except Exception:
                        resultAPI.syntaxError("Erreur : la condition WHERE n'est pas correcte.")
                        return
                else:
                    result.append(line)
            else:
                lineSelect = []
                #On réucpère les noms de colonnes qui doivent être retourner
                for colChoice in parser.columns_name:
                    if self.verify_if_coloumns_exist(colChoice):
                        for col in line:
                            if col["colonne"] == colChoice:
                                lineSelect.append(col)
                                break
                    else:
                        resultAPI.syntaxError(f"Erreur : la colonne '{colChoice}' n'éxiste pas.")

                if len(lineSelect)> 0:
                    if whereCondition:
                        try :
                            try :
                                if self.select_where(line,parser.where):
                                    result.append(line)
                            except Exception:
                                resultAPI.syntaxError("Erreur : la condition WHERE n'est pas correcte.")
                                return
                        except Exception as e:
                            resultAPI.syntaxError(f"Erreur : {e}")
                            return
                    else:
                        result.append(lineSelect)
        

        # On regarde si ORDER BY est spécifié 
        if parser.orderBy != None:
            colNeedToBeOrder = parser.orderBy["colonne"]
            order = parser.orderBy["order"]
            if order == "ASC":
                result = sorted(result, key=lambda row: self.get_value_of_col_in_row(row, colNeedToBeOrder))
            elif order == "DESC":
                result = sorted(result, key=lambda row: self.get_value_of_col_in_row(row, colNeedToBeOrder),reverse=True)
            else:
                resultAPI.syntaxError("Erreur : une erreur s'est produite lors du ORDER BY.")
                return

        #on regarde si on à une LIMIT et par la suite un OFFSET 
        if parser.limit != None:
            #On vérifie directement si il y a un décalage avec OFFSET
            if parser.offset != None:
                result = result[parser.offset:parser.limit + parser.offset]
            if len(result) > parser.limit and parser.offset == None:
                result = result[:parser.limit]
        

        #on retourne les nom de colonnes sélectionner (cas partiiculier si *) 
        columns_name = []
        if parser.columns_name[0] == "*":
            columns_name = self.get_all_column_name()
        else:
            columns_name = parser.columns_name
        #On retourne les données récupérer avec la condition, bien formaté pour le résultat en json
        data = []
        for line in result:
            dataTmp = []
            for col in line:
                dataTmp.append(col["value"])
            data.append(dataTmp)
        resultToSend = json.dumps({"table_name":self.name,"colonnes":columns_name,"data":data})
        resultAPI.sucess("Requête éxécutée avec succès.",resultToSend)  
      
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
                                try :
                                    if self.select_where(row,parser.where):
                                        #la condition est respecter on modifie la colonne
                                        colData["value"] = updateValue
                                except Exception:
                                    resultAPI.syntaxError("Erreur : la condition WHERE n'est pas correcte.")
                                    return
                                
                            else:
                                #On modifie pour toutes les colonnes
                                colData["value"] = updateValue
                            
                        else:
                            resultAPI.syntaxError(f"Erreur : le type de '{colUpdate['value']}' n'est pas le bon.")
                            return
            self.write_updateLine(row)
        resultAPI.create("Les données ont bien été modifiées.")
        
    def delete(self, parser : Parser):
        for line in self.lines:
            if parser.where != None:
                try :
                     if self.select_where(line,parser.where):
                        #la condition est respecter on supprime la ligne
                        self.lines.remove(line)
                        self.write_updateLine(line,delete=True)
                except Exception:
                    resultAPI.syntaxError("Erreur : la condition WHERE n'est pas correcte.")
                    return
               
            else:
                #On supprime la ligne
                self.lines.remove(line)
                self.write_updateLine(line,delete=True)
        resultAPI.sucess("Les données sélectionnées ont bien été supprimées.",None)
    def describe(self):
        data = json.dumps({"table_name":self.name,"colonnes":json.dumps(self.columns)})
        resultAPI.sucess("Requête éxécutée avec succès",data)
      
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
            file.seek(1,1) #on passe le flag de DELETE
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
            size_line = len(rowBytes) - 1 #-1 car on va pas écrire sur le flag de delete
            file.write(struct.pack("?",True))
            empty_data = b" " * size_line 
            file.write(empty_data)


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
            resultAPI.syntaxError(f"Erreur : une erreur s'est produite lors de la mise à jour de l'entête de la table. Détails : {e}")


    def encode_row(self,line):
        #Encodage : on écrit en bytes diretement les valeurs, pour le text on ecrit sur TAILLE_MAX_TEXT bytes
        #Encodage : avant chaques lignes encodé on ajoute un flag (type "?") pour delete si la ligne est supprimer où non 
        #Exemple de line reçu : [{'colonne': '_id', 'type': 'SERIAL', 'value': '0'}, {'colonne': 'age', 'type': 'INT', 'value': '6'}]
        rowBytes = b""
        #on ajoute le flag de delete sur false
        rowBytes += struct.pack("?",False)
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
   
    def get_size_of_line(self):
        """
        Retourne la taille en bytes d'une ligne dans le .db
        """
        size = 0
        #on ajoute le flag de delete sur false
        size += 1
        for col in self.columns:
            if col["type"] == "INT":
                size += 4
            elif col["type"] == "FLOAT":
                rsize += 4
            elif col["type"] == "TEXT":
                size += TAILLE_MAX_TEXT
            elif col["type"] == "BOOL":
                size += 1
            elif col["type"] == "SERIAL":
                size += 4
        
        return size

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
                #On check le flag de delete : si sur True on saute la ligne
                flagDelete = struct.unpack("?",file.read(1))[0]
                line = copy.deepcopy(self.columns)
                for col in line:
                    col["value"] = None

                if flagDelete == False: #la ligne n'est pas supprimé
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
                else:
                    #On saute la ligne supprimer 
                    tailleLine = self.get_size_of_line() - 1 #-1 car on a déjà lu le flag
                    file.seek(tailleLine,1)
            file.close()
        except Exception as e:
            resultAPI.syntaxError(f"Erreur : une erreur s'est produite lors de la lecture des données de la table. Détails : {e}")


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
            resultAPI.syntaxError(f"Erreur : le fichier '{self.path}' est mal formaté.")

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
                resultAPI.syntaxError("Erreur : le champ de type TEXT est trop long.")
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
    
    def verify_if_coloumns_exist(self, colName)->bool:
        for col in self.columns:
            if col["colonne"] == colName:
                return True
        return False
    def select_where(self, line, RPN: ShuntingYard)->bool:
        return RPN.condition_respected(line)
    
    def get_all_column_name(self):
        columns_name = []
        for col in self.columns:
            columns_name.append(col["colonne"])
        return columns_name