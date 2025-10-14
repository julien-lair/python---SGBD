class ShuntingYard:
    def __init__(self,string):
        self.RPN = self.RPN_builder(string)

    def separateur(self, string):
        result = []
        tmp = ""
        guillementOuvert = False

        for elem in string:
            if elem in ['"', "'"]:
                if guillementOuvert == True:
                    guillementOuvert = False 
                else:
                    guillementOuvert = True
                tmp += elem
            elif elem in "()":
                #si ouvre parenthèse on ajoute le tmp puis la parenthèse
                result.append(tmp.strip())
                tmp = ""
                result.append(elem)
            elif elem == " " and guillementOuvert == False:
                #si il y a un espace et on est pas dans une chaine de carcatere "du text par exemple"
                result.append(tmp.strip())
                tmp = ""
            else:
                tmp += elem

        result.append(tmp.strip()) #si l'expréssion ne fini pas par ) on ajoute la fin 
        return result

    def RPN_builder(self,string) :
        #on transforme une expréssion logique (WHERE name = "julien" OR xxx AND (xxxx OR xxx )) en RPN 
        # algo : shunting yard 
        formated_data = self.separateur(string)
        RPN = []
        pile = []
        
        for elem in formated_data:

            # SI c'est AND ou OR
            if elem.strip().upper() == "AND":
                while len(pile) > 0 and pile[-1] == "AND": #si deja un AND dans la pile alors on l'écrit dans notre RPN 
                    RPN.append(pile.pop())
                pile.append("AND")
            elif elem.strip().upper() == "OR":
                while len(pile) > 0 and (pile[-1] == "OR" or pile[-1] == "AND"): #si dejà un opérateur dans la pile et on en ajoute un, plus le AND est prioritaire sur le OR
                    RPN.append(pile.pop())
                pile.append("OR")

            #Si une parenthèse s'ouvre on ajoute à la pile
            elif elem == "(":
                pile.append(elem)

            #si parenthèse se ferme on ajoute les dernier 
            elif elem == ")":
                while pile and pile[-1] != "(": #tant qu'on reevient pas à l'ouverture de la parenthèse on ajoute les opérateur
                    RPN.append(pile.pop())
                pile.pop()  # on supprime (

            #si on est sur une condition classique exemple : user="Julien" on ajoute
            else:
                RPN.append(elem)

        # On a fini, on ajoute toutes la pile dans le retour
        while pile:
            RPN.append(pile.pop())
        
        #On supprime toutes les valeurs vide 
        RPN_without_empty = []
        for i in RPN:
            if i != '':
                RPN_without_empty.append(i)

        return RPN_without_empty

    def condition_respected(self,line) -> bool:
        """
        Algo : parcour RPN de gauche à droite
        Si condition -> sur la pile
        Si opérateur -> applique sur la pile 
        """

        pile = []
        for elem in self.RPN:
            if elem == "AND":
                value1 = pile.pop()
                value2 = pile.pop()
                pile.append(value1 and value2)
            elif elem == "OR":
                value1 = pile.pop()
                value2 = pile.pop()
                pile.append(value1 or value2)
            else:
                #condition
                col,val,condition = self.separateur_condition(elem)
                for colonne in line:
                    if colonne["colonne"] == col:
                        #on regarde si la valeur repsecte la condition
                        if condition == "<=":
                            pile.append(self.string_to_type(colonne["value"],colonne["type"]) <= self.string_to_type(val,colonne["type"]))
                        elif condition == ">=":
                            pile.append(self.string_to_type(colonne["value"],colonne["type"]) >= self.string_to_type(val,colonne["type"]))
                        elif condition == "<":
                            pile.append(self.string_to_type(colonne["value"],colonne["type"]) < self.string_to_type(val,colonne["type"]))
                        elif condition == ">":
                            pile.append(self.string_to_type(colonne["value"],colonne["type"]) > self.string_to_type(val,colonne["type"]))
                        elif condition == "!=":
                            pile.append(self.string_to_type(colonne["value"],colonne["type"]) != self.string_to_type(val,colonne["type"]))
                        elif condition == "=":
                            pile.append(self.string_to_type(colonne["value"],colonne["type"]) == self.string_to_type(val,colonne["type"]))
        return pile[0]
    
    def separateur_condition(self,condition):
        #on retourne : la colonne  /    la valeur   /   le separateur(signe)
        signes = ["<=",">=","<",">","!=","="]
        for signe in signes:
            if signe in condition:
                if len(condition.strip().split(signe)) > 2:
                    #deux fois le caratere signe dans la condition (peut etre de type text), on retourne d'abord pour [0] puis pour [1 -> n]
                    value = ""
                    first = True
                    for i in range(len(condition.strip().split(signe))):
                        if first == True:
                            first = False #pour sauter la première occurence (c'est le nom de la colonne)
                        else:
                            value += condition.strip().split(signe)[i] + signe
                    #on supprime le dernier signe ajouter juste au dessus 
                    return condition.strip().split(signe)[0],value[:-len(signe)],signe
                return condition.strip().split(signe)[0],condition.strip().split(signe)[1],signe
        
    def string_to_type(self,value,type):
        if type == "INT":
            return int(value)
        elif type == "FLOAT":
            return float(value)
        elif type == "TEXT":
            if value[0] == value[-1] and value[0] in ["'",'"']:
                return str(value[1:-1]) #On suppirme les "" du text
            else:
                return str(value)
        elif type == "BOOL":
            try:
                if value.upper() == "TRUE":
                    return True
                elif value.upper() == "FALSE":
                    return False
            except AttributeError:
                return value
        elif type == "SERIAL":
            return int(value)