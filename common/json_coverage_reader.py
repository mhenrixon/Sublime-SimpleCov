import os
import json
import re

class JsonCoverageReader:
    """
    For any file in a project with JSON SimpleCov coverage data,
    makes whole-project, whole-file and line-specific coverage data available.
    """

    def __init__(self, filename):
        """ Load coverage data given the filename for any file in the project. """
        self.project_root = get_project_root(filename)
        self.coverage = self.get_coverage_data() if self.project_root else None

    def get_project_coverage(self):
        coverage_data = dict(self.coverage)
        coverage_data['files'] = list(map(self.make_filename_relative, coverage_data['files']))
        coverage_data['files'].sort(key=lambda file: file['covered_percent'])
        return coverage_data

    def get_file_coverage(self, filename):
        if self.coverage is None or self.is_file_exempt(filename):
            return

        coverage_files = self.coverage['files']
        for coverage_file in coverage_files:
                if coverage_file['filename'] == filename:
                        return coverage_file

    def is_file_exempt(self, filename):
        normalized_filename = os.path.normpath(filename).replace('\\', '/')

        exempt = [r'/test/', r'/spec/', r'/features/', r'Gemfile$', r'Rakefile$', r'\.rake$',
            r'\.gemspec']

        ignore = os.path.join(self.project_root, '.covignore')
        if os.path.isfile(ignore):
            for path in open(ignore).read().rstrip("\n").split("\n"):
                exempt.append(path)

        for pattern in exempt:
            if re.compile(pattern).search(normalized_filename) is not None:
                return True
        return False

    def get_coverage_data(self):
        coverage_filename = self.get_coverage_filename()
        if not coverage_filename:
            return

        return json.load(open(coverage_filename))

    def make_filename_relative(self, file):
        file['filename'] = os.path.relpath(file['filename'], self.project_root)
        return file

    def get_coverage_filename(self):
        if not self.project_root:
            return

        coverage_filename = os.path.join(self.project_root, 'coverage', 'coverage.json')
        if not os.access(coverage_filename, os.R_OK):
            print('Could not find coverage.json file.')
            return

        return coverage_filename

def get_project_root(filename):
    """the parent directory that contains a directory called 'coverage'"""
    coverage_directory = os.path.join(filename, 'coverage')
    if os.access(coverage_directory, os.R_OK):
        return filename

    parent, current = os.path.split(filename)
    if not current:
        print('Could not find coverage directory.')
        return

    return get_project_root(parent)
