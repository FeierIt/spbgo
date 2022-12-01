from validation import Validator
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from db_interaction import DBInteractor
from results import User


SECRET_KEY = "15c8607c67fd93f103b789e85d263f059fa30aa612ffb66d5199685a894b496e"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Result:
    def __init__(self, success: bool, token=None, message="200"):
        self.success = success
        self.token = token
        self.message = message


class UserInteractor:

    @staticmethod
    def register(name: str, login: str, password: str):
        if Validator.validate_reg_data(name, login, password):
            hash_pwd = str(pwd_context.hash(password))
            new_user = User(login, hash_pwd, name)
            if DBInteractor.insert_user(new_user):
                return Result(True)
            return Result(False, message="Username is already taken!")
        return Result(False, message="Invalid data!")

    @staticmethod
    def authorize(login: str, password: str):
        if Validator.validate_auth_data(login, password):
            user = User(login, pwd=password)
            data = DBInteractor.select_user(user)
            if data is None:
                return Result(False, message="There is no user with such login!")
            if pwd_context.verify(password, data[1]):
                return Result(True, UserInteractor.create_token(str(data[0])))
            return Result(False, message="Wrong password!")
        return Result(False, message="Invalid data!")

    @staticmethod
    def authorized_request(token: str):
        idf = UserInteractor.get_id_by_token(token)
        if idf is None:
            return None
        return DBInteractor.find_by_id(idf)

    @staticmethod
    def create_token(idf: str):
        encoded_jwt = jwt.encode({"sub": idf}, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def get_id_by_token(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            idf: str = payload.get("sub")
            if idf is None:
                return None
            return idf
        except JWTError as err:
            print("JWTError: ", err)
            return None
