##  (C) Copyright 2014 Alvaro J. Genial (http://alva.ro)

from django.template.loaders import app_directories, filesystem
from django_synth.template import SynthTemplate

class AppDirectoriesLoader(app_directories.Loader):
    is_usable = True

    def load_template(self, template_name, template_dirs=None):
        source, origin = self.load_template_source(template_name, template_dirs)
        template = SynthTemplate(source, template_dirs)
        return template, origin

class FilesystemLoader(filesystem.Loader):
    is_usable = True

    def load_template(self, template_name, template_dirs=None):
        source, origin = self.load_template_source(template_name, template_dirs)
        template = SynthTemplate(source, template_dirs)
        return template, origin
