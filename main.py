import json
import os
import sys
import urllib2

FILE_DELINEATOR = '!!**!!' # gross, I know.
HASTE_URL = 'http://hastebin.com/'
POST_URL = HASTE_URL + 'documents/'
GET_URL = HASTE_URL + 'raw/'

# Return codes
SUCCESSFUL_ACTION = 1
IMPROPER_FILE_ERROR = 2
FILE_CREATION_ERROR = 3

# post file to hastebin.
# returns hastebin_key if successful;
# returns error code otherwise
def post(signifier):
	try:
		contents = {file: open(file).read() for file in signifier}
	
	# The main thing that I've ran into is file not existing	
	except IOError:
		return IMPROPER_FILE_ERROR
		
	payload = ''
	for header in contents:
		payload += '\n' + FILE_DELINEATOR + header + FILE_DELINEATOR + '\n'
		payload += contents[header]
		
	# Get rid of newline char at beginning of payload due to l.22
	payload = payload[1:]
		
	request = urllib2.Request(POST_URL, payload)
	response = urllib2.urlopen(request).read()
	hastebin_key = json.loads(response)['key']
	return hastebin_key

# downloads files from a given hastebin key
# returns a list of the filenames downloaded if successful;
# returns error code otherwise	
def get(signifier):
	
	# Gross way of flattening the list to a string;
	# since you'd only need to 'get' one hastebin at a time,
	# this should work out okay
	haste_id = signifier[0]
	
	request = urllib2.Request(GET_URL + haste_id)
	response = urllib2.urlopen(request)
	fulltext = response.read()
	
	# Parse the response for separate files, creating a dictionary of the results.
	unsorted_contents = fulltext.split(FILE_DELINEATOR)
	unsorted_contents = unsorted_contents[1:]
	
	# Create some files!
	number_of_files = len(unsorted_contents) / 2
	successful_files = []
	
	for file_index in range(number_of_files):
		file_name = unsorted_contents[file_index * 2]
		file_content = unsorted_contents[file_index * 2 + 1][1:]
		
		# Edge case that I haven't worked with too much
		target_location = './'
		if len(signifier) > 1:
			target_location = signifier[1]
			
			if target_location[-1] != '/':
				target_location += '/'
				
		file_pointer = open(target_location + file_name, 'w')
		file_pointer.write(file_content)
		file_pointer.close()
		successful_files.append(file_name)
	
	return successful_files
			

def main(argv=None):
	if argv is None:
		argv = sys.argv
	
	if len(sys.argv) < 3:
		print 'Usage:'
		print 'celerity post <filename>'
		print 'celerity get <url> [target folder]'
		return 0

	else:
		command = sys.argv[1]
		signifier = sys.argv[2:]
		
		result = actions = {
			'post': post,
			'get': get
		}[command](signifier)
		
		if result == IMPROPER_FILE_ERROR:
			print "Unable to upload file. Be sure to make sure it exists!"
			return 0
		elif result == FILE_CREATION_ERROR:
			print "Able to download file but not write it to disk."
			return 0
		else:
			print "Success!"
			print result
			return 1

if __name__ == '__main__':
	sys.exit(main())