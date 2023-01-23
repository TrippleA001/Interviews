#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import required libraries
import re
import pandas as pd
from bs4 import BeautifulSoup
import random
import mysql.connector
from mysql.connector import Error

# Fetch the html file and parse 
with open("python_class_question.html") as file:
    soup = BeautifulSoup(file, 'html.parser')


# Format the parsed html file
strhtm = soup.prettify()

# Print the first few characters
print (strhtm[:225])


# In[2]:


# Exlore table
for table in soup.find_all('table'):
    print(table)


# In[3]:


# Defining of the dataframe
df = pd.DataFrame(columns=['Day', 'Colour', 'Count'])

# Collecting Data
for row in table.tbody.find_all('tr'): 
    #print("row",row)
    # Find all data for each column
    columns = row.find_all('td')
    #print("col",columns)
    if(columns != []):
        sorted_colours = {}
        day = columns[0].text.strip()
        #print("day",day)
        colours = columns[1].text.strip()
        #print("colours", colours)
        #print("sorted_colours", sorted_colours)
        for colour in colours.split(","):
            colour = colour.strip()
            if colour in sorted_colours.keys():
                sorted_colours[colour]+=1
                #print("sorted_colours", sorted_colours)
            else:
                sorted_colours[colour]=1
                #print("sorted_colours", sorted_colours)
        for colour in sorted_colours:
            df = df.append({'Day': day,  'Colour': colour, 'Count': sorted_colours[colour]}, ignore_index=True)
df


# In[4]:


# Defining of the dataframe
df2 = pd.DataFrame(columns=['Colour', 'Frequency'])
# Create empty dictionary
sorted_colours2 = {}
# Collecting Data
for row in table.tbody.find_all('tr'): 
    # Find all data for each column
    columns = row.find_all('td')
    if(columns != []):
        colours = columns[1].text.strip()
        # Correct spelling error
        colours=colours.replace("BLEW","BLUE")
        for colour in colours.split(","):
            colour = colour.strip()
            if colour in sorted_colours2.keys():
                sorted_colours2[colour]+=1
            else:
                sorted_colours2[colour]=1
# Append colour and frequency to dataframe
for colour in sorted_colours2:
    df2 = df2.append({'Colour': colour, 'Frequency': sorted_colours2[colour]}, ignore_index=True)
df2


# In[5]:


# Sort dataframe
df2.sort_values("Frequency", inplace = True)
df2


# In[6]:


#1.      Which color of shirt is the mean color?
mean_value = df2["Frequency"].mean()
answer1 = df2["Colour"][df2["Frequency"]== mean_value.round()].values
print(f"Colour {answer1[0].lower()} and {answer1[1].lower()} are the mean colour of shirt")


# In[7]:


#2.      Which color is mostly worn throughout the week? 
mode_value = df2["Frequency"].max()
answer2 = df2["Colour"][df2["Frequency"]==mode_value].values
print(f"Colour {answer2[0].lower()} is the mostly worn throughout the week")


# In[8]:


#3.      Which color is the median?
median_value = df2["Frequency"].median()
answer3 = df2["Colour"][df2["Frequency"]==median_value].values
print(f"Colour {answer3[0].lower()} is the median color")


# In[9]:


df2["Frequency"].var()


# In[10]:


#4.      BONUS Get the variance of the colors
variance_value = df2["Frequency"].var()
answer3 = df2["Colour"][df2["Frequency"]==variance_value.round()].values
print(f"Colour {answer2} is the variance of the colors")


# In[12]:


#5      BONUS if a colour is chosen at random, what is the probability that the color is red?
pileOfShirts= []
for colour in df2["Colour"]:
    pileOfShirts.extend([colour] * df2["Frequency"][df2["Colour"]==colour].values[0])
pileOfShirts 

def pick_a_token(container):
    """
    A function to randomly sample from a `container`.
    """
    return random.choice(container)
number_of_repetitions = 10000
samples = [pick_a_token(container=pileOfShirts) for repetition in range(number_of_repetitions)]
samples
sum(token == "RED" for token in samples) / number_of_repetitions


# In[14]:


#6.      Save the colours and their frequencies in postgresql database
#create a connection to a mysql server
def create_server_connection(host_name, user_name, ):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

connection = create_server_connection("localhost", "root")
# Create a database 
def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")

create_database_query = "CREATE DATABASE bincom_colors_db"
create_database(connection, create_database_query)
#connect to an exisiting database
def create_db_connection(host_name, user_name, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection
connection = create_db_connection("localhost", "root", "bincom_colors_db")
# function to execute queries
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")
# sql statement to create dresses table 
create_dresses_table='''CREATE TABLE IF NOT EXISTS bincom_colors_db.dresses (
  `SiteID` INT NOT NULL AUTO_INCREMENT,
  `Color` VARCHAR(45) NOT NULL,
  `Frequency` INT NULL,
  PRIMARY KEY (`SiteID`))
  ENGINE = InnoDB;'''
# excute all sql statement to create tables
print('Creating tables....')
execute_query(connection, create_dresses_table)
print("Tables are created....")
# sql statement to populate dresses table
try:
    cursor = connection.cursor()
    for i in df2[["Colour","Frequency"]].drop_duplicates().values:  
        #here %S means string values 
        sql = "INSERT INTO bincom_colors_db.`dresses`(Color, Frequency) VALUES (%s,%s)"
        cursor.execute(sql, tuple(i))
        print("Record inserted")
        # the connection is not auto committed by default, so we must commit to save our changes
        connection.commit()
except Error as e:
        print("Error while connecting to MySQL", e)


# In[106]:


for i in df2[["Colour","Frequency"]].drop_duplicates().values:
    print (tuple(i))


# In[15]:


#7.      BONUS write a recursive searching algorithm to search for a number entered by user in a list of numbers
# Returns index of x in arr if present, else -1
def binary_search(arr, low, high, x):
 
    # Check base case
    if high >= low:
 
        mid = (high + low) // 2
 
        # If element is present at the middle itself
        if arr[mid] == x:
            print("Element is present at index", str(mid))
            return mid
 
        # If element is smaller than mid, then it can only
        # be present in left subarray
        elif arr[mid] > x:
            return binary_search(arr, low, mid - 1, x)
 
        # Else the element can only be present in right subarray
        else:
            return binary_search(arr, mid + 1, high, x)
 
    else:
        # Element is not present in the array
        print("Element is not present in array")
        return -1
    


# In[30]:


#8.      Write a program that generates random 4 digits number of 0s and 1s and convert the generated number to base 10.
num = ""
for i in range (4):
    digit = random.randint(0, 1)
    num += str(digit)
number =int(num, 2)
print(f"The four digit number randomly generated is {num}, it's decimal equivalent is {number}")


# In[34]:


#9.      Write a program to sum the first 50 fibonacci sequence.
# Python program to sum the Fibonacci sequence up to the 50th term

MAX = 100

# Create an array for memoization
f = [0] * MAX

# Returns n'th Fibonacci number using table f[]
def fib(n):
    n = int(n)

    # Base cases
    if (n == 0):
        return 0
    if (n == 1 or n == 2):
        return (1)

    # If fib(n) is already computed
    if (f[n] == True):
        return f[n]

    k = (n+1)/2 if (n & 1) else n/2

    # Applying above formula [Note value n&1 is 1 if n is odd, else 0].
    f[n] = (fib(k) * fib(k) + fib(k-1) * fib(k-1)) if (n & 1) else (2 * fib(k-1) + fib(k)) * fib(k)
    return f[n]

# Computes value of first Fibonacci numbers
def calculateSum(n):

    return fib(n+2) - 1

# Driver program to test above function
n = 50
print(f"Sum of the first {n} Fibonacci numbers is :", calculateSum(n))


# In[ ]:




