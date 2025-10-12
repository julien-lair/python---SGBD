class NodeCondition:
    def __init__(self,parentId,gauche,droite, parent):
        self.operateur = ""
        self.left = None 
        self.right = None 
        self.openCondition = None 
        self.condition = ""
        self.id = None 
        self.parent : NodeCondition = parent
        self.resultCondition = None # servira lors du test des conditions : True False
        if gauche:
            self.id = parentId + 1
        if droite:
            self.id = parentId + 2    
        if parent == None:
            #c'est le noeud chef 
            self.id = 0
    def new_child_left(self):
        self.left = NodeCondition(self.id,True,False,self)
    def new_child_right(self):
        self.right = NodeCondition(self.id,False,True,self)
    
    def draw(self, profondeur=0):
        espace = "  " * profondeur*2
        print(f"{espace}Noeud ({self.id}):")
        print(f"{espace}  opérateur: {self.operateur}")
        print(f"{espace}  condition: {self.condition}")
        
        print()
        
        if self.left:
            self.left.draw(profondeur + 1)
        if self.right:
            self.right.draw(profondeur + 1)
    
    def child_left_free(self)->bool:
        return self.left == None
    def child_right_free(self)->bool:
        return self.right == None
    def verify_condition(self)->bool:
        #pour éviter une entré utiisateur comme la suivante : WHERE a =a limit 3; 
        #où limit serait une erreur 
        #ou encore ex: WHERE a=b b=c (sans opérateur (AND OR NOT))
        #on vérifie pour chaque condition que il y a 3 élement (sans les parenthèse) ex: a <= b   ou   ( a <= b )

        if self.right:
            return self.right.verify_condition()
        if self.left:
            return self.left.verify_condition() 

        tmp = self.condition
        
        if len(self.condition) >= 2:
            if self.condition[0] == "(" and self.condition[-1] == ")":
                tmp = self.condition[1:-1]

        #on fait l'équivalent de la fonction split mais pour ajouter le fait que : "str avec des espace" soit considérer comme 1 champs

        parts = []
        quoteOppen = False
        strToAdd = ""
        typeQuote = ""
        for i in tmp.strip():
            if i in "'" or i in '"' and quoteOppen == False: #début chaine de carcateres entre "" 
                quoteOppen = True 
                strToAdd = i
                typeQuote = i
            elif i in typeQuote and quoteOppen:  # find e la chaine de caracteres
                quoteOppen = False
                strToAdd += i
            elif i == " " and quoteOppen == False:
                parts.append(strToAdd)
                strToAdd = ""
            else:
                strToAdd += i

        if strToAdd != "":
            parts.append(strToAdd)

        if len(parts) > 3:
            return False
        else: 
            return True
        
        
            