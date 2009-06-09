import os
from django.core.files.base import ContentFile
from django.db.models import signals, TextField, FileField

from vcstorage.storage import VcStorage

DEFAULT_UPLOAD_TO = '%(app_label)s/%(model_name)s/%(field_name)s'

class VcFileField(FileField):
    """
    A file field that uses the VcStorage for version control
    """
    def __init__(self, upload_to='', storage=None, **kwargs):
        if storage is None:
            storage = VcStorage()
        elif not isinstance(storage, VcStorage):
            raise TypeError("'storage' is not an instance of %s." % VcStorage)
        if not upload_to:
            upload_to = DEFAULT_UPLOAD_TO
        super(VcFileField, self).__init__(
            upload_to=upload_to, storage=storage, **kwargs)

    def pre_save(self, model_instance, add):
        "Returns field's value just before saving."
        file = super(VcFileField, self).pre_save(model_instance, add)
        if model_instance.pk:
            old_name = getattr(model_instance.__class__._default_manager.get(
                               pk=model_instance.pk), self.name)
            if file and file.name != old_name and \
                not model_instance.__class__._default_manager.filter(
                    **{self.name: old_name}).exclude(pk=model_instance.pk):
                        self.storage.delete(old_name)
        return file

    def generate_filename(self, instance, filename):
        format_kwargs = {
            'app_label': instance._meta.app_label,
            'model_name': instance._meta.object_name.lower(),
            'instance_pk': instance.pk,
            'field_name': self.attname,
        }
        self.upload_to = self.upload_to % format_kwargs
        return super(VcFileField, self).generate_filename(instance, filename)

class VcTextField(TextField):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        Allow specifying a different format for the key used to identify
        versionized content in the model-definition.
        """
        self.storage = kwargs.pop('storage', VcStorage())
        self.key_format = kwargs.pop('key_format',
            os.path.join(DEFAULT_UPLOAD_TO, '%(instance_pk)s.txt'))
        # so we can figure out that this field is versionized
        super(VcTextField, self).__init__(self, *args, **kwargs)

    def get_internal_type(self):
        return "TextField"

    def post_save(self, instance=None, **kwargs):
        data = getattr(instance, self.attname).encode('utf-8')
        key = self.key_format % {
            'app_label': instance._meta.app_label,
            'model_name': instance._meta.object_name.lower(),
            'instance_pk': instance.pk,
            'field_name': self.attname}
        self.storage.save(key, ContentFile(data))

    def post_delete(self, instance=None, **kwargs):
        key = self.key_format % {
            'app_label': instance._meta.app_label,
            'model_name': instance._meta.object_name.lower(),
            'instance_pk': instance.pk,
            'field_name': self.attname}
        self.storage.delete(key)

    def contribute_to_class(self, cls, name):
        super(VcTextField, self).contribute_to_class(cls, name)
        signals.post_save.connect(self.post_save, sender=cls)
        signals.post_delete.connect(self.post_delete, sender=cls)
