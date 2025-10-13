from sql_parser import Parser
import os
import struct 
from table import Table
from typing import List


class Database:

    def __init__(self):
        self.databaseDir = os.path.dirname(__file__) +  "/data/"
        self.fileExtension = ".db"
        self.tables: List[Table] = []
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
                print("Le champs _id doit être de type SERIAL, vous pouvez ne pas spécifier _id il sera ajouter automatiquement")
                return 
            
        if verificationId == False: 
            #on ajoute un champ _id au début
            columns.insert(0,"_id")
            type.insert(0,"SERIAL")


        header = self.create_header(name,columns,type)

        #On ajoute dans un nouveau .db
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
        try:
            for fileTable in os.scandir(self.databaseDir):
                if fileTable.is_file() and fileTable.name.endswith(self.fileExtension):
                    table = Table(self.databaseDir + fileTable.name)
                    self.tables.append(table)
        except FileNotFoundError:
            #il éxiste aucune table (lors du lancement du projet)
            return
                
    
    def execute(self,request):
        parser = Parser()
        parser.parse(request)
        if parser.expressionValide:
            if parser.action == "CREATE":
                self.create_table(parser.table, parser.columns_name, parser.columns_type)
            elif parser.action == "DROP":
                self.delete_table(parser.table)
            elif parser.action == "INSERT":
                self.insert_table(parser)
            elif parser.action == "DESCRIBE":
                self.describe_table(parser)
            elif parser.action == "SELECT":
                self.select_table(parser)
            elif parser.action == "UPDATE":
                self.update_table(parser)
            else:
                print("Une erreur")
    
    def create_header(self,name,columns,type):
        """
        L'encodage se fera de la façon suivante : 
        [size_name]name[number_col][size_colX]colX[encode_type_colX][number_serial][size_colSerialX]colSerialX[valeur_serial]

        encode_type_colX : 
        "INT"     1
        "FLOAT"   2
        "TEXT"    3
        "BOOL"    4
        "SERIAL"  5

        return : header_size header 
        """
        header_bytes = b""

        name_encode = name.encode("utf-8")
        header_bytes += struct.pack("I",int(len(name_encode))) + name_encode

        nombreColonne = len(columns)
        header_bytes += struct.pack("I",int(nombreColonne))

        serial_col = []
        for col in columns:
            col_encode = col.encode("utf-8")
            header_bytes += struct.pack("I", int(len(col_encode))) + col_encode

            type_col = type[columns.index(col)]
            if type_col == "INT":
                header_bytes += struct.pack("I", int(1))
            elif type_col == "FLOAT":
                header_bytes += struct.pack("I", int(2))
            elif type_col == "TEXT":
                header_bytes += struct.pack("I", int(3))
            elif type_col == "BOOL":
                header_bytes += struct.pack("I", int(4))
            elif type_col == "SERIAL":
                serial_col.append(col)
                header_bytes += struct.pack("I", int(5))
        
        
        header_bytes += struct.pack("I",int(len(serial_col)))
        for col in serial_col:
            col_encode = col.encode("utf-8")
            header_bytes += struct.pack("I",int(len(col_encode))) + col_encode + struct.pack("I",int(0))

        return header_bytes
        
    
    def insert_table(self,parser : Parser):
        if parser.action == "INSERT":
            for table in self.tables:
                if table.name == parser.table:
                    table.insert(parser)
                    return 
            print("Erreur : la table est inconnue")
    
    def describe_table(self,parser : Parser):
        if parser.action == "DESCRIBE":
            for table in self.tables:
                if table.name == parser.table:
                    table.describe()
                    return 
            print("Erreur : la table est inconnue")
    
    def select_table(self,parser : Parser):
        if parser.action == "SELECT":
            for table in self.tables:
                if table.name == parser.table:
                    table.select(parser)
                    return 
            print("Erreur : la table est inconnue")

    def update_table(self,parser : Parser):
        if parser.action == "UPDATE":
            for table in self.tables:
                if table.name == parser.table:
                    table.update(parser)
                    return 
            print("Erreur : la table est inconnue")