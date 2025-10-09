class Parser:

    def parse(self,string):
       
        
        self.action = "CREATE"
        self.table = "users"
        self.columns_name = ["age","nom","fr","taille"]
        self.columns_type = ["INT","TEXT","BOOL","FLOAT"]
         
        """
        self.action = "DROP"
        self.table = "users"
        """