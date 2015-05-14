import json
import urllib
import urllib.parse
import urllib.request
import urllib.error
from keys import BING_API_KEY


def run_query(search_terms):
	root_url = 'https://api.datamarket.azure.com/Bing/Search/'
	source = 'Web'

	results_per_page = 10
	offset = 0

	query = "'{0}'".format("google fibre")

	query = urllib.parse.quote(query)


	search_url = root_url + "Web?$format=json&Query=" + query

	username = ''

	password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, search_url, username, BING_API_KEY)

	results = []

	try:
		handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
		opener = urllib.request.build_opener(handler)
		urllib.request.install_opener(opener)

		response = urllib.request.urlopen(search_url).read().decode('utf-8')
		print(response)
		# print(type(response))

		json_response = json.loads(response)

		for result in json_response['d']['results']:
			print(result['Title'])
			print(result['Url'])
			print(result['Description'])
			results.append({
				'title': result['Title'],
				'link': result['Url'],
				'summary':result['Description']})
	except urllib.error.URLError as e:
		print("Error when querying the Bing API: ", e)

	return results

def main():

	print(BING_API_KEY)
	
	userInput = input("Enter query: ")
	results = run_query(userInput)

	for r in results:
		print(r)


if __name__ == '__main__':
	main()