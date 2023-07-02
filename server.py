# written by Shaked Bitan
# server side: wait for clients to connect and respond accordingly
import io
import socket
import sys
import threading
from database import *
import pickle
from class_pattern import Pattern
import subprocess
import traceback
import os
import csv
import time
import numpy as np
import sklearn
import pandas

# constants
SOCKET_BUFFER_SIZE = 4096
LOCK = threading.Lock()
# this file is used to save the data about users-how long patterns took them
CSV_FILE = r"C:\Users\Toshiba\PycharmProjects\tensorEnv\ml-file.csv"
# this file is the program that runs the machine learning process
ML_PATH = r"C:\Users\Toshiba\PycharmProjects\tensorEnv\ml.py"
NEW_LINES_ADDED = 2


def count_lines_in_csv_file():
    """count lines in the csv file"""
    with open(CSV_FILE, 'r') as file:
        reader = csv.reader(file)
        line_count = sum(1 for _ in reader)  # count the lines in the CSV file
    return line_count


def update_client_when_needed(client_socket):
    """ this method is waiting for the csv file to be changed, and then sends update to all the users to change the dictionary. """
    current_lines_count = int(count_lines_in_csv_file())
    ml_process = subprocess.run([sys.executable, ML_PATH], capture_output=True, text=True)
    prediction = ml_process.stdout.strip()
    send_data_to_client(client_socket, "?"+prediction)

    while True:
        if current_lines_count + NEW_LINES_ADDED == count_lines_in_csv_file():
            # the csv file was modified. now we send updated list of times to the server
            current_lines_count = count_lines_in_csv_file()
            ml_process = subprocess.run([sys.executable, ML_PATH], capture_output=True, text=True)
            prediction = ml_process.stdout.strip()
            send_data_to_client(client_socket, "?" + prediction)


def add_line_to_csv_file(username, level, time):
    """adds a new line to csv file (the file that the ML model reads from)"""
    data = [str(username), level, time]
    with open(CSV_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)
    print("DATA HAS BEEN WRITTEN TO CSV FILE")


def send_data_to_client(client_socket, data):
    """sends to socket the given data"""
    len_message = str(len(data)).zfill(8)
    if isinstance(data, bytes):
        # data is already encoded
        # add length and send.
        message_to_send = len_message.encode() + data
        client_socket.send(message_to_send)
    else:
        message_to_client = len_message + data
        client_socket.send(message_to_client.encode())


def recieve_data_in_chunks(len_message_stripped, client_socket):
    """receive data in chunks"""
    received_data = b""
    while len(received_data) < int(len_message_stripped):
        chunk = client_socket.recv(min(int(len_message_stripped) - len(received_data), SOCKET_BUFFER_SIZE))
        if not chunk:
            break
        received_data += chunk
    return received_data


def receive_data_from_client(client_socket):
    """
    Receives data from client. Loops until the received buffer is smaller than
    the buffer maximal size. Returns the data.
    """
    len_message = client_socket.recv(8).decode().strip()
    # if len is longer than 10000, receive in chunks
    if int(len_message) > 10000:
        # data is pattern object
        buffer_data = recieve_data_in_chunks(len_message,client_socket)
        return buffer_data

    else:
        buffer_data = client_socket.recv(int(len_message))
        return buffer_data.decode()


def connect_to_db():
    """creating connection to db"""
    conn, cursor = create_connection(db_path)
    conn.commit()
    return conn, cursor


def handle_client(data, client_socket):
    """handle client request"""
    LOCK.acquire()  # activate lock
    conn1, cursor1 = connect_to_db()
    try:
        if data == "quit":
            # client wants to close connection, close connection (by returning 0)
            return 0
        if isinstance(data, bytes):
            pattern = pickle.loads(data)
            try:
                # client wants to upload a pattern to server.
                username = pattern.get_username()
                date = pattern.get_date()
                pattern_name = pattern.get_pattern_name()
                category = pattern.get_category()
                subcategory = pattern.get_subcategory()
                d_level = pattern.get_d_level()
                upload_pattern_to_db(cursor1, username, date, pattern_name, category, subcategory, d_level, data)
                conn1.commit()
                # let user know pattern has been uploaded
                send_data_to_client(client_socket, "4.1")
                print("USER: " + username + " UPLOADED A NEW PATTERN")
            except Exception as e:
                print(e)
                # let user know that pattern could not be uploaded
                send_data_to_client(client_socket, "4.0")
            return 1
        if data[0] == "1":
            # client wants to sign up, process data
            [username, gmail, password, salt] = data.split()
            username = username[1:]
            if does_username_exists(cursor1, username):
                # username exists, let user know.
                send_data_to_client(client_socket, "1.0")
            else:
                add_new_user(cursor1, gmail, username, password, salt)
                conn1.commit()
                send_data_to_client(client_socket, "1.1")
                print("NEW USER ADDED: "+username)
            return 1
        elif data[0] == "2":
            # get user password and salt
            username = data[1:]
            [hashed_password, salt] = get_user_password_and_salt(cursor1, username)
            send_data_to_client(client_socket, "2"+hashed_password+" "+salt)
            return 1
        elif data[0] == "3":
            # check if user is a manager
            if is_user_manager(cursor1, data[1:]):
                # user is a manager. send data to client
                send_data_to_client(client_socket, "3.1")
            else:
                # user is not a manager
                send_data_to_client(client_socket, "3.0")
            return 1
        elif data[0] == "5":
            # get random pattern from database
            try:
                send_data_to_client(client_socket, get_random_pattern(cursor1))
                #t.sleep(1)

            except Exception as e:
                print(e)
            return 1
        elif data[0] == "6":
            # client wants to know if pattern was started
            strings = data[1:].split()
            username = strings[0]
            pattern_name = " ".join(strings[1:])
            pattern_started = was_pattern_started(cursor1, username, pattern_name)
            if pattern_started:
                send_data_to_client(client_socket, "6.1")
            else:
                send_data_to_client(client_socket, "6.0")
            return 1
        elif data[0] == "7":
            # update or create a new line in patterns in progress
            try:
                strings = data[3:].split()
                username = strings[0]
                rounds_done = strings[1]
                date = strings[2]
                time = float(strings[3])
                pattern_name = " ".join(strings[4:])
                if data[2] == "0":
                    # we need to create a new line
                    start_new_pattern(cursor1, username, pattern_name, rounds_done, date, time)
                    conn1.commit()
                    send_data_to_client(client_socket, "7.1")
                    print("ADDED A NEW LINE IN PATTERNS IN PROGRESS FOR USER "+username)
                else:
                    # update date and rounds done and time
                    current_time = get_time_pattern(cursor1, username, pattern_name)
                    if current_time is None:
                        current_time = 0
                    sum_time = current_time + time
                    update_pattern_in_progress(cursor1, username, pattern_name, rounds_done, date, sum_time)
                    conn1.commit()
                    send_data_to_client(client_socket, "7.1")
            except Exception as e:
                # something went wrong
                print(e)
                send_data_to_client(client_socket, "7.2")
            return 1
        elif data[0] == "8":
            # client wants to get a pattern from db
            pattern_obj = get_pattern(cursor1, data[1:])
            if not pattern_obj:
                print("an error occured trying to pass a pattern object")
            else:
                send_data_to_client(client_socket, pattern_obj)
            return 1
        elif data[0] == "9":
            # get how many rounds were done in a pattern and username, from db
            strings = data[1:].split()
            username = strings[0]
            pattern_name = " ".join(strings[1:])
            rounds_done = get_rounds_done(cursor1, username, pattern_name)
            send_data_to_client(client_socket, "9"+str(rounds_done))
            return 1
        elif data[0] == "0":
            # client wants to delete row from patterns in progress db
            strings = data[1:].split()
            username = strings[0]
            pattern_name = " ".join(strings[1:])
            try:
                delete_row_from_patterns_in_progress(cursor1, username, pattern_name)
                conn1.commit()
                send_data_to_client(client_socket, "0.1")
            except Exception as e:
                print(e)
                send_data_to_client(client_socket, "0.0")
            return 1
        elif data[0] == "$":
            # client wants to get list of people who wants to become managers
            future_managers = want_to_be_managers(cursor1)
            # now we send the list of names to client
            send_data_to_client(client_socket, "$"+future_managers)
            return 1
        elif data[0] == "#":
            # pattern was done. update patterns done AND the list of times.
            strings = data[1:].split()
            username = strings[0]
            time = float(strings[1])
            level = strings[2]
            pattern_name = " ".join(strings[3:])
            # we check if there is a line in patterns in progress, if so, we add the times. if not- we take the current time.
            if was_pattern_started(cursor1, username, pattern_name):
                # lets get the time
                add_time = get_time_pattern(cursor1, username, pattern_name)
                time += add_time
            # now we write to csv file
            add_line_to_csv_file(username, level, time)
            # now we write the pattern in patterns done
            pattern_done(cursor1, username, pattern_name)
            conn1.commit()
            return 1
        elif data[0] == "@":
            # get users work
            username = data[1:]
            work = users_work(cursor1, username)
            send_data_to_client(client_socket, "@"+work)
            return 1
        elif data[0] == "%":
            username = data[2:]
            if data[1] == "1":
                # user has been approved as manager.
                approve_user(cursor1, username)
                send_data_to_client(client_socket, "%1")
            else:
                # user has not been aproved to be a manager
                disapprove_user(cursor1, username)
                send_data_to_client(client_socket, "%0")
            conn1.commit()
            return 1
        if data[0] == "&":
            # get manager value
            username = data[1:]
            manager_state = get_username_manager_state(cursor1, username)
            send_data_to_client(client_socket, "&"+str(manager_state))
            conn1.commit()
            return 1
        if data[0] == "!":
            # count how many paterns
            rows_number = how_many_patterns(cursor1)
            send_data_to_client(client_socket, "!"+str(rows_number))
            return 1
        if data[0] == "*":
            # send manager request
            try:
                username = data[1:]
                manager_request(cursor1, username)
                conn1.commit()
                send_data_to_client(client_socket, "*")
            except Exception as e:
                print(e)
            return 1
        if data[0] == "+":
            # get list of all patterns in progress of user
            try:
                patterns_in_progress = users_patterns_in_progress(cursor1, data[1:])
                send_data_to_client(client_socket, "+"+patterns_in_progress)
            except Exception as e:
                print(e)
            return 1
        if data[0] == "~":
            # get list of all patterns manager ha uploded
            try:
                user_uploads = users_uploads(cursor1, data[1:])
                send_data_to_client(client_socket, "~"+user_uploads)
            except Exception as e:
                print(e)
            return 1
        return 0
    finally:
        conn1.close()  # close connection to db
        LOCK.release()  # release db lock
        print("Closing connection to SQLite DB")


def client_connect(client_socket, client_address):
    # client connected
    print("NEW CONNECTION FROM " + str(client_socket))
    # call while loop that updates client's ml data:

    # modify the dict of client's ml dict
    current_lines_count = int(count_lines_in_csv_file())
    ml_process = subprocess.run([sys.executable, ML_PATH], capture_output=True, text=True)
    prediction = ml_process.stdout.strip()
    send_data_to_client(client_socket, "?" + prediction)

    while True:
        # get data from client
        data = receive_data_from_client(client_socket)
        value = handle_client(data, client_socket)
        if value == 0:
            # client wants to exit or data is not valid
            print("CLIENT DISCONNECTED")
            break
        # constantly keep updating the dict of each client
        if current_lines_count + NEW_LINES_ADDED == count_lines_in_csv_file():
            # the csv file was modified. now we send updated list of times to the server
            current_lines_count = count_lines_in_csv_file()
            ml_process = subprocess.run([sys.executable, ML_PATH], capture_output=True, text=True)
            prediction = ml_process.stdout.strip()
            send_data_to_client(client_socket, "?" + prediction)
            print("DICT UPDATED")

    print("CLOSING CONNECTION FROM" + str(client_socket))
    client_socket.close()


def main():
    # create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("172.20.10.2", 2800))
    server_socket.listen(5)
    print("Server is up and running")
    while True:
        # constantly wait for clients to connect and create a new thread for each one of them
        client_socket, client_address = server_socket.accept()
        try:
            client_handler = threading.Thread(target=client_connect, args=(client_socket, client_address))
            client_handler.start()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
