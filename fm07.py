import sys
print (sys.argv)

while True:
    text = input("What command do you want to run? ")
    if text == "exit" or text == "Exit":
        break
    print(text)