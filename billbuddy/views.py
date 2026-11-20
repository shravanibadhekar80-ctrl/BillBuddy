
from django.shortcuts import render
from django.db.models import Sum
from customers.models import Customer
from billing.models import Invoice


def dashboard(request):
    total_customers = Customer.objects.count()
    total_invoices = Invoice.objects.count()

    total_revenue = (
        Invoice.objects.filter(status="Paid")
        .aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    pending_amount = (
        Invoice.objects.filter(
            status__in=["Pending", "Overdue"]
        )
        .aggregate(total=Sum("total_amount"))["total"]
        or 0
    )

    overdue_invoices = Invoice.objects.filter(
        status="Overdue"
    ).count()

    recent_invoices = (
        Invoice.objects.select_related("customer")
        .order_by("-created_at")[:5]
    )

    context = {
        "total_customers": total_customers,
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "pending_amount": pending_amount,
        "overdue_invoices": overdue_invoices,
        "recent_invoices": recent_invoices,
    }

    return render(request, "dashboard.html", context)
