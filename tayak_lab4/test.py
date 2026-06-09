with open('1.txt', 'r') as file:
    string = file.read()

for i in string:
    if i == '\n':
        print('skibidi')
    print(i)