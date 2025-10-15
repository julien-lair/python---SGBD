class Result:
    code = None
    error = None
    message = ""

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

    def show(self):
        print({"code": self.code,"error": self.error,"message": self.message})


resultAPI = Result()
