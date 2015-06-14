import os
from sublime import Region
from sublime_plugin import TextCommand

from .common.json_coverage_reader import JsonCoverageReader

PANEL_NAME = 'ruby-coverage-project'

class ShowProjectRubyCoverage(TextCommand):
    """Show coverage of all files in current file's project in a panel."""

    def run(self, edit):
        self.get_project_coverage()
        self.create_output_panel()
        self.display_project_coverage(edit)

    def get_project_coverage(self):
        filename = self.view.file_name()

        r = JsonCoverageReader(filename)
        self.coverage = r.get_project_coverage() if r else None

    def create_output_panel(self):
        self.panel = self.view.window().create_output_panel(PANEL_NAME)

    def display_project_coverage(self, edit):
        panel = self.panel
        panel.set_read_only(False)
        panel.erase(edit, Region(0, panel.size()))
        panel.insert(edit, 0, self.format_project_coverage())
        panel.set_read_only(True)
        panel.show(0)

        self.view.window().run_command("show_panel", {"panel": "output.{}".format(PANEL_NAME)})

    def format_project_coverage(self):
        files = self.coverage['files']

        output = ''

        max_filename_length = len(max(files, key=lambda file: len(file['filename']))['filename'])

        for file in files:
            output += file['filename'].ljust(max_filename_length) + ' {:>5.1f}% covered\n'.format(file['covered_percent'])

        return output
