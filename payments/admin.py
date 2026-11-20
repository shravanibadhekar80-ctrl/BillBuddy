
from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "amount",
        "payment_date",
        "payment_method",
    )

    list_filter = ("payment_method", "payment_date")

    search_fields = ("invoice__invoice_number", "notes")
