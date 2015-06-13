import os
import sublime
import sublime_plugin
import json
import re

from .theme_generator import ThemeGenerator
from .common.json_coverage_reader import JsonCoverageReader

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
            if self.show_coverage():
                settings.set('ruby_coverage.visible', True)
                if self.is_auto_scroll_enabled():
                    self.scroll_to_uncovered()

    def show_coverage(self):
        view = self.view

        filename = view.file_name()
        if not filename:
            return

        r = JsonCoverageReader(filename)
        coverage = r.get_file_coverage(filename) if r else None
        if coverage is None:
            regions.append(sublime.Region(0,view.size()))
            view.set_status('SublimeRubyCoverage', 'NOT COVERED')
            if view.window():
                 sublime.status_message('No coverage data for this file.')
            return

        coverage_levels = sublime.load_settings("SublimeRubyCoverage.sublime-settings").get("coverage_levels")

        uncovered_regions = []
        covered_regions = []
        more_covered_regions = []
        most_covered_regions = []

        current_coverage_regions = None
        current_region_start = None
        current_region_end = None

        for line_number, line_coverage in list(enumerate(coverage['coverage'])):
            if line_coverage is None:
                # first line after different coverage data
                if current_coverage_regions is not None:
                    current_region_end = view.full_line(view.text_point(line_number - 1, 0)).end()
                    current_coverage_regions.append(sublime.Region(current_region_start, current_region_end))
                    current_coverage_regions = None
            elif line_coverage >= coverage_levels['most_covered']:
                # first line after different coverage data
                if current_coverage_regions is not most_covered_regions:
                    if current_coverage_regions is not None:
                        current_region_end = view.full_line(view.text_point(line_number - 1, 0)).end()
                        current_coverage_regions.append(sublime.Region(current_region_start, current_region_end))
                    current_region_start = view.text_point(line_number, 0)
                    current_coverage_regions = most_covered_regions
            elif line_coverage >= coverage_levels['more_covered']:
                # first line after different coverage data
                if current_coverage_regions is not more_covered_regions:
                    if current_coverage_regions is not None:
                        current_region_end = view.full_line(view.text_point(line_number - 1, 0)).end()
                        current_coverage_regions.append(sublime.Region(current_region_start, current_region_end))
                    current_region_start = view.text_point(line_number, 0)
                    current_coverage_regions = more_covered_regions
            elif line_coverage >= coverage_levels['covered']:
                # first line after different coverage data
                if current_coverage_regions is not covered_regions:
                    if current_coverage_regions is not None:
                        current_region_end = view.full_line(view.text_point(line_number - 1, 0)).end()
                        current_coverage_regions.append(sublime.Region(current_region_start, current_region_end))
                    current_region_start = view.text_point(line_number, 0)
                    current_coverage_regions = covered_regions
            else:
                # first line after different coverage data
                if current_coverage_regions is not uncovered_regions:
                    if current_coverage_regions is not None:
                        current_region_end = view.full_line(view.text_point(line_number - 1, 0)).end()
                        current_coverage_regions.append(sublime.Region(current_region_start, current_region_end))
                    current_region_start = view.text_point(line_number, 0)
                    current_coverage_regions = uncovered_regions

        file_ext = get_file_extension(os.path.basename(filename))
        augment_color_scheme(view, file_ext)

        view.add_regions('ruby-coverage-uncovered-lines', uncovered_regions,
                         'coverage.uncovered')
        view.add_regions('ruby-coverage-covered-lines', covered_regions,
                         'coverage.covered')
        view.add_regions('ruby-coverage-more-covered-lines', more_covered_regions,
                         'coverage.covered.more')
        view.add_regions('ruby-coverage-most-covered-lines', most_covered_regions,
                         'coverage.covered.most')
        return True

    def hide_coverage(self):
        view = self.view
        restore_color_scheme(view)
        view.erase_status('SublimeRubyCoverage')
        view.erase_regions('ruby-coverage-uncovered-lines')
        view.erase_regions('ruby-coverage-covered-lines')
        view.erase_regions('ruby-coverage-more-covered-lines')
        view.erase_regions('ruby-coverage-most-covered-lines')

    def is_auto_scroll_enabled(self):
        settings = sublime.load_settings("SublimeRubyCoverage.sublime-settings")
        return settings.get("auto_scoll_to_uncovered", False)

    def scroll_to_uncovered(self):
        view = self.view
        regions = view.sel()
        if len(regions) > 1 or regions[0].size() > 0:
            return

        uncovered_lines = view.get_regions('ruby-coverage-uncovered-lines')
        if uncovered_lines and len(uncovered_lines) > 0:
            first_uncovered = uncovered_lines[0].a

        view.sel().clear()
        view.sel().add(sublime.Region(first_uncovered, first_uncovered))
        view.show_at_center(first_uncovered)

def augment_color_scheme(view, file_ext):
    """
    Given a target view, generate a new color scheme from the original with
    additional coverage-related style rules added. Save this color scheme to
    disk and set it as the target view's active color scheme.

    (Hat tip to GitSavvy for this technique!)
    """
    colors = sublime.load_settings("SublimeRubyCoverage.sublime-settings").get("colors")

    settings = view.settings()
    original_color_scheme = settings.get("color_scheme")
    settings.set("ruby_coverage.original_color_scheme", original_color_scheme)
    themeGenerator = ThemeGenerator(original_color_scheme)
    themeGenerator.add_scoped_style(
        "SublimeRubyCoverage Uncovered Line",
        "coverage.uncovered",
        background=colors["coverage"]["uncovered_background"],
        foreground=colors["coverage"]["uncovered_foreground"]
        )
    themeGenerator.add_scoped_style(
        "SublimeRubyCoverage Covered Line",
        "coverage.covered",
        background=colors["coverage"]["covered_background"],
        foreground=colors["coverage"]["covered_foreground"]
        )
    themeGenerator.add_scoped_style(
        "SublimeRubyCoverage More Covered Line",
        "coverage.covered.more",
        background=colors["coverage"]["covered_background_bold"],
        foreground=colors["coverage"]["covered_foreground_bold"]
        )
    themeGenerator.add_scoped_style(
        "SublimeRubyCoverage Most Covered Line",
        "coverage.covered.most",
        background=colors["coverage"]["covered_background_extrabold"],
        foreground=colors["coverage"]["covered_foreground_extrabold"]
        )
    themeGenerator.apply_new_theme("ruby-coverage-view." + file_ext, view)

def restore_color_scheme(view):
    settings = view.settings()
    original_color_scheme = settings.get("ruby_coverage.original_color_scheme")
    if original_color_scheme:
        settings.set("color_scheme", original_color_scheme)
        settings.erase("ruby_coverage.original_color_scheme")

def get_file_extension(filename):
    period_delimited_segments = filename.split(".")
    return "" if len(period_delimited_segments) < 2 else period_delimited_segments[-1]
