from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category,Page
from rango.forms import CategoryForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate,login
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from bing_search import run_query

def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).days > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response

# def index(request):
#
#     category_list = Category.objects.all()
#     page_list = Page.objects.order_by('-views')[:5]
#     context_dict = {'categories': category_list, 'pages': page_list}
#
#     # Get the number of visits to the site.
#     # We use the COOKIES.get() function to obtain the visits cookie.
#     # If the cookie exists, the value returned is casted to an integer.
#     # If the cookie doesn't exist, we default to zero and cast that.
#     visits = int(request.COOKIES.get('visits', '1'))
#
#     reset_last_visit_time = False
#     response = render(request, 'rango/index.html', context_dict)
#     # Does the cookie last_visit exist?
#     if 'last_visit' in request.COOKIES:
#         # Yes it does! Get the cookie's value.
#         last_visit = request.COOKIES['last_visit']
#         # Cast the value to a Python date/time object.
#         last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
#
#         # If it's been more than a day since the last visit...
#         if (datetime.now() - last_visit_time).days > 0:
#             visits = visits + 1
#             # ...and flag that the cookie last visit needs to be updated
#             reset_last_visit_time = True
#     else:
#         # Cookie last_visit doesn't exist, so flag that it should be set.
#         reset_last_visit_time = True
#
#         context_dict['visits'] = visits
#
#         #Obtain our Response object early so we can add cookie information.
#         response = render(request, 'rango/index.html', context_dict)
#
#     if reset_last_visit_time:
#         response.set_cookie('last_visit', datetime.now())
#         response.set_cookie('visits', visits)
#
#     # Return response back to the user, updating any cookies that need changed.
#     return response

# def index(request):
#     #context_dict = {'boldmessage': "I am a bold font from the context"}
#     request.session.set_test_cookie()
#     category_list= Category.objects.order_by('-likes')[:5]
#     page_list= Page.objects.order_by('-views')[:5]
#
#     context_dict= {'categories': category_list, 'pages': page_list}
#     return render(request, 'rango/index.html', context_dict)
#     #return HttpResponse("<br>Rango says hey there world!</br> <a href='/rango/about'>About</a>")


def about(request):

    if request.session.get("visits"):
        count = request.session.get("visits")
    else:
        count = 0
    context_dict = {'author': "Alex Chilikov", 'visits': count}
    return render(request, 'rango/about.html', context_dict)

def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None
    context_dict['views'] = None

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['views'] = category.views + 1
        context_dict['pages'] = pages
        context_dict['category'] = category

        category.views = context_dict['views']
        category.save()

        if not context_dict['query']:
            context_dict['query'] = category.name

    except Category.DoesNotExist:
        pass



    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

from rango.forms import PageForm

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
                # probably better to use a redirect here.
                return HttpResponseRedirect('/rango/category/' + category_name_slug)

               # return index(request)
               # return render(category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category': cat}

    return render(request, 'rango/add_page.html', context_dict)


def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})
# def register(request):
#
#
#     # A boolean value for telling the template whether the registration was successful.
#     # Set to False initially. Code changes value to True when registration succeeds.
#     registered = False
#
#     # If it's a HTTP POST, we're interested in processing form data.
#     if request.method == 'POST':
#         # Attempt to grab information from the raw form information.
#         # Note that we make use of both UserForm and UserProfileForm.
#         user_form = UserForm(data=request.POST)
#         profile_form = UserProfileForm(data=request.POST)
#
#         # If the two forms are valid...
#         if user_form.is_valid() and profile_form.is_valid():
#             # Save the user's form data to the database.
#             user = user_form.save()
#
#             # Now we hash the password with the set_password method.
#             # Once hashed, we can update the user object.
#             user.set_password(user.password)
#             user.save()
#
#             # Now sort out the UserProfile instance.
#             # Since we need to set the user attribute ourselves, we set commit=False.
#             # This delays saving the model until we're ready to avoid integrity problems.
#             profile = profile_form.save(commit=False)
#             profile.user = user
#
#             # Did the user provide a profile picture?
#             # If so, we need to get it from the input form and put it in the UserProfile model.
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']
#
#             # Now we save the UserProfile model instance.
#             profile.save()
#
#             # Update our variable to tell the template registration was successful.
#             registered = True
#
#         # Invalid form or forms - mistakes or something else?
#         # Print problems to the terminal.
#         # They'll also be shown to the user.
#         else:
#             print user_form.errors, profile_form.errors
#
#     # Not a HTTP POST, so we render our form using two ModelForm instances.
#     # These forms will be blank, ready for user input.
#     else:
#         user_form = UserForm()
#         profile_form = UserProfileForm()
#
#     # Render the template depending on the context.
#     return render(request,
#             'rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )


# def user_login(request):
#
#     # If the request is a HTTP POST, try to pull out the relevant information.
#     if request.method == 'POST':
#         # Gather the username and password provided by the user.
#         # This information is obtained from the login form.
#         username = request.POST['username']
#         password = request.POST['password']
#
#         # Use Django's machinery to attempt to see if the username/password
#         # combination is valid - a User object is returned if it is.
#         user = authenticate(username=username, password=password)
#
#         # If we have a User object, the details are correct.
#         # If None (Python's way of representing the absence of a value), no user
#         # with matching credentials was found.
#         if user:
#             # Is the account active? It could have been disabled.
#             if user.is_active:
#                 # If the account is valid and active, we can log the user in.
#                 # We'll send the user back to the homepage.
#                 login(request, user)
#                 return HttpResponseRedirect('/rango/')
#             else:
#                 # An inactive account was used - no logging in!
#                 return HttpResponse("Your Rango account is disabled.")
#         else:
#             # Bad login details were provided. So we can't log the user in.
#             # print "Invalid login details: {0}, {1}".format(username, password)
#             # if not User.objects.get(username=username):  #
#             #     return HttpResponse("Invalid username")
#             # elif User.objects.get(username=username).check_password(password):
#             #     return HttpResponse("Invalid password")
#             return HttpResponse("Invalid username and password supplied.")
#
#     # The request is not a HTTP POST, so display the login form.
#     # This scenario would most likely be a HTTP GET.
#     else:
#         # No context variables to pass to the template system, hence the
#         # blank dictionary object...
#         return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

# Use the login_required() decorator to ensure only those logged in can access the view.
# @login_required
# def user_logout(request):
#     # Since we know the user is logged in, we can now just log them out.
#     logout(request)
#
#     # Take the user back to the homepage.
#     return HttpResponseRedirect('/rango/')

from django.shortcuts import redirect


def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)


from django.contrib.auth.decorators import login_required

@login_required
def like_category(request):

    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes =  likes
            cat.save()

    return HttpResponse(likes)


def suggest_category(request):

        cat_list = []
        starts_with = ''
        if request.method == 'GET':
                starts_with = request.GET['suggestion']

        cat_list = get_category_list(8, starts_with)

        return render(request, 'rango/category_list.html', {'cat_list': cat_list })


def get_category_list(max_results=0, starts_with=''):
        cat_list = []
        if starts_with:
                cat_list = Category.objects.filter(name__istartswith=starts_with)

        if max_results > 0:
                if len(cat_list) > max_results:
                        cat_list = cat_list[:max_results]

        for cat in cat_list:
            cat.url = url(cat.name)
        return cat_list

def url(url):
    func = lambda s: s[:1].lower() + s[1:] if s else ''
    return func(url).replace(' ', '-')

@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}

    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']

        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)

            pages = Page.objects.filter(category=category).order_by('-views')

            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages

    return render(request, 'rango/page_list.html', context_dict)


def register_profile(request):
    if not request.user.is_authenticated():
        return HttpResponse("Please logged in first.")

    # check if HTTP POST
    if request.method == 'POST':
        form = UserProfileForm(request.POST)

        # is form valid
        if form.is_valid():
            # put saving off to make the reference between profile and user first
            profile = form.save(commit=False)
            profile.user = request.user

            # If picture, add it to the UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # save the UserProfile instance
            profile.save()

            # navigate to homepage
            return index(request)
        else:
            print form.errors #print errors
    else:
        # If Get, create a new ProfileForm instance and send user to profile_registration
        form = UserProfileForm()

    return render(request, 'rango/profile_registration.html', {'form': form})


from models import UserProfile

def profile(request):
    if not request.user.is_authenticated():
        return HttpResponse("Please logged in first.")

    context_dict = {}
    profile = UserProfile.objects.get(user = request.user)

    # if HTTP POST
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        form.fields['website'].initial = profile.website
        context_dict['form'] = form
        context_dict['picture'] = profile.picture

        # If valid form
        if form.is_valid():
            # do not save to get user
            updatedProfile = form.save(commit=False)
            updatedProfile.user = request.user

            # If picture send - add to updatedProfile
            if 'picture' in request.FILES:
                updatedProfile.picture = request.FILES['picture']

            # save the UserProfile instance
            try:
                updatedProfile.save()
            except:
                profile.delete()
                updatedProfile.save()

            return index(request)
        else:
            print form.errors
    else: # if HTTP GET show the page
        form = UserProfileForm()
        form.fields['website'].initial = profile.website
        context_dict['form'] = form
        context_dict['picture'] = profile.picture

    return render(request, 'rango/profile.html', context_dict)

def profiles(request):

    context_dict = {}
    # Query all the profiles from database
    allprofiles = UserProfile.objects.all()
    # Add to context_dict
    context_dict['profiles'] = allprofiles

    # redirect to allProfies.html
    return render(request, 'rango/allProfiles.html', context_dict)