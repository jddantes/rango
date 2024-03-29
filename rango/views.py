from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query

# Create your views here.

def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'boldmessage': "I am bold font from the context", 'categories':category_list, 'pages':page_list}
	
	visits = request.session.get('visits')

	if not visits:
		visits = 1

	reset_last_visit_time = False

	last_visit = request.session.get('last_visit')
	if last_visit:
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
		if (datetime.now() - last_visit_time).seconds > 0:
			visits = visits + 1
			reset_last_visit_time = True
	else:
		reset_last_visit_time = True

	if reset_last_visit_time:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = visits
	context_dict['visits'] = visits

	response = render(request, 'rango/index.html', context_dict)

	return response

def category(request, category_name_slug):
	context_dict = {}

	try:
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages
		context_dict['category'] = category
		context_dict['category_name_slug'] = category_name_slug
	except:
		category = None
		

	result_list = []

	if request.method == 'POST':
		query = request.POST['query']

		if query:
			result_list = run_query(query)
			context_dict['result_list'] = result_list
			context_dict['query'] = query
	try:
		if not context_dict['query']:
			pass
	except:
		if category:
			context_dict['query'] = category.name
		else:
			context_dict['query'] = category_name_slug



	return render(request, 'rango/category.html', context_dict)

def about(request):

	visits = request.session.get('visits')
	reset_last_visit_time = False
	if not visits:
		visits = 1

	last_visit = request.session.get('last_visit')
	if last_visit:
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
		if(datetime.now() - last_visit_time).seconds > 0:
			visits = visits + 1
			reset_last_visit_time = True
	else:
		reset_last_visit_time = True

	if reset_last_visit_time:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = visits

	about_visits = request.session.get('about_visits')
	reset_last_visit_time = False
	if not about_visits:
		about_visits = 1
	last_about_visit = request.session.get('last_about_visit')
	if last_about_visit:
		last_about_visit_time = datetime.strptime(last_about_visit[:-7], "%Y-%m-%d %H:%M:%S")
		if(datetime.now() - last_about_visit_time).seconds > 0:
			about_visits = about_visits + 1
			reset_last_visit_time = True
	else:
		reset_last_visit_time = True

	if reset_last_visit_time:
		request.session['about_visits'] = about_visits
		request.session['last_about_visit'] = str(datetime.now())
	
	context_dict = {'visits': visits, 'about_visits':about_visits, }


	return render(request, 'rango/about.html', context_dict)

@login_required
def add_category(request):
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)

			return index(request)
		else:
			# Print errors to terminal
			print(form.errors)

	else:
		form = CategoryForm()

	return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):

	try:
		cat = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		cat = None

	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()

				return category(request, category_name_slug)
			else:
				print (form.errors)
	else:
		form = PageForm()

	context_dict = {'form':form, 'category': cat}

	return render(request, 'rango/add_page.html', context_dict)

def register(request):

	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()

			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()

			registered = True

		# Invalid form or forms
		# Print in termina
		# Also show to user
		else:
			print (user_form.errors, profile_form.errors)

	# Not POST - render using two ModelForm instances
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	context_dict = {'user_form':user_form, 'profile_form': profile_form, 'registered': registered}
	return render(request, 'rango/register.html', context_dict)

def user_login(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/rango/')
			else:
				return HttpResponse("Your Rango account is disabled")
		else:
			# Bad login details
			print("Invalid login details: {0}, {1}".format(username,password))
			return HttpResponse("Invalid login details supplied.")

	else:
		return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/rango/')

def search(request):
	result_list = []

	if request.method == 'POST':
		query = request.POST['query'].strip()

		if query:
			result_list = run_query(query)


	return render(request, 'rango/search.html', {'result_list': result_list})

def track_url(request):
	if request.method == 'GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try:
				page = Page.objects.get(id=page_id)
				page.views = page.views + 1
				page.save()
				return HttpResponseRedirect(page.url)
			except Exception as e:
				print('Didnt get object with page_id ' + page_id)
				print(e)
				pass
	
	return HttpResponseRedirect('/rango/')

def register_profile(request):

	if request.user.is_authenticated():
		registered = False
		if request.method == 'POST':
			profile_form = UserProfileForm(data=request.POST)	
			if profile_form.is_valid():
				profile = profile_form.save(commit=False)
				profile.user = request.user
				if 'picture' in request.FILES:
					profile.picture = request.FILES['picture']
				profile.save()
				registered = True
			else:
				print(profile_form.errors)
		else:
			profile_form = UserProfileForm()
		context_dict = {'profile_form':profile_form, 'registered': registered}
		return render(request, 'rango/profile_registration.html', context_dict)
	else:
		return HttpResponseRedirect('/rango/accounts/login/')

@login_required
def profile(request):

	context_dict = {}
	return render(request, 'rango/profile.html', context_dict)

	
