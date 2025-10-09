import struct

class Table:
    def __init__(self,path):
        self.path = path
        self.name = ""
        self.columns = []
        self.serialColumns = []
        self.header_decoder()
        self.describe()
        
    def insert(self,columns, values):
        print("")
    
    def select(self,columns, conditions,order,limit,offset):
        print("")
    
    def update(self,conditions,values):
        print("")
    
    def delete(self, condition):
        print("")
    
    def describe(self):
        print(f"Nom de la table : {self.name}\n")

        print("Colonnes :")
        for col in self.columns:
            for nom, typ in col.items():
                print(f"  - {nom} ({typ})")

        if self.serialColumns:
            print("\nColonnes de type SERIAL :")
            for serial in self.serialColumns:
                for nom, compteur in serial.items():
                    print(f"  - {nom} (compteur = {compteur})")
        else:
            print("\nAucune colonne de type SERIAL.")

    def read_content(self):
        print("")

    def write_content(self):
        print("")
    def header_decoder(self):
        file = open(self.path,"rb")
        headerSizeBytes = file.read(4)
        if not headerSizeBytes:
            raise ValueError("Le fichier est vide ou mal formaté")
        headerSize = struct.unpack("I",headerSizeBytes)[0]
        
        headerBytes = file.read(headerSize)
        file.close()
        
        headerStr = headerBytes.decode("utf-8")

        #On parse le header
        #Rapelle de son format :  name||column:type|column:type|...||serialColumn:0|...
        headerParse = headerStr.split("||")
        self.name = headerParse[0]
        
        for value in headerParse[1].split("|"):
            column,type = value.split(":")
            self.columns.append({column:type})
        
        for value in headerParse[2].split("|"):
            serialColumn,compteur = value.split(":")
            self.serialColumns.append({serialColumn:compteur})
        