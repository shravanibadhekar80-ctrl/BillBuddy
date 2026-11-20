
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError, transaction
from customers.models import Customer
from .models import Invoice


def invoice_list(request):
    invoices = Invoice.objects.select_related("customer").all()
    return render(
        request,
        "billing/invoice_list.html",
        {"invoices": invoices},
    )


def create_invoice(request):
    customers = Customer.objects.all()

    if request.method == "POST":
        invoice_number = request.POST.get("invoice_number", "").strip()
        customer_id = request.POST.get("customer", "")
        invoice_date = request.POST.get("invoice_date", "")
        due_date = request.POST.get("due_date", "")
        item_name = request.POST.get("item_name", "").strip()

        try:
            quantity = int(request.POST.get("quantity", "1"))
            unit_price = Decimal(request.POST.get("unit_price", "0"))

            if quantity < 1 or unit_price < 0:
                raise ValueError

            customer = Customer.objects.get(pk=customer_id)

            if not invoice_number or not item_name:
                raise ValueError

            if not invoice_date or not due_date or due_date < invoice_date:
                raise ValueError

            total_amount = (Decimal(quantity) * unit_price).quantize(
                Decimal("0.01")
            )

            with transaction.atomic():
                Invoice.objects.create(
                    invoice_number=invoice_number,
                    customer=customer,
                    invoice_date=invoice_date,
                    due_date=due_date,
                    item_name=item_name,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_amount=total_amount,
                )

            messages.success(request, "Invoice created successfully!")
            return redirect("invoice_list")

        except (
            ValueError,
            InvalidOperation,
            Customer.DoesNotExist,
        ):
            messages.error(
                request,
                "Please check the details. Quantity must be positive, "
                "price cannot be negative, and due date must not precede "
                "the invoice date.",
            )
        except IntegrityError:
            messages.error(
                request,
                "That invoice number already exists. Please use another.",
            )

    return render(
        request,
        "billing/create_invoice.html",
        {
            "customers": customers,
            "today": timezone.localdate().isoformat(),
        },
    )
