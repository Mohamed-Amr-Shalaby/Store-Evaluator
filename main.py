from sqlalchemy import create_engine, text
import pandas as pd

# Read the data from the Excel file
dfprods = pd.read_excel("D:/Work/SIMP/product_list_spreadsheet.xlsx")
dfentries = pd.read_excel("D:/Work/SIMP/entries_spreadsheet_2018.xlsx")
FIFO = {}
errors = []
quantities = {}
zero_values = []

# Connect to the database
username = "root"
password = "13579111315szxM"
engine = create_engine(
    f"mysql+mysqlconnector://{username}:{password}@127.0.0.1/store_evaluator_schema"
)
dfprods.to_sql(name="product_list", con=engine, if_exists="replace", index=False)
dfentries.to_sql(name="entries", con=engine, if_exists="replace", index=False)
c = engine.connect()


def enqueue(product_code, quantity, price, permission_number):
    # Add the product to the queue
    FIFO[product_code].append([quantity, price])


def dequeue(product_code, quantity, permission_number, year):
    # Calculate the total quantity of the product in the queue
    total_quantity = 0
    # Calculate the total quantity of a given product in the store
    if len(FIFO[product_code]) == 0:
        errors.append([year, permission_number, product_code])
        return 1
    for i in range(len(FIFO[product_code])):
        total_quantity += FIFO[product_code][i][0]
    # If the total quantity is less than the quantity requested, add the permission number to the errors list to be fixed manually later
    if total_quantity < quantity:
        errors.append([year, permission_number, product_code])
        return 1
    top = FIFO[product_code][0]
    # Else If the quantity to extract is greater than the quantity of the first element in the queue, remove the first element and call the funciton again with the remainder quality
    if top[0] < quantity:
        quantity -= top[0]
        FIFO[product_code].pop(0)
        dequeue(product_code, quantity, permission_number, year)
    # Otherwise, the quantity is less than that of the first in the queue, just deduct normally
    else:
        top[0] -= quantity
        return "Value equals " + str(top[1] * quantity)


# Create a Dictionary where the key is the product code and the value is a queue.
for i in range(len(dfprods)):
    product_code = dfprods.iloc[i, 0]
    product_name = dfprods.iloc[i, 1]
    FIFO[product_code] = []



# Go over each entry, if the entry is incoming, enqueue the product, if it is outgoing, dequeue the product
for i in range(len(dfentries)):
    year = dfentries.iloc[i, 0]
    permission_number = dfentries.iloc[i, 1]
    product_code = dfentries.iloc[i, 2]
    product_name = dfentries.iloc[i, 3]
    incoming = dfentries.iloc[i, 4]
    unit_price = dfentries.iloc[i, 5]
    outgoing = dfentries.iloc[i, 6]
    if i == 0:
        continue
    if int(incoming) > 0:
        enqueue(product_code, incoming, unit_price, permission_number)
    elif int(outgoing) > 0:
        dequeue(product_code, outgoing, permission_number, year)
    


# Create a Dictionary where the key is the product code and the value is the total quantity of the product in the store
for i in range(len(dfprods)):
    product_code = dfprods.iloc[i, 0]
    product_name = dfprods.iloc[i, 1]
    quantities[product_code] = 0
    if len(FIFO[product_code]) > 0:
        for j in range(len(FIFO[product_code])):
                quantities[product_code] += FIFO[product_code][j][0]

# Check test case for products entered with zero unit price
                
""" for i in range(len(dfentries)):
    year = dfentries.iloc[i, 0]
    permission_number = dfentries.iloc[i, 1]
    product_code = dfentries.iloc[i, 2]
    product_name = dfentries.iloc[i, 3]
    incoming = dfentries.iloc[i, 4]
    unit_price = dfentries.iloc[i, 5]
    outgoing = dfentries.iloc[i, 6]
    if i == 0:
        continue
    if incoming > 0 and unit_price == 0 and quantities[product_code] != 0 and year > 2017 and product_code < 5063:
        zero_values.append(product_code)
set_of_zeros = set(zero_values) """

# Extract results

# Iterate over each product in the dictionary. For each product, pass over the queue and calculate the total value of the product by multiplying the quantity by the price and adding it to the total value of the store
store_total = 0
for product_code in FIFO:
    if len(FIFO[product_code]) == 0:
        continue
    for i in range(len(FIFO[product_code])):
        print("Quantity: ", FIFO[product_code][i][0])
        print("Price: ", FIFO[product_code][i][1])
        store_total += FIFO[product_code][i][0] * FIFO[product_code][i][1]

print(f"{store_total:,}")