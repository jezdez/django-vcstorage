import os
import urlparse
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import smart_str

DEFAULT_BACKEND = getattr(settings, 'VCSTORAGE_DEFAULT_BACKEND', None)
SUPPORTED_BACKENDS = ('mercurial', 'bazaar', 'git')

class VcStorage(FileSystemStorage):
    """
    A Django Storage class that can use anyvc's backends, e.g. 'hg'
    """
    backend = None
    repo = None
    wd = None

    def __init__(self, location=None, base_url=None):
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        if self.backend is None:
            if DEFAULT_BACKEND is None:
                raise ImproperlyConfigured(
                    "You must define VCSTORAGE_DEFAULT_BACKEND setting or "
                    "pass a backend parameter to the storage instance.")
            self.backend = DEFAULT_BACKEND.lower()
        self.location = os.path.join(os.path.realpath(location), self.backend)
        self.base_url = urlparse.urljoin(base_url, self.backend.lower())
        if not self.base_url.endswith("/"):
            self.base_url = self.base_url+"/"

    def load_working_dir(self, retry=False):
        """
        Gets a working dir manager from anyvc
        """
        if self.wd:
            return
        from anyvc.workdir import get_workdir_manager_for_path
        wd = get_workdir_manager_for_path(self.location)
        if wd is None:
            self.create_repository()
            wd = get_workdir_manager_for_path(self.location)
            if wd is None:
                raise ImproperlyConfigured(
                    "You must define VCSTORAGE_DEFAULT_BACKEND setting or "
                    "pass a backend parameter to the storage instance.")
        self.wd = wd

    def load_repository(self):
        """
        Loads the repository class from anyvc
        """
        from anyvc import repository, metadata
        lookup = {}
        for k, v in repository.lookup.items():
            if k.lower() in SUPPORTED_BACKENDS:
                lookup[k.lower()] = v
        if self.backend in metadata.aliases:
            self.backend = metadata.aliases[self.backend]
        return lookup.get(self.backend, None)

    def create_repository(self):
        """
        Loads/creates the repository only if required.
        """
        if self.repo:
            return
        repo_cls = self.load_repository()
        if repo_cls is None:
            raise ImproperlyConfigured(
                "Backend '%s' could not be loaded. Either it couldn't be "
                "found or it's not supported." % self.backend)
        self.repo = repo_cls(path=self.location, create=True)

    def save(self, name, content, message=None):
        """ 
        Saves the given content with the name and commits to the working dir.
        """
        self.load_working_dir()
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
        self.load_working_dir()
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
    backend = 'git'

class MercurialStorage(VcStorage):
    """
    A storage class that will use the Mercurial backend of anyvc
    """
    backend = 'hg'

class BazaarStorage(VcStorage):
    """
    A storage class that will use the Bazaar backend of anyvc
    """
    backend = 'bzr'
