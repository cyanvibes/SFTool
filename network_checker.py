"""
Author: Mariska Temming, S1106242
Summary: This script checks the network of the system, so it checks if the system has a connection to the internet
"""

from urllib.request import urlopen


# Checks if there is a connection to the internet
def internet_on():
    try:
        urlopen('http://216.58.192.142', timeout=1)  # Test the connection to Google.com
        return True
    except Exception as e:
        print(e)
        return False


def main():
    print(internet_on())


if __name__ == '__main__':
    main()
