from django.http import Http404
from django.views.generic import TemplateView

from src.content.selectors import (
    PAGE_SLUGS,
    active_salons,
    home_context,
    published_blog_post,
    published_blog_posts,
    published_brides,
    published_faq,
    published_page,
    published_reviews,
    resolve_title,
    site_settings,
)
from src.content.stubs import PARTNERSHIP_STUB, page_stub


class HomeView(TemplateView):
    template_name = 'content/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(home_context())
        return context


class PageView(TemplateView):
    template_name = 'content/page.html'

    def get_context_data(self, **kwargs):
        slug = kwargs.get('slug') or self.kwargs['slug']
        if slug not in PAGE_SLUGS:
            raise Http404
        page = published_page(slug)
        is_stub = page is None
        if is_stub:
            page = page_stub(slug)
            if page is None:
                raise Http404
        context = super().get_context_data(**kwargs)
        context['page'] = page
        context['is_stub'] = is_stub
        context['page_title'] = resolve_title(page, page.title)
        return context


class FaqView(TemplateView):
    template_name = 'content/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = list(published_faq())
        context['items'] = items
        context['is_stub'] = not items
        context['page_title'] = 'FAQ'
        return context


class BlogListView(TemplateView):
    template_name = 'content/blog_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = list(published_blog_posts())
        context['posts'] = posts
        context['is_stub'] = not posts
        context['page_title'] = 'Блог'
        return context


class BlogDetailView(TemplateView):
    template_name = 'content/blog_detail.html'

    def get_context_data(self, **kwargs):
        post = published_blog_post(self.kwargs['slug'])
        if post is None:
            raise Http404
        context = super().get_context_data(**kwargs)
        context['post'] = post
        context['page_title'] = resolve_title(post, post.title)
        return context


class ReviewListView(TemplateView):
    template_name = 'content/reviews.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reviews = list(published_reviews())
        context['reviews'] = reviews
        context['is_stub'] = not reviews
        context['page_title'] = 'Відгуки'
        return context


class SalonListView(TemplateView):
    template_name = 'content/salons.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        salons = list(active_salons())
        context['salons'] = salons
        context['is_stub'] = not salons
        context['page_title'] = 'Салони'
        return context


class BrideGalleryView(TemplateView):
    template_name = 'content/brides.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = list(published_brides())
        context['items'] = items
        context['is_stub'] = not items
        context['page_title'] = 'Наречені'
        return context


class ContactsView(TemplateView):
    template_name = 'content/contacts.html'

    def get_context_data(self, **kwargs):
        page = published_page('contacts')
        settings_obj = site_settings()
        contacts = settings_obj.contacts_json or {}
        context = super().get_context_data(**kwargs)
        context['page'] = page
        context['contacts'] = contacts
        context['is_stub'] = page is None and not contacts
        context['page_title'] = resolve_title(page, 'Контакти') if page else 'Контакти'
        return context


class PartnershipView(TemplateView):
    template_name = 'content/partnership.html'

    def get_context_data(self, **kwargs):
        page = published_page('partnership')
        is_stub = page is None
        if is_stub:
            page = PARTNERSHIP_STUB
        context = super().get_context_data(**kwargs)
        context['page'] = page
        context['is_stub'] = is_stub
        context['page_title'] = resolve_title(page, page.title)
        return context
