import self as self
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone


class Topic(models.Model):
    name = models.CharField(max_length=200)
    # 3.b
    length = models.IntegerField(default=12)

    def __str__(self):
        return '%s' % (self.name)


class Course(models.Model):
    title = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, related_name='courses', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(100.00, message='Price must be greater than 100.00 !!'),
                                            MaxValueValidator(200.00, message='Price must be less than 200.00 !!')])
    for_everyone = models.BooleanField(default=True)
    # 3.c
    # optional = models.TextField(default=True)
    num_reviews = models.PositiveIntegerField(default=0)
    hours = models.IntegerField(default=10)

    def __str__(self):
        return self.title
    def get_cost(self):
        return self.price


class Student(User):
    LVL_CHOICES = [('HS', 'High School'),
                   ('UG', 'Undergraduate'),
                   ('PG', 'Postgraduate'),
                   ('ND', 'No Degree')
                   ]
    CITY_CHOICES = [('WS', 'Windsor'),
                    ('CG', 'Calgary'), ('MR', 'Montreal'), ('VC', 'Vancouver')]
    level = models.CharField(choices=LVL_CHOICES, max_length=2, default='HS')

    # 3.d
    address = models.CharField(max_length=300, null=True)
    # 3.e
    province = models.CharField(max_length=2, default='ON')
    city = models.CharField(max_length=2, choices=CITY_CHOICES, default='WS')
    registered_courses = models.ManyToManyField(Course, blank=True)
    interested_in = models.ManyToManyField(Topic)
    image = models.ImageField(upload_to='media', blank=True)


    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)


class Order(models.Model):
    ORD_CHOICES = [(0, 'Cancelled'),
                   (1, 'Confirmed'),
                   (2, 'On hold'),
                   ]
    courses = models.ManyToManyField(Course)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    order_status = models.IntegerField(choices=ORD_CHOICES, default=1)
    order_date = models.DateField(default=timezone.now)

    def __str__(self):
        return "Order from " + self.Student.first_name + ' ' + self.Student.last_name + ' with total price %s' % self.total_cost()

    def total_cost(self):
        return sum([courses.price for courses in self.courses.all()])

    def total_items(self):
        return self.courses.count()


class Review(models.Model):
    reviewer = models.EmailField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1, message='Rating must be 1 or greater !!'),
                                                     MaxValueValidator(5, message='Max 5 Rating is allowed !!')])
    comments = models.TextField(null=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return 'Reviewer email: %s, Course: %s, Rating:  %s' % (self.reviewer, self.course, self.rating)
