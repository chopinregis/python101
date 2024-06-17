# Example 1: Reverse a String
def reverse_string(s):
    return s[::-1]

# Example 2: Check if a String is a Palindrome
def is_palindrome(s):
    s = s.lower().replace(' ', '')
    return s == s[::-1]

# Example 3: Count the Number of Vowels in a String
def count_vowels(s):
    vowels = "aeiouAEIOU"
    return sum(1 for char in s if char in vowels)

# Example 4: Remove All Whitespace from a String
def remove_whitespace(s):
    return ''.join(s.split())

# Example 5: Capitalize the First Letter of Each Word in a String
def capitalize_words(s):
    return ' '.join(word.capitalize() for word in s.split())

# Example 6: Find the Longest Word in a String
def longest_word(s):
    words = s.split()
    return max(words, key=len)

# Example 7: Replace All Occurrences of a Substring in a String
def replace_substring(s, old, new):
    return s.replace(old, new)

# Example 8: Remove Punctuation from a String
import string
def remove_punctuation(s):
    return s.translate(str.maketrans('', '', string.punctuation))

# Example 9: Find the Frequency of Each Character in a String
def char_frequency(s):
    freq = {}
    for char in s:
        if char in freq:
            freq[char] += 1
        else:
            freq[char] = 1
    return freq

# Example 10: Check if Two Strings are Anagrams
def are_anagrams(s1, s2):
    return sorted(s1.replace(' ', '').lower()) == sorted(s2.replace(' ', '').lower())

# Testing the functions
print(reverse_string("hello"))  # Output: "olleh"
print(is_palindrome("A man a plan a canal Panama"))  # Output: True
print(count_vowels("hello world"))  # Output: 3
print(remove_whitespace("hello world"))  # Output: "helloworld"
print(capitalize_words("hello world"))  # Output: "Hello World"
print(longest_word("The quick brown fox jumps over the lazy dog"))  # Output: "jumps"
print(replace_substring("hello world", "world", "there"))  # Output: "hello there"
print(remove_punctuation("hello, world!"))  # Output: "hello world"
print(char_frequency("hello"))  # Output: {'h': 1, 'e': 1, 'l': 2, 'o': 1}
print(are_anagrams("listen", "silent"))  # Output: True


i=0
while i==0:
    inputnumber=input("Please provide a number:")
    inputnumber=int(inputnumber)
    if inputnumber%2==0:
        print(f"The number {inputnumber} is an even number")
    elif inputnumber%3==0:
        print(f"The number {inputnumber} is divisible by the number 3")
    elif inputnumber%5==0:
        print(f"The number {inputnumber} is divisible by the number 5")
    elif inputnumber%7==0:
        print(f"The number {inputnumber} is divisible by the number 7")
    else:
        print(f"Sorry the number is not divisible by either 1,3,5,7")
    inputcontinuity=input("Do you want to continue? type 'Y' or 'N'")
    if inputcontinuity=='Y' or inputcontinuity=='y':
        continue
    else:
        i=1

    
# simplified version

while True:
    input_number = input("Please provide a number: ")
    input_number = int(input_number)

    if input_number % 2 == 0:
        print(f"The number {input_number} is an even number.")
    elif input_number % 3 == 0:
        print(f"The number {input_number} is divisible by 3.")
    elif input_number % 5 == 0:
        print(f"The number {input_number} is divisible by 5.")
    elif input_number % 7 == 0:
        print(f"The number {input_number} is divisible by 7.")
    else:
        print("Sorry, the number is not divisible by 2, 3, 5, or 7.")

    input_continuity = input("Do you want to continue? Type 'Y' or 'N': ")
    if input_continuity.lower() != 'y':
        break

# another simplified version

while True:
    input_number = int(input("Please provide a number: "))
    
    if input_number % 2 == 0:
        print(f"The number {input_number} is an even number.")
    elif input_number % 3 == 0:
        print(f"The number {input_number} is divisible by the number 3.")
    elif input_number % 5 == 0:
        print(f"The number {input_number} is divisible by the number 5.")
    elif input_number % 7 == 0:
        print(f"The number {input_number} is divisible by the number 7.")
    else:
        print("Sorry, the number is not divisible by 2, 3, 5, or 7.")
    
    input_continuity = input("Do you want to continue? (Y/N): ").lower()
    if input_continuity != 'y':
        break



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

def task1():
    user_input = input("Enter a string: ")
    return user_input.replace(" ", "+")

def task2():
    user_input = int(input("Enter a number: "))
    if 250 < user_input < 500:
        return True
    else:
        return False

def atm_booth():
    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")
    date_of_birth = input("Enter your date of birth: ")

    while True:
        print(f"Welcome {first_name}, what would you like to do today?")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Take out the card")
        choice = input("Enter your choice: ")

        if choice == "1":
            deposit_amount = float(input("How much money would you like to deposit? "))
            print(f"Deposit successful. Your new balance is {deposit_amount}.")
        elif choice == "2":
            balance = float(input("Enter your current balance: "))
            withdraw_amount = float(input("How much money you would like to withdraw? "))
            if withdraw_amount > balance:
                print("Insufficient balance. You cannot withdraw more than you have.")
            elif withdraw_amount > 500:
                print("You cannot withdraw more than 500.")
            else:
                print(f"Withdrawal successful. Your new balance is {balance - withdraw_amount}.")
        elif choice == "3":
            print(f"Thank you so much, have a wonderful day {first_name}.")
            break
        else:
            print("Invalid choice. Please try again.")

atm_booth()


