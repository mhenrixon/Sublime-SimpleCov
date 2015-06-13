import os
import sublime
import sublime_plugin
import json
import re

class ToggleRubyCoverageCommand(sublime_plugin.TextCommand):
    """Show/hide coverage of current file based on a previous coverage run."""

    def run(self, edit):
        if 'source.ruby' not in self.view.scope_name(0):
            return

        settings = self.view.settings()
        if settings.has('ruby_coverage.visible'):
            self.hide_coverage()
            settings.erase('ruby_coverage.visible')
        else:
            self.show_coverage()
            settings.set('ruby_coverage.visible', True)

    def show_coverage(self):
        view = self.view

        filename = self.get_filename()
        if not filename:
            return

        coverage = get_coverage_for_filename(filename)
        if not coverage:
            regions.append(sublime.Region(0,view.size()))
            view.set_status('SublimeRubyCoverage', 'NOT COVERED')
            if view.window():
                 sublime.status_message('No coverage data for this file.')
            return
        regions = []

        for line_number, line_coverage in list(enumerate(coverage)):
            if line_coverage == 0:
                regions.append(view.full_line(view.text_point(line_number, 0)))

        # update highlighted regions
        if regions:
            view.add_regions('SublimeRubyCoverage', regions,
                             'coverage.uncovered')

    def get_filename(self):
        view = self.view
        filename = view.file_name()
        if not filename or self.file_exempt(filename):
            return
        return filename

    def hide_coverage(self):
        view = self.view
        view.erase_status('SublimeRubyCoverage')
        view.erase_regions('SublimeRubyCoverage')

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

def get_coverage_for_filename(filename):
    coverage = get_coverage(filename)
    coverage_files = coverage['files']
    for coverage_file in coverage_files:
        if coverage_file['filename'] == filename:
            return coverage_file['coverage']

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

def explode_path(path):
    first, second = os.path.split(path)
    if second:
        return explode_path(first) + [second]
    else:
        return [first]

