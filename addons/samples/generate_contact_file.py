import sys, string 
import namegen

# Use namegen : https://github.com/amnong/namegen

   
#640234009,	Teeuw,	Simen ,	Simen @gmail.com,	test subscriber,	1,

test = namegen.NameGenerator()
count_contact = 0
max_contact = 100000
start_phonenumber = 640200000

for it_name in test:
    count_contact = count_contact + 1
    print "%d,	%s%d,	%s%d,	%s%d@newmailer.com,	test subscriber,	1," % (start_phonenumber, it_name, count_contact, it_name, count_contact, it_name, count_contact)
    start_phonenumber = start_phonenumber + 1
    
    if count_contact > max_contact:
        exit()
    
