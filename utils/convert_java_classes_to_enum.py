

file = open("events.javaj", 'r')

for line in file.readlines():
    print('{} = "{}"'.format(line.replace(',','').strip(), line.replace(',','').capitalize().replace('_',' ').strip().title()))
