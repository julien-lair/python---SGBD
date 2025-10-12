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
    
    """def draw(self, prefix="", is_left=None):
       
        # Symbole pour la connexion
        if is_left is None:
            connector = ""
            branch = ""
        elif is_left:
            connector = "├── "
            branch = "│   "
        else:
            connector = "└── "
            branch = "    "
        
        # Affichage du noeud actuel
        print(f"{prefix}{connector}Noeud [{self.id}]")
        
        # Informations du noeud
        info_prefix = prefix + (branch if is_left is not None else "")
        
        if self.operateur:
            print(f"{info_prefix}    Opérateur: {self.operateur}")
        if self.condition:
            print(f"{info_prefix}    Condition: {self.condition}")
        
        # Affichage récursif des enfants
        if self.left is not None or self.right is not None:
            if self.left is not None:
                self.left.draw(info_prefix, True)
            else:
                print(f"{info_prefix}├── [Gauche: vide]")
            
            if self.right is not None:
                self.right.draw(info_prefix, False)
            else:
                print(f"{info_prefix}└── [Droite: vide]")
    """
    def child_left_free(self)->bool:
        return self.left == None
    def child_right_free(self)->bool:
        return self.right == None