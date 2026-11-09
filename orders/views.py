"""Cart and checkout views — thin per the architecture convention.

The three HTMX interactions of the core live here: add-to-cart, quantity
change, and line removal. Each renders a partial (never ``base.html``);
the responses carry the navbar badge as an out-of-band swap via the
``oob_badge`` context flag. Checkout is conventional full-page work:
validate the form, hand everything to ``place_order``. Two checkout-side
HTMX interactions: ``AddressFieldsView`` refills an address section
from a saved address, and ``ApplyCouponView`` previews a coupon in the
order summary.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from accounts.mixins import StaffRequiredMixin
from accounts.models import ADDRESS_KINDS, Address
from products.models import Product

from .forms import CheckoutForm, CouponForm, ManageCouponForm, OrderStatusForm
from .models import Cart, CartItem, Coupon, CouponError, Order
from .services import place_order


class CartView(LoginRequiredMixin, TemplateView):
    """The customer's cart page."""

    template_name = "orders/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart.for_user(self.request.user)
        return context


class AddToCartView(LoginRequiredMixin, View):
    """HTMX: add a product; the button swaps and the badge updates OOB.

    Looks the product up through ``available()``, so adding an
    unavailable product 404s — the same not-for-sale semantics as the
    public catalog.
    """

    def post(self, request, pk):
        product = get_object_or_404(Product.objects.available(), pk=pk)
        item = Cart.for_user(request.user).add(product)
        return render(
            request,
            "orders/partials/_add_button.html",
            {"product": product, "in_cart": item.quantity, "oob_badge": True},
        )


class CartItemActionView(LoginRequiredMixin, View):
    """Base for HTMX line mutations: act, then re-render the cart contents.

    Items are always fetched through the owner's cart — never by bare pk.
    """

    def post(self, request, pk):
        item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        self.act(item)
        return render(
            request,
            "orders/partials/_cart_contents.html",
            {"cart": item.cart, "oob_badge": True},
        )

    def act(self, item):
        raise NotImplementedError


class IncrementCartItemView(CartItemActionView):
    def act(self, item):
        item.increment()


class DecrementCartItemView(CartItemActionView):
    def act(self, item):
        item.decrement()


class RemoveCartItemView(CartItemActionView):
    def act(self, item):
        item.delete()


class CheckoutView(LoginRequiredMixin, FormView):
    """The single checkout page: validate the form, hand off to the service.

    A cart that can't check out (empty, or holding a product that has
    since become unavailable) is sent back to the cart page to be fixed —
    ``place_order`` enforces the same rules transactionally as the
    backstop.

    Two forms share the one POST: ``CheckoutForm`` (addresses, card) and
    ``CouponForm`` (the coupon box). Both are validated every time, so all
    errors show at once; the order is placed only when both are valid.
    """

    template_name = "orders/checkout.html"
    form_class = CheckoutForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        cart = Cart.for_user(request.user)
        if not cart.items.exists():
            messages.info(request, "Your cart is empty — add something first.")
            return redirect("orders:cart")
        unavailable = [
            line.product.name for line in cart.lines() if not line.product.is_available
        ]
        if unavailable:
            messages.warning(
                request,
                f"No longer available: {', '.join(unavailable)}. "
                "Remove them from the cart to check out.",
            )
            return redirect("orders:cart")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        """Open with the customer's default addresses already filled in."""
        initial = super().get_initial()
        for kind in ADDRESS_KINDS:
            address = self.request.user.default_address(kind)
            if address is not None:
                initial.update(address.as_checkout_initial(kind))
        return initial

    def get_coupon_form(self):
        data = self.request.POST if self.request.method == "POST" else None
        return CouponForm(data, cart=Cart.for_user(self.request.user))

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        coupon_form = self.get_coupon_form()
        # A list, not ``and``: validate both so every error shows at once.
        if all([form.is_valid(), coupon_form.is_valid()]):
            return self.form_valid(form, coupon_form)
        return self.form_invalid(form, coupon_form)

    def form_invalid(self, form, coupon_form):
        return self.render_to_response(
            self.get_context_data(form=form, coupon_form=coupon_form)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cart = Cart.for_user(user)
        coupon_form = kwargs.get("coupon_form")
        if coupon_form is None:
            coupon_form = self.get_coupon_form()
        context["cart"] = cart
        context["coupon_form"] = coupon_form
        context["saved_addresses"] = list(user.addresses.all())
        context["summary"] = cart.checkout_summary(
            coupon_form["coupon_code"].value() or ""
        )
        return context

    def form_valid(self, form, coupon_form):
        cart = Cart.for_user(self.request.user)
        try:
            order = place_order(
                cart,
                self.request.user,
                form.cleaned_data,
                coupon_code=coupon_form.cleaned_data["coupon_code"],
            )
        except CouponError as error:
            # The backstop: the coupon changed between validation and now.
            coupon_form.add_error("coupon_code", str(error))
            return self.form_invalid(form, coupon_form)
        except ValueError as error:
            form.add_error(None, str(error))
            return self.form_invalid(form, coupon_form)
        # After the order, deliberately outside its transaction: the order
        # matters more than the address book.
        for kind in ADDRESS_KINDS:
            if form.cleaned_data[f"save_{kind}"]:
                Address.objects.save_from_checkout(
                    self.request.user, form.cleaned_data, prefix=kind
                )
        messages.success(self.request, f"Order {order.number} placed. Thank you!")
        return redirect(reverse("orders:confirmation", kwargs={"pk": order.pk}))


class AddressFieldsView(LoginRequiredMixin, View):
    """HTMX: one checkout address section, refilled from a saved address.

    ``?address=<pk>`` picks the address — looked up through the customer's
    own book, so another customer's pk is a 404. A blank value renders the
    section empty, for typing a new address. The section's "save"
    checkbox always comes back unchecked: a saved address needn't be
    saved again.
    """

    def get(self, request, prefix):
        if prefix not in ADDRESS_KINDS:
            raise Http404
        pk = request.GET.get("address", "")
        initial = {}
        if pk:
            if not pk.isdigit():
                raise Http404
            address = get_object_or_404(request.user.addresses, pk=pk)
            initial = address.as_checkout_initial(prefix)
        form = CheckoutForm(initial=initial)
        return render(
            request,
            "orders/partials/_address_fields.html",
            {"section": form.address_section(prefix)},
        )


class ApplyCouponView(LoginRequiredMixin, View):
    """HTMX: preview a coupon — re-render the checkout order summary.

    Stores nothing: the code rides along in the checkout form, and the
    checkout POST validates it again. The response also swaps the
    "Place order" button's total out-of-band.
    """

    def post(self, request):
        summary = Cart.for_user(request.user).checkout_summary(
            request.POST.get("coupon_code", "")
        )
        return render(
            request,
            "orders/partials/_order_summary.html",
            {"summary": summary, "oob_total": True},
        )


class OwnOrdersMixin(LoginRequiredMixin):
    """Orders are always fetched through the owner — never by bare pk."""

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderConfirmationView(OwnOrdersMixin, DetailView):
    template_name = "orders/confirmation.html"
    context_object_name = "order"


class OrderHistoryView(OwnOrdersMixin, ListView):
    """The customer's orders, most recent first per the model ordering."""

    template_name = "orders/order_history.html"
    context_object_name = "orders"


class OrderDetailView(OwnOrdersMixin, DetailView):
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("items")


# --- The back office --------------------------------------------------------
#
# Staff-only order oversight: every customer's orders, filterable by
# status, with the status dropdown on the detail page. The ``section``
# context entry drives the active tab in the staff shell.


class ManageOrderListView(StaffRequiredMixin, ListView):
    """All orders, most recent first, filterable via ``?status=``."""

    template_name = "orders/manage_orders.html"
    context_object_name = "orders"
    paginate_by = 20
    extra_context = {"section": "orders"}

    def get_queryset(self):
        orders = Order.objects.select_related("user")
        status = self.request.GET.get("status", "")
        if status in Order.Status.values:
            orders = orders.filter(status=status)
        return orders

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Order.Status.choices
        context["active_status"] = self.request.GET.get("status", "")
        return context


class ManageOrderDetailView(StaffRequiredMixin, DetailView):
    """Any order's detail, with the status form alongside."""

    template_name = "orders/manage_order_detail.html"
    context_object_name = "order"
    queryset = Order.objects.select_related("user").prefetch_related("items")
    extra_context = {"section": "orders"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_form"] = OrderStatusForm(instance=self.object)
        return context


class UpdateOrderStatusView(StaffRequiredMixin, View):
    """POST-only: set an order's status from the back-office dropdown."""

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"{order.number} is now {order.get_status_display().lower()}.",
            )
        else:
            messages.error(request, "That isn't a status an order can have.")
        return redirect("orders:manage_order_detail", pk=order.pk)


# Staff-only coupon management: list, create, edit. Retiring is the
# "Active" toggle on the edit form — there is deliberately no delete, so
# an order's link to its coupon survives for reporting (the order's own
# snapshot never depended on it).


class ManageCouponListView(StaffRequiredMixin, ListView):
    """Every coupon, alphabetical by code, with its Active/Expired/Retired status."""

    template_name = "orders/manage_coupons.html"
    context_object_name = "coupons"
    extra_context = {"section": "coupons"}

    def get_queryset(self):
        return Coupon.objects.select_related("product")


class ManageCouponCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    model = Coupon
    form_class = ManageCouponForm
    template_name = "orders/manage_coupon_form.html"
    success_url = reverse_lazy("orders:manage_coupons")
    success_message = "Coupon %(code)s created."
    extra_context = {"section": "coupons"}


class ManageCouponUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Coupon
    form_class = ManageCouponForm
    template_name = "orders/manage_coupon_form.html"
    success_url = reverse_lazy("orders:manage_coupons")
    success_message = "Coupon %(code)s saved."
    extra_context = {"section": "coupons"}
