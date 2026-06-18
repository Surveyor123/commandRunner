# Command Runner

A small global plugin for [NVDA](https://www.nvaccess.org/) that adds "Run" buttons to the Input Gestures dialog, so you can try out the command currently selected in the tree right away — no need to close the dialog, switch windows, or remember which key combination it's bound to.

## Features

- **Run a command directly from the Input Gestures dialog.** Select any command in the tree and run it on the spot.
- **Run it 1, 2, 3 or 4 times in a row.** Many NVDA commands behave differently depending on how many times in a row they're pressed (for example, reporting the time on the first press and the date on the second). The four buttons let you test each of those behaviours without having to physically press the real gesture multiple times quickly.
- **Works with NVDA's own built-in commands**, as well as commands added by other add-ons.
- **Speech stays clean while testing.** The dialog briefly hides and reappears while a command runs; speech is automatically muted around that hide/show so NVDA's own focus announcements don't interrupt or get tangled up with whatever the command itself reports.

## How to use

1. Open NVDA's Input Gestures dialog (NVDA menu > Preferences > Input gestures…).
2. In the tree, select the command you want to try out.
3. Once a runnable command is selected, the **Run 1x**, **Run 2x**, **Run 3x** and **Run 4x** buttons become enabled. Click one of them, or use **alt+1** through **alt+4**, to run the command that many times in a row.
4. The dialog hides for a moment while the command runs, then reappears with focus back on the tree.

## Notes

- Not every entry in the tree corresponds to a runnable NVDA script — plain keyboard-emulation entries, for instance, can't be run this way, so the buttons will stay disabled for those.
- If a command raises an error while running, NVDA plays a short error tone and logs the details to the NVDA log.

## Requirements

NVDA 2025.1 or later. Tested up to NVDA 2026.1.1.

## Author

Çağrı Doğan ([cagrid@hotmail.com](mailto:cagrid@hotmail.com))

## License

This add-on is licensed under the GNU General Public License version 2.