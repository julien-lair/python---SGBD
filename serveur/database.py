from sql_parser import Parser
import os
import struct 
from table import Table



class Database:

    def __init__(self):
        self.databaseDir = os.path.dirname(__file__) +  "/data/"
        self.fileExtension = ".db"
        self.tables = []
        self.load_table()
    def create_table(self, name, columns : list[str], type : list[str]):
        #Vérification si la table existe déjà
        if(os.path.exists(self.databaseDir + name + self.fileExtension)):
           print(f"erreur la table {name} existe déjà")
           return
        

        #Vérification d'un champs "_id" de type SERIAL 
        verificationId = False 
        
        if "_id" in columns:
            if(type[columns.index("_id")] == "SERIAL"):
                verificationId = True 
            else:
                raise ValueError("Le champs _id doit être de type SERIAL, vous pouvez ne pas spécifier _id il sera ajouter automatiquement")

        if verificationId == False: 
            #on ajoute un champ _id au début
            columns.insert(0,"_id")
            type.insert(0,"SERIAL")


        header = self.create_header(name,columns,type)
       
        #On ajoute le tous dans un nouveau .db
        file = open(self.databaseDir + name + self.fileExtension, "wb")
        file.write(header)
        file.close()

        #on ajoute la table à notre mémoire 
        table = Table(self.databaseDir + name + self.fileExtension)
        self.tables.append(table)
    def delete_table(self,name):
        #DROP TABLE name 
        #Vérification si la table éxiste
        if(not(os.path.exists(self.databaseDir + name + self.fileExtension))):
           print(f"erreur la table {name} n'existe pas")
           return
        os.remove(self.databaseDir + name + self.fileExtension)

        #on suppirme la table de notre mémoire 
        for table in self.tables:
            if table.name == name:
                self.tables.remove(table)
                break

    def load_table(self):
        #On récupère toutes les tables et on les stockes dans un array 
        for fileTable in os.scandir(self.databaseDir):
            if fileTable.is_file() and fileTable.name.endswith(self.fileExtension):
                table = Table(self.databaseDir + fileTable.name)
                self.tables.append(table)
                
    
    def execute(self,request):
        print("Je reçoit bien la requete")
        parser = Parser()
        parser.parse(request)
        if parser.action == "CREATE":
            self.create_table(parser.table, parser.columns_name, parser.columns_type)
        elif parser.action == "DROP":
            self.delete_table(parser.table)
        else:
            print("Une erreur")
    
    def create_header(self,name,columns,type):
        """
        L'encodage se fera de la façon suivante : 
        name||column:type|column:type|...||serialColumn:0|...

        return : header_size header 
        """
        header = name + "||"
        
        columnsSerial = []
        for i in range(len(columns)):
            header += f"{columns[i]}:{type[i]}|"

            #on check si il y a des columns type SERIAL 
            if type[i] == "SERIAL":
                columnsSerial.append(columns[i])
        header += "|"

        for elem in columnsSerial:
            header += f"{elem}:0|"
        header += "|"

        #On encode le tous 

        header_bytes = header.encode("utf-8")
        header_size = len(header_bytes)

        #ajoute la taille devant 
        header_final = struct.pack("I",header_size) + header_bytes

        return header_final
