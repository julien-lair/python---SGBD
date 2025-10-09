import re

class Parser:
    def __init__(self):
        self.expressionValide = False
        self.action = ""
        self.table = ""
        self.columns_name = []
        self.columns_type = []

    def parse(self,string):
       
        """
        CREATE TABLE users (id SERIAL, firstname TEXT, age INT, salary FLOAT, disabled BOOL);
        
        DROP TABLE users;
        """
        
        
        if string[-1] != ";":
            print("L'expréssion doit finir par un ;")
            self.expressionValide = False
            return
        

        stringElement = string[:-1].split() #on supprime le ;
        #On regarde l'action 
        action = stringElement[0]
        if action == "CREATE":
            self.create(stringElement)
        elif action == "DROP":
            self.drop(stringElement)
        else:
            print(f"{action} n'est pas reconnue")
            self.expressionValide = False

    def create(self, expression):
        self.action = "CREATE"
    
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

    def verify_table_name(self,name)->bool:
         if not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", name):
            print(f"Erreur : nom de table '{name}' invalide. Il doit commencer par une lettre et ne contenir que des caractères alphanumériques ou '_'.")
            return False
         return True
         