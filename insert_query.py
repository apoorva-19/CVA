# state = input('Enter the state')
# num_dis = input('Enter the number of districts')

from state_district import code
state = list(code.keys())

insert_query = 'INSERT INTO user_id(state_district) VALUES("'
insert_end = '");'
import sys
sys.stdout = open('insert_query.sql', "a")

for i in range(len(state)):
	num_dis = len(code.get(state[i]))
	for j in range(num_dis):
		state_district = state[i]+str(j+1).zfill(2)
		new_insert = insert_query+state_district+insert_end
		print(new_insert)
