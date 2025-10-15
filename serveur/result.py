class Result:
    code = None
    error = None
    message = ""
    data = None

    def syntaxError(self, message):
        self.code = 400
        self.error = True
        self.message = message
        return self.show()

    def unauthorized(self, message):
        self.code = 401
        self.error = True
        self.message = message
        return self.show()

    def notFound(self, message):
        self.code = 404
        self.error = True
        self.message = message
        return self.show()

    def conflitError(self, message):
        self.code = 409
        self.error = True
        self.message = message
        return self.show()

    def sucess(self,message="",data = None):
        self.code = 200
        self.error = False
        self.message = message
        self.data = data

    def create(self,message):
        self.code = 201
        self.error = False
        self.message = message

    def show(self):
        if self.error:
            return({"statut":"error", "code": self.code,"message": self.message})
        else:
            return({"statut":"sucess", "code": self.code,"message": self.message,"data":self.data})
        
    def reset(self):
        self.code = None
        self.error = None
        self.message = None
        self.data = None
resultAPI = Result()
