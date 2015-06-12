import os
import sublime
import sublime_plugin
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
        filename = view.file_name()
        if not filename:
            return

        if self.file_exempt(filename):
            return

        project_root = find_project_root(filename)
        if not project_root:
            print('Could not find coverage directory.')
            return

        relative_file_path = os.path.relpath(filename, project_root)

        coverage_filename = '-'.join(explode_path(relative_file_path))[1:].replace(".rb", "_rb.csv").replace(".y", "_y.csv")
        coverage_filepath = os.path.join(project_root, 'coverage', 'sublime-ruby-coverage', coverage_filename)

        regions = []

        try:
            with open(coverage_filepath) as coverage_file:
                for current_line, line in enumerate(coverage_file):
                    if line.strip() != '1':
                        region = view.full_line(view.text_point(current_line, 0))
                        regions.append(region)
        except IOError as e:
            # highlight the entire view
            regions.append(sublime.Region(0,view.size()))
            view.set_status('SublimeRubyCoverage', 'UNCOVERED!')
            if view.window():
                 sublime.status_message("Coverage file not found: " + coverage_filepath)

        # update highlighted regions
        if regions:
            view.add_regions('SublimeRubyCoverage', regions,
                             'coverage.uncovered')

    def hide_coverage(self):
        view = self.view
        view.erase_status('SublimeRubyCoverage')
        view.erase_regions('SublimeRubyCoverage')

    def file_exempt(self, filename):
        normalized_filename = os.path.normpath(filename).replace('\\', '/')

        exempt = [r'/test/', r'/spec/', r'/features/', r'Gemfile$', r'Rakefile$', r'\.rake$',
            r'\.gemspec']

        root = find_project_root(self.view.file_name())
        ignore = os.path.join(root, '.covignore')
        if os.path.isfile(ignore):
            for path in open(ignore).read().rstrip("\n").split("\n"):
                exempt.append(path)

        for pattern in exempt:
            if re.compile(pattern).search(normalized_filename) is not None:
                return True
        return False

def find_project_root(file_path):
    """the parent directory that contains a directory called 'coverage'"""
    if os.access(os.path.join(file_path, 'coverage'), os.R_OK):
        return file_path

    parent, current = os.path.split(file_path)
    if current:
        return find_project_root(parent)

def explode_path(path):
    first, second = os.path.split(path)
    if second:
        return explode_path(first) + [second]
    else:
        return [first]

