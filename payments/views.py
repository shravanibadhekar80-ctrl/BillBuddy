
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from billing.models import Invoice
from .models import Payment


def payment_list(request):
    payments = Payment.objects.select_related(
        "invoice", "invoice__customer"
    ).all()

    total_received = (
        payments.aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    payment_summaries = []

    for payment in payments:
        total_paid = (
            Payment.objects.filter(invoice=payment.invoice)
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        balance = payment.invoice.total_amount - total_paid

        payment_summaries.append({
            "payment": payment,
            "balance": max(balance, Decimal("0.00")),
        })

    context = {
        "payments": payments,
        "payment_summaries": payment_summaries,
        "total_received": total_received,
    }

    return render(request, "payments/payment_list.html", context)


def record_payment(request):
    invoices = Invoice.objects.select_related("customer").all()

    if request.method == "POST":
        invoice_id = request.POST.get("invoice", "")
        amount_text = request.POST.get("amount", "").strip()
        payment_date = request.POST.get("payment_date", "")
        payment_method = request.POST.get("payment_method", "Cash")
        notes = request.POST.get("notes", "").strip()

        try:
            amount = Decimal(amount_text)

            if not amount.is_finite() or amount <= 0:
                raise ValueError

            if amount.as_tuple().exponent < -2:
                raise ValueError

            if not payment_date:
                raise ValueError

            parsed_date = timezone.datetime.strptime(
                payment_date, "%Y-%m-%d"
            ).date()

            if parsed_date > timezone.localdate():
                raise ValueError

            if payment_method not in dict(Payment.PAYMENT_METHODS):
                raise ValueError

            with transaction.atomic():
                invoice = get_object_or_404(
                    Invoice.objects.select_for_update(),
                    pk=invoice_id,
                )

                already_paid = (
                    Payment.objects.filter(invoice=invoice)
                    .aggregate(total=Sum("amount"))["total"]
                    or Decimal("0.00")
                )

                balance = invoice.total_amount - already_paid

                if balance <= 0:
                    messages.error(
                        request,
                        "This invoice is already fully paid."
                    )

                elif amount > balance:
                    messages.error(
                        request,
                        f"Amount exceeds the remaining balance of ₹{balance:.2f}."
                    )

                else:
                    Payment.objects.create(
                        invoice=invoice,
                        amount=amount,
                        payment_date=parsed_date,
                        payment_method=payment_method,
                        notes=notes,
                    )

                    new_paid = already_paid + amount

                    if new_paid >= invoice.total_amount:
                        invoice.status = "Paid"
                    else:
                        invoice.status = "Pending"

                    invoice.save(update_fields=["status"])

                    messages.success(
                        request,
                        "Payment recorded successfully!"
                    )
                    return redirect("payment_list")

        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ):
            messages.error(
                request,
                "Enter a valid payment amount and date. "
                "The amount must have at most two decimal places."
            )

    context = {
        "invoices": invoices,
        "today": timezone.localdate().isoformat(),
    }

    return render(
        request,
        "payments/record_payment.html",
        context,
    )
