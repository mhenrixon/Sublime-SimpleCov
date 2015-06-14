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
        panel = self.panel
        files = self.coverage['files']

        output = ''

        viewport_width = int(panel.viewport_extent()[0] / panel.em_width())
        max_filename_length = len(max(files, key=lambda file: len(file['filename']))['filename'])
        coverage_length = len('100%')
        graph_width = viewport_width - max_filename_length - coverage_length - 4

        for file in files:
            graph_bar_width = int(file['covered_percent'] / 100.0 * graph_width)

            filename = file['filename'].ljust(max_filename_length)
            graph    = ''.ljust(graph_bar_width, '█') + ''.ljust(graph_width - graph_bar_width)
            coverage = '{:>5.1f}%'.format(file['covered_percent'])

            output += '{} {} {}\n'.format(filename, graph, coverage)

        return output
