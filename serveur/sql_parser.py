class Parser:

    def parse(self,string):
        print("ok je vais parser")
        
        self.action = "CREATE"
        self.table = "users"
        self.columns_name = ["age","nom","fr","taille"]
        self.columns_type = ["INT","TEXT","BOOL","FLOAT"]
