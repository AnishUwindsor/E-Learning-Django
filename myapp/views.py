import datetime

from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import views
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from .forms import SearchForm, OrderForm, ReviewForm, RegisterForm
from .models import Course, Student, Order, Topic


def index(request):
    top_list = Topic.objects.all().order_by('id')[:10]
    list_courses = Course.objects.all().order_by('-title')[:5]
    response = HttpResponse()
    heading1 = '<p>' + 'List of topics: ' + '</p>'
    response.write(heading1)
    for topic in top_list:
        para = '<p>' + str(topic.id) + ': ' + str(topic.name) + '</p>'
        response.write(para)

    heading2 = '<br> <p>' + 'List of Courses' + '</p>'
    response.write(heading2)
    for course in list_courses:
        para = '<p> <b>Title: </b>' + str(course.title) + ' <b> Price: </b>' \
               + str(course.price) + '</p>'
        response.write(para)

    return render(request, 'myapp/index.html', {'top_list': top_list})


def about(request):
    about_visits = request.session.get('about_visits', 1)
    request.session['about_visits'] = about_visits + 1
    request.session.set_expiry(300)
    return render(request, 'myapp/about.html', {'visits': about_visits})


def detail(request, topic_id):
    response = HttpResponse()
    try:
        topic = get_object_or_404(Topic, id=topic_id)
        topic_name = '<h2>' + str(topic.name).upper() + '</h2>'
        response.write(topic_name)
        topic_len = '<p><b>Length: </b>' + str(topic.length) + '</p>'
        response.write(topic_len)
        courses = get_list_or_404(Course, topic=topic_id)
        paragraph = '<p>' + '<b>Courses:</b>' + '</p>'
        response.write(paragraph)
        for course in courses:
            list_course = '<p> &emsp;&emsp;' + str(course.title) + '</p>'
            response.write(list_course)
    except Topic.DoesNotExist:
        response = get_object_or_404(Topic, pk=topic_id)

    return render(request, 'myapp/detail.html', {'topic': topic, 'courses': courses})


def findcourses(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            price = form.cleaned_data['max_price']
            length = form.cleaned_data['length'] or None
            if length is not None:
                topics = Topic.objects.filter(length=length)
            elif length == None:
                topics = Topic.objects.all()
            list_of_course = []
            for top in topics:
                list_of_course = list_of_course + list(top.courses.filter(price__lte=float(price)))
            return render(request, 'myapp/results.html', {'list_of_course': list_of_course, 'name': name})
        else:
            return HttpResponse('Invalid Data')
    else:
        form = SearchForm()
        return render(request, 'myapp/findcourses.html', {'form': form})


def place_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            courses = form.cleaned_data['courses']
            order = form.save(commit=True)
            student = order.student
            status = order.order_status
            order.save()
            if status == 1:
                for c in order.courses.all():
                    student.registered_courses.add(c)
            return render(request, 'myapp/order_response.html',
                          {'courses': courses, 'order': order, 'student': student})
        else:
            return render(request, 'myapp/place_order.html', {'form': form})
    else:
        form = OrderForm()
        return render(request, 'myapp/place_order.html', {'form': form})


def review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            course = form.cleaned_data['course']
            if 1 <= rating <= 5:
                review = form.save(commit=True)
                review.course.num_reviews = review.course.num_reviews + 1
                course.save()
                review.save()
                response = redirect('myapp:index')
                return response
            else:
                return render(request, 'myapp/review.html',
                              {'form': form, 'msg': 'You must enter a rating between 1 and 5!'})
        else:
            return render(request, 'myapp/review.html', {'form': form, 'msg': ""})
    else:
        form = ReviewForm()
        return render(request, 'myapp/review.html', {'form': form, 'msg': ''})


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print('Printing....  ' + request.GET.get('next', ''))
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                now = datetime.datetime.now()
                request.session['last_login'] = now.strftime("%m/%d/%Y, %H:%M:%S")
                request.session.set_expiry(3600)
                if request.GET.get('next', ''):
                    print('If executed..')
                    return HttpResponseRedirect(request.GET['next'])
                return HttpResponseRedirect(reverse('myapp:my_account'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        logout(request)
        return render(request, 'myapp/login.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('myapp:user_login'))


@login_required
def my_account(request):
    if request.user.is_authenticated:
        user = request.user
        if len(Student.objects.filter(username=user)) > 0:
            student = Student.objects.get(pk=user.id)
            return render(request, 'myapp/my_account.html',
                          {'fullname': user.get_full_name(), 'interested_in': student.interested_in.all(),
                           'registered': student.registered_courses.all(), 'image': student.image, 'student': True})
        else:
            return render(request, 'myapp/my_account.html', {'student': False, 'fullname': user.get_full_name()})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            msg = 'Student has been registered successfully'
            top_list = Topic.objects.all().order_by('id')[:10]
            return render(request, 'myapp/login.html', {'top_list': top_list, 'msg': msg})
        else:
            msg = 'Student registration failed. Please provide valid data!'
            form = RegisterForm()
            return render(request, 'myapp/register.html', {'msg': msg, 'form': form})
    else:
        form = RegisterForm()
        return render(request, 'myapp/register.html', {'form': form})
