"""
Author: Mariska Temming, S1106242
Summary: - The startmenu is the main of the SFTool
         - First it makes a memory dump of the system
         - Then it shows the GUI of the SFTool
         - The user could choose three options in the GUI: "View database", "Quit" and "Start malware scan"
         - When the user clicks on "Start malware scan", SFTool is scanning the system of availability of malware
         - When the user clicks on "View database", the database (SFT.db) is shown in the console
         - When the user clicks on "Quit", the GUI closes
"""

import PySimpleGUI as sg  # pip install PySimpleGUI
import datetime
from psutil import virtual_memory
from time import sleep

from case import Case
from database_helper import insert_data_case_information
from database_helper import select_database
from sys_specs import register_system_specs_to_database
from hashing import get_pathname_and_hashes
from compare_hashes import compare_hashes
from hashing import convert_md5_to_sha1
from network_checker import internet_on
from virustotal import register_malware_to_database
from malware_copy import malware_copy
import shutil


# Shows the data of the database in the console
def view_database():
    select_database()
    return None


# Update the status mode in the GUI
def update_status_mode(window, status_mode):
    window.FindElement('_STATUS_').Update(status_mode)
    window.Refresh()
    sleep(1)


def creating_memory_dump(window):
    empty_row = sg.Text('', size=(1, 1))
    mem = virtual_memory()
    mem = mem.total


    total, used, free = shutil.disk_usage("\\")

    print("Total: %d GB" % (total // (2 ** 30)))
    print("Used: %d GB" % (used // (2 ** 30)))
    print("Free: %d GB" % (free // (2 ** 30)))

    start = sg.Button('Start memory dump', size=(17, 1), font=('Arial', 18), button_color=('black', 'white'))
    cancel = sg.Button('Cancel', size=(5, 1), font=('Arial', 18), button_color=('black', 'white'))

    layout2 = [
        [sg.Text('Memory Dump', size=(31, 2), text_color='blue', font=('Arial', 30))],
        [sg.Text('Total disk space: ', size=(25, 1), font=('Arial', 14)), sg.Text(total, size=(15, 1), font=('Arial', 14))],
        [sg.Text('Used disk space: ', size=(25, 1), font=('Arial', 14)), sg.Text(used, size=(15, 1), font=('Arial', 14))],
        [sg.Text('Free disk space: ', size=(25, 1), font=('Arial', 14)), sg.Text(free, size=(15, 1), font=('Arial', 14))],
        [sg.Text('Total system memory size: ', size=(25, 1), font=('Arial', 14)), sg.Text(mem, size=(15, 1), font=('Arial', 14))],
        [empty_row],
        [sg.Text('Please enter an output destination: '), sg.InputText(key='path'), sg.FolderBrowse()],
        [start, cancel]
    ]

    window2 = sg.Window('SFT - Memory Dump').Layout(layout2)

    while True:
        event, value = window2.Read()
        if event == 'Cancel':
            window2.Close()
            break

        elif event == 'Start memory dump':
            path = value['path']
            if path == '':
                sg.Popup('Please select an output destination')
            else:
                print("Creating memory dump...")
                print(path)
                update_status_mode(window, "Creating memory dump...")

    return window


# The function scan malware is the main program of the SFTool: SFTool is scanning the system of availability of malware
def scan_malware(window, file_size):
    result = 'OK'
    try:
        print("The malware scan has been started" + "\n")
        update_status_mode(window, "The malware scan has been started")

        print('Registrating the system specifications... ' + "\n")
        update_status_mode(window, "Registrating the system specifications... ")
        register_system_specs_to_database()  # Write system specifications to database

        print('Calculating hashes... ' + "\n")
        update_status_mode(window, "Calculating hashes...")
        get_pathname_and_hashes(file_size)  # Calculate the md5 hashes of the files on the system

        # Check if the system has an connection to the internet
        if internet_on():
            print('The system is connected to the internet!' + "\n")
            update_status_mode(window, "The system is connected to the internet!")

            print('Comparing system hashes with VirusShare... ' + "\n")
            update_status_mode(window, "Comparing system hashes with VirusShare... ")
            compare_hashes()  # Offline database: virusshare (compare system hashes with the hahses of VirusShare)

            print('Converting MD5 to SHA1...' + "\n")
            update_status_mode(window, "Converting MD5 to SHA1...")
            convert_md5_to_sha1()  # Converts the malware md5 hashes to sha1

            print("\n" + 'Checking malware name in VirusTotal... ' + "\n")
            update_status_mode(window, "Checking malware name in VirusTotal...  ")
            register_malware_to_database()  # Online database: VirusTotal (writes the malware information to the
            # database)
        elif not internet_on():
            print('The system is not connected to the internet!' + "\n")
            update_status_mode(window, "The system is not connected to the internet!")

            print('Comparing system hashes with VirusShare... ' + "\n")
            update_status_mode(window, "Comparing system hashes with VirusShare... ")
            compare_hashes()  # Offline database: virusshare (compare system hashes with the hahses of VirusShare)

            print('Converting MD5 to SHA1...' + "\n")
            update_status_mode(window, "Converting MD5 to SHA1...")
            convert_md5_to_sha1()  # Converts the malware md5 hashes to sha1

        print('Copying malware to USB drive...')
        update_status_mode(window, "Copying malware to USB drive...")
        malware_copy()  # Copies the malware to dictionary "malware_copies" on the USB-drive

        print('The malware scan is finished!')
        update_status_mode(window, "The malware scan is finished!")

    except Exception as e:
        print(e)
        result = e

    return result


# Shows the GUI of the SFTool
def show_window():
    status_mode = sg.Text('Welcome!', size=(45, 1), font=('Arial', 14), text_color='red', key='_STATUS_')
    empty_row = sg.Text('', size=(1, 1))  # creates a empy row for the format of the GUI
    # create buttons
    start_malware = sg.Button('Start malware scan', size=(17, 1), font=('Arial', 18), button_color=('black', 'white'),
                              enable_events=True, )
    create_memory_dump = sg.Button('Create memory dump', size=(17, 1), font=('Arial', 18),
                                   button_color=('black', 'white'),
                                   enable_events=True, )
    view_databasee = sg.Button('View Database', size=(13, 1), font=('Arial', 18), button_color=('black', 'white'))
    quit_startmenu = sg.Button('Quit', size=(5, 1), font=('Arial', 18), button_color=('black', 'white'))

    # Layout the design of the GUI
    layout = [
        #[sg.Text('SFTool - Synergy Forensics Triage Tool', size=(31, 2), text_color='blue', font=('Arial', 30))],
        [sg.Image(filename='SF_logo.png')],
        [sg.Text('Case information', size=(15, 1), font=('Arial', 16, 'bold'))],
        [sg.Text('Case Name:', size=(15, 1), font=('Arial', 14)), sg.InputText(key='_CASE_NAME_', font=('Arial', 14))],
        [sg.Text('Start Number:', size=(15, 1), font=('Arial', 14)),
         sg.InputText(key='_START_NUMBER', font=('Arial', 14))],
        [sg.Text('Investigator:', size=(15, 1), font=('Arial', 14)),
         sg.InputText(key='_INVESTIGATOR_', font=('Arial', 14))],
        [sg.Text('Comment:', size=(15, 1), font=('Arial', 14)), sg.InputText(key='_COMMENT_', font=('Arial', 14))],
        [empty_row],
        [sg.Text('Filters', size=(15, 1), font=('Arial', 16, 'bold'))],
        [sg.Text('File Size Limit (MB):', size=(15, 1), font=('Arial', 14)),
         sg.InputText(key='_FILE_SIZE_', font=('Arial', 14))],
        [empty_row],
        [sg.Text('Status: ', size=(15, 1), font=('Arial', 14)), status_mode],
        [empty_row],
        [empty_row],
        [view_databasee, empty_row, quit_startmenu, empty_row, create_memory_dump, start_malware],
        [empty_row]
    ]

    window = sg.Window('SFT - Start menu').Layout(layout)  # Shows the window to the user

    while True:
        event, value = window.Read()  # Read the Window
        # Take appropriate action based on button
        if event == 'View Database':
            view_database()

        elif event == 'Create memory dump':
            creating_memory_dump(window)

        elif event == 'Start malware scan':

            case_name = value['_CASE_NAME_']
            start_number = value['_START_NUMBER']
            investigator_name = value['_INVESTIGATOR_']
            comment = value['_COMMENT_']
            file_size = value['_FILE_SIZE_']
            time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

            # If case information is filled then start the malware scan
            if case_name == '' or start_number == '' or investigator_name == '':
                sg.Popup("Fill in the case data on the start menu. " + "\n" +
                         "Required: case name, start number and investigator's name" + "\n")
                print("Fill in the case data on the start menu. " + "\n" +
                      "Required: case name, start number and investigator's name" + "\n")

            # Else if file size is not a number, then show a pop up
            elif not file_size.isdigit():
                sg.Popup("Please fill in a number for the file size(MB)")
                print("Please fill in a number for the file size(MB)")

            # Else do not start the malware scan and fill in the blanks
            else:
                print("Time: " + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
                print("Event: " + event + "\n" + "\n", "Case Name: " + "\t" + case_name + "\n",
                      "Start Number: " + "\t" +
                      start_number + "\n", "Investigator: " + "\t" + investigator_name + "\n", "Comment: " +
                      "\t" + "\t" + comment + "\n")

                case_data = Case(case_name, start_number, investigator_name, comment, time)
                insert_data_case_information(case_data)  # Write case information to database

                result = scan_malware(window, file_size)
                print(result)  # Print the status on the console
                status_mode.Update(result)  # Update the status in the GUI

        elif event == 'Quit' or event is None:
            window.Close()
            break

    return window


def sftool():
    try:
        show_window()
    except Exception as e:
        print(e)


def main():
    sftool()


if __name__ == '__main__':
    main()
