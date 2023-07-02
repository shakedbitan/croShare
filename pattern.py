import sys
import threading
import tkinter
import pickle
from tkinter import *
from client import Client
import tk
from tkinter import messagebox
from class_user import User
from class_pattern import Pattern
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk

PORT = 2800
IP = "127.0.0.1"

#pictures
logo = r"c:\logo.png"
background = r"c:\background.png"

client = Client(IP, PORT)

my_user = User("0", "0")

class windows(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        # Adding a title to the window
        self.title("Test Application")
        self.label = Tk.Label(self, )

        self.protocol = Tk.protocol("deletewindow")


def check_client_code(client ):
    if client.code == "1":
        return 1
    return 0


def create_message(message):
    print(message)
    client.send_message(message)


def change_window(root, screen):
    root.withdraw()
    new_root = Tk()
    new_root = screen


# def recieve_messages(self):
#     while True:
#         message = client.receive_data_from_server()
#         print(message)


class Open_screen(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.geometry("1000x2000")

        self.protocol("WM_DELETE_WINDOW", client.close_socket)
        # Add image file
        self.lg = PhotoImage(file=logo)

        # Show image using label
        # self.label1 = Label(self, image=self.bg)
        # self.label1.place(x=0, y=0)

        self.configure(background="#FFDEE3")

        self.label2 = Label(self, image=self.lg)
        self.label2.place(x=400, y=300)

        # Create Frame
        #self.frame1 = Frame(self)
        #self.frame1.pack()

        # Add buttons
        self.button1 = Button(self, text="Friendly mode", bg="#F098A2")
        self.button1.place(x=30, y=40)

        self.button2 = Button(self, text="Log in", command=self.change_to_log_in_screen, bg="#F098A2")
        self.button2.place(x=140,y=40)

        self.button3 = Button(self, text="Sign up", command=self.change_to_sign_up_screen,bg="#F098A2")
        self.button3.place(x=210,y=40)

        self.button4 = Button(self, text="search pattern", command=lambda: create_message("search pattern"), bg="#F098A2")
        self.button4.place(x=280, y=40)

    def change_to_sign_up_screen(self):
        self.withdraw()
        Sign_up_screen(self)

    def change_to_log_in_screen(self):
        self.withdraw()
        Log_in_screen(self)


class Sign_up_screen(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.label5 = None
        self.geometry("1000x2000")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)

        self.username = tk.StringVar()
        self.gmail = tk.StringVar()
        self.password = tk.StringVar()

        # self.bg = PhotoImage(file=background)
        # self.label1 = Label(self, image=self.bg)
        # self.label1.place(x=0, y=0)

        self.configure(background="#FFDEE3")

        self.label2 = Label(self,text="username", bg="#FFB6C1")
        self.label2.place(x=30,y=30)
        self.label3 = Label(self,text="email", bg="#FFB6C1")
        self.label3.place(x=30,y=60)
        self.label4 = Label(self,text="password", bg="#FFB6C1")
        self.label4.place(x=30,y=90)

        # create Entry

        self.entry1 = Entry(self, textvariable=self.username)
        self.entry1.place(x=100, y=30)
        self.entry2 = Entry(self, textvariable=self.gmail)
        self.entry2.place(x=100, y=60)
        self.entry3 = Entry(self, textvariable=self.password)
        self.entry3.place(x=100, y=90)
        # Create Frame
        #self.frame1 = Frame(self)
        #self.frame1.pack()
        # Add buttons
        self.button1 = Button(self, text="submit", command=self.process_information, bg="#FFB6C1")
        self.button1.place(x=30, y=200)

        self.button2 = Button(self, text="go back", command=self.change_to_open_screen, bg="#FFB6C1")
        self.button2.place(x=600, y=30)
        # self.button1.pack(padx=30,pady=120,side=LEFT)

    def process_information(self):
        username = self.username.get()
        gmail = self.gmail.get()
        password = self.password.get()
        if username == "" or password == "" or gmail == "":
            messagebox.showerror("Error", "Please fill out all entries")
            self.username.set("")
            self.gmail.set("")
            self.password.set("")
        else:
            user_info = "1" + str(username) + " " + str(gmail) + " " + str(password)
            client.send_message(user_info)
            # wait for the response from client
            self.response_for_sign_up()

    def response_for_sign_up(self):
        while client.code != 1.0 and client != 1.1:
            if client.code == 1.0:
                # username exists, tell it to user
                self.username.set("")
                self.gmail.set("")
                self.password.set("")
                messagebox.showerror("Error", "username already exists")
                self.withdraw()
                Sign_up_screen(self)
                break

            elif client.code == 1.1:
                # username is fine, let user know he created his account
                self.username.set("")
                self.gmail.set("")
                self.password.set("")
                messagebox.showinfo("Great", "your account has been created, log in now")
                self.withdraw()
                Open_screen(self)
                break

    def change_to_open_screen(self):
        self.withdraw()
        Open_screen(self)


class Log_in_screen(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.protocol("WM_DELETE_WINDOW", client.close_socket)

        self.password = StringVar()
        self.username = StringVar()

        self.geometry("1000x2000")

        # self.bg = PhotoImage(file=background)
        # self.label1 = Label(self, image=self.bg)
        # self.label1.place(x=0, y=0)

        self.configure(background="#FFDEE3")

        self.label2 = Label(self, text="username", bg="#FFDEE3")
        self.label2.place(x=30, y=30)
        self.label3 = Label(self, text="password", bg="#FFDEE3")
        self.label3.place(x=30, y=60)

        self.entry1 = Entry(self, textvariable=self.username)
        self.entry1.place(x=100, y=30)
        self.entry2 = Entry(self, textvariable=self.password)
        self.entry2.place(x=100, y=60)

        self.button1 = Button(self, text="log in", command=self.log_in, bg="#FFB6C1")
        self.button1.place(x=30, y=200)

        self.button2 = Button(self, text="go back", command=self.change_to_open_screen, bg="#FFB6C1")
        self.button2.place(x=600, y=30)

    def change_to_open_screen(self):
        self.withdraw()
        Open_screen(self)

    def log_in(self):
        # send info to socket and see if user exists
        # store info in local variables so that they will stay stringvar type to get more info
        username = self.username.get()
        password = self.password.get()
        if username == "" or password == "":
            messagebox.showerror("Error", "Please fill out all entries")
            # reset variables so user can type again
            self.username.set("")
            self.password.set("")
        else:
            # send user info
            user_login = "2" + str(username)+" "+str(password)
            client.send_message(user_login)
            self.username.set("")
            self.password.set("")
            self.response_log_in(username, password)

    def response_log_in(self, username, password):
        while True:
            if client.logged_in or client.code == 2.2:
                # maybe reset username and password here mate
                messagebox.showinfo("WELCOME", "you are logged in now, welcome "+str(username))
                # save these variables for later activities
                my_user.set_username(username)
                my_user.set_password(password)
                self.withdraw()
                Logged_in_screen(self)
                break
            elif client.code == 2.1:
                self.username.set("")
                self.password.set("")
                messagebox.showerror("Error", "password is incorrect")
                self.withdraw()
                Log_in_screen(self)
                break
            elif client.code == 2.0:
                self.username.set("")
                self.password.set("")
                messagebox.showerror("Error", "username does not exist, please create account first.")
                self.withdraw()
                Open_screen(self)
                break


class Logged_in_screen(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.label5 = None
        self.geometry("1000x2000")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)

        # self.bg = PhotoImage(file=background)
        # self.label1 = Label(self, image=self.bg)
        # self.label1.place(x=0, y=0)

        self.configure(background="#FFDEE3")

        # self.label1 = Label(self, text="hello, "+str(self.username), bg="#FFDEE3")
        # self.label1.place(x=30, y=15) -TAKE CARE OF THIS- PRINT CLIENT NAME WHEN LOGGED IN

        self.button1 = Button(self, text="Friendly mode", bg="#F098A2")
        self.button1.place(x=30, y=40)

        self.button2 = Button(self, text="Upload pattern", command=self.upload_pattern, bg="#F098A2")
        self.button2.place(x=140, y=40)

        self.button3 = Button(self, text="Log out", bg="#F098A2")
        self.button3.place(x=260, y=40)

        self.button4 = Button(self, text="search pattern", bg="#F098A2")
        self.button4.place(x=340, y=40)

        self.button5 = Button(self, text="my uploads", bg="#F098A2")
        self.button5.place(x=460, y=40)

        self.button4 = Button(self, text="search pattern", bg="#F098A2")
        self.button4.place(x=560, y=40)

    def manager_update(self, username):
        # checks if user is manager and updates accordingly
        send_data = "3"+str(username)
        client.send_message(send_data)
        while True:
            if client.manager is not None:
                break
            else:
                continue

    def upload_pattern(self):
        self.manager_update(my_user.get_username())
        if client.manager:
            self.withdraw()
            Upload_pattern(self)
        else:
            messagebox.showerror("Error", "sorry, only managers can upload patterns.")


class Upload_pattern(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.button9 = None
        self.optionmenu4 = None
        self.optionmenu5 = None
        self.current_stitch = None
        self.label4 = None
        self.optionmenu1 = None
        self.beginning = None
        self.label2 = None
        self.geometry("1000x2000")
        self.configure(background="#FFDEE3")
        self.protocol("WM_DELETE_WINDOW", client.close_socket)

        self.my_pattern = Pattern()

        self.rounds = StringVar()

        self.label1 = Label(self, text="number of rounds: ", bg="#FFDEE3")
        self.label1.place(x=10, y=10)
        self.entry1 = Entry(self, textvariable=self.rounds)
        self.entry1.place(x=120, y=10)
        self.button3 = Button(self, text="restart", command=self.start_pattern_again, bg="#FFB6C1")
        self.button3.place(x=500, y=10)
        self.button4 = Button(self, text="submit pattern", command=self.submit_pattern, bg="#FFB6C1")
        self.button4.place(x=600, y=10)
        self.button1 = Button(self, text="submit", command=self.create_pattern_interface, bg="#FFB6C1")
        self.button1.place(x=250, y=10)

    def start_pattern_again(self):
        self.withdraw()
        Upload_pattern(self)

    def is_num(self, str):
        # checking if str is a number, if not, displaying a messagebox indicationg an error
        # will use it in various places.
        if not str.isnumeric():
            messagebox.showerror("Error", "Please enter a number.")
            return False
        return True

    def create_pattern_interface(self):
        is_num = self.is_num(self.rounds.get())
        if is_num:
            rounds = self.rounds.get()
            # save number of rounds in our pattern object
            self.my_pattern.rounds = self.rounds.get()

            # make button and entry dissapear.
            self.button1.place_forget()
            self.entry1.place_forget()

            # display number of rounds.
            self.label1.config(text="number of rounds: "+str(self.my_pattern.rounds))

            self.label2 = Label(self, text="beginning: ", bg="#FFDEE3")
            self.label2.place(x=10, y=30)

            # intiate beginning variable
            self.beginning = StringVar()
            self.beginning.set("None")
            begin_options = ["MR", "Ch"]
            self.optionmenu1 = OptionMenu(self, self.beginning, *begin_options)
            self.optionmenu1.configure(bg="#FFB6C1")
            self.optionmenu1.place(x=80, y=30)
            self.beginning.trace("w", self.beginning_changed)
        else:
            self.rounds.set("")

    def beginning_changed(self, *args):
        if self.beginning.get() == "Ch":
            # self.beginning.trace("w", self.beginning_changed)
            self.chain_num = StringVar()
            self.entry2 = Entry(self, textvariable=self.chain_num)
            self.entry2.place(x=150, y=30)
            self.button2 = Button(self, text="submit", command=self.chain_submitted, bg="#FFB6C1")
            self.button2.place(x=270, y=30)
        elif self.beginning.get() == "MR":
            self.my_pattern.beginning = "MR"
            # self.beginning.trace("w", self.beginning_changed)
            self.optionmenu1.place_forget()
            self.label2.config(text="beginning: MR")
            self.create_rounds_list()

    def chain_submitted(self):
        chain_num = self.chain_num.get()
        if chain_num == "":
            messagebox.showerror("Error", "please fill out number of rounds")
            self.chain_num.set("")
        else:
            self.my_pattern.beginning = "Ch"+str(self.chain_num.get())

            self.label2.config(text="chains: "+str(self.chain_num.get()))
            self.optionmenu1.place_forget()
            self.entry2.place_forget()
            self.button2.place_forget()
            self.create_rounds_list()

    def create_rounds_list(self):

        # ADD ABBERVATIONS WINDOW
        # COUNT TOTAL AUTOMATICALLY

        # define places we will use later.
        x_place = 10
        y_place = 50
        self.x_place_st_button = 10
        self.y_place_st_button = 100

        # this variable controls the for loop, and stops until submit round is pressed
        self.continue_loop = tk.BooleanVar()
        self.continue_loop.set(False)

        #intiate this variable
        self.current_stitch = tk.StringVar(value="")

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        for i in range(int(self.my_pattern.rounds)):
            # initiating these values each round
            self.serial_number = 1
            self.current_round = [""]
            self.times = tk.StringVar()
            self.total = tk.StringVar()
            self.additional_info = tk.StringVar()

            self.label3 = Label(self, text="round " + str(i + 1) + ": ", bg="#FFDEE3")
            self.label3.place(x=x_place, y=y_place)

            self.stitches_label = Label(self, text=self.stringing_current_round(), bg="#FFDEE3")
            self.stitches_label.place(x=x_place + 50, y=y_place)
            # this frame cotains all the option menus that will be created
            self.menus_frame = Frame(self, width=800, height=40, bg="#FFDEE3")
            self.menus_frame.place(x=5, y=y_place + 20)

            self.button5 = Button(self, text="add stitch", command=self.add_stitch, bg="#FFB6C1")
            self.button5.place(x=x_place, y=y_place+55)

            self.button6 = Button(self, text="submit round", command=self.submit_round, bg="#FFB6C1")
            self.button6.place(x=x_place+80, y=y_place+55)

            self.label4 = Label(self, text="] X", bg="#FFDEE3")
            self.label4.place(x=x_place+60, y=y_place)

            self.entry3 = Entry(self, width=5, textvariable=self.times)
            self.entry3.place(x=x_place+80, y=y_place)

            self.label5 = Label(self, text="(", bg="#FFDEE3")
            self.label5.place(x=x_place+120, y=y_place)

            self.entry4 = Entry(self, width=5, textvariable=self.total)
            self.entry4.place(x=x_place + 130, y=y_place)

            self.label6 = Label(self, text=")", bg="#FFDEE3")
            self.label6.place(x=x_place+160, y=y_place)

            self.entry5 = Entry(self, width=60, textvariable=self.additional_info)
            self.entry5.insert(0, "Additional explanation/clarification/information")  # default string
            self.entry5.bind("<FocusIn>", lambda event: self.on_entry_click(event))
            self.entry5.place(x=x_place+175, y=y_place)
            # creating the first option menu, serial number is 0
            self.create_option_menu(0)

            # the for loop waits until continue_loop is changed (when submit round is pressed)
            while not self.continue_loop.get():
                root.update()
            # it was pressed-now update x and y for next round
            y_place += 20
            self.x_place_st_button = x_place
            self.y_place_st_button += 20

            # set as false for next round
            self.continue_loop.set(value=False)
        # all rounds were uploaded-lets call the next method
        # MAKE SURE IF SUBMIT Pattern WAS PRESSED THAT NUMBER OF ROUNDS IS CORRRECT?
        self.pattern_name(y_place)

    def close_window(self):
        # TAKE CARE OF THIS- doesnt exit properly
        self.withdraw()
        client.close_socket()

    def on_entry_click(self, event):
        # deletes default text from entry 5
        if self.entry5.get() == "Additional explanation/clarification/information":
            self.entry5.delete(0, tk.END)

    def stringing_current_round(self):
        # this method turns the current round list into an arranged string-in order to use print in on screen
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
        # button submit round was pressed- lets submit the round!
        # starting by making sure user uploaded all the information we need:
        if not self.current_round:
            messagebox.showerror("Error", "please select stitch type")
        elif self.times.get() == "":
            messagebox.showerror("Error", "please fill out number of times")
        elif self.total.get() == "":
            messagebox.showerror("Error", "please fill out total number of stitches")
        else:
            # all info was uploaded. first we shorten the list in case user didnt use all stitches
            while "" in self.current_round:
                self.current_round.remove("")

            if self.additional_info.get() != "" and self.additional_info.get() != "Additional explanation/clarification/information":
                # let's add information to rounds_list- adding the additional info (which is not necessary)
                self.my_pattern.rounds_list.append([self.current_round, self.times.get(), self.total.get(), self.additional_info.get()])

                # printing nicely all the information from this round
                self.stitches_label.configure(text=self.stringing_current_round() + " X " + self.times.get() + " ( " + self.total.get() + " )  " + self.additional_info.get())
            else:
                # let's add information to rounds_list
                self.my_pattern.rounds_list.append([self.current_round, self.times.get(), self.total.get()])

                # user did not add info
                self.stitches_label.configure(text=self.stringing_current_round() + " X " + self.times.get() + " ( " + self.total.get() + " )")

            # deleting this round's widgets
            self.label4.place_forget()
            self.label5.place_forget()
            self.label6.place_forget()
            self.entry3.place_forget()
            self.entry4.place_forget()
            self.entry5.place_forget()
            self.button5.place_forget()
            self.button6.place_forget()
            # deleting all the option menus
            for widget in self.menus_frame.winfo_children():
                widget.destroy()
            # letting the for loop know it may continue to next round!
            self.continue_loop.set(True)
            print(self.my_pattern.rounds_list)

    def add_stitch(self):
        # add stitch button was pressed! lets add a stitch
        # add an empty string to current_round- it will be updated when user chooses stitch
        self.current_round.append("")
        # create the new option menu
        self.create_option_menu(self.serial_number)
        # add 1 to the number of our stitches (in this round)
        self.serial_number+=1

    def create_option_menu(self, serial_number):
        # create an option menu
        stitches_options = ["ch", "sc", "inc", "dec", "dc", "hdc", "tc", "slst", "sk", "invdec"]
        self.optionmenu2 = OptionMenu(self.menus_frame, self.current_stitch, *stitches_options, command=lambda *args: self.stitch_chosen(serial_number, self.current_stitch.get(), *args))
        self.optionmenu2.configure(bg="#FFB6C1")
        self.optionmenu2.pack(side=LEFT, padx=5)

    def stitch_chosen(self, serial_number, value, *args):
        # user chose stitch
        # update current round list
        self.current_round[serial_number] = value
        # set current stitch to an empty string
        self.current_stitch.set("")
        # save the current length of stitches label
        current_length = self.stitches_label.winfo_reqwidth()
        # configure this label into what user chose, using stringing_currnet_round()
        self.stitches_label.configure(text=self.stringing_current_round())
        # calculate how many pixels were added to stitches label, and update the rest of the widgets accordingly
        add_lendth = self.stitches_label.winfo_reqwidth()-current_length
        self.label4.place(x=self.label4.winfo_x() + add_lendth, y=self.label4.winfo_y())
        self.label5.place(x=self.label5.winfo_x() + add_lendth, y=self.label5.winfo_y())
        self.label6.place(x=self.label6.winfo_x() + add_lendth, y=self.label6.winfo_y())
        self.entry3.place(x=self.entry3.winfo_x() + add_lendth, y=self.entry3.winfo_y())
        self.entry4.place(x=self.entry4.winfo_x() + add_lendth, y=self.entry4.winfo_y())
        self.entry5.place(x=self.entry5.winfo_x() + add_lendth, y=self.entry5.winfo_y())

    def pattern_name(self, y):
        # entering pattern's name
        self.label7 = Label(self, text="pattern name: ", bg="#FFDEE3")
        self.label7.place(x=10, y=y)
        self.name = tk.StringVar()
        self.entry6 = Entry(self, width=20, textvariable=self.name)
        self.entry6.place(x=100, y=y)
        self.button7 = Button(self, text="submit", command=lambda: self.name_submitted(y), bg="#FFB6C1")
        self.button7.place(x=235, y=y-3)

        self.label8 = Label(self, text="upload picture: ", bg="#FFDEE3")

    def name_submitted(self, y):
        # name entered and submitted-print it on the screen, update my_pattern
        self.my_pattern.pattern_name = self.name.get()
        self.entry6.place_forget()
        self.button7.place_forget()
        self.label7.configure(text="pattern name: "+self.name.get())
        self.pattern_category(y+20)

    def pattern_category(self, y):
        # enter pattern's category
        self.categories = ["Amigurumi", "Clothing", "Other"]
        self.category = tk.StringVar()
        self.optionmenu3 = OptionMenu(self, self.category, *self.categories, command=lambda x: self.category_selected(y))
        self.optionmenu3.configure(bg="#FFB6C1")
        self.label9 = Label(self, text="Category: ", bg="#FFDEE3")
        self.label9.place(x=10, y=y)
        self.optionmenu3.place(x=70, y=y)
        # PUT OPTION MENUS AND DEFINES IN THE INIT

    def category_selected(self, y):
        self.amigurumi = ["animals", "dolls", "plants", "characters", "other"]
        self.clothes = ["cardigans", "shirts and tops", "dresses", "scarfs", "beanies", "swimwear", "bags", "other"]
        self.optionmenu3.place_forget()
        self.my_pattern.category = self.category.get()
        self.label9.configure(text="Category: "+self.category.get())
        if self.category.get() == "Amigurumi":
            self.subcategory = tk.StringVar()
            self.optionmenu4 = OptionMenu(self, self.subcategory, *self.amigurumi, command=lambda x: self.subcategory_selected(y))
            self.optionmenu4.configure(bg="#FFB6C1")
            self.optionmenu4.place(x=135, y=y)
        elif self.category.get() == "Clothing":
            self.subcategory = tk.StringVar()
            self.optionmenu5 = OptionMenu(self, self.subcategory, *self.clothes, command=lambda x: self.subcategory_selected(y))
            self.optionmenu5.configure(bg="#FFB6C1")
            self.optionmenu5.place(x=120, y=y)
        else:
            self.pattern_hook(y+20)

    def subcategory_selected(self, y):
        self.label9.configure(text="Category: "+self.category.get()+", "+self.subcategory.get())
        self.my_pattern.subcategory = self.subcategory.get()
        if self.optionmenu4 is not None:
            self.optionmenu4.place_forget()
        if self.optionmenu5 is not None:
            self.optionmenu5.place_forget()
        self.pattern_hook(y+20)

    def pattern_hook(self, y):
        self.hooks = ["0.6 mm", "0.75 mm", "1.0 mm", "1.25 mm", "1.5 mm", "1.75 mm", "2.0 mm", "2.25 mm", "2.5 mm", "2.75 mm", "3.0 mm", "3.25 mm", "3.75 mm", "4.0 mm", "4.5 mm", "5.0 mm", "5.5 mm", "6.0 mm", "6.5 mm", "7.0 mm", "8.0 mm", "9.0 mm", "10.0 mm", "12.0 mm", "15.0 mm", "16.0 mm"]
        self.hook = tk.StringVar()
        self.label10 = Label(self, text="Hook size: ", bg="#FFDEE3")
        self.label10.place(x=10, y=y)
        self.optionmenu6 = OptionMenu(self, self.hook, *self.hooks, command=lambda x: self.hook_selected(y))
        self.optionmenu6.configure(bg="#FFB6C1")
        self.optionmenu6.place(x=70, y=y)

    def hook_selected(self, y):
        self.optionmenu6.place_forget()
        print(self.hook.get())
        self.label10.configure(text="Hook size: "+self.hook.get())
        self.my_pattern.hook = self.hook.get()
        self.materials(y+20)

    def materials(self, y):
        self.eyes = tk.IntVar()
        self.scissors = tk.IntVar()
        self.needle = tk.IntVar()
        self.fill = tk.IntVar()
        self.buttons = tk.IntVar()
        self.label13 = Label(self, text="Materials-", bg="#FFDEE3")
        self.label13.place(x=10, y=y)
        self.cb1 = Checkbutton(self, text="Safety eyes", variable=self.eyes, onvalue=1, offvalue=0, command=lambda: self.eyes_checked(y+20), bg="#FFDEE3")
        self.cb1.place(x=10, y=y+20)
        self.cb2 = Checkbutton(self, text="Scissors", variable=self.scissors, onvalue=1, offvalue=0, command=lambda: self.scissors_checked(y+40), bg="#FFDEE3")
        self.cb2.place(x=10, y=y+40)
        self.cb3 = Checkbutton(self, text="Tapestry needle", variable=self.needle, onvalue=1, offvalue=0, command=lambda: self.needle_checked(y + 60), bg="#FFDEE3")
        self.cb3.place(x=10, y=y+60)
        self.cb4 = Checkbutton(self, text="Pollyfiber fill", variable=self.fill, onvalue=1, offvalue=0, command=lambda: self.fill_checked(y + 80), bg="#FFDEE3")
        self.cb4.place(x=10, y=y + 80)
        self.cb5 = Checkbutton(self, text="Buttons", variable=self.buttons, onvalue=1, offvalue=0, command=lambda: self.buttons_checked(y + 100), bg="#FFDEE3")
        self.cb5.place(x=10, y=y + 100)
        self.y_pictures = 40
        self.button8 = tk.Button(self, text='Upload Picture', width=20, command=lambda: self.upload_file(), bg="#FFB6C1")
        self.button8.place(x=10, y=y+130)

    # def upload_file(self):
    #     try:
    #         f_types = [('Jpg Files', '*.jpg')]
    #         filename = filedialog.askopenfilename(filetypes=f_types)
    #         pil_image = Image.open(filename)
    #         pil_image.thumbnail((200, 200))
    #         #img_resized = pil_image.resize((400, 200))  # new width & height
    #         img = ImageTk.PhotoImage(pil_image)
    #         #img_bytes = img.tobytes()
    #
    #         self.display_picture(img)
    #         #self.my_pattern.pictures.append(img_bytes)
    #     except Exception as e:
    #         print(e)
    #
    # def display_picture(self, img):
    #     self.button9 = tk.Button(self, image=img)
    #     self.button9.place(x=500, y=self.y_pictures)
    #     self.y_pictures += 200

    def upload_file(self):
        try:
            f_types = [('Jpg Files', '*.jpg')]
            filename = filedialog.askopenfilename(filetypes=f_types)
            if filename:
                pil_image = Image.open(filename)
                pil_image.thumbnail((200, 200))
                img = ImageTk.PhotoImage(pil_image)

                if img:
                    self.display_picture(img)
                else:
                    messagebox.showerror("Error", "Could not load image")

            else:
                messagebox.showerror("Error", "No file selected")

        except Exception as e:
            print("Error:", e)

    def display_picture(self, img):

        self.button9 = tk.Button(self, image=img)
        self.button9.place(x=500, y=self.y_pictures)
        # Make sure that the button is visible by checking the current value of self.y_pictures
        self.y_pictures += 200

    def eyes_checked(self, y):
        self.cb1.place_forget()
        self.label11 = Label(self, text="Safety eyes: ", bg="#FFDEE3")
        self.label11.place(x=10, y=y)
        self.eyes_sizes = ["5 mm", "6 mm", "7 mm", "8 mm", "9 mm", "10 mm", "12 mm", "14 mm", "16 mm"]
        self.eyes_size = tk.StringVar()
        self.optionmenu7 = OptionMenu(self, self.eyes_size, *self.eyes_sizes, command=self.eyes_chosen)
        self.optionmenu7.configure(bg="#FFB6C1")
        self.optionmenu7.place(x=75, y=y)

    def eyes_chosen(self, size):
        self.label11.configure(text="-Safety eyes: "+self.eyes_size.get())
        self.optionmenu7.place_forget()

    def scissors_checked(self, y):
        self.cb2.place_forget()
        self.label12 = Label(self, text="-Scissors", bg="#FFDEE3")
        self.label12.place(x=10, y=y)

    def needle_checked(self, y):
        self.cb3.place_forget()
        self.label13 = Label(self, text="-Tapestry needle", bg="#FFDEE3")
        self.label13.place(x=10, y=y)

    def fill_checked(self, y):
        self.cb4.place_forget()
        self.label14 = Label(self, text="-Polyfiber fill", bg="#FFDEE3")
        self.label14.place(x=10, y=y)

    def buttons_checked(self, y):
        self.cb5.place_forget()
        self.b_amount = tk.StringVar()
        self.label15 = Label(self, text="-Buttons- amount: ", bg="#FFDEE3")
        self.label15.place(x=10, y=y)
        self.entry7 = Entry(self, width=5, textvariable=self.b_amount)
        self.entry7.place(x=115, y=y)
        self.button8 = Button(self, text="submit", command=lambda: self.button_ammount(y), bg="#FFB6C1")
        self.button8.place(x=160, y=y)

    def button_ammount(self, y):
        self.entry7.place_forget()
        self.button8.place_forget()
        self.label15.configure(text="-Buttons- amount: "+self.b_amount.get()+"  ,size: ")
        self.button_sizes = ["7.5 mm", "8 mm", "9 mm", "9.5 mm", "10 mm", "10.5 mm", "11.5 mm", "12.5 mm", "14 mm", "15 mm", "16 mm", "18 mm", "19 mm", "20 mm", "21 mm", "23 mm", "24 mm", "25 mm", "26 mm", "28 mm"]
        self.b_size = tk.StringVar()
        self.optionmenu8 = OptionMenu(self, self.b_size, *self.button_sizes, command=self.size_selected)
        self.optionmenu8.configure(bg="#FFB6C1")
        self.optionmenu8.place(x=160, y=y)

    def size_selected(self, a):
        self.optionmenu8.place_forget()
        self.label15.configure(text="-Buttons- amount: "+self.b_amount.get()+"  ,size: "+self.b_size.get())

    def submit_pattern(self):
            # check that pattern is full
            if len(self.my_pattern.rounds_list) == 0:
                messagebox.showerror("Error", "sorry, you can not submit an empty pattern")
            else:
                # create materials list. first make sure we have what we need.
                if self.buttons.get() == 1 and (self.b_size.get() == "" or self.b_amount.get() == ""):
                    messagebox.showerror("Error", "please fill out buttons' amount and size.")
                else:
                    if self.eyes.get() == 1 and self.eyes_size.get() == "":
                        messagebox.showerror("Error", "please fill out eyes' size.")
                    else:
                        # creating materials list.
                        if self.eyes.get():
                            self.my_pattern.materials.append([1, self.eyes_size.get()])
                        else:
                            self.my_pattern.materials.append([0, 0])
                        self.my_pattern.materials.extend((self.scissors.get(), self.needle.get(), self.fill.get()))
                        if self.buttons.get():
                            self.my_pattern.materials.append([1, self.b_amount.get(), self.b_size.get()])
                        else:
                            self.my_pattern.materials.append([0, 0, 0])
                        print(self.my_pattern.materials)
                        # send pattern to server
                        self.my_pattern.print_pattern()

                        self.my_pattern.code = "4"
                        serialized_object = pickle.dumps(self.my_pattern)
                        client.my_socket.send(serialized_object)
                        messagebox.showinfo("Great", "Your pattern has been uploaded to the server")
                        # TAKE CARE OF SERER SIDE

        # for round in range(self.rounds.get()):

        # self.var = StringVar(self)
        # self.var.set(self.list_history[0][1])  # Set the default value to the first question
        # self.question_list = [' '.join(question.split()[:-2]) for time, question, answer in self.list_history]
        # self.option_menu = OptionMenu(self, self.var, *self.question_list, command=self.print_answer_for_question)
        # self.option_menu.config(font=('Open Sans', 12, 'normal'), width=30)
        # self.option_menu["menu"].config(font=('Open Sans', 12, 'normal'))
        # self.option_menu.place(x=605, y=55)



root = tk.Tk()
root.withdraw()
Open_screen(root)
root.mainloop()


