import logging
import csv
from pymongo import MongoClient
from loguru import logger

LOG_FORMAT = "\n%(asctime)s %(filename)s:%(lineno)-3d %(levelname)s" "\n%(message)s"
FORMATTER = logging.Formatter(LOG_FORMAT)
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class MongoDBConnection():

    def __init__(self, host="127.0.0.1", port=27017):
        self.host = host
        self.port = port
        self.connection = None

    def __enter__(self):
        self.connection = MongoClient(self.host, self.port)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
    logging.info('Database connected')


def import_data(directory_name, product_file, customer_file, rentals_file):

    parsed_product_file = parse_csv_input((directory_name + product_file))
    parsed_customer_file = parse_csv_input(directory_name + customer_file)
    parsed_rentals_file = parse_csv_input(directory_name + rentals_file)

    product_count = 0
    customer_count = 0
    rental_count = 0

    product_errors = 0
    customer_errors = 0
    rental_errors = 0

    try:
        with MONGO:
            DATABAE = MONGO.connection.assignment_05

            product_collection = DATABAE["product"]
            for product in parsed_product_file:
                product_collection.insert_one(product)

    except TypeError as excep:
        LOGGER.info("Error saving product info to database: %s", excep)
        product_errors += 1
    else:
        LOGGER.info("Successfully saved product info")
        product_count = len(parsed_product_file)

    try:
        with MONGO:
            DATABAE = MONGO.connection.assignment_05
            customer_collection = DATABAE["customer"]

            for customer in parsed_customer_file:
                customer_collection.insert_one(customer)
    except TypeError as excep:
        LOGGER.info("Error saving customer info to database: %s", excep)
        customer_errors += 1
    else:
        LOGGER.info("Successfully saved customer info.")
        customer_count = len(parsed_customer_file)

    try:
        with MONGO:
            DATABAE = MONGO.connection.assignment_05
            rental_collection = DATABAE["rental"]

            for rental in parsed_rentals_file:
                rental_collection.insert_one(rental)
    except TypeError as excep:
        LOGGER.info("Error saving rental info to database: %s", excep)
        rental_errors += 1
    else:
        LOGGER.info("Successfully saved rental info.")
        rental_count = len(parsed_rentals_file)

    return (
        (product_count, customer_count, rental_count),
        (product_errors, customer_errors, rental_errors),
    )


def parse_csv_input(input_file):
    parsed_infile = []
    try:
        with open(input_file) as infile:
            for line in csv.reader(infile):
                parsed_infile.append(line)

        temp_object_storage = []

        for line_index, line in enumerate(parsed_infile[1:]):
            temp_object_storage.append({})
            for category_index, category in enumerate(parsed_infile[0]):
                if category_index == 0:
                    category = category[3:]
                temp_object_storage[line_index][category] = line[category_index]

        return temp_object_storage
    except FileNotFoundError as excep:
        LOGGER.info("error parsing csv file: %s", excep)


def show_available_products(db):
    available_products = {}
    for product_id in db.products.find():
        product_dict = {'description': product_id['description'],
                        'product_type': product_id['product_type'],
                        'quantity_available': product_id['quantity_available']}
        if product_id['quantity_available'] != '0':
            available_products[product_id['product_id']] = product_dict
            continue
        else:
            continue

    return available_products


def show_rentals(product_id):
    mongo = MongoDBConnection()
    logger.debug('Connecting to MongoDB')
    with mongo:
        logger.debug('Connecting to hpnorton database')
        db = mongo.connection.hpnorton
        renters = set()
        for item in db.rentals.find({'product_id': product_id}):
            renters.add(item['user_id'])
        records = {}
        for item in renters:
            renter = db.customer.find_one({'user_id': item})
            del renter['_id']
            records[item] = renter
    return records


def clear_data(db):
    db.products.drop()
    db.customers.drop()
    db.rentals.drop()


if __name__ == "__main__":

    MONGO = MongoDBConnection()
    import_data("../data/", "product_with_error.csv", "customers.csv", "rental.csv")

    print(show_available_products())

    print(show_rentals("prd010"))

    TO_DROP_INPUT = input(
        "Do you want to drop the newly created database?" "\nY or N: "
    )
    if TO_DROP_INPUT.lower() == "y":
        with MONGO:
            TO_DROP = MONGO.connection
            TO_DROP.drop_database("assignment_05")