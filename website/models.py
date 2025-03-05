class user:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def setPassword(self, pwd):
        if len(pwd) > 5:
            self.password = pwd
        else:
            return False
    