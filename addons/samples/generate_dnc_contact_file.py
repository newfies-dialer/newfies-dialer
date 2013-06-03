import sys, string
import namegen

# Use namegen : https://github.com/amnong/namegen


#640234009

test = namegen.NameGenerator()
count_contact = 0
max_contact = 10
start_phonenumber = 660200000

for it_name in test:
    count_contact = count_contact + 1

    if count_contact > max_contact:
        exit()

    print "%d" % (start_phonenumber)
    start_phonenumber = start_phonenumber + 1

