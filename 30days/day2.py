#variables in python
#variables are used to store data in python
#variable name should start with a letter or underscore
#variable_name = "Hello, World!"
#print(variable_name)
#this is integer variable
# a=10
# #this is float variable
# b=20.0
# #this is string variable
# c="Hello, World!"
# #this is boolean variable
# d=True
# #this is None variable
# e=None
# #this is list variable
# f= [1, 2, 3, 4, 5]
# #this is tuple variable
# g= (1, 2, 3, 4, 5)
# #this is dictionary variable
# h={"name": "John", "age": 30, "city": "New York"}
# #this is set variable
# i={1, 2, 3, 4, 5}
# print('b',type(b), b)
# print('c',type(c), c)
# print('d',type(d), d)
# print('e',type(e), e)
# print('f',type(f), f)
# print('g',type(g), g)
# print('h',type(h), h)
# print('i',type(i), i)
# name1 = 'dhara'
# name1 += 'riya'
# print(name1)
#string concatenation
#string concatenation is the process 
# of combining two or more strings into a single string
#it can be done using the + operator or the join() method
#it can also be done using the format() method or f-strings
#it can also be done using the % operator
#it can also be done using the str() function
#it can also be done using the repr() function
#it can also be done using the ascii() function
#it can also be done using the encode() method
#it can also be done using the decode() method
#it can also be done using the bytes() function
#it can also be done using the bytearray() function

app = 'dhara' 
app += str(1) 
print(app)
#int concatenation
#int concatenation is the process of combining two or more integers into a single integer
#it can be done using the + operator or the join() method


#dynamic typing
#dynamic typing is the process of changing the type of a variable at runtime
#it can be done using the type() function or the isinstance() function
#it can also be done using the eval() function or the exec() function
#it can also be done using the globals() function or the locals() function
#it can also be done using the vars() function or the dir() function
a = 10
a = "Hello, World!"
print('dynamic typing',type(a), a)#this will print "dynamic typing <class 'str'> Hello, World!" because the type of a is string and we are concatenating it with a string representation of an integer

#strong typing
#strong typing is the process of enforcing the type of a variable at runtime
#it can be done using the type() function or the isinstance() function
#it can also be done using the eval() function or the exec() function
#it can also be done using the globals() function or the locals() function
#it can also be done using the vars() function or the dir() function
a = "hell"
a + str(5)
print(a) #this will print "hell5" because the type of a is string and we are concatenating it with a string representation of an integer

#string formatting
#string formatting is the process of formatting a string using placeholders
#it can be done using the format() method or f-strings
#it can also be done using the % operator
#it can also be done using the str() function
#it can also be done using the repr() function
a = 200
print("The value of a is {}".format(a)) #this will print "The value of a is 200" because we are using the format() method to format the string

first = "dhara"
last = "riya"
print("the first of her name {0} and the last of her name {1}".format(first, last)) #this will print "the first of her name dhara and the last of her name riya" because we are using the format() method to format the string


# j= b"Hello, World!"
# k= bytearray(b"Hello, World!")
# l= memoryview(b"Hello, World!")
# m= complex(1, 2)
# n= range(10)
# o= frozenset([1, 2, 3, 4, 5])
# p= lambda x: x + 1
# print('j',type(j), j)
# print('k',type(k), k)
# print('l',type(l), l)
# print('m',type(m), m)
# print('n',type(n), n)
# print('o',type(o), o)
# print('p',type(p), p(5))

#input function
#input function is used to take input from the user
#it can be done using the input() function
#it can also be done using the raw_input() function in python 2.x
#name = input("Enter your name: ")
a = int(input("Enter your age: "))
b = float(input("Enter your age: "))
print("Hello, {}! You are {} years old.".format(a, b)) #this will print "Hello, dhara! You are 20 years old." because we are using the format() method to format the string
print(a + b)


#boolean values
#boolean values are used to represent the truth value of an expression
true = True
false = False
print("The value of true is: ", true) #this will print "The value of
