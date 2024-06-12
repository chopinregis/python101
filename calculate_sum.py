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