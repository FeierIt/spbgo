import re


class Validator:
    @staticmethod
    def validate_reg_data(name, login, password):
        try:
            return Validator.validate_name(name) and Validator.validate_login(login) \
                   and Validator.validate_password(password)
        except TypeError:
            return False

    @staticmethod
    def validate_auth_data(login, password):
        try:
            return Validator.validate_login(login) and Validator.validate_password(password)
        except TypeError:
            return False

    @staticmethod
    def validate_name(name: str):
        if 2 <= len(name) <= 30:
            if re.search(r'[^а-яё]', name.lower()):
                if re.search(r'[^a-z]', name.lower()):
                    print("bad name")
                    return False
                return True
            return True
        return False

    @staticmethod
    def validate_login(login: str):
        if 3 <= len(login) <= 15:
            if re.search(r'[^a-z0-9]', login.lower()):
                print("bad login")
                return False
            return True
        return False

    @staticmethod
    def validate_password(password: str):
        if 5 <= len(password) <= 20:
            if re.search(r'[a-z]', password.lower()) and re.search(r'[0-9]', password):
                return True
            print("bad password")
            return False
        return False
