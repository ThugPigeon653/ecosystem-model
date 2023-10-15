from your_module_name import SQLiteConnection

# Initialize the connection
db_connection = SQLiteConnection("mydb.sqlite")

# Create the table (call this only once)
db_connection.create_table()

# Script 1 (Writer)
def insert_data():
    for i in range(1, 11):
        last_row_id = db_connection.write_to_db(f"Data {i}")
        print(f"Inserted data with ID {last_row_id}")

# Script 2 (Reader)
def read_data():
    while True:
        data = db_connection.read_from_db()
        print("Read data:", data)

if __name__ == "__main__":
    insert_data()