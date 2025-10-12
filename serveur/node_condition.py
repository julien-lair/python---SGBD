class NodeCondition:
    def __init__(self,parentId,gauche,droite, parent):
        self.operateur = ""
        self.left = None 
        self.right = None 
        self.openCondition = None 
        self.condition = ""
        self.id = None 
        self.parent : NodeCondition = parent
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
        tmp = self.condition
        if len(self.condition) >= 2:
            if self.condition[0] == "(" and self.condition[-1] == ")":
                tmp = self.condition[1:-1]
        if len(tmp.strip().split()) > 3:
            return False
        if self.right:
            self.right.verify_condition()
        if self.left:
            self.left.verify_condition() 
        return True
            