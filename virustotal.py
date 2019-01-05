# Mariska Temming, S1106242

import json
import requests     # pip install requests
import os
import time
import datetime
import csv
from SFTool.malware import Malware
from SFTool.database_helper import insert_data_malware_detection

from SFTool.get_path_malware import get_malware_path


class Virustotal:
    def __init__(self, hash, key, output):
        self.hash = hash
        self.key = key
        self.output = output

    def get_hash(self):
        return self.hash

    def get_key(self):
        return self.key

    def get_output(self):
        return self.output


# checks if key is valid
def is_valid_key(key):
    if len(key) == 64:
        return True
    else:
        print("This key is not valid.")
        return False


# checks if hashes appear valid
def is_valid_hash(hash):
    if len(hash) == 32:     # MD5
        return True
    elif len(hash) == 40:    # SHA-1
        return True
    elif len(hash) == 64:   # SHA-256
        return True
    else:
        print("The Hash: " + hash + " input does not appear to be valid.")
        return False


def file_exists(filepath):
    try:
        if os.path.isfile(filepath):
            return filepath
        else:
            print("There is no file at:" + filepath)
            exit()
    except Exception as e:
        print(e)


def get_malware_name(key, hash):
    json_response = []

    params = {'apikey': key, 'resource': hash}
    url = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params)
    try:
        json_response = url.json()
    except json.decoder.JSONDecodeError as e:
        print(e)
    print("json: " + str(json_response))

    if json_response != []:
        response = int(json_response.get('response_code'))

        if response == 0:
            print(hash + ' is not in Virus Total')
            result = None
        elif response == 1:
            positives = int(json_response.get('positives'))
            if positives == 0:
                print(hash + ' is not malicious')
                result = None
            else:
                print(hash + ' is malicious')
                result = json_response["scans"]["F-Secure"]["result"]
        else:
            print(hash + ' could not be searched. Please try again later.')
            result = None
    else:
        result = None

    return result


def register_malware_to_database():
    input_file = 'malware_hashes.txt'
    file_exists(input_file)
    key = '672e7867c8c51efca05872894e865a92630883316d06d9d73b9284bc92977dd5'

    if is_valid_key(key):
        with open(input_file) as malware_hashes:  # open text file with malware hashes and close automatically
            for line in malware_hashes.readlines():
                hash = line.rstrip()
                if is_valid_hash(hash):
                    time_detection = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                    malware_name = str(get_malware_name(key, line.rstrip()))
                    path = ''
                    with open('malware_sha_path.csv', 'r') as e:  # opens file with path and sha1 hashes
                        path_dict = dict(filter(None, csv.reader(e)))  # convert CSV-file to dictionary
                        path = path_dict.get(hash)  # if the hash exists then get the path of that hash
                    malware = Malware(malware_name, hash, path, time_detection)
                    insert_data_malware_detection(malware)
                time.sleep(15)  # 4 requests to VirusTotal per minut, so there is a sleep needed


def main():
    register_malware_to_database()


if __name__ == '__main__':
    main()

