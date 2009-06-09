import os
import sys
import urlparse
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import smart_str

class VcStorage(FileSystemStorage):
    """
    A Django Storage class that can use anyvc's backends, e.g. 'hg'
    """
    label = None
    workdir = None
    repository = None
    wd = None
    repo = None

    def __init__(self, location=None, base_url=None):
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        if None in (self.workdir, self.repository, self.label):
            raise ImproperlyConfigured(
                "You can't call the VcStorage directly. Use one of the "
                "implementations, e.g. 'vcstorage.storage.MercurialStorage'.")
        self.label = self.label.lower()
        self.location = os.path.join(os.path.realpath(location), self.label)
        self.base_url = urlparse.urljoin(base_url, self.label)
        if not self.base_url.endswith("/"):
            self.base_url = self.base_url+"/"

    def load(self, backend, *args, **kwargs):
        i = backend.rfind('.')
        module, attr = backend[:i], backend[i+1:]
        try:
            __import__(module)
            mod = sys.modules[module]
        except ImportError, e:
            raise ImproperlyConfigured(
                "Error importing upload handler module %s: '%s'" % (module, e))
        try:
            cls = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured(
                "Module '%s' does not define a '%s' backend" % (module, attr))
        return cls(*args, **kwargs)

    def save(self, name, content, message=None):
        """ 
        Saves the given content with the name and commits to the working dir.
        """
        self.populate()
        if message is None:
            message = "Automated commit: adding %s" % name
        name = super(VcStorage, self).save(name, content)
        full_paths = [smart_str(os.path.join(self.location, self.path(name)))]
        try:
            self.wd.add(paths=full_paths)
            self.wd.commit(message=message, paths=full_paths)
        except OSError:
            pass
        return name

    def delete(self, name, message=None):
        """
        Deletes the specified file from the storage system.
        """
        self.populate()
        if message is None:
            message = "Automated commit: removing %s" % name
        full_paths = [smart_str(self.path(name))]
        try:
            self.wd.remove(paths=full_paths)
            self.wd.commit(message=message, paths=full_paths)
        except OSError:
            pass

class GitStorage(VcStorage):
    """
    A storage class that will use the Git backend of anyvc
    """
    label = 'git'
    workdir = 'anyvc.workdir.git.Git'
    repository = 'anyvc.repository.git.GitRepository'

    def populate(self):
        if None not in (self.wd, self.repo):
            return
        try:
            repo = self.load(self.repository, path=self.location, create=True)
        except:
            repo = self.load(self.repository, path=self.location)
        self.wd = self.load(self.workdir, versioned_path=self.location)

class MercurialStorage(VcStorage):
    """
    A storage class that will use the Mercurial backend of anyvc
    """
    label = 'hg'
    workdir = 'anyvc.workdir.hg.Mercurial'
    repository = 'anyvc.repository.hg.MercurialRepository'

    def populate(self):
        if None not in (self.wd, self.repo):
            return
        try:
            repo = self.load(self.repository, path=self.location, create=True)
        except:
            repo = self.load(self.repository, path=self.location)
        self.wd = self.load(self.workdir, path=self.location)

class BazaarStorage(VcStorage):
    """
    A storage class that will use the Bazaar backend of anyvc
    """
    label = 'bzr'
    workdir = 'anyvc.workdir.bzr.Bazaar'
    repository = 'anyvc.repository.bzr.BazaarRepository'

    def populate(self):
        if None not in (self.wd, self.repo):
            return
        try:
            repo = self.load(self.repository, path=self.location, create=True)
        except:
            repo = self.load(self.repository, path=self.location)
        self.wd = self.load(self.workdir, path=self.location)

