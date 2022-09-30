'''Program with intended error to demonstrate traceback from nested call'''

def invminus4(x):
    return 1.0/(x-4)

def main():
    print('This program is INTENDED to cause an execution error.')
    print('Ok call to invminus4(6) next:')
    print(invminus4(6))
    print('Bad call invminus4(4) next:')
    print(invminus4(4))
    print("Won't get to here!")

main()
