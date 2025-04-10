class role:
    def __init__(self, name: str, level: int, description: str):
        self.name = name
        self.level = level
        self.description = description


class user_role:
    def __init__(self, roles_list: list[type[role]], role_index: int):
        if role_index > (len(roles_list) + 1):
            raise ValueError('Invalid Index for Role')
        roleObj = roles_list[role_index]
        self.name = roleObj.name
        self.desc = roleObj.description
        self.level = roleObj.level

    def getName(self):
        return self.name


class user:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def setPassword(self, pwd):
        if len(pwd) > 5:
            self.password = pwd
        else:
            return False
    
    def setRole(self, user_role: type[user_role]):
        self.role = user_role

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
