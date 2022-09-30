'''Test float formatting.'''

x = 23.457413902458498
print(x, 'to 5 places:', format(x, '.5f'), 'to 2 places:', format(x, '.2f'))
                                  
x = 2.876543
y = 16.3591
print('x:', x, 'y:', y)
print('x long: {:.5f}, x short: {:.3f}, y: {:.2f}.'.format(x, x, y))
print('Same from locals dictionary:')
print('x long: {x:.5f}, x short: {x:.3f}, y: {y:.2f}.'.format(**locals()))

print('Python approximations to 20 digits for .1, .2, .1 + .2, and .3:')
print(format(.1, '.20f'))
print(format(.2, '.20f'))
print(format(.1 + .2, '.20f'))
print(format(.3, '.20f'))
print()
print('Note that the results for .1 + .2 and for .3 are different!')
