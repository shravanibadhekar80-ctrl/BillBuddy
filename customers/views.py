
from django.shortcuts import render, redirect
from .models import Customer


def customer_list(request):
    customers = Customer.objects.all()
    query = request.GET.get('q', '').strip()

    if query:
        customers = customers.filter(name__icontains=query)

    return render(
        request,
        'customers/customer_list.html',
        {'customers': customers, 'query': query}
    )


def add_customer(request):
    if request.method == 'POST':
        Customer.objects.create(
            name=request.POST.get('name', '').strip(),
            business_name=request.POST.get('business_name', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            email=request.POST.get('email', '').strip(),
            address=request.POST.get('address', '').strip(),
        )
        return redirect('customer_list')

    return render(request, 'customers/add_customer.html')
