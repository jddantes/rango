import urllib, urllib2
import json

def main():

	accountKey = 'eri80JPiqDgBIyLqEiWmIZvVX/sxGkuVRfWyGX03lK0'

	queryBingFor = "'google fibre'" # the apostrophe's required as that is the format the API Url expects. 
	quoted_query = urllib.quote(queryBingFor)

	rootURL = "https://api.datamarket.azure.com/Bing/Search/"
	searchURL = rootURL + "Web?$format=json&Query=" + quoted_query
	search_url = searchURL
	username = ''

	password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, searchURL,username,accountKey)

	handler = urllib2.HTTPBasicAuthHandler(password_mgr)
	opener = urllib2.build_opener(handler)
	urllib2.install_opener(opener)
	readURL = urllib2.urlopen(searchURL).read()

	results = []

	try:
	    # Prepare for connecting to Bing's servers.
	    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
	    opener = urllib2.build_opener(handler)
	    urllib2.install_opener(opener)

	    # Connect to the server and read the response generated.
	    response = urllib2.urlopen(search_url).read()

	    # Convert the string response to a Python dictionary object.
	    json_response = json.loads(response)

	    # Loop through each page returned, populating out results list.
	    for result in json_response['d']['results']:
	    	

	        results.append({
	        'title': result['Title'],
	        'link': result['Url'],
	        'summary': result['Description']})

    # Catch a URLError exception - something went wrong when connecting!
	except urllib2.URLError, e:
		print "Error when querying the Bing API: ", e

	for r in results:
	 		print r


if __name__ == '__main__':
	main()
