import os
import sublime
from sublime_plugin import TextCommand

from .common.json_coverage_reader import JsonCoverageReader
from .common.theme_generator import ThemeGenerator

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
        output, regions = self.format_project_coverage()

        panel = self.panel
        panel.set_read_only(False)
        panel.erase(edit, sublime.Region(0, panel.size()))
        panel.insert(edit, 0, output)
        panel.set_read_only(True)
        panel.show(0)

        self.augment_color_scheme()
        self.apply_regions(regions)

        self.view.window().run_command("show_panel", {"panel": "output.{}".format(PANEL_NAME)})

    def format_project_coverage(self):
        panel = self.panel
        files = self.coverage['files']

        output = ''

        viewport_width = int(panel.viewport_extent()[0] / panel.em_width())
        max_filename_length = len(max(files, key=lambda file: len(file['filename']))['filename'])
        coverage_length = len('100%')
        graph_width = viewport_width - max_filename_length - coverage_length - 7

        regions = [[], [], [], [], [], [], [], [], [], [], []]
        for file in files:
            graph_bar_width = int(file['covered_percent'] / 100.0 * graph_width)

            filename = file['filename'].ljust(max_filename_length)
            graph    = ''.ljust(graph_bar_width)
            coverage = '{:>5.1f}%'.format(file['covered_percent'])

            graph_region_start = len(output) + max_filename_length + len(coverage) + 2
            output += '{} {} {}\n'.format(filename, coverage, graph)

            decile = int(file['covered_percent'] / 10)
            regions[decile].append(sublime.Region(graph_region_start, graph_region_start + graph_bar_width))

        return output, regions

    def apply_regions(self, regions):
        view = self.panel

        for decile, decile_regions in list(enumerate(regions)):
            decile_percent = decile * 10
            view.add_regions('coverage-graph-{}'.format(decile_percent),
                             decile_regions,
                             'coverage.graph.{}'.format(decile_percent))

    def augment_color_scheme(self):
        """
        Generate a new color scheme from the original with additional coverage-
        related style rules added. Save this color scheme to disk and set it as
        the target view's active color scheme.

        (Hat tip to GitSavvy for this technique!)
        """
        view = self.panel

        settings = view.settings()
        self.restore_color_scheme()
        original_color_scheme = settings.get("color_scheme")
        settings.set("ruby_coverage.original_color_scheme", original_color_scheme)
        colors = sublime.load_settings("SublimeRubyCoverage.sublime-settings").get("colors")
        themeGenerator = ThemeGenerator(original_color_scheme)
        themeGenerator.add_scoped_style(
            "Coverage bar graph 0-9%",
            "coverage.graph.0",
            foreground = colors["graph"]["0"],
            background = "#1B1E22"
            )
        themeGenerator.add_scoped_style(
            "Coverage bar graph 10-19%",
            "coverage.graph.10",
            foreground = colors["graph"]["10"],
            background = "#1B1E22"
            )
        themeGenerator.add_scoped_style(
            "Coverage bar graph 20-29%",
            "coverage.graph.20",
            foreground = colors["graph"]["20"],
            background = "#1B1E22"
            )
        themeGenerator.add_scoped_style(
            "Coverage bar graph 30-39%",
            "coverage.graph.30",
            foreground = colors["graph"]["30"],
            background = "#1B1E22"
            )
        themeGenerator.add_scoped_style(
            "Coverage bar graph 40-49%",
            "coverage.graph.40",
            foreground = colors["graph"]["40"],
            background = "#1B1E22"
            )
        themeGenerator.add_scoped_style(
            "Coverage bar graph 50-59%",
            "coverage.graph.50",
            foreground = colors["graph"]["50"],
            background = "#1B1E22"
            )
        themeGenerator.add_scoped_style(
            "Coverage bar graph 60-69%",
            "coverage.graph.60",
            foreground = colors["graph"]["60"],
            background = "#1B1E22"
            )
        themeGenerator.add_scoped_style(
            "Coverage bar graph 70-79%",
            "coverage.graph.70",
            foreground = colors["graph"]["70"],
            background = "#1B1E22"
            )
        themeGenerator.add_scoped_style(
            "Coverage bar graph 80-89%",
            "coverage.graph.80",
            foreground = colors["graph"]["80"],
            background = "#1B1E22"
            )
        themeGenerator.add_scoped_style(
            "Coverage bar graph 90-99%",
            "coverage.graph.90",
            foreground = colors["graph"]["90"],
            background = "#1B1E22"
            )
        themeGenerator.add_scoped_style(
            "Coverage bar graph 100%",
            "coverage.graph.100",
            foreground = colors["graph"]["100"],
            background = "#1B1E22"
            )
        themeGenerator.apply_new_theme("ruby-coverage-graph", view)

    def restore_color_scheme(self):
        settings = self.panel.settings()
        original_color_scheme = settings.get("ruby_coverage.original_color_scheme")
        if original_color_scheme:
            settings.set("color_scheme", original_color_scheme)
            settings.erase("ruby_coverage.original_color_scheme")
