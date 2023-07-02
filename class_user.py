# Written by Shaked Bitan
# user class
class User:
    def __init__(self, username, password, manager=0):
        # user attributes
        self.__username = username
        self.__password = password
        self.__manager = manager


    def get_username(self):
        return self.__username

    def make_manager(self):
        self.__manager = 1

    def set_username(self, username):
        self.__username = username

    def set_password(self, password):
        self.__password = password


#class Manager(User):
 #   def create_pattern(self):

