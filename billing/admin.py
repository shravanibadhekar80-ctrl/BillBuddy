
from django.contrib import admin
from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "customer",
        "invoice_date",
        "due_date",
        "total_amount",
        "status",
    )
    search_fields = ("invoice_number", "customer__name")
    list_filter = ("status", "invoice_date")
