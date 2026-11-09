"""Coupon snapshot fields on Order (plans/coupons.md, Phase 2).

Three steps so existing orders get a real subtotal rather than a
placeholder: add ``subtotal`` as nullable, backfill it from ``total``
(no existing order has a discount), then make it required.
"""

from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


def backfill_subtotal(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    Order.objects.filter(subtotal__isnull=True).update(subtotal=models.F("total"))


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0003_coupon"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="discount_amount",
            field=models.DecimalField(
                decimal_places=2, default=Decimal("0.00"), max_digits=10
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="subtotal",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.RunPython(backfill_subtotal, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="order",
            name="subtotal",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AddField(
            model_name="order",
            name="coupon",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="orders",
                to="orders.coupon",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="coupon_code",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="order",
            name="coupon_percent_off",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="coupon_product_name",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
