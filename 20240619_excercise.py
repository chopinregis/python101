### Class work Count Vowels in a String
#please take an input from the user and count vowels in the given string



user = input("Enter a string: ")
print(user)

def count_vowels(user):
    vowels = "aeiouAEIOU"
    count = 0
    for vowel in user:
        if vowel in vowels:
            count += 1
    return count

number_of_vowesls = count_vowels(user)
print(number_of_vowesls)
print(f"The number of vowels in {user} is {number_of_vowesls}")

### Please give user an option to give a list of integer, once input is provided, then ask the question, "do you want the minimum or maximum? type 'minimum; to see the number that is smallest" and vice versa the maxmum

user = input("Enter a list of integers: ")

question = input("Do you want the minimum or maximum? type 'minimum' to see the number that is smallest; type 'maximum' to see the number that is largest: ")
if question == "minimum":
    minimum = min(user)
    print(minimum)
    print(f"The number that is smallest is {minimum}")

elif question == "maximum":
    maximum = max(user)
    print(maximum)
    print(f"The number that is largest is {maximum}")
print("Thank you")


### sum_even_numbers([1, 2, 3, 4, 5, 6]) should return 12
### please try this problem, so it should sum only the even numbers here from the list

def sum_even_numbers(numbers):
  sum_of_evens = 0
  for number in numbers:
    if number % 2 == 0:  # Check if the number is even (divisible by 2 with no remainder)
      sum_of_evens += number
  return sum_of_evens

# Example usage
numbers = [1, 2, 3, 4, 5, 6]
sum_of_evens = sum_even_numbers(numbers)
print(f"The sum of even numbers in {numbers} is {sum_of_evens}")
