import win32file
win32file._setmaxstdio(2048)
from itertools import zip_longest
from collections import Counter
import glob
import json
 
def count_user_posts(array):
	#count number of posts a specific user did through the period
	counter = Counter()
	for post in array:
		x = json.loads(post)
		author = x['author']['id']
		counter[author] += 1
	
	#count number of users who have a specific number of posts:
	counter1 = Counter()
	for item in counter:
		#print(item + ' : ' + str(counter[item]))
		counter1[counter[item]] += 1

	NumOfPosts = sum(counter.values())
	NumOfAuthors=sum(counter1.values())
	
	print('Total number of Reddit posts: ' + str(NumOfPosts))
	print('Total number of Reddit users in subreddit: ' + str(NumOfAuthors))
	print('Average posts per user:' + str(NumOfPosts/NumOfAuthors))

	for item1 in sorted(counter1):
		print('Number of users who posted ' + str(item1) + ' posts: ' + str(counter1[item1]))

def count_post_comments(array):
	#count number of posts that had a specific number of comments through the period
	NumOfSubmissions = 0
	NumOfComments = 0
	counter = Counter()
	for post in array:
		x = json.loads(post)
		if 'title' in x.keys():
			NumOfSubmissions += 1
			comments = x['num_comments']
			NumOfComments += comments
			counter[comments] += 1
	
	print('Total number of Reddit threads: ' + str(NumOfSubmissions))
	print('Total number of Reddit comments in subreddit: ' + str(NumOfComments))
	print('Average number of comments per post:' + str(NumOfComments/NumOfSubmissions))

	for item in sorted(counter):
		print('Number of Reddit submissions that had ' + str(item) + ' comments: ' + str(counter[item]))

# Find all *.txt files in the directory
path = '/Users/phaiy/democrats/*.json'  
path1 = '/Users/phaiy/republicans/*.json' 
file_name_list = glob.glob(path)
file_name_list1 = glob.glob(path1)
 
# Try to open all of the files 
# Can't use 'with' as we have an unknown set of files 
 
# Open all of the files - trapping exceptions as we go 
try: 
	open_files = [open(file_name) for file_name in file_name_list]
	open_files1 = [open(file_name) for file_name in file_name_list1]
except OSERROR: 
	raise  
 
# Read all the lines at the same time 
# unpack the open_files list into zip 
# each open file is an iterator in it's own right 
try:
	democrat_arr = []
	republican_arr = []
	# lines will be a tuple of all of the 
	# corresponding lines from the files
	list_of_tuples = list(zip_longest(*open_files))
	list_of_tuples1 = list(zip_longest(*open_files1))
	tuple0_as_list = list(list_of_tuples[0])
	tuple0_as_list1 = list(list_of_tuples1[0])

	for lines in tuple0_as_list: 
		democrat_arr.append(lines)

	for lines1 in tuple0_as_list1: 
		republican_arr.append(lines1)

	print('Nov 6, 2020 - Nov 7, 2020:')
	print('Democrat statistics:')
	count_user_posts(democrat_arr)
	print("\n")
	count_post_comments(democrat_arr)

	print("\n\n")
	print('Republican statistics:')
	count_user_posts(republican_arr)
	print("\n")
	count_post_comments(republican_arr)
except: 
	raise 
finally: 
	#since we aren't using a context manager (with) 
	# we have to ensure all files get closed. 
	for open_file in open_files: 
		open_file.close() 