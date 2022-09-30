f = open('formatExamples.py')
line = f.readline()
while line and line[-1] == '\n':
    print('y')
    line = f.readline()
print('Final:', line)
line = f.readline()
print('Final:', line)
f.close()
