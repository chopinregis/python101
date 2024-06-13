def greet(name):
    return f"Hello, {name}!"
 
print(greet("Alice"))
 
def howmuchmoneydoihave(money):
    return f"Hello, you have CAD {money} in your account"
 
print(howmuchmoneydoihave(1))
 
def calculate_sum(numbers):
    return sum(numbers)

#1st step
input_numbers = input("Enter numbers separated by spaces: ")
 #2nd step
aftersplit = (input_numbers.split())
aftermap = (map(int, aftersplit))
afterlist = (list(aftermap))
print(afterlist)
print(aftermap)
print(afterlist)
numbers_list = list(map(int, input_numbers.split()))
print(numbers_list)
total_sum = calculate_sum(numbers_list)
print("The sum of the numbers is:", total_sum)

input_number1 = int(input("Please input a number: "))
input_number2 = int(input("Please input another number: "))
def sum_numbers(number1, number2):
    return f"The substraction of both numbers are {number1 + number2}"
print(sum_numbers(input_number1,input_number2))
 
def subtract_numbers(number1, number2):
    return f"The substraction of both numbers are {number1 - number2}"
print(subtract_numbers(input_number1,input_number2))
 
def multiplication_numbers(number1, number2):
    return f"The multiplication of both numbers are {number1*number2}"
print(multiplication_numbers(input_number1,input_number2))
