from django.urls import path
from myapp import views
from mysiteS21 import settings
from django.conf.urls.static import static

app_name = 'myapp'

urlpatterns = [
                  path(r'', views.index, name='index'),
                  path(r'about/', views.about, name='about'),
                  path(r'<int:topic_id>', views.detail, name='detail'),
                  path(r'findcourses/', views.findcourses, name='findcourses'),
                  path(r'place_order/', views.place_order, name='place_order'),
                  path(r'review/', views.review, name='review'),
                  path(r'user_login/', views.user_login, name='user_login'),
                  path(r'user_logout/', views.user_logout, name='user_logout'),
                  path(r'my_account/', views.my_account, name='my_account'),
                  path(r'register/', views.register, name='register'),
              ]
