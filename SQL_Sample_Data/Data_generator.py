import csv
from faker import Faker
import random
from datetime import datetime

'''
this script generates sample data for the database and saves it as csv files
'''

employee_list = { 1: 1111, 2: 2222, 3: 3333, 4: 4444, 5: 5555,
    6: 6666, 7: 7777, 8: 8888, 9: 9999, 10: 1000, 11: 2000,
    12: 3000, 13: 4000, 14: 5000, 15: 6000, 16: 7000, 17: 8000,
    18: 9000, 19: 1001, 20: 2002, 21: 3003, 22: 4004, 23: 5005,
    24: 6006, 25: 7007, 26: 8008, 27: 9009
}

menu_id_to_price = { 27: 5.75, 8: 7.99, 28: 5.75, 29: 5.75, 9: 6.99, 36: 0,
    19: 6.5, 33: 9.5, 10: 7.5, 22: 7.5, 23: 0.99, 31: 9.99, 24: 1.5, 15: 1.99,
    34: 9.5, 20: 7.5, 35: 9.5, 25: 1.25, 16: 5.75, 17: 6.5, 18: 5.99, 1: 7.5,
    11: 8.5, 5: 6.25, 12: 6.5, 13: 6.5, 2: 8.5, 26: 5.75, 21: 7.5, 32: 9.5,
    0: 88.8, 3: 6.5, 4: 6.99, 6: 6.75, 7: 7.5, 14: 8.5
}

def getRandomEmployee():
    employeeID = employee_list[random.randint(1,27)]
    return employeeID

def getRandomCustomer():
    customer_number = random.randint(1,10000)
    return int(customer_number)

def getRandomDate():
    month = random.choice([1, 1, 1, 8, 8, 8] + list(range(2, 8)) + list(range(9, 13)))
    day = random.randint(1, 28)
    return datetime(2023, month, day)

def addRandomOrder(date, ordernumber):
    # select 1-5 random menu items
    number_of_items = random.randint(1,5)
    curr_order_menu_items = []
    curr_price = 0

    # populate order breakout with items and calculates the order price
    for j in range(number_of_items):
        new_menu_item = random.randint(0,36)
        
        if new_menu_item == 30:
            new_menu_item = 10
        
        curr_order_menu_items.append(new_menu_item)
        newline = (ordernumber, new_menu_item)
        breakout_data.append(newline)

        curr_price += menu_id_to_price[new_menu_item]
    

    # get random customer
    customer = getRandomCustomer()

    # get random employee 
    employee = getRandomEmployee()


    order_data.append((ordernumber, customer, employee, round(curr_price, 2), date))


# generate customers 
fake = Faker()
data = []
customer_headers = ['id', 'first name', 'last name']

# generates the 10,000 customers 
for i in range(1, 10001):
    newline = (i, fake.first_name(), fake.last_name())
    data.append(newline)

# opens and writes CSV
csv_filename = 'SQL_Data/Updated_Sample_Data/csv/customer.csv'
with open(csv_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(customer_headers)
    writer.writerows(data)


# generate orders
'''
generates 100,000 orders
orders headers: order_number, customer, employee, total_price, order_time
breakout headers: order_number, fooditem
'''

# initialize orders csv with headers
order_data = []

# initialize order breakout csv with headers
breakout_data = []

for i in range(100000):
   addRandomOrder(getRandomDate(), i)

#TODO: add 3 bump days 
bump_day_1 = datetime(2023, 1, 21)
bump_day_2 = datetime(2023, 8, 28)
bump_day_3 = datetime(2023, 9, 15)

for i in range(600):
    addRandomOrder(bump_day_1, 100000 + i)
    addRandomOrder(bump_day_2, 101000 + i)
    addRandomOrder(bump_day_3, 102000 + i)

# writes data to the csv
with open("SQL_Data/Updated_Sample_Data/csv/order_breakout.csv", 'w', newline='') as order_breakout_csv:
    breakout_writer = csv.writer(order_breakout_csv)
    breakout_writer.writerow(['order_number', 'foodItem'])
    for row in breakout_data:
        breakout_writer.writerow(row)

with open("SQL_Data/Updated_Sample_Data/csv/orders.csv", 'w', newline='') as order_csv:
    order_writer = csv.writer(order_csv)
    order_writer.writerow(['order_number', 'customer', 'employee', 'food_price', 'order_time'])
    for row in order_data:
        order_writer.writerow(row)
