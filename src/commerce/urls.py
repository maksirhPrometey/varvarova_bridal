from django.urls import path

from src.commerce.cart_views import CartAddView, CartDetailView, CartQtyView, CartRemoveView
from src.commerce.checkout_views import (
    CheckoutThanksView,
    CheckoutView,
    NpCitiesView,
    NpWarehousesView,
)
from src.commerce.views import AccountOrderDetailView, AccountOrderListView

app_name = 'commerce'

urlpatterns = [
    path('koshyk/', CartDetailView.as_view(), name='cart'),
    path('koshyk/add/', CartAddView.as_view(), name='cart_add'),
    path('koshyk/qty/', CartQtyView.as_view(), name='cart_qty'),
    path('koshyk/remove/', CartRemoveView.as_view(), name='cart_remove'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/dyakuyemo/', CheckoutThanksView.as_view(), name='checkout_thanks'),
    path('api/np/cities/', NpCitiesView.as_view(), name='np_cities'),
    path('api/np/warehouses/', NpWarehousesView.as_view(), name='np_warehouses'),
    path('kabinet/zamovlennya/', AccountOrderListView.as_view(), name='account_orders'),
    path(
        'kabinet/zamovlennya/<str:number>/',
        AccountOrderDetailView.as_view(),
        name='account_order_detail',
    ),
]
