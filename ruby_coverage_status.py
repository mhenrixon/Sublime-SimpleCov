import os
import sublime
import sublime_plugin
import json
import re

from .common.json_coverage_reader import JsonCoverageReader

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

        filename = view.file_name()
        if not filename:
            self.erase_status()

        r = JsonCoverageReader(filename)
        coverage = r.get_file_coverage(filename) if r else None
        if coverage is None:
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

    def get_line_number(self):
        view = self.view

        regions = view.sel()
        if len(regions) > 1:
            return

        return view.rowcol(regions[0].a)[0]
