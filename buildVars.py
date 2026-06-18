# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries
from site_scons.site_tools.NVDATool.utils import _

# Add-on information variables
addon_info = AddonInfo(
	# add-on Name/identifier, internal for NVDA
	addon_name="commandRunner",
	
	# Add-on summary/title, usually the user visible name of the add-on
	# Translators: Summary/title for this add-on
	addon_summary=_("Command runner for NVDA input gesture dialog"),
	
	# Add-on description
	# Translators: Long description to be shown for this add-on
	addon_description=_("""Adds "Run" buttons to NVDA's Input Gestures dialog, so you can try out the command currently selected in the tree right away, without closing the dialog or having to remember its assigned key combination.
	Four buttons are provided (Run 1x, 2x, 3x and 4x), each running the command that many times in a row. This makes it easy to test commands whose behaviour changes depending on how many times in a row they are pressed, such as reporting the time on the first press and the date on the second.
	Works both with NVDA's own built-in commands and with commands added by other add-ons. While a command runs, the dialog is briefly hidden, with speech muted around the hide/show so NVDA's own focus announcements don't interrupt or get mixed up with whatever the command itself reports."""),
	
	# version
	addon_version="0.2.0",
	
	# Brief changelog for this version
	# Translators: what's new content for the add-on version
	addon_changelog=_("""
Added: Buttons to run the selected command 2, 3 or 4 times in a row, to test commands that behave differently on repeated presses.
Added: The selected command can now be NVDA's own built-in commands (previously only commands added by add-ons could be run).
Fixed: Speech is now muted while the dialog is briefly hidden and shown again to run a command, so NVDA's focus announcements no longer interrupt or get cut off by the command's own speech.
"""),
	
	# Author(s)
	addon_author="Çağrı Doğan <cagrid@hotmail.com>",
	
	# URL for the add-on documentation support
	addon_url=None,
	
	# URL for the add-on repository where the source code can be found
	addon_sourceURL=None,
	
	# Documentation file name
	addon_docFileName="readme.html",
	
	# Minimum NVDA version supported
	addon_minimumNVDAVersion="2025.1.0",
	
	# Last NVDA version supported/tested
	addon_lastTestedNVDAVersion="2026.1.1",
	
	# Add-on update channel (None denotes stable releases)
	addon_updateChannel=None,
	
	# Add-on license
	addon_license="GPL-2.0",
	addon_licenseURL=None,
)

# Define the python files that are the sources of your add-on.
# We point to the specific directory where your code lives.
pythonSources: list[str] = ["addon/globalPlugins/commandRunner/*.py"]

# Files that contain strings for translation. Usually your python sources
i18nSources: list[str] = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
excludedFiles: list[str] = []

# Base language for the NVDA add-on
# Since your code strings (e.g. _("Table")) are in English, we keep this as "en".
baseLanguage: str = "en"

# Markdown extensions for add-on documentation
markdownExtensions: list[str] = []

# Custom braille translation tables
brailleTables: BrailleTables = {}

# Custom speech symbol dictionaries
symbolDictionaries: SymbolDictionaries = {}