import logging
import yaml

log = logging.getLogger('binstar.auth')


class ProjectFilesInspector(object):
    def __init__(self, pfiles):
        self.pfiles = pfiles

    def update(self, metadata):
        metadata['files'] = [pfile.to_dict() for pfile in self.pfiles]
        return metadata


class DocumentationInspector(object):
    valid_names = [
        'README.md',
        'README.rst',
        'README.txt',
        'README'
    ]

    def __init__(self, pfiles):
        self.pfiles = pfiles
        self.doc_pfile = None

    def update(self, metadata):
        if self.has_doc():
            with open(self.doc_pfile.fullpath) as docfile:
                metadata['readme'] = docfile.read()
        return metadata

    def has_doc(self):
        def is_readme(basename, relativepath, fullpath):
            return basename == relativepath and basename in self.valid_names

        for pfile in self.pfiles:
            if pfile.validate(is_readme):
                self.doc_pfile = pfile
                break

        return self.doc_pfile is not None


class ConfigurationInspector(object):
    valid_names = [
        'project.yml',
        'project.yaml'
    ]

    def __init__(self, pfiles):
        self.pfiles = pfiles
        self.config_pfile = None

    def update(self, metadata):
        try:
            if self.has_config():
                with open(self.config_pfile.fullpath) as configfile:
                    metadata['configuration'] = yaml.load(configfile)
        except yaml.YAMLError:
            log.warn("Could not parse configuration file.")
        return metadata

    def has_config(self):
        def is_config(basename, relativepath, fullpath):
            return basename == relativepath and basename in self.valid_names

        for pfile in self.pfiles:
            if pfile.validate(is_config):
                self.config_pfile = pfile
                break

        return self.config_pfile is not None


inspectors = [
    DocumentationInspector,
    ProjectFilesInspector,
    ConfigurationInspector
]