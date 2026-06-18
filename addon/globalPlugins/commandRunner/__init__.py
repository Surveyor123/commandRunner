# __init__.py
import wx
import sys
import time
import weakref
import globalPluginHandler
import addonHandler
import logHandler
import speech
import config
import scriptHandler
from gui.inputGestures import InputGesturesDialog

addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self._patchInputGesturesDialog()

    def _patchInputGesturesDialog(self):
        self._orig_makeSettings = InputGesturesDialog.makeSettings
        self._orig_refreshButtonState = InputGesturesDialog._refreshButtonState
        plugin_self = self

        def new_makeSettings(dialog_self, settingsSizer):
            plugin_self._orig_makeSettings(dialog_self, settingsSizer)
            dialog_self.runCommandBtns = []
            try:
                btnSizer = dialog_self.removeButton.GetContainingSizer()
            except Exception:
                btnSizer = None
                logHandler.log.error("runCommandAddon: Could not find button sizer.", exc_info=True)

            for pressCount in range(1, 5):
                # Translators: Label for a button that runs the selected command a given
                # number of times in a row (used to test commands that behave differently
                # on double/triple/etc. presses). The digit is also the keyboard
                # accelerator, e.g. alt+2 activates the "Run &2x" button.
                label = _("Run &%dx") % pressCount
                btn = wx.Button(dialog_self, label=label)
                btn.Bind(wx.EVT_BUTTON, lambda evt, n=pressCount: plugin_self._onRunCommand(dialog_self, n))
                btn.Disable()
                dialog_self.runCommandBtns.append(btn)
                if btnSizer:
                    btnSizer.Add(btn, 0, wx.LEFT, 5)

            if btnSizer:
                dialog_self.Layout()

        def new_refreshButtonState(dialog_self):
            plugin_self._orig_refreshButtonState(dialog_self)
            try:
                if not hasattr(dialog_self, 'runCommandBtns') or not dialog_self.runCommandBtns:
                    return
                scriptFunc = plugin_self._getScriptFunc(dialog_self)
                canRun = scriptFunc is not None
                for btn in dialog_self.runCommandBtns:
                    btn.Enable(canRun)
            except RuntimeError:
                pass

        InputGesturesDialog.makeSettings = new_makeSettings
        InputGesturesDialog._refreshButtonState = new_refreshButtonState

    def _getScriptFunc(self, dialog_self):
        try:
            selectedItems = dialog_self.tree.getSelectedItemData()
            if selectedItems is None:
                return None
            catVM, scriptVM, gestureVM = selectedItems
            if scriptVM is None:
                return None
            scriptInfo = getattr(scriptVM, 'scriptInfo', None)
            if scriptInfo is None:
                return None
            cls = getattr(scriptInfo, 'cls', None)
            scriptName = getattr(scriptInfo, 'scriptName', None)
            if cls is None or not scriptName:
                return None
            if scriptName.startswith('kb:'):
                return None
            # First search for instance in prevFocus chain
            import gui
            func = self._findScriptOnObject(gui.mainFrame.prevFocus, cls, scriptName)
            if func:
                return func
            for ancestor in (gui.mainFrame.prevFocusAncestors or []):
                func = self._findScriptOnObject(ancestor, cls, scriptName)
                if func:
                    return func
            # Search for browse mode (tree interceptor) commands
            treeInterceptor = getattr(gui.mainFrame.prevFocus, 'treeInterceptor', None)
            func = self._findScriptOnObject(treeInterceptor, cls, scriptName)
            if func:
                return func
            # Search global plugin instances
            for plugin in globalPluginHandler.runningPlugins:
                if isinstance(plugin, cls):
                    method = getattr(plugin, 'script_%s' % scriptName, None)
                    if method:
                        return method
            # Search NVDA's own built-in commands (globalCommands)
            import globalCommands
            func = self._findScriptOnObject(globalCommands.commands, cls, scriptName)
            if func:
                return func
            func = self._findScriptOnObject(globalCommands.configProfileActivationCommands, cls, scriptName)
            if func:
                return func
            # Search appModule instances
            import appModuleHandler
            appModule = appModuleHandler.getAppModuleForNVDAObject(gui.mainFrame.prevFocus)
            if appModule and isinstance(appModule, cls):
                method = getattr(appModule, 'script_%s' % scriptName, None)
                if method:
                    return method
            return None
        except Exception:
            logHandler.log.error("runCommandAddon: _getScriptFunc failed.", exc_info=True)
            return None

    def _findScriptOnObject(self, obj, cls, scriptName):
        if obj is not None and isinstance(obj, cls):
            method = getattr(obj, 'script_%s' % scriptName, None)
            return method
        return None

    def _getSpeechMode(self):
        # Returns the current speech mode, or None if it could not be read.
        try:
            return speech.getState().speechMode
        except Exception:
            logHandler.log.error("runCommandAddon: Could not read speech mode.", exc_info=True)
            return None

    def _setSpeechMode(self, mode):
        # mode may be None (e.g. if it couldn't be read earlier); in that
        # case there is nothing safe to restore, so just leave things as is.
        if mode is None:
            return
        try:
            speech.setSpeechMode(mode)
        except Exception:
            logHandler.log.error("runCommandAddon: Could not set speech mode.", exc_info=True)

    def _runScriptWithRepeat(self, scriptFunc, gesture):
        # Updates scriptHandler's repeat-count bookkeeping the same way a real
        # key press would (see scriptHandler.executeScript), so that a script
        # checking scriptHandler.getLastScriptRepeatCount() behaves as if it
        # had actually been pressed multiple times in a row. Unlike
        # executeScript, this does not swallow exceptions raised by
        # scriptFunc itself, so the caller's own error beep still works.
        try:
            rawFunc = getattr(scriptFunc, "__func__", scriptFunc)
            now = time.time()
            lastRef = scriptHandler._lastScriptRef() if scriptHandler._lastScriptRef else None
            timeDiffMs = (now - scriptHandler._lastScriptTime) * 1000
            if timeDiffMs <= config.conf["keyboard"]["multiPressTimeout"] and rawFunc == lastRef:
                scriptHandler._lastScriptCount += 1
            else:
                scriptHandler._lastScriptCount = 0
            scriptHandler._lastScriptRef = weakref.ref(rawFunc)
            scriptHandler._lastScriptTime = now
        except Exception:
            # If scriptHandler's internals ever change shape, fail soft: the
            # command still runs, just always as if it were the first press.
            logHandler.log.error("runCommandAddon: Could not update script repeat count.", exc_info=True)
        scriptFunc(gesture)

    def _onRunCommand(self, dialog_self, pressCount=1):
        scriptFunc = self._getScriptFunc(dialog_self)
        if not scriptFunc:
            return

        pressCount = max(1, pressCount)

        # Hiding and re-showing the dialog moves the system focus back and
        # forth, which makes NVDA announce the newly focused object each
        # time. That announcement can interrupt or get cut off by speech
        # produced by the command itself. To avoid this, speech is muted
        # right around those focus changes, and only re-enabled while the
        # command is actually running. The user's original speech mode
        # (whatever it was) is restored once everything settles.
        originalSpeechMode = self._getSpeechMode()
        self._setSpeechMode(speech.SpeechMode.off)

        dialog_self.Hide()

        def execute_and_restore():
            # Speech is back on for the duration of the command, so its
            # own output (if any) is heard normally.
            self._setSpeechMode(originalSpeechMode)
            try:
                for _ in range(pressCount):
                    self._runScriptWithRepeat(scriptFunc, None)
            except Exception:
                logHandler.log.error("runCommandAddon: Script execution failed.", exc_info=True)
                import tones
                tones.beep(500, 200)
            finally:
                # Mute again before bringing the dialog back into focus.
                self._setSpeechMode(speech.SpeechMode.off)
                try:
                    dialog_self.Show()
                    dialog_self.tree.SetFocus()
                except RuntimeError:
                    pass
                # Give NVDA a moment to silently process the resulting
                # focus event, then restore the original speech mode.
                wx.CallLater(300, lambda: self._setSpeechMode(originalSpeechMode))

        wx.CallLater(300, execute_and_restore)

    def terminate(self):
        if hasattr(self, '_orig_makeSettings'):
            InputGesturesDialog.makeSettings = self._orig_makeSettings
        if hasattr(self, '_orig_refreshButtonState'):
            InputGesturesDialog._refreshButtonState = self._orig_refreshButtonState