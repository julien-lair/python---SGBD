from sql_parser import Parser
import os
import struct 

class Database:

    def __init__(self):
        self.databaseDir = os.path.dirname(__file__) +  "/data/"

    def create_table(self, name, columns : list[str], type : list[str]):
        #Vérification si la table existe déjà
        if(os.path.exists(self.databaseDir + name)):
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
        print("mon header à été créer")
        print(header.hex())
    
    def delete_table(self,name):
        print("")
    
    def get_table(self):
        print("")
    
    def execute(self,request):
        print("Je reçoit bien la requete")
        parser = Parser()
        parser.parse(request)
        if parser.action == "CREATE":
            self.create_table(parser.table, parser.columns_name, parser.columns_type)
        else:
            print("Une erreur")
    
    def create_header(self,name,columns,type):
        """
        L'encodage se fera de la façon suivante : 
        name||column:type|column:type|...||SERIAL_columns:0|...

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
            header += f"SERIAL_{elem}:0|"
        header += "|"

        #On encode le tous 

        header_bytes = header.encode("utf-8")
        header_size = len(header_bytes)

        #ajoute la taille devant 
        header_final = struct.pack("I",header_size) + header_bytes

        return header_final

