# written by Shaked Bitan
# user interface using tkinter
import sys
import pyttsx3
import pickle
import numpy
import ast
import tk
from tkinter import *
from client import Client
from tkinter import messagebox
from class_user import User
from class_pattern import Pattern
from tkinter import filedialog
from PIL  import Image, ImageTk
import datetime as dt
import time
from datetime import datetime
import bcrypt
from tkinter import ttk
import io


PORT = 2800
IP = "172.20.10.2"
COUNT_DICT = {"ch": 0, "dec": 1, "inc": 2, "sc": 1, "dc": 1, "hdc": 1, "tr": 1, "sk": 0, "invdec": 1, "slst": 0, "FLO": 1, "BLO":1}
   
# pictures
logo = r"c:\logo.png"

client = Client(IP, PORT)

my_user = User("0", "0")


def create_scroll_bar(root):
    # create a Canvas widget with a scrollbar
    canvas = tk.Canvas(root, bg="#FFDEE3")
    scrollbar = tk.Scrollbar(root, command=canvas.yview, bg="#FFDEE3")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # configure the Canvas to scroll with the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    return canvas


def font_method(root, friendly_mode):
    """add fonts for all the widgets in root"""
    root.option_add("*Font", "ariel")
    # Set the font for the Label widget
    if friendly_mode:
        root.option_add("*Label.Font", "aerial 18 bold")
        root.option_add("*Button.Font", "aerial 18 bold")
        root.option_add("*Entry.Font", "aerial 18 bold")
        root.option_add("*OptionMenu.Font", "aerial 18 bold")
        root.option_add("*Checkbutton.Font", "aerial 18 bold")
    else:
        root.option_add("*Label.Font", "aerial 12")
        root.option_add("*Button.Font", "aerial 12")
        root.option_add("*Entry.Font", "aerial 12")
        root.option_add("*OptionMenu.Font", "aerial 12")
        root.option_add("*Checkbutton.Font", "aerial 12")
    # define the backround color for all the widgets
    root.option_add("*Background", "#F098A2")


def display_pattern(username, pattern_name, fm):
    # check if pattern was started
    client.send_message("6"+username+" "+pattern_name)
    while True:
        if client.pattern_started is not None:
            # get pattern from database
            pattern = get_pattern_from_database(pattern_name)
            if client.pattern_started is True:
                # call display functions
                client.pattern_started = None
                # get how many rounds were done
                rounds_done = get_rounds_done(username, pattern_name)
                DisplayPattern(pattern, rounds_done, username, friendly_mode=fm)
                break
            else:
                client.pattern_started = None
                # it is the first time-display from the beginning
                DisplayPattern(pattern, 0, username, friendly_mode=fm)
                break


def get_pattern_from_database(pattern_name):
    """get pattern from db"""
    client.send_message("8"+pattern_name)
    while True:
        if client.pattern:
            pattern = pickle.loads(client.pattern)
            client.pattern = None
            return pattern


def get_rounds_done(username, pattern_name):
    """get how many rounds were done in user’s pattern"""
    client.send_message("9"+username+" "+pattern_name)
    while True:
        if client.rounds_done is not None:
            rounds_done = client.rounds_done
            client.rounds_done = None
            return rounds_done


def handle_pattern_leave(pattern_name, username, rounds_done, s_time):
    """save rounds done, return 1 if scusseful """
    client.send_message("6" + username + " " + pattern_name)
    current_date = dt.date.today().strftime("%Y-%m-%d")
    while True:
        if client.pattern_started is not None:
            # find out if pattern was already started
            if client.pattern_started is True:
                # pattern was started, send message to update db
                client.pattern_started = None
                # we need to update the rounds done and date and time
                client.send_message("7.1" + username + " " + str(rounds_done) + " " + current_date+" "+str(s_time) + " " + pattern_name)
                break
            else:
                client.pattern_started = None
                # it is the first time-create new round in patterns in progress in db
                client.send_message("7.0" + username + " " + str(rounds_done) + " " + current_date+" "+str(s_time)+" "+pattern_name)
                break
    while True:
        # wait for server to say we can exit.
        if client.pattern_updated is not None:
            if client.pattern_updated:
                # we updated pattern in db, we can exit
                client.pattern_started = None
                client.pattern_updated = None
                return 1
            else:
                # an error occurred
                client.pattern_started = None
                client.pattern_updated = None
                messagebox.showerror("Error", "Sorry, please try to exit later")
                return 0


def handle_pattern_quit(pattern_name, username, rounds_done, s_time):
    """close connection and save rounds done"""
    code = handle_pattern_leave(pattern_name, username, rounds_done, s_time)
    if code == 1:
        client.close_socket()
    else:
        messagebox.showerror("Error", "Sorry, please try to exit later")


class OpenScreen(tk.Toplevel):
    def __init__(self, master=None, friendly_mode=False):
        super().__init__(master)
        self.geometry("1000x2000")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)
        self.configure(background="#FFDEE3")

        # add image file
        self.lg = PhotoImage(file=logo)
        self.lg = self.lg.subsample(2, 2)  # (x, y)

        self.imgrefs = []
        self.pattern_names = []

        self.fm = friendly_mode
        # Add fonts for all the widgets
        font_method(self, self.fm)

        self.frame1 = Frame(self, width=1000, height=200, bg="#FFDEE3")
        self.frame1.place(x=0, y=0)
        # Add image label
        self.label2 = Label(self.frame1, image=self.lg)
        self.label2.pack(side=RIGHT, padx=50)
        if self.fm:
            self.button1 = Button(self.frame1, text="Regular mode", command=self.regular_mode_open_screen,bg="#F098A2")
            self.button1.pack(side=LEFT, padx=5)
        else:
            self.button1 = Button(self.frame1, text="Friendly mode", command=self.friendly_mode_open_screen, bg="#F098A2")
            self.button1.pack(side=LEFT, padx=5)

        self.button2 = Button(self.frame1, text="Log in", command=self.change_to_log_in_screen, bg="#F098A2")
        self.button2.pack(side=LEFT, padx=5)

        self.button3 = Button(self.frame1, text="Sign up", command=self.change_to_sign_up_screen, bg="#F098A2")
        self.button3.pack(side=LEFT,padx=5)

        self.button4 = Button(self.frame1, text="search pattern", command=self.change_to_display_pattern_screen, bg="#F098A2")
        self.button4.pack(side=LEFT,padx=5)
        # creating the buttons of the patterns
        # HERE
        self.patterns_buttons()

    def friendly_mode_open_screen(self):
        """calls openscreen again but display with friendly mode"""
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        self.fm = True
        OpenScreen(self, friendly_mode=self.fm)

    def regular_mode_open_screen(self):
        """calls openscreen again with regular mode"""
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        self.fm = False
        OpenScreen(self, friendly_mode=self.fm)

    def change_to_sign_up_screen(self):
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        SignUpScreen(self, friendly_mode=self.fm)

    def change_to_log_in_screen(self):
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        LogInScreen(self, friendly_mode=self.fm)

    def change_to_display_pattern_screen(self):
        """user can’t start pattern in open screen-prints an error message"""
        messagebox.showerror("Error", "please log in before using the system")

    def patterns_buttons(self):
        """display all buttons of patterns"""
        self.frame = Frame(self, width=600, height=200, bg="#FFDEE3")
        self.frame.place(x=20, y=300)
        i = 1
        try:
            while i < 4:
                client.send_message("5")
                while True:
                    try:
                        if client.pattern is not None:
                            # load pattern from server
                            pattern = pickle.loads(client.pattern)

                            if pattern.pattern_name in self.pattern_names:
                                # make sure pattern is not displayed twice
                                break
                            # open image
                            img = Image.open(io.BytesIO(pattern.pictures[0]))
                            # trim image
                            img.thumbnail((250, 250))
                            # get image ready for display
                            photo = ImageTk.PhotoImage(img)
                            # save image info
                            self.imgrefs.append(photo)
                            self.pattern_names.append(pattern.pattern_name)
                            # display image and text on button
                            button_side = RIGHT
                            if i == 1:
                                button_side = LEFT
                            button = Button(self.frame, image=photo, text=pattern.pattern_name + "\n" + "Uploaded By: " + pattern.username, compound=TOP, bg="#FFDEE3", command=self.change_to_display_pattern_screen)
                            button.pack(side=button_side, padx=10)
                            # image was displayed hence we can increase i var
                            i += 1
                            break
                    except Exception as e:
                        print(e)
                        break
                    finally:
                        # no matter what we initiate this var
                        client.pattern = None
                        time.sleep(0.01)  # Add a delay of 1 second before sending the next message

        except Exception as e:
            print(e)


class SignUpScreen(tk.Toplevel):
    def __init__(self, master=None, friendly_mode=False):
        super().__init__(master)
        # Basic settings
        self.geometry("1000x2000")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)
        self.configure(background="#FFDEE3")

        self.fm = friendly_mode
        font_method(self, self.fm)

        # widgets for later
        self.label5 = None

        self.frame = Frame(self, width=600, height=200, bg="#FFDEE3")
        self.frame.place(x=0, y=0)
        self.frame1 = Frame(self.frame, width=200, height=200, bg="#FFDEE3")
        self.frame1.pack(side=LEFT)
        self.frame2 = Frame(self.frame, width=200, height=200, bg="#FFDEE3")
        self.frame2.pack(side=LEFT)

        # Create labels
        self.label2 = Label(self.frame1, text="username", bg="#FFDEE3")
        self.label2.pack(side=TOP)
        self.label3 = Label(self.frame1, text="email", bg="#FFDEE3")
        self.label3.pack(side=TOP)
        self.label4 = Label(self.frame1, text="password", bg="#FFDEE3")
        self.label4.pack(side=TOP)

        # Entry vars
        self.username = tk.StringVar()
        self.gmail = tk.StringVar()
        self.password = tk.StringVar()

        self.entry1 = Entry(self.frame2, textvariable=self.username)
        self.entry1.pack(side=TOP, pady=5)
        self.entry2 = Entry(self.frame2, textvariable=self.gmail)
        self.entry2.pack(side=TOP, pady=5)
        self.entry3 = Entry(self.frame2, textvariable=self.password)
        self.entry3.pack(side=TOP)

        # Add buttons
        self.button1 = Button(self, text="submit", command=self.process_information, bg="#FFB6C1")
        self.button1.place(x=30, y=200)
        self.button2 = Button(self, text="go back", command=self.change_to_open_screen, bg="#FFB6C1")
        self.button2.place(x=600, y=30)

    def process_information(self):
        # get information from vars
        username = self.username.get()
        gmail = self.gmail.get()
        password = self.password.get()
        if username == "" or password == "" or gmail == "":
            # make sure users filled all fields
            messagebox.showerror("Error", "Please fill out all entries")
            self.username.set("")
            self.gmail.set("")
            self.password.set("")
        else:
            # encrypt password:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            # send info to server
            user_info = "1" + str(username) + " " + str(gmail) + " " + str(hashed_password)+" "+str(salt)
            client.send_message(user_info)
            # wait for response from client
            self.response_for_sign_up()

    def response_for_sign_up(self):
        while client.code != 1.0 and client != 1.1:
            # wait for client.code to change
            if client.code == 1.0:
                # username exists, tell it to user
                self.username.set("")
                self.gmail.set("")
                self.password.set("")
                client.code = None
                messagebox.showerror("Error", "username already exists")
                self.withdraw()
                SignUpScreen(self, friendly_mode=self.fm)
                break

            elif client.code == 1.1:
                # username is fine, let user know he created his account
                self.username.set("")
                self.gmail.set("")
                self.password.set("")
                client.code = None
                messagebox.showinfo("Great", "your account has been created, log in now")
                self.withdraw()
                OpenScreen(self, friendly_mode=self.fm)
                break

    def change_to_open_screen(self):
        self.withdraw()
        OpenScreen(self, friendly_mode=self.fm)


class LogInScreen(tk.Toplevel):
    def __init__(self, master=None, friendly_mode=False):
        super().__init__(master)
        # Basic settings
        self.protocol("WM_DELETE_WINDOW", client.close_socket)
        self.geometry("1000x2000")
        self.configure(background="#FFDEE3")

        self.fm = friendly_mode
        font_method(self, self.fm)

        self.frame = Frame(self, width=400, height=200, bg="#FFDEE3")
        self.frame.place(x=10,y=10)
        self.frame1 = Frame(self.frame, width=200, height=200, bg="#FFDEE3")
        self.frame1.pack(side=LEFT)
        self.frame2 = Frame(self.frame, width=200, height=200, bg="#FFDEE3")
        self.frame2.pack(side=LEFT)
        # Create labels
        self.label2 = Label(self.frame1, text="username", bg="#FFDEE3")
        self.label2.pack(side=TOP)
        self.label3 = Label(self.frame1, text="password", bg="#FFDEE3")
        self.label3.pack(side=TOP)

        # Entry vars
        self.password = StringVar()
        self.username = StringVar()

        # Create entries
        self.entry1 = Entry(self.frame2, textvariable=self.username)
        self.entry1.pack(side=TOP, pady=5)
        self.entry2 = Entry(self.frame2, textvariable=self.password)
        self.entry2.pack(side=TOP)

        # Create buttons
        self.button1 = Button(self, text="log in", command=self.log_in, bg="#FFB6C1")
        self.button1.place(x=30, y=200)
        self.button2 = Button(self, text="go back", command=self.change_to_open_screen, bg="#FFB6C1")
        self.button2.place(x=600, y=30)

    def change_to_open_screen(self):
        self.withdraw()
        OpenScreen(self, friendly_mode=self.fm)

    def log_in(self):
        """send info to socket and see if user exists
        store info in local variables so that they will stay stringvar type to get more info"""
        username = self.username.get()
        password = self.password.get()
        if username == "" or password == "":
            # make sure all fields were filled
            messagebox.showerror("Error", "Please fill out all entries")
            # reset variables so user can type again
            self.username.set("")
            self.password.set("")
        else:
            # send user info to server
            user_login = "2" + str(username)
            client.send_message(user_login)
            self.username.set("")
            self.password.set("")
            self.response_log_in(username, password)

    def response_log_in(self, username, password):
        while True:
            if client.password is not None:
                if client.password == "0":
                    # username does not exist in db
                    messagebox.showerror("Error", "Username does not exist")
                    self.username.set("")
                    self.password.set("")
                    break
                is_password_correct = self.verify_password(password, client.password, client.salt)
                if is_password_correct == 0:
                    # the password was incorrect
                    self.username.set("")
                    self.password.set("")
                    messagebox.showerror("Sorry", "Your password is incorrect")
                    break
                else:
                    # password is correct!
                    messagebox.showinfo("WELCOME", "You are logged in now, Welcome "+str(username))
                    # save these variables for later activities
                    client.username = username
                    my_user.set_username(username)
                    client.password = None
                    client.salt = None
                    self.withdraw()
                    LoggedInScreen(self, friendly_mode=self.fm)
                    break

    def verify_password(self, password, hashed_password, salt):
        """hash the entered password with the database salt"""
        salt = ast.literal_eval(salt)  # turn the string of bytes salt into bytes salt
        entered_password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        # compare the hashed entered password against the stored hashed password
        return str(entered_password_hash) == hashed_password


class LoggedInScreen(tk.Toplevel):
    def __init__(self, master=None, friendly_mode=False):
        super().__init__(master)
        # basic settings
        self.geometry("1000x2000")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)
        self.configure(background="#FFDEE3")

        self.imgrefs = []
        self.pattern_names = []

        self.fm = friendly_mode
        font_method(self, self.fm)

        # widgets for later
        self.label5 = None

        # check if client has become a manager
        self.check_if_manager(my_user.get_username())

        # update if client is manager
        self.update_manager(my_user.get_username())

        self.frame = Frame(self, width=600, height=200, bg="#FFDEE3")
        self.frame.place(x=0, y=0)
        self.frame2 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame2.pack(side=TOP)
        self.frame3 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame3.pack(side=TOP)
        # Create buttons
        if self.fm:
            self.button1 = Button(self.frame2, text="Regular mode", bg="#F098A2", command=self.regular_mode_button)
            self.button1.pack(side=LEFT, padx=5)
        else:
            self.button1 = Button(self.frame2, text="Friendly mode", bg="#F098A2", command=self.friendly_mode_button)
            self.button1.pack(side=LEFT, padx=5)
        self.button2 = Button(self.frame2, text="Upload pattern", command=self.upload_pattern_button, bg="#F098A2")
        self.button2.pack(side=LEFT, padx=5)
        self.button3 = Button(self.frame2, text="Log out", bg="#F098A2", command=self.log_out_button)
        self.button3.pack(side=LEFT, padx=5)
        self.button4 = Button(self.frame2, text="search pattern", bg="#F098A2", command=self.search_pattern_button)
        self.button4.pack(side=LEFT, padx=5)
        self.button5 = Button(self.frame3, text="my uploads", bg="#F098A2", command=self.my_uploads_button)
        self.button5.pack(side=LEFT, padx=5)
        self.button6 = Button(self.frame3, text="patterns in progress", bg="#F098A2", command=self.patterns_in_progress_button)
        self.button6.pack(side=LEFT, padx=5)
        self.patterns_buttons()
        if client.manager:
            self.button7 = Button(self.frame3, text="manager requests", bg="#F098A2", command=self.manager_requests_button)
            self.button7.pack(side=LEFT, padx=5)
        else:
            self.button7 = Button(self.frame3, text="i want to become a manager", bg="#F098A2", command=lambda: self.become_manager_button(my_user.get_username()))
            self.button7.pack(side=LEFT, padx=5)
        self.label6 = Label(self.frame,bg="#FFDEE3", text="Credits: blog.mohumohu.com, Hooked by robin, Cherilyn Q, repeatcrafterme.com")
        self.label6.pack(side=TOP)

    def search_pattern_button(self):
        """ call search pattern screen"""
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        SearchPatternScreen(self, friendly_mode=self.fm)

    def my_uploads_button(self):
        """check if user is a manager. call my uploads screen"""
        if client.manager:
            self.withdraw()
            self.imgrefs = []
            self.pattern_names = []
            MyUploadsScreen(self, friendly_mode=self.fm)
        else:
            messagebox.showerror("Error", "You are not a manager, you don't have any uploads")

    def friendly_mode_button(self):
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        self.fm = True
        LoggedInScreen(self, friendly_mode=self.fm)

    def regular_mode_button(self):
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        self.fm = False
        LoggedInScreen(self, friendly_mode=self.fm)

    def update_manager(self, username):
        """check if user is manager and update accordingly"""
        client.send_message("3"+str(username))
        while True:
            if client.manager is not None:
                return

    def check_if_manager(self, username):
        """check if user's request to be a manager has been approved or disapproved"""
        client.send_message("&"+str(username))
        while True:
            if client.manager_state is not None:
                if client.manager_state == "3":
                    messagebox.showinfo("Congratulations", "Your request to be a manager has been Approved \n You may upload patterns now")
                elif client.manager_state == "4":
                    messagebox.showinfo("Sorry", "Your request to be a manager has been disapproved. \n Please try again after completing more patterns")
                client.manager_state = None
                break

    def manager_requests_button(self):
        """manager wants to approve new managers. we call the screen that does that"""
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        ApproveManagersScreen(self, friendly_mode=self.fm)

    def become_manager_button(self, username):
        """user wants to become a manager, we change the state ot manager to 2"""
        client.send_message("*"+username)
        while True:
            if client.manager_req is not None:
                if client.manager_req:
                    messagebox.showinfo("Great", "Your request to be a manager was sent")
                client.manager_req = None
                break

    def log_out_button(self):
        """ client wants to log out, return to first screen"""
        client.logged_in = None
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        OpenScreen(self, friendly_mode=self.fm)

    def patterns_in_progress_button(self):
        """client wants to see their patterns in progress, call the screen that does that"""
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        PatternsInProgress(self, friendly_mode=self.fm)

    def upload_pattern_button(self):
        if client.manager:
            # user is a manager and can upload patterns
            self.withdraw()
            self.imgrefs = []
            self.pattern_names = []
            UploadPattern(self, friendly_mode=self.fm)
        else:
            # user is not a manager and therefore can not upload patterns
            messagebox.showerror("Error", "sorry, only managers can upload patterns.")

    def patterns_buttons(self):
        self.frame1 = Frame(self, width=600, height=200, bg="#FFDEE3")
        self.frame1.place(x=20, y=300)
        i = 1
        while i < 4:
            client.send_message("5")
            while True:
                try:
                    if client.pattern is not None:
                        # load pattern from server
                        pattern = pickle.loads(client.pattern)

                        if pattern.pattern_name in self.pattern_names:
                            # make sure pattern is not displayed twice
                            break

                        self.pattern_names.append(pattern.pattern_name)

                        # open image
                        img = Image.open(io.BytesIO(pattern.pictures[0]))
                        # trim image
                        img.thumbnail((250, 250))
                        # get image ready for display
                        photo = ImageTk.PhotoImage(img)
                        # save image info
                        self.imgrefs.append(photo)
                        # display image and text on button
                        button_side = RIGHT
                        if i == 1:
                            button_side = LEFT
                        pattern_level = pattern.get_d_level()
                        button = Button(self.frame1, image=photo,
                                        text=pattern.pattern_name + "\n" + "Uploaded By: " + pattern.username+"\n" +
                                            "skill level: "+pattern_level+" ,estimated time: "+str(client.ml_dict[int(pattern_level)])+" minutes",
                                            compound=TOP, bg="#FFDEE3", command=lambda
                                pattern_name=pattern.pattern_name: self.change_to_display_pattern_screen(pattern_name))
                        button.pack(side=button_side, padx=10)
                        # image was displayed hence we can increase i var
                        i += 1
                        break
                except Exception as e:
                    print(e)
                    break
                finally:
                    # no matter what we initiate this var
                    client.pattern = None
                    time.sleep(0.01)

    def change_to_display_pattern_screen(self, pattern_name):
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        display_pattern(my_user.get_username(), pattern_name, self.fm)


class UploadPattern(tk.Toplevel):
    def __init__(self, master=None, friendly_mode=False):
        super().__init__(master)
        # basic settings
        self.label17 = None
        self.geometry("1000x2000")
        self.configure(background="#FFDEE3")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)
        self.fm=friendly_mode
        font_method(self, self.fm)

        # widgets for later
        self.optionmenu4 = None
        self.optionmenu5 = None
        self.current_stitch = None
        self.label4 = None
        self.optionmenu1 = None
        self.beginning = None
        self.label2 = None
        self.entry2 = None
        self.chain_num = None
        self.entry7 = None
        self.label16 = None
        self.pics_frame = None
        self.img_refs = []
        self.eyes_size = None
        self.eyes_sizes = None
        self.label15 = None
        self.button8 = None
        self.label14 = None
        self.cb5 = None
        self.cb3 = None
        self.cb4 = None
        self.cb2 = None
        self.buttons = None
        self.fill = None
        self.needle = None
        self.scissors = None
        self.eyes = None
        self.optionmenu6 = None
        self.label10 = None
        self.hook = None
        self.subcategory = None
        self.label12 = None
        self.b_amount = None
        self.cb1 = None
        self.label9 = None
        self.optionmenu8 = None
        self.b_size = None
        self.hooks = None
        self.clothes = None
        self.optionmenu7 = None
        self.label13 = None
        self.optionmenu3 = None
        self.button_sizes = None
        self.amigurumi = None
        self.category = None
        self.categories = None
        self.button7 = None
        self.entry6 = None
        self.label11 = None
        self.name = None
        self.entry5 = None
        self.label7 = None
        self.label6 = None
        self.button9 = None
        self.entry4 = None
        self.label5 = None
        self.optionmenu2 = None
        self.entry3 = None
        self.button6 = None
        self.button5 = None
        self.menus_frame = None
        self.stitches_label = None
        self.label3 = None
        self.additional_info = None
        self.total = None
        self.times = None
        self.current_round = None
        self.serial_number = None
        self.continue_loop = None
        self.y_place_st_button = None
        self.button2 = None

        # create a new pattern object
        self.my_pattern = Pattern()

        # entry var
        self.rounds = StringVar()

        # Create labels and buttons
        self.frame = Frame(self, width=1000, height=1000, bg="#FFDEE3")
        self.frame.place(x=0, y=0)
        self.frame1 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame1.pack(side=TOP)

        self.label1 = Label(self.frame1, text="Number of rounds: ", bg="#FFDEE3")
        self.label1.pack(side=LEFT)
        self.entry1 = Entry(self.frame1, textvariable=self.rounds)
        self.entry1.pack(side=LEFT)
        self.button1 = Button(self.frame1, text="Submit", command=self.create_pattern_interface, bg="#FFB6C1")
        self.button1.pack(side=LEFT)

        self.button3 = Button(self.frame1, text="Restart", command=self.start_pattern_again, bg="#FFB6C1")
        self.button3.pack(side=LEFT)
        self.button4 = Button(self.frame1, text="Submit pattern", command=self.submit_pattern, bg="#FFB6C1")
        self.button4.pack(side=LEFT)
        self.button10= Button(self.frame1, text="Go Back", command=self.go_back_button, bg="#FFB6C1")
        self.button10.pack(side=LEFT)

    def go_back_button(self):
        self.withdraw()
        LoggedInScreen(self, friendly_mode=self.fm)

    def start_pattern_again(self):
        self.withdraw()
        UploadPattern(self, friendly_mode=self.fm)

    def is_num(self, string):
        """checking if str is a number, if not, displaying a messagebox indicationg an error
        will use it in various places."""
        if not string.isnumeric():
            messagebox.showerror("Error", "Please enter a number.")
            return False
        return True

    def create_pattern_interface(self):
        is_num = self.is_num(self.rounds.get())  # make sure rounds.get is a number
        if is_num:
            # save number of rounds in our pattern object
            self.my_pattern.rounds = self.rounds.get()

            # make button and entry disappear.
            self.button1.pack_forget()
            self.entry1.pack_forget()

            # display number of rounds for user.
            self.label1.config(text="Number of rounds: "+str(self.my_pattern.rounds))

            self.frame2 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
            self.frame2.pack(side=TOP)
            # Create new label
            self.label2 = Label(self.frame2, text="Beginning: ", bg="#FFDEE3")
            self.label2.pack(side=LEFT)

            # initiate beginning variable
            self.beginning = tk.StringVar()
            # Create optionmenu
            begin_options = ["MR", "Ch"]
            self.optionmenu1 = OptionMenu(self.frame2, self.beginning, *begin_options, command=self.beginning_changed)
            self.optionmenu1.configure(bg="#FFB6C1")
            self.optionmenu1.pack(side=LEFT)
        else:
            # number of rounds is not a number, initiate self.rounds
            self.rounds.set("")

    def beginning_changed(self, *args):
        """check which option user chose"""
        if self.beginning.get() == "Ch":
            # user need to enter how many chains.
            self.chain_num = StringVar()
            self.label2.config(text="Beginning: Chains: ")
            self.optionmenu1.pack_forget()
            # Create an entry and a button
            self.entry2 = Entry(self.frame2, textvariable=self.chain_num)
            self.entry2.pack(side=LEFT)
            self.button2 = Button(self.frame2, text="Submit", command=self.chain_submitted, bg="#FFB6C1")
            self.button2.pack(side=LEFT)
        elif self.beginning.get() == "MR":
            # he chose MR, we can call create_rounds_list
            self.my_pattern.beginning = "MR"
            self.optionmenu1.pack_forget()
            self.label2.config(text="Beginning: MR")
            self.create_rounds_list()

    def chain_submitted(self):
        """number of chains was submitted"""
        # make sure chain_num is a number
        is_num = self.is_num(self.chain_num.get())
        if is_num:
            # show user what he chose
            self.my_pattern.beginning = "Ch"+str(self.chain_num.get())
            self.label2.config(text="Chains: "+str(self.chain_num.get()))
            # make optionmenu, entry and button disappear
            self.optionmenu1.pack_forget()
            self.entry2.pack_forget()
            self.button2.pack_forget()
            # call next method
            self.create_rounds_list()
        else:
            # chain_num is not a number. initiate it.
            self.chain_num.set("")

    def create_rounds_list(self):
        """in this method, user enters all rounds in patterns"""

        # this variable controls the for loop, and stops it until submit round is pressed
        self.continue_loop = tk.BooleanVar()
        self.continue_loop.set(False)

        # initiate var
        self.current_stitch = tk.StringVar(value="")

        for i in range(int(self.my_pattern.rounds)):  # for round in rounds
            # initiating these values each round
            self.serial_number = 1
            self.current_round = [""]
            self.times = tk.StringVar()
            self.total = tk.StringVar()
            self.additional_info = tk.StringVar()
            # this frame contains all the option menus that will be created
            self.frames_frame = Frame(self.frame, width=600, height=300, bg="#FFDEE3")
            self.frames_frame.pack(side=TOP)

            # Create labels
            self.frame3 = Frame(self.frames_frame, width=600, height=100, bg="#FFDEE3")
            self.frame3.pack(side=TOP)

            # this frame contains all the option menus that will be created
            self.menus_frame = Frame(self.frames_frame, width=600, height=100, bg="#FFDEE3")
            self.menus_frame.pack(side=TOP)

            self.frame4 = Frame(self.frames_frame, width=600, height=100, bg="#FFDEE3")
            self.frame4.pack(side=TOP)

            self.label3 = Label(self.frame3, text="Round " + str(i + 1) + ": ", bg="#FFDEE3")
            self.label3.pack(side=LEFT)
            self.stitches_label = Label(self.frame3, text=self.stringing_current_round(), bg="#FFDEE3")
            self.stitches_label.pack(side=LEFT)

            # Create buttons, labels and entries
            self.label4 = Label(self.frame3, text="X", bg="#FFDEE3")
            self.label4.pack(side=LEFT)

            self.entry3 = Entry(self.frame3, width=5, textvariable=self.times)
            self.entry3.pack(side=LEFT)
            self.label5 = Label(self.frame3, text="(", bg="#FFDEE3")
            self.label5.pack(side=LEFT)
            self.label17 = Label(self.frame3, text=self.count_total_stitches(self.current_round), bg="#FFDEE3")
            self.label17.pack(side=LEFT)
            self.label6 = Label(self.frame3, text=")", bg="#FFDEE3")
            self.label6.pack(side=LEFT)
            self.entry5 = Entry(self.frame3, width=40, textvariable=self.additional_info)
            self.entry5.insert(0, "Additional explanation/clarification/information")  # default string
            self.entry5.bind("<FocusIn>", lambda event: self.on_entry_click(event))
            self.entry5.pack(side=LEFT)
            self.button5 = Button(self.frame4, text="Add stitch", command=self.add_stitch, bg="#FFB6C1")
            self.button5.pack(side=LEFT, padx=5)
            self.button6 = Button(self.frame4, text="Submit round", command=self.submit_round, bg="#FFB6C1")
            self.button6.pack(side=LEFT)
            # creating the first option menu, serial number is 0
            self.create_option_menu(0)

            # the for loop waits until continue_loop is changed to True (when submit round is pressed)
            while not self.continue_loop.get():
                self.update()

            # set continue_loop as False for next round
            self.continue_loop.set(value=False)
        # all rounds were uploaded-lets call the next method
        self.pattern_name()

    def close_window(self):
        self.withdraw()
        client.close_socket()

    def on_entry_click(self, event):
        """ delete default text from entry 5"""
        if self.entry5.get() == "Additional explanation/clarification/information":
            self.entry5.delete(0, tk.END)

    def is_number(self, str):
        """ checks if str is a number"""
        try:
            if type(str) == list:
                return False
            int(str)
            return True
        except ValueError:
            return False

    def count_total_stitches(self, current_round, times=1):
        """count how many stitches are in round"""
        if not current_round or all(cell == '' for cell in current_round):
            return 0
        else:
            count = 0
            if any(self.is_number(cell) for cell in current_round):
                for stitch in current_round[0]:
                    if not stitch: continue
                    count += COUNT_DICT[str(stitch)] * int(times)
            else:
                for stitch in current_round:
                    if not stitch: continue
                    count += COUNT_DICT[str(stitch)] * times
            return count

    def stringing_current_round(self):
        """this method turns the current round list into an arranged string-in order to use in on screen"""
        string = "[ "
        for i, stitch in enumerate(self.current_round):
            if i == len(self.current_round)-1:
                # last stitch in list
                string += str(stitch)+" ]"
                return string
            string += str(stitch)+", "
        # in case self.current_round is empty
        return "[]"

    def submit_round(self):
        """button submit round was pressed-lets submit the round!
        starting by making sure user uploaded all the information we need:"""
        if not self.current_round:
            messagebox.showerror("Error", "Please select stitch type")
        elif self.times.get() == "":
            messagebox.showerror("Error", "Please fill out number of times")
            is_num = self.is_num(self.times.get())
            if not is_num:
                # make sure self.times is a number
                self.times.set("")
        elif self.total.get() == "":
            messagebox.showerror("Error", "Please fill out total number of stitches")
            is_num = self.is_num(self.total.get())
            if not is_num:
                # make sure self.total is a number
                self.times.set("")
        else:
            # all info of current round was uploaded correctly. first we shorten the list in case user didnt use all stitches
            while "" in self.current_round:
                self.current_round.remove("")
            if self.additional_info.get() != "" and self.additional_info.get() != "Additional explanation/clarification/information":
                # user added information-lets add it to my_pattern
                self.my_pattern.rounds_list.append([self.current_round, self.times.get(), self.total.get(), self.additional_info.get()])
                # printing nicely all the information from this round
                self.stitches_label.configure(text=self.stringing_current_round() + " X " + self.times.get() + " ( " + str(self.count_total_stitches(self.my_pattern.rounds_list[-1], times=self.times.get())) + " ) " + self.additional_info.get())
            else:
                # let's add information to rounds_list without the additional explanation.
                self.my_pattern.rounds_list.append([self.current_round, self.times.get(), self.total.get()])
                # printing nicely this round's information
                self.stitches_label.configure(text=self.stringing_current_round() + " X " + self.times.get() + " ( " + str(self.count_total_stitches(self.my_pattern.rounds_list[-1], times=self.times.get())) + " ) ")

            # deleting this round's widgets
            self.label4.pack_forget()
            self.label5.pack_forget()
            self.label6.pack_forget()
            self.entry3.pack_forget()
            #self.entry4.pack_forget()
            self.entry5.pack_forget()
            self.button5.pack_forget()
            self.button6.pack_forget()
            self.frames_frame.pack_forget()
            self.frame3.pack_forget()
            self.frame4.pack_forget()
            self.label18 = Label(self.frame, text=self.stitches_label.cget("text"), bg="#FFDEE3")
            self.label18.pack(side=TOP)
            # deleting all the option menus
            for widget in self.menus_frame.winfo_children():
                widget.destroy()
            # letting the for loop know it may continue to the next round!
            self.continue_loop.set(True)

    def add_stitch(self):
        """add stitch button was pressed! let's add a stitch
        add an empty string to current_round- it will be updated when user chooses stitch"""
        self.current_round.append("")
        # create the new option menu
        self.create_option_menu(self.serial_number)
        # add 1 to the number of our stitches (in this round)
        self.serial_number += 1

    def create_option_menu(self, serial_number):
        """create an option menu"""
        stitches_options = ["ch", "sc", "inc", "dec", "dc", "hdc", "tr", "slst", "sk", "invdec", "FLO", "BLO"]
        self.optionmenu2 = OptionMenu(self.menus_frame, self.current_stitch, *stitches_options, command=lambda *args: self.stitch_chosen(serial_number, self.current_stitch.get(), *args))
        self.optionmenu2.configure(bg="#FFB6C1")
        self.optionmenu2.pack(side=LEFT, padx=3)

    def stitch_chosen(self, serial_number, value, *args):
        """user chose stitch
        update current round list"""
        self.current_round[serial_number] = value
        # set current stitch to an empty string
        self.current_stitch.set("")
        # configure this label into what user chose, using stringing_current_round()
        self.stitches_label.configure(text=self.stringing_current_round())
        self.total.set(self.count_total_stitches(self.current_round))
        self.label17.configure(text=self.total.get())

    def pattern_name(self):
        """entering pattern's name
        Create label, entry and button in a frame"""
        self.frame5 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame5.pack(side=TOP)
        self.label7 = Label(self.frame5, text="pattern name: ", bg="#FFDEE3")
        self.label7.pack(side=LEFT)
        self.name = tk.StringVar()
        self.entry6 = Entry(self.frame5, width=20, textvariable=self.name)
        self.entry6.pack(side=LEFT)
        self.button7 = Button(self.frame5, text="submit", command=lambda: self.name_submitted(), bg="#FFB6C1")
        self.button7.pack(side=LEFT)

    def name_submitted(self):
        """name entered and submitted-print it on the screen, update my_pattern"""
        if self.name.get().find(",") != -1:
            messagebox.showerror("Error", "Please do not use commas in pattern names")
            return
        self.my_pattern.pattern_name = self.name.get()
        self.entry6.pack_forget()
        self.button7.pack_forget()
        self.label7.configure(text="pattern name: "+self.name.get())
        # call next method
        self.pattern_difficulty_level()

    def pattern_difficulty_level(self):
        """enter patterns dificulty level"""
        self.frame6 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame6.pack(side=TOP)
        self.label19 = Label(self.frame6, text="pattern's difficulty level: ", bg="#FFDEE3")
        self.label19.pack(side=LEFT)
        self.level = tk.StringVar()
        difficulty_levels = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        self.optionmenu9 = OptionMenu(self.frame6, self.level, *difficulty_levels, command=self.level_submitted)
        self.optionmenu9.configure(bg="#FFB6C1")
        self.optionmenu9.pack(side=LEFT, padx=3)

    def level_submitted(self, *args):
        """diff level submitted- update label"""
        self.my_pattern.d_level = self.level.get()
        self.optionmenu9.pack_forget()
        self.label19.configure(text="difficulty level: "+self.level.get())
        self.pattern_category()

    def pattern_category(self):
        """enter pattern's category
        Create a category optionmenu and label"""
        self.frame7 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame7.pack(side=TOP)
        self.categories = ["Amigurumi", "Clothing", "Other"]
        self.category = tk.StringVar()
        self.optionmenu3 = OptionMenu(self.frame7, self.category, *self.categories, command=self.category_selected)
        self.optionmenu3.configure(bg="#FFB6C1")
        self.label9 = Label(self.frame7, text="Category: ", bg="#FFDEE3")
        self.label9.pack(side=LEFT)
        self.optionmenu3.pack(side=LEFT)

    def category_selected(self, *args):
        """category selected-update my_pattern.update label as well."""
        self.my_pattern.category = self.category.get()
        self.label9.configure(text="Category: "+self.category.get())
        # Create option menus for subcategories
        self.optionmenu3.pack_forget()
        self.amigurumi = ["animals", "dolls", "plants", "characters", "other"]
        self.clothes = ["cardigans", "shirts and tops", "dresses", "scarfs", "beanies", "swimwear", "bags", "other"]
        if self.category.get() == "Amigurumi":
            self.subcategory = tk.StringVar()
            self.optionmenu4 = OptionMenu(self.frame7, self.subcategory, *self.amigurumi, command=self.subcategory_selected)
            self.optionmenu4.configure(bg="#FFB6C1")
            self.optionmenu4.pack(side=LEFT)
        elif self.category.get() == "Clothing":
            self.subcategory = tk.StringVar()
            self.optionmenu5 = OptionMenu(self.frame7, self.subcategory, *self.clothes, command=self.subcategory_selected)
            self.optionmenu5.configure(bg="#FFB6C1")
            self.optionmenu5.pack(side=LEFT)
        else:
            # category is "other", so no other optionmenu needed-therefore we call next method
            self.pattern_hook()

    def subcategory_selected(self, *args):
        """user chose subcategory. update my_pattern and print it onscreen"""
        self.label9.configure(text="Category: "+self.category.get()+", "+self.subcategory.get())
        self.my_pattern.subcategory = self.subcategory.get()
        if self.optionmenu4 is not None:
            # if option menu4 was in use
            self.optionmenu4.pack_forget()
        if self.optionmenu5 is not None:
            # if option menu5 was in use
            self.optionmenu5.pack_forget()
        # call next method
        self.pattern_hook()

    def pattern_hook(self):
        """Enter pattern's hook size
        Create an option menu and a label"""
        self.frame9 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame9.pack(side=TOP)
        self.hooks = ["0.6 mm", "0.75 mm", "1.0 mm", "1.25 mm", "1.5 mm", "1.75 mm", "2.0 mm", "2.25 mm", "2.5 mm", "2.75 mm", "3.0 mm", "3.25 mm", "3.75 mm", "4.0 mm", "4.5 mm", "5.0 mm", "5.5 mm", "6.0 mm", "6.5 mm", "7.0 mm", "8.0 mm", "9.0 mm", "10.0 mm", "12.0 mm", "15.0 mm", "16.0 mm"]
        self.hook = tk.StringVar()
        self.label10 = Label(self.frame9, text="Hook size: ", bg="#FFDEE3")
        self.label10.pack(side=LEFT)
        self.optionmenu6 = OptionMenu(self.frame9, self.hook, *self.hooks, command=self.hook_selected)
        self.optionmenu6.configure(bg="#FFB6C1")
        self.optionmenu6.pack(side=LEFT)

    def hook_selected(self, *args):
        """Hook size was chosen. Update my_pattern and print it onscreen"""
        self.optionmenu6.pack_forget()
        self.label10.configure(text="Hook size: "+self.hook.get())
        self.my_pattern.hook = self.hook.get()
        # call next method
        self.materials()

    def materials(self):
        """enter materials needed
        Create checkbutton vars"""
        self.frame10 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame10.pack(side=TOP)
        self.frame11 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame11.pack(side=TOP)
        self.frame12 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame12.pack(side=TOP)
        self.frame13 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame13.pack(side=TOP)
        self.frame14 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame14.pack(side=TOP)
        self.frame15 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame15.pack(side=TOP)
        self.eyes = tk.IntVar()
        self.scissors = tk.IntVar()
        self.needle = tk.IntVar()
        self.fill = tk.IntVar()
        self.buttons = tk.IntVar()
        # Create labels and check buttons
        self.label13 = Label(self.frame10, text="Materials:", bg="#FFDEE3")
        self.label13.pack(side=LEFT)
        self.cb1 = Checkbutton(self.frame11, text="Safety eyes", variable=self.eyes, onvalue=1, offvalue=0, command=self.eyes_checked, bg="#FFDEE3")
        self.cb1.pack(side=LEFT)
        self.cb2 = Checkbutton(self.frame12, text="Scissors", variable=self.scissors, onvalue=1, offvalue=0, command=self.scissors_checked, bg="#FFDEE3")
        self.cb2.pack(side=LEFT)
        self.cb3 = Checkbutton(self.frame13, text="Tapestry needle", variable=self.needle, onvalue=1, offvalue=0, command=self.needle_checked, bg="#FFDEE3")
        self.cb3.pack(side=LEFT)
        self.cb4 = Checkbutton(self.frame14, text="Polly-fiber fill", variable=self.fill, onvalue=1, offvalue=0, command=self.fill_checked, bg="#FFDEE3")
        self.cb4.pack(side=LEFT)
        self.cb5 = Checkbutton(self.frame15, text="Buttons", variable=self.buttons, onvalue=1, offvalue=0, command=self.buttons_checked, bg="#FFDEE3")
        self.cb5.pack(side=LEFT)
        # Create frame in order to display pictures later
        self.pics_frame = Frame(self.frame, width=800, height=200, bg="#FFDEE3")
        self.pics_frame.pack(side=BOTTOM)
        self.frame8 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame8.pack(side=TOP)
        self.button8 = tk.Button(self.frame8, text='Upload Picture', width=20, command=lambda: self.upload_picture(), bg="#FFB6C1")
        self.button8.pack(side=LEFT)

    def upload_picture(self):
        """clients wants to upload a picture"""
        try:
            f_types = [('Jpg Files', '*.jpg')]  # define filetypes we accept
            filename = filedialog.askopenfilename(filetypes=f_types)
            pil_image = Image.open(filename)  # open file
            pil_image.thumbnail((200, 200))  # trim picture
            img = ImageTk.PhotoImage(pil_image)
            # Store a reference to the PhotoImage object in a list
            self.img_refs.append(img)
            # Call display method
            self.display_picture(img, filename)
        except Exception as e:
            print(e)

    def display_picture(self, img, filename):
        """display picture to user in frame"""
        self.label16 = Label(self.pics_frame, image=img)
        self.label16.pack(side=LEFT, padx=5)
        # Store the image bytes in the Pattern object
        with open(filename, 'rb') as f:
            bytes_image = f.read()
        self.my_pattern.pictures.append(bytes_image)

    def eyes_checked(self):
        """user checked eyes. create a label"""
        self.cb1.pack_forget()
        self.label11 = Label(self.frame11, text="Safety eyes: ", bg="#FFDEE3")
        self.label11.pack(side=LEFT)
        # let user choose eyes size, using an optionmenu
        self.eyes_sizes = ["5 mm", "6 mm", "7 mm", "8 mm", "9 mm", "10 mm", "12 mm", "14 mm", "16 mm"]
        self.eyes_size = tk.StringVar()
        self.optionmenu7 = OptionMenu(self.frame11, self.eyes_size, *self.eyes_sizes, command=self.eyes_chosen)
        self.optionmenu7.configure(bg="#FFB6C1")
        self.optionmenu7.pack(side=LEFT)

    def eyes_chosen(self,event=None):
        """change label according to what user chose."""
        self.label11.configure(text="-Safety eyes: "+self.eyes_size.get())
        self.optionmenu7.pack_forget()

    def scissors_checked(self):
        """user checked scissors"""
        self.cb2.pack_forget()
        # change label
        self.label12 = Label(self.frame12, text="-Scissors", bg="#FFDEE3")
        self.label12.pack(side=LEFT)

    def needle_checked(self):
        """users checked needle"""
        self.cb3.pack_forget()
        # change label
        self.label13 = Label(self.frame13, text="-Tapestry needle", bg="#FFDEE3")
        self.label13.pack(side=LEFT)

    def fill_checked(self):
        """user checked polly-fiber fill"""
        self.cb4.pack_forget()
        # change label
        self.label14 = Label(self.frame14, text="-Polly-fiber fill", bg="#FFDEE3")
        self.label14.pack(side=LEFT)

    def buttons_checked(self):
        """user checked buttons"""
        self.cb5.pack_forget()
        self.label15 = Label(self.frame15, text="-Buttons- amount: ", bg="#FFDEE3")
        self.label15.pack(side=LEFT)
        # create entry to enter buttons amount
        self.b_amount = tk.StringVar()
        self.entry7 = Entry(self.frame15, width=5, textvariable=self.b_amount)
        self.entry7.pack(side=LEFT)
        self.button8 = Button(self.frame15, text="submit", command=self.button_ammount, bg="#FFB6C1")
        self.button8.pack(side=LEFT)

    def button_ammount(self, *args):
        """user entered buttons amount"""
        self.entry7.pack_forget()
        self.button8.pack_forget()
        # update label
        self.label15.configure(text="-Buttons- amount: "+self.b_amount.get()+"  ,size: ")
        # let user choose buttons size. create an option menu
        self.button_sizes = ["7.5 mm", "8 mm", "9 mm", "9.5 mm", "10 mm", "10.5 mm", "11.5 mm", "12.5 mm", "14 mm", "15 mm", "16 mm", "18 mm", "19 mm", "20 mm", "21 mm", "23 mm", "24 mm", "25 mm", "26 mm", "28 mm"]
        self.b_size = tk.StringVar()
        self.optionmenu8 = OptionMenu(self.frame15, self.b_size, *self.button_sizes, command=self.size_selected)
        self.optionmenu8.configure(bg="#FFB6C1")
        self.optionmenu8.pack(side=LEFT)

    def size_selected(self, *args):
        """user selected buttons size, update label"""
        self.optionmenu8.pack_forget()
        self.label15.configure(text="-Buttons- amount: "+self.b_amount.get()+"  ,size: "+self.b_size.get())

    def submit_pattern(self):
            """check that pattern is full"""
            if len(self.my_pattern.rounds_list) == 0 or self.buttons is None:
                messagebox.showerror("Error", "sorry, you can not submit an empty pattern")
            else:
                # create materials list. first make sure we have what we need.
                if self.buttons.get() == 1 and (self.b_size.get() == "" or self.b_amount.get() == ""):
                    messagebox.showerror("Error", "please fill out buttons' amount and size.")
                else:
                    if self.eyes.get() == 1 and self.eyes_size.get() == "":
                        messagebox.showerror("Error", "please fill out eyes' size.")
                    else:
                        # creating materials list, using info we collected in materials()
                        if self.eyes.get():
                            self.my_pattern.materials.append([1, self.eyes_size.get()])
                        else:
                            self.my_pattern.materials.append([0, 0])
                        self.my_pattern.materials.extend((self.scissors.get(), self.needle.get(), self.fill.get()))
                        if self.buttons.get():
                            self.my_pattern.materials.append([1, self.b_amount.get(), self.b_size.get()])
                        else:
                            self.my_pattern.materials.append([0, 0, 0])
                        # update current date and username in my_pattern
                        current_date = dt.date.today()
                        self.my_pattern.date = current_date.strftime("%Y-%m-%d")
                        self.my_pattern.username = client.username
                        if not self.my_pattern.pictures:
                            # adding a piture in case user did not
                            with open(logo, 'rb') as f:
                                bytes_image = f.read()
                            self.my_pattern.pictures.append(bytes_image)
                        # turn my_pattern into bytes
                        serialized_object = pickle.dumps(self.my_pattern)
                        # add prefix to the object before sending it
                        #sock_data = str(sys.getsizeof(serialized_object)).zfill(8).encode()
                        #sock_data += serialized_object
                        # send my_pattern to server
                        client.send_message(serialized_object)
                        self.response_uploading_pattern()

    def response_uploading_pattern(self):
        # wait for response from server
        while True:
            if client.pattern_code != 0:
                if client.pattern_code == 4.1:
                    # pattern was uploaded successfully
                    messagebox.showinfo("Great", "Your pattern has been uploaded!")
                else:
                    # pattern was not uploaded: an error occurred
                    messagebox.showerror("Error", "Sorry, your pattern could not be uploaded. Please try again")
                break
        # initiate var for future patterns.
        client.pattern_code = 0
        self.withdraw()
        LoggedInScreen(self, self.fm)


class DisplayPattern(tk.Toplevel):
    def __init__(self, my_pattern, rounds_done, username, master=None, friendly_mode=False):
        super().__init__(master)
        # basic settings
        self.start_time = datetime.now()

        self.cb1 = None
        self.label2 = None
        self.label1 = None
        self.geometry("1000x2000")
        self.configure(background="#FFDEE3")
        self.pictures = []

        self.fm = friendly_mode
        # Add fonts for all the widgets
        font_method(self, self.fm)

        # HANDLE PATTERN CLOSE
        self.rounds_done = self.list_rounds_done(rounds_done, my_pattern.rounds)

        self.protocol("WM_DELETE_WINDOW", lambda: handle_pattern_quit(my_pattern.get_pattern_name(), username, self.count_rounds_done(), self.calculate_minutes(self.start_time)))
        self.cb_list = []
        try:

            self.canvas = tk.Canvas(self, bg="#FFDEE3")

            scrollbar = ttk.Scrollbar(self, command=self.canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.configure(yscrollcommand=scrollbar.set)

            self.frame = tk.Frame(self.canvas, bg="#FFDEE3")
            self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.button = Button(self.frame, text="Back to Main screen", command=lambda: self.button_main_screen(my_pattern.get_pattern_name(), username, self.count_rounds_done()), bg="#FFB6C1")
            self.button.pack(side=RIGHT)
            self.button3 = Button(self.frame, text="Abbervations",command=self.abbervations_window, bg="#FFB6C1")
            self.button3.pack(side=RIGHT)
            self.label1 = Label(self.frame, text=my_pattern.get_pattern_name(), bg="#FFDEE3")
            self.label1.pack(side=TOP)
            self.label8 = Label(self.frame, text="Uploaded by: "+my_pattern.username+" ,Category: "+my_pattern.category+", "+my_pattern.subcategory, bg="#FFDEE3")
            self.label8.pack(side=TOP, pady=5)
            self.label2 = Label(self.frame, text="Materials: ", bg="#FFDEE3")
            self.label2.pack(side=TOP, pady=5)
            for i, element in enumerate(my_pattern.materials):
                if isinstance(element, list) and element[0] == 1:
                    # element is a list and starts with 1
                    if len(element) == 2:
                        # it is eyes list
                        label3 = Label(self.frame, text="-"+element[1]+" safety eyes", bg="#FFDEE3")
                        label3.pack(side=TOP, pady=5)
                    else:
                        # it is buttons list
                        label4 = Label(self.frame, text="-"+element[2]+" "+element[1]+" buttons", bg="#FFDEE3")
                        label4.pack(side=TOP, pady=5)
                elif element == 1:
                    # element is an int
                    if i == 2:
                        # scissors
                        self.label5 = Label(self.frame, text="- Scissors", bg="#FFDEE3")
                        self.label5.pack(side=TOP, pady=5)
                    elif i == 3:
                        # needle
                        self.label6 = Label(self.frame, text="- Tapestry needle", bg="#FFDEE3")
                        self.label6.pack(side=TOP, pady=5)
                    else:
                        # fill
                        self.label7 = Label(self.frame, text="- Polly-fiber fill", bg="#FFDEE3")
                        self.label7.pack(side=TOP, pady=5)
            self.label9 = Label(self.frame, text="- "+my_pattern.hook+" crochet hook", bg="#FFDEE3")
            self.label9.pack(side=TOP, pady=5)
            # DATE?
            self.label10 = Label(self.frame, text="Beginning:"+my_pattern.beginning, bg="#FFDEE3")
            self.label10.pack(side=TOP, pady=5)

            for i,round in enumerate(my_pattern.rounds_list):
                # printing all rounds
                if self.rounds_done[i].get() is True:
                    self.create_round_cb(i, round, True, my_pattern.get_pattern_name(), username, my_pattern.get_d_level())
                else:
                    self.create_round_cb(i, round, False, my_pattern.get_pattern_name(), username, my_pattern.get_d_level())
            for pic in my_pattern.pictures:
                # create a PIL Image object from the bytes
                img = Image.open(io.BytesIO(pic))
                img.thumbnail((250, 250))
                # create a PhotoImage object from the PIL Image object
                photo = ImageTk.PhotoImage(img)
                # save references to photos
                self.pictures.append(photo)
                # create a Tkinter Label object with the PhotoImage object as its image option
                label = tk.Label(self.frame, image=photo)
                label.image = photo  # Attach the PhotoImage object to the label
                label.pack(side=TOP, padx=10)

            self.frame.update_idletasks()
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception as e:
            print("ERROR: "+str(e))
            print("Error occurred at line:", sys.exc_info()[-1].tb_lineno)

    def read_label_text(self, string):
        engine = pyttsx3.init()
        engine.say(string)
        engine.runAndWait()

    def on_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def calculate_minutes(self, start_time):
        """calc the time in minutes a client has been in a pattern"""
        current_time = datetime.now()
        hours = current_time.hour - start_time.hour
        minutes = current_time.minute - start_time.minute
        seconds = current_time.second - start_time.second
        sum_in_minutes = hours * 60 + minutes + seconds / 60
        return numpy.round(sum_in_minutes, 2)

    def list_rounds_done(self, rounds_done, my_p_length):
        """creating a list of tk booleans- for the checkbuttons to know if to be true or false"""
        list = []
        if rounds_done == "0" or rounds_done == 0:
            for i in range(int(my_p_length)):
                list.append(tk.BooleanVar(value=False))
            return list
        else:
            for n in rounds_done:
                list.append(tk.BooleanVar(value=True))
            for i in range(int(my_p_length)-int(rounds_done)):
                list.append(tk.BooleanVar(value=False))
            return list

    def create_round_cb(self, i, round, cb_state_bool, pattern_name, username, level):
        """create label of round with all the data"""
        cb_var = BooleanVar(value=cb_state_bool)
        self.frame1 = Frame(self.frame, width=800, height=100, bg="#FFDEE3")
        self.frame1.pack(side=TOP)
        cb = Checkbutton(self.frame1, wraplength=600, text="Round " + str(i + 1) + ": " + str(round[0]) + " X " + (round[1]) + " ( " + (round[2]) + " ) ", variable=cb_var, onvalue=True, offvalue=False,command=lambda: self.change_state(i, cb_var, pattern_name, username, level), bg="#FFDEE3")
        cb.pack(side=LEFT, padx=5)
        self.cb_list.append(cb)
        if self.fm:
            # we add an option to read the instructions
            self.button1 = Button(self.frame1, text="Read Round", command=lambda: self.read_label_text(cb.cget("text")), bg="#FFB6C1")
            self.button1.pack(side=LEFT)

        if len(round) > 3:
            self.frame2 = Frame(self.frame, width=2000, height=1000, bg="#FFDEE3")
            self.frame2.pack(side=TOP)
            label = Label(self.frame2, text="Explanations: " + str(round[3]), wraplength=600, bg="#FFDEE3")
            label.pack(side=LEFT, padx=8)
            if self.fm:
                # we add an option to read the instructions
                self.button2 = Button(self.frame2, text="Read Explanation", command=lambda: self.read_label_text(label.cget("text")), bg="#FFB6C1")
                self.button2.pack(side=LEFT)

    def change_state(self, i, cb_state_bool, pattern_name, username, level):
        """change the state of a checkbutton. make sure it is not checked before other rounds.
        check if it is the last round- which means pattern is done. if so- let server know and write it in db. call Logged_in_screen."""
        for m in range(i):
            if self.rounds_done[m].get() is False:
                messagebox.showerror("Error", "Please finish previous rounds before moving on to next ones.")
                cb_state_bool.set(False)
                return
        self.rounds_done[i] = cb_state_bool
        #for r in self.rounds_done:
        if self.count_rounds_done() == len(self.rounds_done):
            # user finished all rows!!!
            messagebox.showinfo("Congratulations", "You have completed " + str(pattern_name))
            # save pattern done in db
            client.send_message("#"+username+" " + str(self.calculate_minutes(self.start_time))+" " +str(level)+ " " +pattern_name)
            # check if pattern was started and recorded in db
            client.send_message("6"+username+" "+pattern_name)
            while True:
                if client.pattern_started is not None:
                    if client.pattern_started:
                        # pattern was already started.it is in db. now we delete it from db
                        client.pattern_started = None
                        client.send_message("0"+username+" "+pattern_name)

                        while True:
                            if client.deleted_row is not None:
                                if client.deleted_row == "0.1":
                                    client.deleted_row = None
                                    break
                                else:
                                    # error occurred when we tried to delete the row
                                    messagebox.showerror("Error", "An error occurred")
                                    client.deleted_row = None
                                    break
                        break
                    else:
                        # pattern was never in db hence it is not need deleting
                        client.pattern_started = None
                        break
            self.withdraw()
            LoggedInScreen(self, friendly_mode=self.fm)

    def button_main_screen(self, pattern_name, username, rounds_done):

        code = handle_pattern_leave(pattern_name, username, rounds_done, self.calculate_minutes(self.start_time))
        if code == 1:
            self.withdraw()
            LoggedInScreen(self, friendly_mode=self.fm)
        else:
            messagebox.showerror("Error", "Sorry, please try to exit later")

    def count_rounds_done(self):
        """count how many Trues there are in rounds_done list"""
        count = 0
        for n in self.rounds_done:
            if n.get() is True:
                count += 1
        return count

    def abbervations_window(self):
        self.window = tk.Toplevel(self)
        self.window.title("Abbervations")
        self.window.attributes("-topmost", True)  # Make the window appear on top
        self.window.geometry("300x600+200+200")  # Set the window size and position
        self.window.configure(background="#FFDEE3")

        # Add widgets to the jumping window
        label = tk.Label(self.window, text="Sc- Single crochet \n "
                         "Dc- Double crochet \n "
                         "Hdc- Half Double crochet \n "
                         "Blo- Back loop only \n "
                         "Flo- front loop only \n "
                         "Ch- chain \n "
                         "slst- Slip stitch \n "
                         "Sk- skip \n "
                         "Dec- decrease \n "
                         "Inc- Increase \n "
                         "Tr- Treble \n "
                         "Invdec- Invisible Decrease \n ", bg="#FFDEE3")
        label.pack(padx=20, pady=50)


class ApproveManagersScreen(tk.Toplevel):
    def __init__(self, master=None, friendly_mode=False):
        super().__init__(master)
        # basic settings
        self.geometry("1000x2000")
        self.configure(background="#FFDEE3")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)
        self.fm = friendly_mode
        # Add fonts for all the widgets
        font_method(self, self.fm)
        # get the string of users who wants to be managers
        client.send_message("$")
        while True:
            if client.future_managers is not None:
                # we turn the string into a list
                want_to_be_managers = client.future_managers.split()
                client.future_managers = None
                break
        # now we print out all the names
        self.frame1 = Frame(self, width=400, height=1000, bg="#FFDEE3")
        self.frame1.place(x=260, y=10)
        self.frame2 = Frame(self, width=400, height=1000, bg="#FFDEE3")
        self.frame2.place(x=560, y=10)
        self.button1 = Button(self, text="Back to Main screen", bg="#F098A2", command=self.main_screen_button)
        self.button1.place(x=10, y=10)
        if not want_to_be_managers:
            self.label = Label(self.frame1, text="There arent any manager requests", bg="#FFDEE3")
            self.label.pack(side=TOP)
        else:
            for manager in want_to_be_managers:
                self.label = Label(self.frame1, text=manager+" wants to be a manager!", bg="#FFDEE3")
                self.label.pack(side=TOP)
                self.button = Button(self.frame2, text="see their work!", bg="#F098A2", command=lambda: self.users_work_button(manager))
                self.button.pack(side=TOP)

    def users_work_button(self, username):
        self.withdraw()
        DisplayUsersWork(self, username, friendly_mode=self.fm)

    def main_screen_button(self):
        self.withdraw()
        LoggedInScreen(self, friendly_mode=self.fm)


class DisplayUsersWork(tk.Toplevel):
    def __init__(self, master=None, username=None, friendly_mode=False):
        super().__init__(master)
        # basic settings
        self.geometry("1000x2000")
        self.configure(background="#FFDEE3")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)
        self.fm = friendly_mode
        # Add fonts for all the widgets
        font_method(self, self.fm)
        # display all work of a certain user, in order to judge if they can become manager
        self.label1 = Label(self, text="The work of "+username+":", bg="#FFDEE3")
        self.label1.pack(side=TOP)
        client.send_message("@"+username)
        while True:
            if client.user_work is not None:
                patterns = client.user_work
                client.user_work = None
                break
        if not patterns:
            self.label2 = Label(self, text=username+" has not completed any patterns.", bg="#FFDEE3")
            self.label2.pack(side=TOP)
        else:
            patterns = patterns.split("|")
            for pattern in patterns:
                pattern = pattern.split(",")
                if pattern == ['']:
                    break
                self.label = Label(self, text="Pattern: "+pattern[0]+" ,times: "+pattern[1], bg="#FFDEE3")
                self.label.pack(side=TOP)
        self.frame = Frame(self, width=200, height=1000, bg="#FFDEE3")
        self.frame.place(x=10, y=10)
        self.button1 = Button(self.frame, text="Approve manager", bg="#F098A2", command=lambda: self.manager_approved(username))
        self.button1.pack(side=TOP)
        self.button2 = Button(self.frame, text="Disapprove manager", bg="#F098A2", command=lambda: self.manager_disapproved(username))
        self.button2.pack(side=TOP)

    def manager_approved(self, username):
        client.send_message("%1"+username)
        while True:
            if client.approve_req is not None:
                messagebox.showinfo("Great", username + " has been approved to be a manger")
                client.approve_req = None
                break
        self.withdraw()
        ApproveManagersScreen(self, friendly_mode=self.fm)

    def manager_disapproved(self, username):
        client.send_message("%0"+username)
        while True:
            if client.approve_req is not None:
                messagebox.showinfo("Great", username + " has not been approved to be a manger")
                client.approve_req = None
                break
        self.withdraw()
        ApproveManagersScreen(self, friendly_mode=self.fm)


class SearchPatternScreen(tk.Toplevel):
    def __init__(self, master=None, friendly_mode=False):
        super().__init__(master)
        # basic settings
        self.button3 = None
        self.geometry("1000x2000")
        self.configure(background="#FFDEE3")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)
        self.fm = friendly_mode
        # Add fonts for all the widgets
        font_method(self, self.fm)

        self.imgrefs = []
        self.pattern_names = []
        self.pattern_names2 = []

        canvas = create_scroll_bar(self)
        canvas.pack(fill=tk.BOTH, expand=True)  # Fill the available space

        self.frame4 = tk.Frame(canvas, bg="#FFDEE3")
        canvas.create_window((0, 0), window=self.frame4, anchor=tk.NW)

        self.frame = Frame(self.frame4, width=10000, height=10000, bg="#FFDEE3")
        self.frame.pack(side=TOP, fill=tk.BOTH, expand=True)
        self.frame2 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
        self.frame2.pack(side=TOP)
        self.label2 = Label(self.frame2, text="Search in Patterns: ", bg="#FFDEE3")
        self.label2.pack(side=LEFT)
        self.string_to_search = tk.StringVar()
        self.entry1 = Entry(self.frame2, textvariable=self.string_to_search)
        self.entry1.pack(side=LEFT, pady=5)
        self.button1 = Button(self.frame2, text="Search!", command=self.search_in_pattern_names)
        self.button1.pack(side=LEFT)
        self.button2 = Button(self.frame, text="Go Back", command=self.go_back_button)
        self.button2.pack(side=RIGHT)
        self.frame3 = Frame(self.frame, width=600, height=100)

        self.frame3.pack(side=TOP)
        self.label1 = Label(self.frame3, text="All Patterns: ", bg="#FFDEE3")
        self.label1.pack(side=TOP)

        # we display all the patterns that are in the system
        client.send_message("!")
        while True:
            if client.num_patterns is not None:
                break
        self.displayed=False
        self.frames_list = []
        self.patterns_display(client.num_patterns)
        client.num_patterns = None

    def patterns_display(self, num_patterns):
        """creating all the buttons according to how many patterns"""
        i = 1
        try:
            while i <= int(num_patterns):
                client.send_message("5")
                while True:
                    try:
                        if client.pattern is not None:
                            # load pattern from server
                            pattern = pickle.loads(client.pattern)
                            if pattern.pattern_name in self.pattern_names:
                                # make sure pattern is not displayed twice
                                break
                            # open image
                            img = Image.open(io.BytesIO(pattern.pictures[0]))
                            # trim image
                            img.thumbnail((250, 250))
                            # get image ready for display
                            photo = ImageTk.PhotoImage(img)
                            # save image info
                            self.imgrefs.append(photo)
                            self.pattern_names.append(pattern.pattern_name)
                            # display image and text on button
                            if i%3 == 1:
                                self.frame1 = Frame(self.frame, width=600, height=200, bg="#FFDEE3")
                                self.frame1.pack(side=TOP)
                                self.frames_list.append(self.frame1)
                            button = Button(self.frame1, image=photo, text=pattern.pattern_name + "\n" + "Uploaded By: " + pattern.username+"\n" + "Estimated time: " + str(client.ml_dict[int(pattern.get_d_level())]) + " minutes", compound=TOP, bg="#FFDEE3", command=lambda pattern_name=pattern.pattern_name: self.change_to_display_pattern_screen(pattern_name))
                            button.pack(side=LEFT, padx=10)
                            # image was displayed hence we can increase i var
                            i += 1
                            break
                    except Exception as e:
                        print(e)
                        break
                    finally:
                        # no matter what we initiate this var
                        client.pattern = None
                        time.sleep(0.01)  # Add a delay of 1 second before sending the next message

        except Exception as e:
            print(e)

    def patterns_display_search(self, patterns_to_display):
        """display only patterns that are in patterns_to_display"""
        i = 1
        try:
            while i <= len(patterns_to_display):
                client.send_message("5")
                while True:
                    try:
                        if client.pattern is not None:
                            # load pattern from server
                            pattern = pickle.loads(client.pattern)
                            if pattern.pattern_name in self.pattern_names2 or pattern.pattern_name not in patterns_to_display:
                                # make sure pattern is not displayed twice
                                break
                            # open image
                            img = Image.open(io.BytesIO(pattern.pictures[0]))
                            # trim image
                            img.thumbnail((250, 250))
                            # get image ready for display
                            photo = ImageTk.PhotoImage(img)
                            # save image info
                            self.imgrefs.append(photo)
                            self.pattern_names2.append(pattern.pattern_name)
                            # display image and text on button
                            if i%3 == 1:
                                self.frame1 = Frame(self.frame, width=600, height=200, bg="#FFDEE3")
                                self.frame1.pack(side=TOP)
                                self.frames_list.append(self.frame1)
                            button = Button(self.frame1, image=photo,text=pattern.pattern_name + "\n" + "Uploaded By: " + pattern.username,compound=TOP, bg="#FFDEE3", command=lambda pattern_name=pattern.pattern_name: self.change_to_display_pattern_screen(pattern_name))
                            button.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH)
                            self.displayed=True
                            # image was displayed hence we can increase i var
                            i += 1
                            break
                    except Exception as e:
                        print(e)
                        break
                    finally:
                        # no matter what we initiate this var
                        client.pattern = None
                        time.sleep(0.01)  # Add a delay of 1 second before sending the next message

        except Exception as e:
            print(e)

    def search_in_pattern_names(self):
        self.displayed = False
        self.pattern_names2 = []
        for f in self.frames_list:
            f.pack_forget()
        if self.frame3:
            self.frame3.pack_forget()
        if self.button3:
            self.button3.pack_forget()
        pattern_names = []
        search_string = self.string_to_search.get()  # Retrieve the value from the StringVar
        for name in self.pattern_names:
            if search_string in name:
                pattern_names.append(name)
        self.string_to_search.set("")
        self.button3 = Button(self.frame, text="All Patterns", command=self.all_patterns_display)
        self.button3.pack(side=RIGHT)
        self.patterns_display_search(pattern_names)
        if self.displayed is False:
            messagebox.showerror("Error", "Sorry, No patterns matched your search")

    def change_to_display_pattern_screen(self, pattern_name):
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        self.pattern_names2 = []
        display_pattern(my_user.get_username(), pattern_name, self.fm)

    def all_patterns_display(self):
        self.pattern_names = []
        self.withdraw()
        SearchPatternScreen(self, friendly_mode=self.fm)

    def go_back_button(self):
        self.withdraw()
        self.imgrefs = []
        self.pattern_names = []
        self.pattern_names2 = []
        LoggedInScreen(self, friendly_mode=self.fm)


class PatternsInProgress(tk.Toplevel):
    def __init__(self, master=None, friendly_mode=False):
        super().__init__(master)
        # basic settings
        self.button3 = None
        self.geometry("1000x2000")
        self.configure(background="#FFDEE3")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)
        self.fm = friendly_mode
        # Add fonts for all the widgets
        font_method(self, self.fm)
        self.patterns_to_display = []

        self.imgrefs = []

        self.frame = Frame(self, width=1000, height=2000, bg="#FFDEE3")
        self.frame.place(x=0, y=0)

        self.label2 = Label(self, text="Patterns In Progress: ", bg="#FFDEE3")
        self.label2.pack(side=TOP)

        self.button1 = Button(self, text="Go Back", command = self.go_back_button)
        self.button1.pack(side=RIGHT)

        client.send_message("+"+my_user.get_username())
        while True:
            if client.patterns_in_progress is not None:
                self.patterns_to_display = client.patterns_in_progress[:-1].split(",")
                client.patterns_in_progress = None
                break
        if self.patterns_to_display == ['']:
            self.label1 = Label(self.frame, text="You don't have any patterns in progress", bg="#FFDEE3")
            self.label1.pack(side=TOP)
        else:
            for i, pattern in enumerate(self.patterns_to_display):
                current_pattern = get_pattern_from_database(pattern)
                # open image
                img = Image.open(io.BytesIO(current_pattern.pictures[0]))
                # trim image
                img.thumbnail((250, 250))
                # get image ready for display
                photo = ImageTk.PhotoImage(img)
                # save image info
                self.imgrefs.append(photo)
                # display image and text on button
                pattern_level = current_pattern.get_d_level()
                if i%3 == 0:
                    self.frame1 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
                    self.frame1.pack(side=TOP)
                self.button2 = Button(self.frame1, image=photo, text=current_pattern.pattern_name + "\n" + "Uploaded By: " + current_pattern.username + "\n" + "skill level: " + pattern_level + " ,estimated time left: " + str(client.ml_dict[int(pattern_level)]-current_pattern.get_sum_time()) + " minutes", compound=TOP, bg="#FFDEE3", command=lambda pattern_name=current_pattern.pattern_name: self.change_to_display_pattern_screen(pattern_name))
                self.button2.pack(side=LEFT, padx=10)

    def go_back_button(self):
        self.imgrefs = []
        self.withdraw()
        LoggedInScreen(self, friendly_mode=self.fm)

    def change_to_display_pattern_screen(self, pattern_name):
        self.withdraw()
        self.imgrefs = []
        display_pattern(my_user.get_username(), pattern_name, self.fm)


class MyUploadsScreen(tk.Toplevel):
    def __init__(self, master=None, friendly_mode=False):
        super().__init__(master)
        # basic settings
        self.button3 = None
        self.geometry("1000x2000")
        self.configure(background="#FFDEE3")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)
        self.fm = friendly_mode
        # Add fonts for all the widgets
        font_method(self, self.fm)
        self.patterns_to_display = []

        self.imgrefs = []

        self.frame = Frame(self, width=1000, height=2000, bg="#FFDEE3")
        self.frame.place(x=0, y=0)

        self.label2 = Label(self, text="My Uploads: ", bg="#FFDEE3")
        self.label2.pack(side=TOP)

        self.button1 = Button(self, text="Go Back", command=self.go_back_button)
        self.button1.pack(side=RIGHT, padx=5)

        self.button3 = Button(self, text="Upload now!", command=self.upload_pattern)
        self.button3.pack(side=RIGHT, padx=5)

        client.send_message("~"+my_user.get_username())
        while True:
            if client.users_uploads is not None:
                self.patterns_to_display = client.users_uploads[:-1].split(",")
                client.users_uploads = None
                break
        if not self.patterns_to_display:
            self.label1 = Label(self.frame, text="You haven't uploaded any patterns yet", bg="#FFDEE3")
            self.label1.pack(side=TOP)
        for i, pattern in enumerate(self.patterns_to_display):
            current_pattern = get_pattern_from_database(pattern)
            # open image
            img = Image.open(io.BytesIO(current_pattern.pictures[0]))
            # trim image
            img.thumbnail((250, 250))
            # get image ready for display
            photo = ImageTk.PhotoImage(img)
            # save image info
            self.imgrefs.append(photo)
            # display image and text on button
            pattern_level = current_pattern.get_d_level()
            if i%3 == 0:
                self.frame1 = Frame(self.frame, width=600, height=100, bg="#FFDEE3")
                self.frame1.pack(side=TOP)
            self.button2 = Button(self.frame1, image=photo, text=current_pattern.pattern_name + "\n" + "Uploaded By: " + current_pattern.username + "\n" + "skill level: " + pattern_level + " ,estimated time: " + str(client.ml_dict[int(pattern_level)]) + " minutes", compound=TOP, bg="#FFDEE3", command=lambda pattern_name=current_pattern.pattern_name: self.change_to_display_pattern_screen(pattern_name))
            self.button2.pack(side=LEFT, padx=10)

    def go_back_button(self):
        self.imgrefs = []
        self.withdraw()
        LoggedInScreen(self, friendly_mode=self.fm)

    def change_to_display_pattern_screen(self, pattern_name):
        self.withdraw()
        self.imgrefs = []
        display_pattern(my_user.get_username(), pattern_name, self.fm)

    def upload_pattern(self):
        self.withdraw()
        self.imgrefs = []
        UploadPattern(self, friendly_mode=self.fm)


root = tk.Tk()
root.withdraw()
OpenScreen(root)
root.mainloop()
