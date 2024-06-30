### Class work Count Vowels in a String
#please take an input from the user and count vowels in the given string



user = input("Enter a string: ")

def count_vowels(user):
    vowels = "aeiouAEIOU"
    count = 0
    for vowel in vowels:
        if vowel in user:
            count += 1
    return count

number_of_vowesls = count_vowels(user)
print(number_of_vowesls)
print(f"The number of vowels in {user} is {number_of_vowesls}")


user = input("Enter a string: ")

def count_vowels(user):
    vowels = "aeiouAEIOU"
    count = 0
    for char in user:  # Iterate over each character in the input string
        if char in vowels:
            count += 1
    return count

number_of_vowels = count_vowels(user)
print(f"The number of vowels in '{user}' is {number_of_vowels}")