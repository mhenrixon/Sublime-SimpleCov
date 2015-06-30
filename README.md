Sublime SimpleCov
=================

A plugin for Sublime Text 3 for visualising SimpleCov code coverage data in your editor.

Features
--------

* Toggle highlighting of covered (green) and uncovered (red) lines of code.
  * Shade of green indicates coverage level (with configurable thresholds).
  * Highlight colors configurable.
* View whole file and current line coverage statistics in the status bar.
  * Can be disabled in user settings.
* View list of all covered files in project, from least to most coverage.
  * Includes color-coded coverage graph (colors configurable).
  * Supports wide and compact layouts depending on window width.

Installation
------------

First, you must have [SimpleCov](https://github.com/colszowka/simplecov) installed and configured for your project.

Next, install and set up the [simplecov-json](https://github.com/vicentllongo/simplecov-json) formatter. If you’re using SimpleCov 0.9 or later, you have the option of using multiple formatters, so you can continue to generate the default HTML report along with the JSON report required by this package.

Finally, install this package using [Package Control](https://packagecontrol.io):

1. With Package Control installed, go to Tools > Command Palette.
2. Select the **Package Control: Install Package** command and hit Enter.
3. Type **SimpleCov** and hit Enter.

Usage
-----

Run your tests to generate a **coverage/coverage.json** file in your project. Then:

* Move your cursor around in one of the project’s Ruby files to see file and line coverage info in the status bar.
* Open Command Palette and choose **SimpleCov: Toggle Coverage Highlight** to display file coverage as green and red colored highlights. By default, lines covered once are highlighted in dark green, lines covered twice are highlighted in brighter green, and lines covered 50 or more times are displayed in very bright green. Invoke the command again to turn highlights off.
    * **Note:** Currently, to update the highlights after a test run, you’ll need to toggle highlighting off and then on again. This will be improved in a future update.
* Open Command Palette and choose **SimpleCov: Show Project Coverage** to open a panel containing a list of covered Ruby files in your project, from least to most coverage, with a color-coded bar graph indicating the coverage for each file.

Ignoring Files
--------------

Common “non-code” Ruby files, such as spec files, are ignored automatically. Add a .covignore file to your project root in order to add additional, custom ignores.
