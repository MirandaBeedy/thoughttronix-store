from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import AddressForm, SignInForm, SignupForm
from .models import ADDRESS_KINDS


class SignupView(SuccessMessageMixin, CreateView):
    """Create a customer account, then hand off to the login page.

    New users sign in themselves — auto-login after signup is left as a
    student exercise.
    """

    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:login")
    success_message = "Account created — you can now sign in."


class SignInView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = SignInForm


class SignOutView(LogoutView):
    def post(self, request, *args, **kwargs):
        # Flash after super() has flushed the session, or the message
        # would be wiped along with it.
        response = super().post(request, *args, **kwargs)
        messages.info(request, "You have signed out.")
        return response


# --- My addresses -------------------------------------------------------------


class OwnAddressMixin(LoginRequiredMixin):
    """Scope every address lookup to the signed-in customer's own book:
    another customer's address is a 404, never a bare-pk fetch."""

    success_url = reverse_lazy("accounts:addresses")

    def get_queryset(self):
        return self.request.user.addresses.all()


class AddressListView(OwnAddressMixin, ListView):
    template_name = "accounts/address_list.html"
    context_object_name = "addresses"


class AddressCreateView(OwnAddressMixin, SuccessMessageMixin, CreateView):
    """Add an address; it fills any default slot that is still empty."""

    form_class = AddressForm
    template_name = "accounts/address_form.html"
    success_message = "Address saved."

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        self.request.user.fill_empty_defaults(self.object)
        return response


class AddressUpdateView(OwnAddressMixin, SuccessMessageMixin, UpdateView):
    form_class = AddressForm
    template_name = "accounts/address_form.html"
    success_message = "Address updated."


class AddressDeleteView(OwnAddressMixin, SuccessMessageMixin, DeleteView):
    """Delete an address; a default slot it held is emptied (SET_NULL)."""

    template_name = "accounts/address_confirm_delete.html"
    success_message = "Address deleted."


class SetDefaultAddressView(LoginRequiredMixin, View):
    """POST-only: make an address the default shipping or billing address."""

    def post(self, request, pk, kind):
        if kind not in ADDRESS_KINDS:
            raise Http404
        address = get_object_or_404(request.user.addresses, pk=pk)
        request.user.set_default_address(kind, address)
        messages.success(request, f"Default {kind} address updated.")
        return redirect("accounts:addresses")
