#python operators
#Arithmetic operators
#logical operators
#Comparison operators
#equality


'''
logical operators are used to combine conditional statements
and - returns True if both statements are true
or - returns True if at least one of the statements is true
not - returns True if the statement is false'''

#type(True and False) #returns boolean value True or False
# True and False #returns False
# True or False #returns True
# not True #returns False
# not False #returns True
# age = int(input("entere your age: "))
# if age>18 and age<=35:
#     print('earn money!!')


#true and true is always true
#true and false is always false
#true or true is always true
#true or false is always true

#false or false is always false
#false and false is always false
#false and true is always false
#false or true is always true


#logical not is used to reverse the logical state of its operand


age = int(input("entere your age: "))
if age>18 or age<=35:
    print('earn money!!')


'''
equality operators are used to compare values
== - equal to
!= - not equal to
> - greater than
< - less than
>= - greater than or equal to
<= - less than or equal to
is - returns True if both variables are the same object
is not - returns True if both variables are not the same object
'''