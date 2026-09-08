from tinymce.widgets import TinyMCE


class TinyMCEAdminMixin:
    tinymce_fields: tuple[str, ...] = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.tinymce_fields:
            kwargs['widget'] = TinyMCE()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
