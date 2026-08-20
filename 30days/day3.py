#if statements
#if statements are used to execute a block of code only if a certain condition is true
#if statements can be used to make decisions in your code
#if statements can be used to check if a condition is true or false
#if statements can be used to check if a variable is equal to a certain value
#they can also be used to check if a variable is greater than or less than a certain value
#they can also be used to check if a variable is not equal to a certain value

#if - else statements are used to execute a block of code if a certain condition is true, and another block of code if the condition is false
#they can be used to make decisions in your code
#they can be used to check if a variable is equal to a certain value, and execute a block of code if it is, and another block of code if it is not
#they can also be used to check if a variable is greater than or less than a certain value, and execute a block of code if it is, and another block of code if it is not

# ask = input("enter age: ")
# a = int(ask)
# if (a > 20):
#     print ("you are older than 20")
# else:
#     print ("you are younger than 20")
# #this is an example of an if statement that checks if the variable a is greater than 20. If it is, it will print "you are older than 20". If it is not, it will print "you are younger than 20".
# if (a%2 == 0):
#     print ("you are even")
# else:
#     print ("you are odd")

#nested if else statements are used to check multiple conditions in a single block of code
# age forms
#nested if statements are used to check multiple conditions in a single block of code
#if statements can be nested inside of other if statements to check for multiple conditions
#they can be used to check if a variable is equal to a certain value, and then check if it is greater than or less than another value
#they can also be used to check if a variable is not equal to a certain value, and then check if it is greater than or less than another value
#they can also be used to check if a variable is equal to a certain value, and then check if it is equal to another value
# age = int(input("enter your age: "))
# if (age >= 18):
#     print("you are an adult!")
# elif (age >= 13 and age <= 18):
#     print("you are a teenager!")
# else:
#     print("you are not a teenager or an adult..you are a child!")

# new
# age = int(input("enter your age: "))
# if (age >= 18):
#     print("you are an adult!")
#     if (age >= 18):
#         print("!!start working!!")
#     else:
#         print("!!start studying!!")
# elif (age >= 13 and age <= 18):
#     print("you are a teenager!")
# else:
#     print("you are not a teenager or an adult..you are a child!")


#loops
#loops are used to execute a block of code multiple times
#they can be used to iterate over a sequence of values, such as a list or a string
#they can also be used to execute a block of code while a certain condition is true
#there are two types of loops in python: for loops and while loops
#for loops are used to iterate over a sequence of values, such as a list or a string
#while loops are used to execute a block of code while a certain condition is true
#the break statement is used to exit a loop before it has finished iterating over all of the values in the sequence
#the continue statement is used to skip the current iteration of a loop and move on to the next iteration
#statements can be used to control the flow of a loop, such as break and continue

# for loops are used to iterate over a sequence of values, such as a list or a string
# list = [1, 2, 3, 4, 5]
# for i in list:
#     print(i**2)

#sum of numbers using for loop
# list = [1, 2, 3, 4, 5]
# summi = 0
# for i in list:
#     summi += i
# print(summi)

# #sum of even and odd numbers using for loop
# even_sum = 0
# odd_sum = 0
# for i in list:
#     if (i%2==0):
#         even_sum = even_sum + i
#     else:
#         odd_sum = odd_sum + i
# print("sum of even numbers: ", even_sum)
# print("sum of odd numbers: ", odd_sum)

#while loops are used to execute a block of code while a certain condition is true
#while loops can be used to execute a block of code multiple times, as long as the condition is true
#while loop conditions can be used to check if a variable is equal to a certain value, and execute a block of code if it is, and another block of code if it is not
# i = 0
# a = 0
# b = 0
# while (i <= 10):
#     if (i % 2 == 0):
#         a = a + i
#     else:
#         b = b + i
#     i=i+1
# print(a, b)

#break statement is used to exit a loop before it has finished iterating over all of the values in the sequence
#continue statement is used to skip the current iteration of a loop and move on to the next
#break and continue statements can be used to control the flow of a loop, such as break and continue
#they can be used to exit a loop before it has finished iterating over all of the values in the sequence, or to skip the current iteration of a loop and move on to the next
#the break statement can be used to exit a loop before it has finished iterating over all of the values in the sequence
# x = 1
# while (x <10):
#     print(x)
#     if (x==7):
#         break #here the loop will break when x is equal to 7
#     x=x+1

#continue statement is used to skip the current iteration of a loop and move on to the next
y = 0
while y <= 10:
    y = y + 3
    if y == 3:
        continue #here the loop will skip the current iteration when y is equal to 6
    print(y)
    