class user:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def setPassword(self, pwd):
        if len(pwd) > 5:
            self.password = pwd
        else:
            return False
    
    def setLogged_in(self, val, date):
        self.logged_in = val
        self.logged_in_date = date

    
    
class user_log:
    def __init__(self, type, user_name, date):
        self.type = type
        self.user_name = user_name
        self.date = date
        self.content = ''

    def setContent(self, content):
        self.content = content
