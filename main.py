import utils as utils
import json
import psycopg2
from datetime import date

if __name__ == "__main__":
    # Change the random bytes every so often, but do so with caution!
    # The bytes are for masking the device ID and IP address.
    # Changing the bytes could make two of the same IP addresses or IDs
    # appear to be different, or vice versa.
    random_bytes_device_id = "224033be7d655c74f76ca70c84038c3d7899d1bc74c0d7f41d96de7c984c200fca7187e03a24b28a0d6093d998021b4bbd85ee1a13a86be70d7ef79f4ecfdddcfeda5f6cf08f1fd95c1e85ad9ac72834eadd94d5545aa8bcc806d89906f1928dea12570c5b8cbe9b590b93192780b7d4a1d3eaf05b3dc4032ee5f75753225c2ad4564d998526031def6830e93ce993c265f7a52438d91bda8bd3fbf959407f99f667198ba186b57e54e87e82ba589f3882fff14acb9dc1780f0ced1670753a70b06b833cf8ac19477ab872a9fb2f6fb0c94169761f2adf01debf33ab51c5cfb716c8bb2dcc1c58c2c41efa21b58c5e2efeefbc79e3a6f7886d66ff68ad1ba466"
    random_bytes_ip = "7463af3043990786cbaab9279fa3070b2749aa1445d323a247de93591a3b4b9580c2b4675f68a942453dffcf448cbc690ae7b45ca1878adff764a49ac9c3941692a229976fbd13639a18e6f1e4a8a5a45b295d863e0c242d474aee392744cf3bf10c3a87f30de997ead2377748c38748f9314e1d18d99a11f0dbb8e77b9ad72ae474cc44a71862e7bb0da2ad967fb5a29f8ea739d233633e2d2ff50aa0c1eab9c02234d67f1ca6896fb3e08534e4e76a4ed0aba30e83d3b075e7f75f18d8b8ca8139924a654ef6129dfc46ec0555c92431ab1187a9ba0a1c38bf9868f14087cfc19ac3c0797b0c9696b8b3c4356dff4542338a0fbdc2e4c64f9679245228c214"
    queue_port = 4566
    postgres_port = 5432
    while True:
    # This function returns the JSON of the received message from the queue.
        parsed_json = utils.receive_message(queue_port)
        if parsed_json is None:
            break
        request_dict = json.loads(parsed_json)
        if 'device_id' not in request_dict.keys():
            continue
        cleaned_id = request_dict['device_id'].replace('-', '')
        encrypted_device_id = utils.convert_and_xor(cleaned_id, random_bytes_device_id)
        ip_as_hex = utils.ip_to_hex(request_dict['ip'])
        encrypted_ip = utils.convert_and_xor(ip_as_hex, random_bytes_ip)
        database_name = 'user_logins'
        username = 'postgres'
        password = "postgres"
        connection = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="postgres", port="5432")
        utils.create_table(connection)
        inputs_tuple = (request_dict['user_id'], request_dict['device_type'], encrypted_ip, encrypted_device_id, request_dict['locale'], utils.version_to_int(request_dict['app_version']), date.today())
        utils.send_to_postgres(connection, inputs_tuple)
        connection.close()