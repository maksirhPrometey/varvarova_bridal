from django.urls import path

from src.content.views import (
    BlogDetailView,
    BlogListView,
    BrideGalleryView,
    ContactsView,
    FaqView,
    HomeView,
    PageView,
    PartnershipView,
    ReviewListView,
    SalonListView,
)

app_name = 'content'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', PageView.as_view(), {'slug': 'about'}, name='about'),
    path('delivery/', PageView.as_view(), {'slug': 'delivery'}, name='delivery'),
    path('care/', PageView.as_view(), {'slug': 'care'}, name='care'),
    path('offer/', PageView.as_view(), {'slug': 'offer'}, name='offer'),
    path('privacy/', PageView.as_view(), {'slug': 'privacy'}, name='privacy'),
    path('faq/', FaqView.as_view(), name='faq'),
    path('blog/', BlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
    path('vidhuky/', ReviewListView.as_view(), name='reviews'),
    path('salony/', SalonListView.as_view(), name='salons'),
    path('narecheni/', BrideGalleryView.as_view(), name='brides'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('partnership/', PartnershipView.as_view(), name='partnership'),
]
