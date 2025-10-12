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
    def new_child(self):
        self.left = NodeCondition(self.id,True,False,self)
        self.right = NodeCondition(self.id,False,True,self)
    def drawing(self):
        print(f"Noeud : operateur {self.operateur}, open ? {self.openCondition}, condition {self.condition}")
        if self.left != None and self.right != None:
            self.left.drawing()
            self.right.drawing