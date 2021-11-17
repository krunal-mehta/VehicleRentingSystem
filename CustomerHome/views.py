from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from CustomerHome.models import *
from Owner.models import Owner
from Manager.models import Manager
from Vehicles.models import Vehicle
from RentVehicle.models import RentVehicle

from datetime import datetime
from datetime import date

isLogin = False
isLogout = False

# Create your views here.
def index(request):
    global isLogin
    global isLogout

    if('customeruser_email' in request.session):
        isLogin = True
        return redirect('/CustomerHome/')
        
    # vehicle = Vehicle.objects.all()
    if('customeruser_email' not in request.session and isLogout):
        isLogin = False
        isLogout = False
        Message = "Successfully Logged Out!!"
        # return render(request,'index.html',{'Message':Message,'vehicle':vehicle})
        return render(request,'index1.html',{'Message':Message})
    # return render(request,'index.html',{'vehicle':vehicle})
    return render(request,'index1.html')

def customersignin(request):
    return render(request,'CustomerSignIn.html')

def aboutus(request):
    return render(request,'aboutus.html')

def customerregister(request):
    return render(request,'CustomerRegister.html')

def CustomerLoginAuthentication(request):
    global isLogin
    login_email=request.POST.get('login_email','')
    login_password=request.POST.get('login_password','')
    # customer = Customer.objects.all()

    result_customer = Customers.objects.filter(customer_email=login_email,customer_password=login_password)

    if result_customer.exists():
        request.session['customeruser_email'] = login_email
        isLogin = True
        return redirect('/CustomerHome/')
    else:
        Message = "Invalid Email or password!!"
        return render(request,'CustomerSignIn.html',{'Message':Message})

def CustomerRegisterCustomer(request):
    global isLogin

    customer_name=request.POST.get('name','')
    customer_email=request.POST.get('email','')
    customer_password=request.POST.get('password','')

    result_customer = Customers.objects.filter(customer_email=customer_email)

    if result_customer.exists():
        Message = "This Email address already exist!!"
        return render(request,'CustomerRegister.html',{'Message':Message})
    else:
        customer=Customers(customer_name=customer_name,customer_email=customer_email,
        customer_password=customer_password)
        
        customer.save()
        Message = "Successfully Registered, Please Log-in!!"
        return render(request,'CustomerSignIn.html',{'Message_success':Message})
        

def Logout(request):
    global isLogout
    del request.session['customeruser_email']
    isLogout = True
    Message = "Successfully Logged Out!!"
    return redirect('/')

def CustomerHome(request):
    if('customeruser_email' not in request.session):
        return redirect('/customersignin/')
    customer_email = request.session.get('customeruser_email')
    customer = Customers.objects.get(customer_email=customer_email)
    #vehicle = Vehicle.objects.all()
    #Message="Welcome Aboard!!"
    return render(request,'CustomerHome1.html',{'customer':customer})

def Home(request):
    if('customeruser_email' not in request.session):
        return redirect('/customersignin/')
    customer_email = request.session.get('customeruser_email')
    customer = Customers.objects.get(customer_email=customer_email)
    vehicle = Vehicle.objects.all()
    return render(request,'CustomerHome.html',{'vehicle':vehicle,'customer':customer})

def Profile(request):
    if('user_email' not in request.session):
        return redirect('/signin/')
    customer_email = request.session.get('user_email')
    customer = Customer.objects.get(customer_email=customer_email)
    return render(request,'Profile.html',{'customer':customer})

def showdetails(request,Vehicle_license_plate):
    vehicle = Vehicle.objects.get(Vehicle_license_plate=Vehicle_license_plate)
    if('user_email' not in request.session):
        return render(request,'showdetails_not_login.html',{'vehicle':vehicle})
    else:
        customer_email = request.session.get('user_email')
        customer = Customer.objects.get(customer_email=customer_email)
        return render(request,'showdetails_loggedin.html',{'vehicle':vehicle,'customer':customer})

def CheckAvailability(request,Vehicle_license_plate):
    if('user_email' not in request.session):
        return redirect('/signin/')

    RentVehicle_Date_of_Booking=request.POST.get('RentVehicle_Date_of_Booking','')
    RentVehicle_Date_of_Return=request.POST.get('RentVehicle_Date_of_Return','')
    
    RentVehicle_Date_of_Booking = datetime.strptime(RentVehicle_Date_of_Booking, '%Y-%m-%d').date()
    RentVehicle_Date_of_Return = datetime.strptime(RentVehicle_Date_of_Return, '%Y-%m-%d').date()

    rentvehicle = RentVehicle.objects.filter(Vehicle_license_plate=Vehicle_license_plate)
    vehicle = Vehicle.objects.get(Vehicle_license_plate=Vehicle_license_plate)

    customer_email = request.session.get('user_email')
    customer = Customer.objects.get(customer_email=customer_email)

    if RentVehicle_Date_of_Booking < date.today():
        Incorrect_dates = "Please give proper dates"
        return render(request,'showdetails_loggedin.html',{'Incorrect_dates':Incorrect_dates,'vehicle':vehicle,'customer':customer})

    if RentVehicle_Date_of_Return < RentVehicle_Date_of_Booking:
        Incorrect_dates = "Please give proper dates"
        return render(request,'showdetails_loggedin.html',{'Incorrect_dates':Incorrect_dates,'vehicle':vehicle,'customer':customer})
    
    days=(RentVehicle_Date_of_Return-RentVehicle_Date_of_Booking).days+1
    total=days*vehicle.Vehicle_price
    
    rent_data = {"RentVehicle_Date_of_Booking":RentVehicle_Date_of_Booking, "RentVehicle_Date_of_Return":RentVehicle_Date_of_Return,"days":days, "total":total}
    
    for rv in rentvehicle:

        if (rv.RentVehicle_Date_of_Booking >= RentVehicle_Date_of_Booking and RentVehicle_Date_of_Return >= rv.RentVehicle_Date_of_Booking) or (RentVehicle_Date_of_Booking >= rv.RentVehicle_Date_of_Booking and RentVehicle_Date_of_Return <= rv.RentVehicle_Date_of_Return) or (RentVehicle_Date_of_Booking <= rv.RentVehicle_Date_of_Return and RentVehicle_Date_of_Return >= rv.RentVehicle_Date_of_Return):
            if rv.isAvailable:
                Available = True
                Message = "Note that somebody has also requested for this vehicle from " + str(rv.RentVehicle_Date_of_Booking) + " to " + str(rv.RentVehicle_Date_of_Return)
                return render(request,'showdetails_loggedin.html',{'Message':Message,'Available':Available,'vehicle':vehicle,'customer':customer,'rent_data':rent_data})

            NotAvailable = True
            return render(request,'showdetails_loggedin.html',{'NotAvailable':NotAvailable,'dates':rv,'vehicle':vehicle,'customer':customer})

        # if (RentVehicle_Date_of_Booking < rv.RentVehicle_Date_of_Booking and RentVehicle_Date_of_Return < rv.RentVehicle_Date_of_Booking) or (RentVehicle_Date_of_Booking > rv.RentVehicle_Date_of_Return and RentVehicle_Date_of_Return > rv.RentVehicle_Date_of_Return):
        #     Available = True
        #     return render(request,'showdetails_loggedin.html',{'Available':Available,'vehicle':vehicle,'customer':customer,'rent_data':rent_data})


    Available = True
    return render(request,'showdetails_loggedin.html',{'Available':Available,'vehicle':vehicle,'customer':customer,'rent_data':rent_data})

def SentRequests(request):
    if('user_email' not in request.session):
        return redirect('/signin/')

    customer_email = request.session.get('user_email')
    customer = Customer.objects.get(customer_email=customer_email)

    rentvehicle = RentVehicle.objects.filter(customer_email=customer_email)
    if rentvehicle.exists():
        vehicle = Vehicle.objects.all()
        return render(request,'SentRequests.html',{'customer':customer,'rentvehicle':rentvehicle,'vehicle':vehicle})
    else:
        Message = "You haven't rented any vehicle yet!!"
        return render(request,'SentRequests.html',{'customer':customer,'rentvehicle':rentvehicle,'Message':Message})

def about_us(request):
    return HttpResponse('About Us')
    
def contact_us(request):
    return HttpResponse('Contact Us')

def search(request):
    return HttpResponse('search')