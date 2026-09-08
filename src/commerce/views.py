from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import TemplateView

from src.commerce.selectors import order_for_account, orders_for_user


class AccountOrderListView(LoginRequiredMixin, TemplateView):
    template_name = 'commerce/account_orders.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Замовлення'
        context['account_nav'] = 'orders'
        context['orders'] = list(orders_for_user(self.request.user))
        return context


class AccountOrderDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'commerce/account_order_detail.html'

    def get_context_data(self, **kwargs):
        order = order_for_account(user=self.request.user, number=self.kwargs['number'])
        if order is None:
            raise Http404
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Замовлення {order.number}'
        context['account_nav'] = 'orders'
        context['order'] = order
        return context
