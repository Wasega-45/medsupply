from django.shortcuts import render, redirect

def home(request):
    # If the user is logged in, redirect them to their specific dashboard
    if request.user.is_authenticated:
        if request.user.role == 'county_admin':
            return redirect('county_admin_approvals')
        elif request.user.role == 'logistics':
            return redirect('logistics_dashboard')
        elif request.user.role == 'facility':
            return redirect('facility_dashboard')
        elif request.user.is_superuser or request.user.role == 'national_admin':
            return redirect('/admin/')
        elif request.user.role == 'monitoring':
            return redirect('order_list')
            
    # If they are not logged in, show the public homepage
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def terms(request):
    return render(request, 'terms.html')


def privacy(request):
    return render(request, 'privacy.html')