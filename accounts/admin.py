from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Address, User


class AddressInline(admin.TabularInline):
    """A customer's saved addresses, viewable and fixable on their user page."""

    model = Address
    extra = 0


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        *DjangoUserAdmin.fieldsets,
        (
            "ThoughtTronix",
            {
                "fields": (
                    "job_title",
                    "default_shipping_address",
                    "default_billing_address",
                )
            },
        ),
    )
    # Raw ids: a dropdown would list every customer's addresses.
    raw_id_fields = ("default_shipping_address", "default_billing_address")
    list_display = ("username", "email", "job_title", "is_staff")
    inlines = [AddressInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "zip")
    search_fields = ("name", "street", "city", "user__username")
