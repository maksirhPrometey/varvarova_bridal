from django.http import Http404
from django.views.generic import TemplateView

from src.catalog.selectors import (
    SORT_CHOICES,
    SORT_NEW,
    catalog_facets,
    category_ancestors,
    category_by_slug,
    filter_catalog,
    filter_chips,
    gallery_rows,
    grid_cols_for,
    parse_filter_query,
    product_by_slug,
)
from src.content.selectors import resolve_title
from src.content.stubs import category_stub


class CatalogListView(TemplateView):
    def get_template_names(self):
        if getattr(self.request, 'htmx', False):
            return ['catalog/partials/results.html']
        return ['catalog/list.html']

    def get_context_data(self, **kwargs):
        slug = self.kwargs['slug']
        category = category_by_slug(slug)
        is_stub = category is None
        chips = []
        ancestors = []
        if is_stub:
            category = category_stub(slug)
            if category is None:
                raise Http404
            products = []
            children = []
            facets = []
            selected = {}
            sort = SORT_NEW
        else:
            selected = parse_filter_query(self.request.GET)
            sort = self.request.GET.get('sort', SORT_NEW)
            if sort not in SORT_CHOICES:
                sort = SORT_NEW
            products = list(filter_catalog(category, selected=selected, sort=sort))
            children = list(
                category.children.filter(is_active=True).order_by('sort_order', 'name')
            )
            ancestors = category_ancestors(category)
            facets = []
            for facet in catalog_facets(category):
                code = facet['attribute'].code
                chosen = selected.get(code, set())
                facets.append(
                    {
                        'attribute': facet['attribute'],
                        'values': [
                            {
                                'obj': value,
                                'checked': value.slug in chosen,
                                'query': f'{code}={value.slug}',
                            }
                            for value in facet['values']
                        ],
                    }
                )
            chips = filter_chips(self.request, facets)
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'category': category,
                'children': children,
                'ancestors': ancestors,
                'products': products,
                'facets': facets,
                'selected': selected,
                'filter_chips': chips,
                'sort': sort,
                'grid_cols': grid_cols_for(len(products)),
                'is_stub': is_stub,
                'page_title': resolve_title(category, category.name),
            }
        )
        return context


class ProductDetailView(TemplateView):
    template_name = 'catalog/detail.html'

    def get_context_data(self, **kwargs):
        product = product_by_slug(self.kwargs['slug'])
        if product is None:
            raise Http404
        gallery = list(product.images.all())
        attributes = []
        for link in product.attribute_values.all():
            attributes.append(link.attribute_value)
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'product': product,
                'gallery': gallery,
                'gallery_rows': gallery_rows(gallery),
                'attributes': attributes,
                'page_title': resolve_title(product, product.name),
            }
        )
        return context
