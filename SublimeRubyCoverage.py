import os
import sublime
import sublime_plugin
PLUGIN_FILE = os.path.abspath(__file__)

def find_project_root(file_path):
    """Project Root is defined as the parent directory that contains a directory called 'coverage'"""
    breadcrumbs = os.path.split(file_path)
    while breadcrumbs:
        if os.access(os.path.join(*breadcrumbs, 'coverage'), os.R_OK)
            return os.path.join(*breadcrumbs)
        breadcrumbs.pop()

class SublimeRubyCoverageListener(sublime_plugin.EventListener):
    """Event listener to highlight uncovered lines when a Ruby file is loaded."""

    def on_load(self, view):
        if 'source.python' not in view.scope_name(0):
            return

        view.run_command('show_ruby_coverage')

class ShowRubyCoverageCommand(sublime_plugin.TextCommand):
    """Highlight uncovered lines in the current file based on a previous coverage run."""

    def run(self, edit):
        view = self.view
        filename = view.file_name()
        if not filename:
            return

        project_root = find_project_root(filename)
        if not project_root:
            print 'Could not find coverage directory.'
            return

        relative_file_path = os.path.relpath(filename, project_root)
        coverage_filename = os.path.split(relative_file_path).join('-')
        coverage_filepath = os.path.join(project_root, 'coverage', 'csv-more', coverage_filename)

        with open(coverage_filepath) as coverage_file:
            current_line = -1
            outlines = []
            for line in coverage_file:
                if line.strip() != 'true' and current_line >= 0:
                    outlines.append(view.full_line(view.text_point(current_line, 0)))

                current_line += 1

        # update highlighted regions
        view.erase_regions('SublimeRubyCoverage')
        if outlines:
            view.add_regions('SublimeRubyCoverage', outlines, 'comment',
                sublime.DRAW_EMPTY | sublime.DRAW_OUTLINED)
