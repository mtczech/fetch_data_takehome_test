import requests
import xml.etree.ElementTree as ET

"""
Takes in the port where the queue is located
Returns a message from the designated queue
Also parses the XML of the message so the JSON body is returned
Note: Virtual environment must be activated/contain the appropriate packages 
(requests, xml, json)
"""

"http://localhost:4566/000000000000/login-queue?Action=ReceiveMessage"

def receive_message(port):
    url = "http://localhost:" + str(port) + "/000000000000/login-queue?Action=ReceiveMessage"
    returned_request = requests.get(url)
    # Writes the XML from the request to a request tree
    request_tree = ET.fromstring(returned_request.text)
    if len(request_tree[0].keys()) == 0:
        print("Queue is empty")
        return None
    BODY_INDEX = 3 # No magic numbers
    body = request_tree[0][0][BODY_INDEX] # Hardcoded to get the body from the XML request
    # Since we only need the body for this case, hardcoding is fine
    return body.text

# Function that encrypts the text with a given key by XORing it
# Takes in the text and key
# Returnes the encrypted message

def convert_and_xor(text, bytes_key):
    bytes_text = bytes(text, 'utf-8')
    sample_bytes_key = bytes_key[0:len(bytes_text)]
    return ''.join(format(int(a, 16) ^ int(b, 16), 'x') for a,b in zip(text, sample_bytes_key))

# Takes an IP address and converts it into a hexadecimal value
# NOTE: This only works with IPV4 addresses. It could be made to work with IPV6,
# but as of right now that's not the case.

def ip_to_hex(ip):
    ip = ip.split(".")
    ip_as_hex = ""
    print(ip)
    for value in ip:
        temp = int(value, 10)
        if temp < 16:
            ip_as_hex = ip_as_hex + '0' + hex(temp)[2:]
        else:
            ip_as_hex = ip_as_hex + hex(temp)[2:]
    return ip_as_hex

# Straightforward, creates the table. Does not do anything if the table already exists.

def create_table(connection):
    table_setup = """CREATE TABLE IF NOT EXISTS user_logins(
    user_id varchar(128),
    device_type varchar(32),
    masked_ip varchar(256),
    masked_device_id varchar(256),
    locale varchar(32),
    app_version integer,
    create_date date
    );
    """
    cursor = connection.cursor()
    cursor.execute(table_setup)
    connection.commit()

# Helper function for sending a table row to the postgres database.
# Takes in a connection and a set of values to be sent to the database.
# Does not return anything.

def send_to_postgres(connection, inputs_tuple):
    cursor = connection.cursor()
    # NOTE: user_logins is hardcoded in, in the future this could be changed to allow adding into different tables
    insert_message = """ INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date) VALUES (%s, %s, %s, %s, %s, %s, %s);"""
    cursor.execute(insert_message, inputs_tuple)
    connection.commit()

# This is a helper function for converting a version string (e.g. 2.3.0) to an integer.
# It takes in the version and returns the version converted to an integer.
# The function below it is for reversing this process.
# Works only if the values in the version are between 0 and 254.

def version_to_int(version):
    version_vals_list = version.split(".")
    version_vals_list = [int(x) for x in version_vals_list]
    index = 0
    for i in range(-1, -1 * (len(version_vals_list) + 1), -1):
        version_vals_list[i] = (version_vals_list[i]+1 << 8*index) & (0x000000FF << 8*index)
        index += 1
    returned = 0
    for val in version_vals_list:
        returned = returned | val
    return int(returned)

# Not used in this particular case, but necessary when the uploaded version values
# need to be decoded. The decoding assumes that there are at most 3 values,
# it does not work otherwise

def int_to_version(val):
    major = ((val & 0x00FF0000) >> 16) - 1
    minor = ((val & 0x0000FF00) >> 8) - 1
    tiny = (val & 0x000000FF) - 1
    if major > -1:
        return str(major) + '.' + str(minor) + '.' + str(tiny)
    else:
        return str(minor) + '.' + str(tiny)
