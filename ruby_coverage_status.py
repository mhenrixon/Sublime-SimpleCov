import os
import sublime
import sublime_plugin
import json
import re

STATUS_KEY = 'ruby-coverage-status'

class RubyCoverageStatusListener(sublime_plugin.EventListener):
    """Show coverage statistics in status bar."""

    def on_selection_modified(self, view):
        if 'source.ruby' not in view.scope_name(0):
            return

        self.view = view
        if sublime.load_settings('SublimeRubyCoverage.sublime-settings').get('coverage_status_in_status_bar'):
            sublime.set_timeout_async(self.update_status, 0)
        else:
            self.erase_status()

    def update_status(self):
        view = self.view
        view.set_status(STATUS_KEY, self.get_view_coverage_status())

    def erase_status(self):
        view = self.view
        view.erase_status(STATUS_KEY)

    def get_view_coverage_status(self):
        view = self.view

        filename = self.get_filename()
        if not filename:
            self.erase_status()

        coverage = get_coverage_for_filename(filename)
        if not coverage:
            self.erase_status()

        line_number = self.get_line_number()
        if line_number is None:
            self.erase_status()

        file_coverage = "File covered {:.1f}% ({}/{})".format(
            coverage['covered_percent'],
            coverage['covered_lines'],
            coverage['lines_of_code']
        )

        line_coverage = coverage['coverage'][line_number]
        if line_coverage is None:
            line_coverage = 'Line not executable'
        elif line_coverage > 0:
            line_coverage = 'Line covered × {}'.format(line_coverage)
        else:
            line_coverage = 'Line not covered'

        return file_coverage + ', ' + line_coverage

    def get_filename(self):
        view = self.view
        filename = view.file_name()
        if not filename or self.file_exempt(filename):
            return
        return filename

    def file_exempt(self, filename):
        normalized_filename = os.path.normpath(filename).replace('\\', '/')

        exempt = [r'/test/', r'/spec/', r'/features/', r'Gemfile$', r'Rakefile$', r'\.rake$',
            r'\.gemspec']

        root = get_project_root_directory(self.view.file_name())
        ignore = os.path.join(root, '.covignore')
        if os.path.isfile(ignore):
            for path in open(ignore).read().rstrip("\n").split("\n"):
                exempt.append(path)

        for pattern in exempt:
            if re.compile(pattern).search(normalized_filename) is not None:
                return True
        return False

    def get_line_number(self):
        view = self.view

        regions = view.sel()
        if len(regions) > 1:
            return

        return view.rowcol(regions[0].a)[0]

def get_coverage_for_filename(filename):
    coverage = get_coverage(filename)
    coverage_files = coverage['files']
    for coverage_file in coverage_files:
        if coverage_file['filename'] == filename:
            return coverage_file

def get_coverage(filename):
    filename = get_coverage_filename(filename)
    with open(filename) as json_file:
        return json.load(json_file)

def get_coverage_filename(filename):
    project_root = get_project_root_directory(filename)
    if not project_root:
        return

    coverage_filename = os.path.join(project_root, 'coverage', 'coverage.json')
    if not os.access(coverage_filename, os.R_OK):
        print('Could not find coverage.json file.')
        return

    return coverage_filename

def get_project_root_directory(filename):
    """the parent directory that contains a directory called 'coverage'"""
    coverage_directory = os.path.join(filename, 'coverage')
    if os.access(coverage_directory, os.R_OK):
        return filename

    parent, current = os.path.split(filename)
    if not current:
        print('Could not find coverage directory.')

    return get_project_root_directory(parent)
