
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from billing.models import Invoice


class Payment(models.Model):
    PAYMENT_METHODS = [
        ("Cash", "Cash"),
        ("UPI", "UPI"),
        ("Card", "Card"),
        ("Bank Transfer", "Bank Transfer"),
        ("Other", "Other"),
    ]

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    payment_date = models.DateField()

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default="Cash"
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-created_at"]

    def __str__(self):
        return f"{self.invoice.invoice_number} - ₹{self.amount}"

    @property
    def balance(self):
        total_paid = self.invoice.payments.aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")

        return self.invoice.total_amount - total_paid
