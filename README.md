How to run this program:

Step 1: Activate a Python 3 virtual environment (I used Python 3.10.4). If you do not have one, they can be created using Miniconda.

Step 2: Install the necessary packages. This can be done by going to your virtual environment and running the following commands into the terminal:

pip install xml
pip install psycopg2
pip install requests

Step 3: Activate your virtual environment, go to the folder where this program is stored, and run the command "python main.py". The program will run.

GOOD TO KNOW: The following values are hardcoded:

queue_port (The port reading messages from the queue) -------------> 4566
postgres_port (The port used to host the postgres database) -------> 5432
db_name (The name of the overall database) ------------------------> postgres
database_name (The name of the table within the overall database) -> user_logins
username ----------------------------------------------------------> postgres
password ----------------------------------------------------------> postgres
input_host (The IP address of the queue) --------------------------> 127.0.0.1/localhost
output_host (The IP address of the database) ----------------------> 127.0.0.1/localhost

Notes for the reader about my application: 

How is the sensitive data encrypted (device_id and ip)?

Step 1: Generate a random key that is stored locally, to be used as the encryption key. There should be one encryption key for the device IDs and one for the IP addresses.
Step 2: XOR all of the bits in the device ID and the IP address with the appropriate random key, this is the encrypted key.
Note: The same random key needs to be used for all device_id values and for all IP address values. Although this is a security risk, it is necessary in order to easily detect duplicate values, since any two values that have the same encrypted key must also have the same original key. 
Step 3: Load the encrypted key into the database.
Step 4: To decrypt, XOR the encrypted message with the device ID or IP address again. XORing any message with the same key twice yields the original message, since XORing is commutative, any message XORed with itself is equal to 0, and any message XORed with 0 gives the original message.
Another note: Another weakness of this method is that if two different users have different random keys, the data may appear different despite being the same if it is encrypted by two different users. That is not relevant in this case, since there will only be one computer reading the sample data in. However, other options if there are more users reading in the data than one include routing all the data through a server that is designated to encrypt everything (could slow things down) or giving every user a common key (bigger security risk). A good solution would be to give every user a passcode that is then hashed into the key.

Questions:

-How should this application be deployed in production?

The way the application works is by requesting messages from the queue, encrypting the sensitive information, then sending the encrypted data to the Postgres database. This process continues until the queue is empty. Once the queue is empty, the system will print "Queue is empty" and close the connection.

-Other components to add to make it production ready:

As of right now, the database values (database name, username, password) are hardcoded in. In order for this code to be production ready, there would have to be some sort of way for the user to input the databse name, username, and password.

The encryption system is there, but it is not perfect. See above description for why (How is the sensitive data encrypted?)

The system for converting the version number into the corresponding integer is fine, but the system for doing the reverse conversion is not as good since it only works if there are either two or three values to be converted. If there are four or more, or only one value, an edit needs to be made to allow this.

-How can this application scale?

Because this application goes through each individual request, it will take more time the more requests there are. To speed things up in the event of a larger dataset, the application could be changed to take more than one request at once, and send them all to the database at once. Since a new connection is opened and closed with each request, the amount of time it takes for the connections to open and close would add up. This could be fixed by creating one connection when the program starts, using it to send all of the messages, then closing it when the queue is empty. Also, in its current iteration the program shuts down when the queue is empty. This is not ideal because the queue might be empty during down periods, and when this happens the program will terminate, but can be solved by continuing the loop instead of exiting it when there is no message.

-How can PII be recovered later on? 

See step 4 of "How is the sensitive data encrypted" above.

-What are the assumptions made?

I assumed the IP addresses would be written in IPv4 format (e.g. "100.100.100.100"). The encryption of the IP address does not work if the address is not in IPv4 format. This must be addressed if this code is meant to be used. I also hardcoded in the queue port (4566) and the postgres port (5432), as well as assuming the device ID characters would be separated by dashes (another value hardcoded in).