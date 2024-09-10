from django import forms
from django.conf.urls.static import static
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.safestring import mark_safe

class CustomRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):
    """
        Based on RelatedFieldWidgetWrapper, this does the same thing
        outside of the admin interface

        the parameters for a relation and the admin site are replaced
        by a url for the add operation
    """

    def __init__(self, widget, add_url,permission=True):
        # self.is_hidden = widget.is_hidden
        self.widget = widget
        self.needs_multipart_form = widget.needs_multipart_form
        self.attrs = widget.attrs
        self.choices = widget.choices
        print('aaaaaaaaaaaaaa', self.choices)
        self.add_url = add_url
        self.permission = permission

    def render(self, name, value, *args, **kwargs):
        self.widget.choices = self.choices
        print('bbbbbbbbbbbbb', self.widget.choices)
        output = [self.widget.render(name, value, *args, **kwargs)]
        # plus_img_url = static('admin/img/icon_addlink.svg')
        plus_img_url = 'http://localhost:8000/static/admin/img/icon-addlink.svg'
        if self.permission:
            output.append(u'<a href="%s" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % (self.add_url, name))
            output.append(u'<img src="%s" width="10" height="10" alt="%s"/></a>' % (plus_img_url, 'Add Another'))
        return mark_safe(u''.join(output))

class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list':'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = u'<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += u'<option value="%s">' % item
        data_list += u'</datalist>'

        return mark_safe(text_html + data_list)