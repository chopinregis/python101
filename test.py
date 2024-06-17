# Task 1: Create a function that takes an input from the user and fills up the whitespaces with + sign
# Task 2: Create a function that takes a number as an input from the user and checks if
# it is lower than 500 but higher than 250
# Task 3: Create a ATM booth, where you can deposit any amount of money,
# first step is to input your first name and lastname and date of birth
# ----After this step, put a prompt on what the user wants to do, for example say "Welcome Firstname, what would you like to do today? 1. deposit 2. withdraw 3. take out the card"
# second step, it should prompt you to provide if option 1-->"How much money would you like to deposit?"
# third step, after deposit, you can have withdraw option as well, if option 2 --->"How much money you would like to withdraw?"
# you need to also put a limit to withdrawal, you cannot withdraw more than you have in atm or the limit of 500, maximum you can withdraw is 500
# if the user chooses number 3, print "Thank you so much, have a wonderful day Firstname"


user = input("Enter your name: ")   # Take input from the user

def fill_whitespaces(user):         # Create a function that takes an input from the user and fills up the whitespaces with + sign
    return user.replace(" ", "+")   # Replace all whitespaces with + sign

print(fill_whitespaces(user))       # Print the result

number = input("Enter a number: ")

def number_check(number):                           # Create a function that takes a number as an input from the user and checks if
    if int(number) < 500 and int(number) > 250:     # it is lower than 500 but higher than 250
        print("The number is between 250 and 500")  
    else:                                           
        print("The number is not between 250 and 500") 

number_check(number)    

firstname = input("Enter your first name: ")
lastname  = input("Enter your last name: ")
dob       = input("Enter your date of birth: ")

print(f"Welcome {firstname}, what would you like to do today? 1. deposit 2. withdraw 3. take out the card")

i = 0
while i == 0:
    choice = int(input("Enter your choice: "))
    if choice == 1:
        deposit = input("How much money would you like to deposit?")
    elif choice == 2:
        withdraw = input("How much money you would like to withdraw?")
    elif choice == 3:
        print("Thank you so much, have a wonderful day")




"""
def atm(atm_display): 
    if atm_display == "1":
       deposit = input("How much money would you like to deposit?")
    elif atm_display == "2":
       withdraw = input("How much money you would like to withdraw?")
    elif atm_display == "3":
       print("Thank you so much, have a wonderful day")
def client_information(firstname, lastname, dob):
    print(f"Welcome {firstname}, what would you like to do today? 1. deposit 2. withdraw 3. take out the card")
"""