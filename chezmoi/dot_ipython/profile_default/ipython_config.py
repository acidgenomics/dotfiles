"""
IPython default configuration.
Updated 2022-05-27.

Generate default template with 'ipython profile create default'.
"""

# pylint: disable=undefined-variable
c = get_config()  # noqa

c.TerminalInteractiveShell.highlighting_style = "dracula"
c.TerminalInteractiveShell.true_color = True
