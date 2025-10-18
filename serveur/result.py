class Result:
    
    def __init__(self):
        self.code = None
        self.message = ""
        self.data = None
        self.commande = ""
        self.action = ""    
        self.statut = ""
    
    def setAction(self,action):
        self.action = action
    
    def setCommande(self,commande):
        self.commande = commande

    def syntaxError(self, message):
        self.statut = "error"
        self.code = 400
        self.message = message
        return self.show()

    def unauthorized(self, message):
        self.statut = "error"
        self.code = 401
        self.message = message
        return self.show()

    def notFound(self, message):
        self.statut = "error"
        self.code = 404
        self.message = message
        return self.show()

    def conflitError(self, message):
        self.statut = "error"
        self.code = 409
        self.message = message
        return self.show()

    def sucess(self, message, data):
        self.statut = "sucess"
        self.code = 200
        self.error = False
        self.message = message
        self.data = data

    def create(self, message):
        self.statut = "sucess"
        self.code = 201
        self.error = False
        self.message = message

    def show(self):
        """
        {
            "statut":[succes|error],
            "action":[inser|update|select|create|drop|delete],
            "commande":[commande],
            "code": [code],
            "message": [message],
            "data":[null | [...]]
        }
        """
       
        return(
            {
                "statut":self.statut,
                "action":self.action,
                "commande":self.commande,
                "code": self.code,
                "message": self.message,
                "data":self.data
            }
        )
        
    def reset(self):
        self.__init__()

resultAPI = Result()
