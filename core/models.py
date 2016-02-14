from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils import timezone


class StrippedCharField(models.CharField):
    """ CharField that strips trailing and leading spaces."""
    def clean(self, value, *args, **kwds):
        if value is not None:
            value = value.strip()
        return super(StrippedCharField, self).clean(value, *args, **kwds)


class ModelBase(models.Model):
    """ Base models class in the collector module

    This class provides a simple base class from which other Django models
    are derived.  In particular, this class will provide fields for a create
    and update timestamp and a flag to specify that the data should be
    considered as read-only.

    To allow for initial saving of a read-only model, as can occur after
    deserializing a saved model, pass the 'force=True' argument to the
    'save' method.  Likewise, to purge a read-only model, pass the
    'force=True' argument to the 'delete' method.

    Fields / Attributes:
        created (timezone):   The UTC timestamp when this model was created
        updated (timezone):   The UTC timestamp when this model last saved a change
        write_protect (bool): If true, the entire model should be treated as read-only
    """
    # TODO: Investigate how to make the created field read-only but to still allow deserialization...

    created = models.DateTimeField(auto_now_add=True, default=timezone.now)
    updated = models.DateTimeField(auto_now=True, default=timezone.now)
    write_protect = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        allow_delete = kwargs.get('force', False)
        if allow_delete:
            del kwargs['force']

        if self.write_protect and not allow_delete:
            raise PermissionDenied("Delete denied: %s has its write_protect flag set" % self.__class__.__name__)

        super(ModelBase, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # If write-protected, only allow changes if the 'force' flag is true
        force_save = kwargs.get('force', False)
        if force_save:
            del kwargs['force']

        if self.write_protect and not force_save:
            raise PermissionDenied("Save denied: %s has its write_protect flag set" % self.__class__.__name__)

        # TODO do we want to modify the 'updated' here?
        # TODO Will any items ever be read-only (after first commit)?
        super(ModelBase, self).save(*args, **kwargs)

