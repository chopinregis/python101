"""
This code calculates the sum of numbers entered by the user. Here's a breakdown of the steps:

**1. Define `calculate_sum` function:**

- This function takes a list of numbers (`numbers`) as input.
- It uses the built-in `sum` function to calculate the sum of all numbers in the list.
- It returns the calculated sum.

**2. Get user input:**

- The code prompts the user to enter numbers separated by spaces using `input`.
- The input is stored in the variable `input_numbers`.

**3. Convert input to a list of numbers (multiple ways):**

- The commented-out section shows a longer approach to achieve what the last line does more concisely. 
    - `input_numbers.split()`: Splits the user input string based on spaces, creating a list of individual numbers as strings.
    - `map(int, aftersplit)`: This creates an iterator object (`aftermap`) that applies the `int` function to each element in `aftersplit`, converting them from strings to integers.
    - `list(aftermap)`: Converts the iterator (`aftermap`) back to a regular list (`afterlist`).

**4. Concise way to convert input (recommended):**

- The last line uses `list(map(int, input_numbers.split()))` in one go.
    - It splits the input using `split` and directly converts each string to an integer using `map(int, ... )`.
    - Finally, it converts the resulting iterator to a list using `list`. This is a more efficient and readable approach.

**5. Calculate and print the sum:**

- The converted list (`numbers_list`) is passed to the `calculate_sum` function.
- The function returns the total sum, which is stored in `total_sum`.
- Finally, the sum is printed with a message.

This code demonstrates two ways to achieve the same result. The last line with `map` is the recommended approach for its efficiency and readability.
"""
def greet(name):
    return f"Hello, {name}!"
 
print(greet("Alice"))
 
def howmuchmoneydoihave(money):
    return f"Hello, you have CAD {money} in your account"
 
print(howmuchmoneydoihave(1))
 
# Define a function to calculate the sum of a list of numbers
def calculate_sum(numbers):
    """
    Calculate the sum of numbers in a list.
    
    Parameters:
    numbers (list): A list of integers.
    
    Returns:
    int: The sum of the numbers in the list.
    """
    return sum(numbers)

# First step: Prompt the user to enter numbers separated by spaces
input_numbers = input("Enter numbers separated by spaces: ")

# Second step: Split the input string into a list of substrings at each space
aftersplit = input_numbers.split()

# Convert each element in the list from a string to an integer using map
aftermap = map(int, aftersplit)

# Convert the map object to a list to make it usable multiple times
afterlist = list(aftermap)

# Print the list to verify the conversion from strings to integers
print(afterlist)

# This print statement will not print the list again as expected because the map object is exhausted
print(aftermap)

# This print statement is a duplicate and will print the same list as before
print(afterlist)

# Perform the input, splitting, and conversion in one line for efficiency
numbers_list = list(map(int, input_numbers.split()))

# Print the new list to confirm it matches the previous list
print(numbers_list)

# Calculate the sum of the numbers using the calculate_sum function
total_sum = calculate_sum(numbers_list)

# Print the calculated sum with a descriptive message
print("The sum of the numbers is:", total_sum)


input_number1 = int(input("Please input a number: "))
input_number2 = int(input("Please input another number: "))
def sum_numbers(number1, number2):
    return f"The addition of both numbers are {number1 + number2}"
print(sum_numbers(input_number1,input_number2))
 
def subtract_numbers(number1, number2):
    if number1 < number2:
        return "Sorry number 1 is smaller than number 2"
    else:
        return f"The substraction of both numbers are {number1 - number2}"
print(subtract_numbers(input_number1,input_number2))
 
def multiplication_numbers(number1, number2):
    return f"The multiplication of both numbers are {number1*number2}"
print(multiplication_numbers(input_number1,input_number2))