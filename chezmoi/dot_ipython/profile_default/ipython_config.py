"""IPython default configuration.

Generate default template with 'ipython profile create default'.

Theme configuration details:
https://ipython.readthedocs.io/en/stable/config/details.html

Dracula configuration:
https://draculatheme.com/pygments
"""

from copy import deepcopy
from IPython.utils.PyColorize import linux_theme, theme_table

# pylint: disable=undefined-variable
c = get_config()  # noqa

dracula = deepcopy(linux_theme)
dracula.base = "dracula"
theme_table["dracula"] = dracula

c.TerminalInteractiveShell.colors = "dracula"
c.TerminalInteractiveShell.editor = "nvim"
c.TerminalInteractiveShell.true_color = True
