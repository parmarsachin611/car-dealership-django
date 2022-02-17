from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages, auth
from django.contrib.auth.models import User
from datetime import datetime

from .forms import UserForm, TestDriveForm, CompareForm
from .models import Car, TestDrive, Order

# Create your views here.
def index(request):
    return render(request, 'web/index.html')

def about(request):
    return render(request, 'web/about.html')

def register(request):
    if request.method == 'POST':
        # Get form values
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Check if passwords match
        if password == password2:
            # Check username
            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is taken')
                return redirect('web:register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'That email is being used')
                    return redirect('web:register')
          
                else:
                    # Looks good
                    user = User.objects.create_user(username=username, password=password,email=email, first_name=first_name, last_name=last_name)
                    # Login after register
                    # auth.login(request, user)
                    # messages.success(request, 'You are now logged in')
                    # return redirect('index')
                    user.save()
                    messages.success(request, 'You are now registered and can log in')
                    return redirect('web:login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('web:register')

    else:
        return render(request, 'web/register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)    

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('web:cars')

        else:
            messages.error(request, 'Invalid credentials')
            return redirect('web:login')
    else:
        return render(request, 'web/login.html')

    
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You are now logged out')
        return redirect('web:index')

def cars_page(request, pg=1):

    # Each page has 9 requests. That is fixed.
    start = (pg-1) * 9
    end = start + 9

    car_list = Car.objects.all()[start:end]
    context = {
        'cars': car_list
    }

    return render(request, 'web/cars.html', context)

def car_search(request):
    if request.method == 'GET':
        if request.GET.get('search'):
            search = request.GET.get('search')
        else:
            search = ''
        if request.GET.get('start'):
            start = int(request.GET.get('start'))
        else:
            start = 0
        if request.GET.get('end'):
            end = int(request.GET.get('end'))
        else:
            end = 9

        objs = Car.objects.filter(
            Q(brand__icontains=search) | Q(name__icontains=search)
        )[start:end]
        data = serializers.serialize('json', objs)
        return HttpResponse(data)


def cars(request):
    if request.method == 'GET':
        if request.GET.get('start'):
            start = int(request.GET.get('start'))
        else:
            start = 0
        if request.GET.get('end'):
            end = int(request.GET.get('end'))
        else:
            end = 9
        if request.GET.get('make'):
            make = request.GET.get('make')
            if make == 'all':
                make = ''
        else:
            make = ''
        if request.GET.get('cost_min'):
            cost_min = int(float(request.GET.get('cost_min')))
        else:
            cost_min = 0
        if request.GET.get('cost_max'):
            cost_max = int(float(request.GET.get('cost_max')))
        else:
            cost_max = 999999999
        if request.GET.get('fuel'):
            fuel = request.GET.getlist('fuel')
        else:
            fuel = ['petrol', 'diesel']

        if len(fuel) > 1:
            objs = Car.objects.filter(
                Q(car_make__icontains=make) &
                Q(price__gte=cost_min) &
                Q(price__lte=cost_max) &
                (Q(fuel__icontains=fuel[0]) | Q(fuel__icontains=fuel[1]))
            )[start:end]

        else:
            objs = Car.objects.filter(
                car_make__icontains=make,
                price__gte=cost_min,
                price__lte=cost_max,
                fuel__icontains=fuel[0]
            )[start:end]

    else:
        objs = Car.objects.all()[:9]

    data = serializers.serialize('json', objs)
    return HttpResponse(data)

def car_details(request, cid):
    car = Car.objects.get(pk=cid)
    form = TestDriveForm(initial={'car': car})
    context = {
        'car': car,
        'form': form
    }
    return render(request, 'web/car_details.html', context)


def order_car(request, cid):
    if not request.user.is_authenticated:
        return redirect('web:login')
    user = request.user
    car = Car.objects.get(pk=cid)

    if request.method == 'POST':
        try:
            address = request.POST['address']
            new = Order(
                user=user,
                car=car,
                amount=car.price,
                address=address
            ).save()

            return HttpResponse("Your order has been placed!")
        except Exception as e:
            return HttpResponse("Uh Oh! Something's wrong! Report to the developer with the following error" +
                                e.__str__())
    return HttpResponseForbidden()


def testdrive(request, cid):
    if not request.user.is_authenticated:
        return redirect('web:login')
    user = request.user
    car = Car.objects.get(pk=cid)

    if request.method == 'POST':
        try:
            date = request.POST['date']
            new_date = datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
            test = TestDrive(
                user=user,
                car=car,
                time=new_date
            ).save()

            return HttpResponse("Your testdrive has been booked!")
        except Exception as e:
            return HttpResponse("Uh Oh! Something's wrong! Report to the developer with the following error" +
                                e.__str__())
    return HttpResponseForbidden()


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('web:login')

    user = request.user
    test = TestDrive.objects.filter(user=user)
    orders = Order.objects.filter(user=user)

    context = {
        'tests': test,
        'orders': orders
    }

    return render(request, 'web/dashboard.html', context)


def compare(request):

    form = CompareForm(request.POST or None)
    if request.method == 'POST':
        car1 = int(request.POST['car1'])
        car2 = int(request.POST['car2'])

        car1 = Car.objects.get(pk=car1)
        car2 = Car.objects.get(pk=car2)

        data = {
            'car1_id': car1.id,
            'car1_name': car1.brand + " " + car1.name,
            'car1_pic': car1.picture.url,
            'car1_price': car1.price,
            'car1_seats': car1.seats,
            'car1_tank_capacity': car1.tank_capacity,
            'car1_transmission': car1.transmission,
            'car1_gears': car1.gears,
            'car1_engine_displacement': car1.engine_displacement,
            'car1_power': car1.power,
            'car1_dimensions': car1.dimensions,
            'car2_id': car2.id,
            'car2_name': car2.brand + " " + car2.name,
            'car2_pic': car2.picture.url,
            'car2_price': car2.price,
            'car2_seats': car2.seats,
            'car2_tank_capacity': car2.tank_capacity,
            'car2_transmission': car2.transmission,
            'car2_gears': car2.gears,
            'car2_engine_displacement': car2.engine_displacement,
            'car2_power': car2.power,
            'car2_dimensions': car2.dimensions,
        }

        html = '''
        <table class="table table-bordered" id="cmpTable">
            <tbody>
            <tr>
                <td>
                </td>
                <td>
                    <a href="car/{car1_id}">{car1_name}</a>
                </td>
                <td>
                    <a href="car/{car2_id}">{car2_name}</a>
                </td>
            </tr>
            <tr>
                <td>
                </td>
                <td>
                    <img class="img-fluid" src="{car1_pic}" alt="">
                </td>
                <td>
                    <img class="img-fluid" src="{car2_pic}" alt="">
                </td>
            </tr>
            <tr>
                <td>
                    Price (in &#8377;)
                </td>
                <td>
                    {car1_price}
                </td>
                <td>
                    {car2_price}
                </td>
            </tr>
            <tr>
                <td>
                    Seating capacity
                </td>
                <td>
                    {car1_seats}
                </td>
                <td>
                    {car2_seats}
                </td>
            </tr>
            <tr>
                <td>
                    Fuel Tank Capacity (litres)
                </td>
                <td>
                    {car1_tank_capacity}
                </td>
                <td>
                    {car2_tank_capacity}
                </td>
            </tr>
            <tr>
                <td>
                    Transmission type
                </td>
                <td>
                    {car1_transmission}
                </td>
                <td>
                    {car2_transmission}
                </td>
            </tr>
            <tr>
                <td>
                    Gears
                </td>
                <td>
                    {car1_gears}
                </td>
                <td>
                    {car2_gears}
                </td>
            </tr>
            <tr>
                <td>
                    Engine displacement (cc)
                </td>
                <td>
                    {car1_engine_displacement}
                </td>
                <td>
                    {car2_engine_displacement}
                </td>
            </tr>
            <tr>
                <td>
                    Maximum power (PS)
                </td>
                <td>
                    {car1_power}
                </td>
                <td>
                    {car2_power}
                </td>
            </tr>
            <tr>
                <td>
                    Dimensions (mm)
                </td>
                <td>
                    {car1_dimensions}
                </td>
                <td>
                    {car2_dimensions}
                </td>
            </tr>
            </tbody>
        </table>
        '''.format(**data)

        return HttpResponse(html)

    context = {
        'form': form
    }

    return render(request, 'web/compare.html', context)
