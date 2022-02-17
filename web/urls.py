from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('cars/', views.cars_page, name='cars'),
    path('car_dy/', views.cars, name='car_dy'),
    path('car_s/', views.car_search, name='search'),
    path('car/<int:cid>', views.car_details, name='details'),
    path('testdrive/<int:cid>', views.testdrive, name="testdrive"),
    path('ordercar/<int:cid>', views.order_car, name='order'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('compare/', views.compare, name='compare'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
