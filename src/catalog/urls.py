from django.urls import path

from src.catalog.views import CatalogListView, ProductDetailView
from src.catalog.wishlist_views import WishlistMergeView, WishlistToggleView, WishlistView

app_name = 'catalog'

urlpatterns = [
    path('katalog/<slug:slug>/', CatalogListView.as_view(), name='list'),
    path('suknya/<slug:slug>/', ProductDetailView.as_view(), name='detail'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/toggle/', WishlistToggleView.as_view(), name='wishlist_toggle'),
    path('wishlist/merge/', WishlistMergeView.as_view(), name='wishlist_merge'),
]
