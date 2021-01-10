#Yen Pham
import win32file
win32file._setmaxstdio(2048)
from itertools import zip_longest
from collections import Counter
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer
from sklearn import svm 
import glob
import json
import string
import random

stemmer = PorterStemmer()
tokenizer = WordPunctTokenizer() 
stop_words = set(stopwords.words('english')) 

#process text, remove stop words, punctuations, crazy symbols, etc.
def process_text(array):
	stemmed_posts = []
	most_common_words = []	

	#tokenize and stem clean the words in the posts
	for post in array:
		x = json.loads(post)
		
		for i in range(len(x['posts'])):
			post_content = x['posts'][i]['text']

			word_tokens = tokenizer.tokenize(post_content.lower()) 
			filtered_words = []

			for word in word_tokens:
				if word not in stop_words and word not in string.punctuation and len(word) != 1:
					filtered_words.append(word)
		
			stemmed_words = []				
			for filtered_word in filtered_words:
				if filtered_word.isalpha() or filtered_word.isdigit():
					stemmed_words.append(stemmer.stem(filtered_word))
		
			if stemmed_words:
				stemmed_posts.append(stemmed_words)
	return stemmed_posts

#get the most common words and calculate the frequency each word appear per one Party's post 
def get_common_words(stemmed_posts):
	words_to_count = []
	counter = Counter()

	for post in stemmed_posts:
		for word in post:
			words_to_count.append(word)

	#count the number of times each word is used by one party
	for word in words_to_count:
		counter[word] += 1

	NumofPost = len(stemmed_posts)

	most_common_words = counter.most_common(1000)
	print(most_common_words)

	most_common_words_frequency = []
	for word in most_common_words:
		most_common_words_frequency.append( (word[0], word[1]/NumofPost) )

	#print(most_common_words_frequency)
	return most_common_words_frequency

#get list of words that has "identification" power (words that are mostly used by only one Party, or the frequency that word appeared in that Party is significantly higher than the other Party) 
def get_unique_words(democrat, republican):
	#create key word list that can identify democrat and republican
	democrat_list = []
	republican_list = []
	word_list = []
	counter = Counter()

	#check if there are words frequently used by both Party. If so, we have to see who used more frequently
	duplicate = False
	for word in democrat:
		for word1 in republican:
			if word[0] == word1[0]:
				duplicate = True
				num = word[1]/word1[1]
				if num > 1.2 or num < 0.5:
					word_list.append(word[0])
					#if democrats used more frequently
					if num > 1.2:
						democrat_list.append(word[0])
					#if republicans used the word more frequently
					if num < 0.5:
						republican_list.append(word1[0])
		if duplicate == False:
			#append back the words only frequently used by Democrats
			word_list.append(word[0])
			democrat_list.append(word[0])

	duplicate = False
	for word in republican:
		for word1 in democrat:
			if word[0] == word1[0]:
				duplicate = True
		if duplicate == False:
			#append back the words only frquently used by Republicans
			word_list.append(word[0])
			republican_list.append(word[0])

	#for word in word_list:
	#	counter[word] += 1
	#print(counter)
	
	#Print words list
	print("\nWords list to identify Democrats:\n")
	print(democrat_list)
	print("\nWords list to identify Republicans:\n")
	print(republican_list)
	#print('\n')
	#print(word_list)

	return word_list

#process the word list to put it into training and testing
def convert_to_data_points(post_array, keyword_list):
	data_points_array = []
	
	for post in post_array:
		post_data_point = []
		for key_word in keyword_list:
			post_data_point.append(post.count(key_word))	
		data_points_array.append(post_data_point)
	#print(data_points_array)
	return data_points_array

# Find all *.txt files in the directory
path = '/Users/phaiy/democrat_users/*.json'  
path1 = '/Users/phaiy/republican_users/*.json' 
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

	democrat_stemmed_posts = []
	democrat_stemmed_posts = process_text(democrat_arr)

	democrat_common_words = []
	print("\nTop 1000 words mostly used by Democrats: \n")
	democrat_common_words = get_common_words(democrat_stemmed_posts)

	republican_stemmed_posts = []
	republican_stemmed_posts = process_text(republican_arr)
	
	republican_common_words = []
	print("\nTop 1000 words mostly used by Republicans: \n")
	republican_common_words = get_common_words(republican_stemmed_posts)

	combined_word_list = []
	combined_word_list = get_unique_words(democrat_common_words, republican_common_words)

	democrat_data_points = []
	democrat_data_points = convert_to_data_points(democrat_stemmed_posts, combined_word_list)

	republican_data_points = []
	republican_data_points = convert_to_data_points(republican_stemmed_posts, combined_word_list)

	combined_data_points = []
	combined_data_points = democrat_data_points + republican_data_points
	#print(combined_data_points)

	classify_array = []
	for i in range(len(democrat_stemmed_posts)):
		classify_array.append(int(1))

	for i in range(len(republican_stemmed_posts)):
		classify_array.append(int(0))

	print("\nTotal number of posts for training and testing: " + str(len(classify_array)))
	#print(len(classify_array))
	#print(len(combined_data_points))

	temp_arr = []
	for i in range(len(classify_array)):
		temp_arr.append((combined_data_points[i], classify_array[i]))

	data_point_2train = []
	data_point_2test = []
	classifyarr_2train = []
	classifyarr_2test = []

	#randomly take 20% for training, 80% posts for testing
	for i in range(len(classify_array)):
		rand_num = random.randint(1,10)
		if rand_num <= 8:
			data_point_2train.append(temp_arr[i][0])
			classifyarr_2train.append(temp_arr[i][1])
		else:
			data_point_2test.append(temp_arr[i][0])
			classifyarr_2test.append(temp_arr[i][1])

	print("Number of Democrats posts: " + str(len(democrat_stemmed_posts)))
	print("Number of Republicans posts: " + str(len(republican_stemmed_posts)))
	print("Number of posts for training: " + str(len(data_point_2train)))
	#print(data_point_2train)
	#print(classifyarr_2train)
	#print(len(data_point_2train))
	#print(len(classifyarr_2train))
	print("Number of posts for testing: " + str(len(data_point_2test)))
	#print(len(data_point_2test))

	test_result = []
	classifier = svm.SVC()
	classifier.fit(data_point_2train, classifyarr_2train)
	test_result = classifier.predict(data_point_2test)

	#print(len(test_result))
	#print(len(classifyarr_2test))

	test_democrat_count = 0
	test_republican_count = 0
	for i in range(len(classifyarr_2test)):
		if classifyarr_2test[i] == 1:
			test_democrat_count += 1
		else:
			test_republican_count += 1

	correct_count = 0
	wrong_democrat = 0
	wrong_republican = 0
	for i in range(len(test_result)):
		if test_result[i] == classifyarr_2test[i]:
			correct_count +=1
		else:
			#if the label says the post belongs to Republican while the testing says it belongs to Democrat, we count how many republican got wrong prediction result
			if test_result[i] == 1:
				wrong_republican +=1
			#if the other way, the labels says the post belongs to Democrat while the testing says it belongs to Republican
			elif test_result[i] == 0:
				wrong_democrat +=1
	#Question: Is the post Democrat?
	TP = test_democrat_count - wrong_democrat
	TN = test_republican_count - wrong_republican
	FP = wrong_republican
	FN = wrong_democrat
	precision = TP/(TP+FP)
	recall = TP/(TP+FN)
	specificity =  TN / test_republican_count
	F1 = (2*precision*recall)/(precision + recall)

	#Question: Is the post Republican?
	TP_1 = test_republican_count - wrong_republican
	TN_1 = test_democrat_count - wrong_democrat
	FP_1 = wrong_democrat
	FN_1 = wrong_republican
	precision_1 = TP_1/(TP_1+FP_1)
	recall_1 = TP_1/(TP_1+FN_1)
	specificity_1 =  TN_1 / test_democrat_count
	F1_1 = (2*precision_1*recall_1)/(precision_1 + recall_1)

	print("Out of " + str(test_democrat_count) + " Democrat/Liberals posts being tested, number of Democrat/Liberal posts was predicted correctly: " + str(TP) )
	print("Out of " + str(test_republican_count) + " Republican/Conservative posts being tested, number of Republican/Conservative posts was predicted correctly: " + str(TP_1) )
	print("Prediction accuracy % of Democrat/Liberal posts: " + str(TP*100/test_democrat_count) )
	print("Prediction accuracy % of Republican/Conservative posts: " + str( TP_1*100/test_republican_count ) )
	print("Overall testing prediction accuracy %: " + str(correct_count*100/len(test_result)))
	print("\nTake Democrat as positive class: ")
	print("Precision: " + str(precision) )
	print("Recall: " + str(recall) )
	print("Specificity: " + str(specificity))
	print("F-1 score: " + str(F1) )

	print("\nTake Republican as positive class: ")
	print("Precision: " + str(precision_1) )
	print("Recall: " + str(recall_1) )
	print("Specificity: " + str(specificity_1))
	print("F-1 score: " + str(F1_1) )



except: 
	raise 
finally: 
	#since we aren't using a context manager (with) 
	# we have to ensure all files get closed. 
	for open_file in open_files: 
		open_file.close() 
