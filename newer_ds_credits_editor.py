#!/usr/bin/python
# -*- coding: latin-1 -*-

# Newer DS Credits Editor - Edits Newer DS's
# zh_cutscenes/A_CREDITS/2848 Credits_Sequence.bin
# Version 1.0
# Copyright (C) 2013-2019 RoadrunnerWMC

# This file is part of Newer DS Credits Editor.

# Newer DS Credits Editor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Newer DS Credits Editor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Newer DS Credits Editor.  If not, see <http://www.gnu.org/licenses/>.



# newer_ds_credits_editor.py
# This is the main executable for Newer DS Credits Editor


################################################################
################################################################


version = '1.0'

import re
import struct
import sys
import uuid

from PyQt5 import QtCore, QtGui, QtWidgets; Qt = QtCore.Qt




################################################################
################################################################
################################################################
########################### Commands ###########################


class Command():
    """
    Base class for all commands
    """
    name = ''
    description = ''
    dynamicDescription = None

    def __init__(self):
        self.widgets = []
        self.layout = QtWidgets.QVBoxLayout()
        self.uuid = uuid.uuid4()

    @classmethod
    def fromData(cls, data):
        """
        Create a Command instance based on some data
        """
        return cls()

    def asData(self):
        """
        Return data based on current settings
        """
        return ()

    def generateLayout(self):
        """
        Create a layout from self.widgets
        """
        if len(self.widgets) > 0:
            L = QtWidgets.QFormLayout()
            for name, W in self.widgets:
                if name is None:
                    L.addRow(W)
                else:
                    L.addRow(name, W)
            self.layout = L
        else: self.layout = getNullLayout()


NEWER_DS_FILE_SLOTS = [
    'Logo',
    'Header Font',
    'Body Font',
    'The End',
    'Coin Counter Font',
    'Darkness']


class DelayCommand(Command):
    """
    Command which indicates a delay
    """
    name = 'Wait'
    description = 'Causes a delay before the next command is processed.'

    def __init__(self):
        super().__init__()

        W = QtWidgets.QSpinBox()
        W.setMaximum(0xFFFF)
        self.widgets = []
        self.widgets.append(('Time (in frames):', W))
        self.generateLayout()

    @classmethod
    def fromData(cls, data):
        cmd = cls()
        delay = (data[1] << 8) | data[0]
        cmd.widgets[0][1].setValue(delay)
        return cmd

    def asData(self):
        return struct.pack('<H', self.widgets[0][1].value())

    @property
    def dynamicDescription(self):
        n = self.widgets[0][1].value()
        return 'for 1 frame' if n == 1 else f'for {n} frames'


class SwitchSceneCommand(Command):
    """
    Command which indicates a scene switch
    """
    name = 'Switch Scene'
    description = 'Causes the level to switch to another scene.'

    def __init__(self):
        super().__init__()

        self.widgets = []

        W = QtWidgets.QSpinBox()
        W.setMaximum(0xFFFF)
        self.widgets.append(('Area ID:', W))

        W = QtWidgets.QSpinBox()
        W.setMaximum(0xFFFF)
        self.widgets.append(('Entrance ID:', W))

        W = QtWidgets.QSpinBox()
        W.setMaximum(0xFF)
        self.widgets.append(('Background ID (top):', W))

        W = QtWidgets.QSpinBox()
        W.setMaximum(0xFF)
        self.widgets.append(('Background ID (bottom):', W))

        W = QtWidgets.QSpinBox()
        W.setMaximum(0xFF)
        self.widgets.append(('Tileset Slot:', W))

        W = QtWidgets.QCheckBox('Is Ending Scene')
        self.widgets.append((None, W))

        self.generateLayout()

    @classmethod
    def fromData(cls, data):
        cmd = cls()
        aid, eid, bgidt, bgidb, ts, ies = struct.unpack_from('<HH3B?', data, 0)
        cmd.widgets[0][1].setValue(aid)
        cmd.widgets[1][1].setValue(eid)
        cmd.widgets[2][1].setValue(bgidt)
        cmd.widgets[3][1].setValue(bgidb)
        cmd.widgets[4][1].setValue(ts)
        cmd.widgets[5][1].setChecked(ies)
        return cmd

    def asData(self):
        values = [self.widgets[i][1].value() for i in range(5)]
        values.append(self.widgets[5][1].isChecked())
        return struct.pack('<HH3B?', *values)

    @property
    def dynamicDescription(self):
        a, e = self.widgets[0][1].value(),  self.widgets[1][1].value()
        return f'to area {a}, entrance {e}'


class FadeLogoInCommand(Command):
    """
    Command which causes the logo to fade in
    """
    name = 'Fade Logo In'
    description = 'Causes the logo to begin to fade in.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class DropLogoCommand(Command):
    """
    Command which causes the logo to drop to the bottom screen
    """
    name = 'Drop Logo'
    description = 'Causes the logo to drop to the lower screen.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class FadeToBlackCommand(Command):
    """
    Command which causes the screen to fade to black.
    """
    name = 'Fade to Black'
    description = 'Causes the screen to fade to black.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class FadeFromBlackCommand(Command):
    """
    Command which causes the screen to fade from black.
    """
    name = 'Fade from Black'
    description = 'Causes the screen to fade in from black.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class FadeToWhiteCommand(Command):
    """
    Command which causes the screen to fade to white.
    """
    name = 'Fade to White'
    description = 'Causes the screen to fade to white.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class FadeFromWhiteCommand(Command):
    """
    Command which causes the screen to fade from white.
    """
    name = 'Fade from White'
    description = 'Causes the screen to fade in from white.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class ShowTextCommand(Command):
    """
    Command which shows the current text
    """
    name = 'Show Text'
    description = 'Causes the current header and body text to fade in.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class HideTextCommand(Command):
    """
    Command which hides the current text
    """
    name = 'Hide Text'
    description = 'Causes the current header and body text to fade out.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class SetHeaderTextCommand(Command):
    """
    Command which sets the current header text
    """
    name = 'Set Header Text'
    description = 'Changes the current header text.'

    def __init__(self):
        super().__init__()

        X = QtWidgets.QPlainTextEdit()
        X.setLineWrapMode(X.NoWrap)
        self.widgets = [('Text:', X)]
        self.generateLayout()

    @classmethod
    def fromData(cls, data):

        strLen = data[0]
        s = data[1 : 1+strLen].decode('latin-1')

        cmd = cls()
        cmd.widgets[0][1].setPlainText(s)
        return cmd

    def asData(self):
        s = self.widgets[0][1].toPlainText()
        return bytes([len(s)]) + s.encode('latin-1')

    @property
    def dynamicDescription(self):
        s = self.widgets[0][1].toPlainText()
        s = s.replace('\n', ' / ')
        if len(s) > 16 + 3:
            s = s[:16] + '...'
        return f'to "{s}"'


class ShowHeaderTextCommand(Command):
    """
    Command which shows the current header text
    """
    name = 'Show Header Text'
    description = 'Causes the current header text to fade in.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class HideHeaderTextCommand(Command):
    """
    Command which hides the current header text
    """
    name = 'Hide Header Text'
    description = 'Causes the current header text to fade out.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class SetBodyTextCommand(Command):
    """
    Command which sets the current body text
    """
    name = 'Set Body Text'
    description = 'Changes the current body text.'

    def __init__(self):
        super().__init__()

        X = QtWidgets.QPlainTextEdit()
        X.setLineWrapMode(X.NoWrap)
        self.widgets = [('Text:', X)]
        self.generateLayout()

    @classmethod
    def fromData(cls, data):

        strLen = data[0]
        s = data[1 : 1+strLen].decode('latin-1')

        cmd = cls()
        cmd.widgets[0][1].setPlainText(s)
        return cmd

    def asData(self):
        s = self.widgets[0][1].toPlainText()
        return bytes([len(s)]) + s.encode('latin-1')

    @property
    def dynamicDescription(self):
        s = self.widgets[0][1].toPlainText()
        s = s.replace('\n', ' / ')
        if len(s) > 16 + 3:
            s = s[:16] + '...'
        return f'to "{s}"'


class ShowBodyTextCommand(Command):
    """
    Command which shows the current body text
    """
    name = 'Show Body Text'
    description = 'Causes the current body text to fade in.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class HideBodyTextCommand(Command):
    """
    Command which hides the current body text
    """
    name = 'Hide Body Text'
    description = 'Causes the current body text to fade out.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class DisablePlayerControlCommand(Command):
    """
    Command which disables player control
    """
    name = 'Disable Player Control'
    description = 'Prevents Mario from receiving button inputs.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class EnablePlayerControlCommand(Command):
    """
    Command which enables player control
    """
    name = 'Enable Player Control'
    description = 'Allows Mario to receive button inputs again.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class EnableLowGravityPhysicsCommand(Command):
    """
    Command which enables low-gravity physics
    """
    name = 'Enable Low-Gravity Physics'
    description = 'Causes Mario to experience low-gravity physics.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class DisableLowGravityPhysicsCommand(Command):
    """
    Command which disables low-gravity physics
    """
    name = 'Disable Low-Gravity Physics'
    description = 'Switches Mario back to normal physics.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class UnlockInactiveCharacterCommand(Command):
    """
    Command which causes the inactive character to become
    unlocked.
    """
    name = 'Unlock Inactive Character'
    description = 'Causes the inactive character to be able to move.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class SetPlayersFacingScreenCommand(Command):
    """
    Command which causes all players to face the screen
    """
    name = 'Set Players Facing Screen'
    description = 'Causes all of the players to face the screen.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class LoadAndPlacePeachCommand(Command):
    """
    Command which loads Peach and places her at a particular
    location
    """
    name = 'Load and Place Peach'
    description = 'Loads Peach and positions her at a given location.'

    def __init__(self):
        super().__init__()

        self.widgets = []

        W = HexSpinBox(8)
        W.setMaximum(0xFFFFFFFF)
        self.widgets.append(('X:', W))

        W = HexSpinBox(8)
        W.setMaximum(0xFFFFFFFF)
        self.widgets.append(('Y:', W))

        self.generateLayout()

    @classmethod
    def fromData(cls, data):
        cmd = cls()
        x, y = struct.unpack_from('<xxII', data)
        cmd.widgets[0][1].setValue(x)
        cmd.widgets[1][1].setValue(y)
        return cmd

    def asData(self):
        x = self.widgets[0][1].value()
        y = self.widgets[1][1].value()
        return struct.pack('<xxII', x, y)

    @property
    def dynamicDescription(self):
        x, y = self.widgets[0][1].value(), self.widgets[1][1].value()
        return f'at position (0x%08X, 0x%08X)' % (x, y)


class PlayCharacterWinAnimationsCommand(Command):
    """
    Command which causes the characters to play their "win"
    animations
    """
    name = 'Play Character Win Animations'
    description = 'Causes the characters to play their "win" animations.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class BeginFireworksCommand(Command):
    """
    Command which begins the fireworks animation
    """
    name = 'Begin Fireworks'
    description = 'Starts the fireworks firing.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class EndFireworksCommand(Command):
    """
    Command which ends the fireworks animation
    """
    name = 'End Fireworks'
    description = 'Stops the fireworks.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class ShowDarknessOverlayCommand(Command):
    """
    Command which causes the wipe at the end
    """
    name = 'Show Darkness Overlay'
    description = 'Causes the wipe behind "The End" to occur.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class ShowTheEndCommand(Command):
    """
    Command which causes "The End" to be displayed
    """
    name = 'Show "The End"'
    description = 'Causes "The End" to be displayed on-screen.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class HideTheEndCommand(Command):
    """
    Command which hides "The End"
    """
    name = 'Hide "The End"'
    description = 'Causes "The End" to be hidden.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class ShowCoinCounterCommand(Command):
    """
    Command which shows the coin counter
    """
    name = 'Show Coin Counter'
    description = 'Displays the coin counter.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class HideCoinCounterCommand(Command):
    """
    Command which hides the coin counter
    """
    name = 'Hide Coin Counter'
    description = 'Hides the coin counter.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


class LoadFileCommand(Command):
    """
    Command which indicates that a file should be loaded
    """
    name = 'Load File'
    description = 'Causes a file to be loaded.'

    def __init__(self):
        super().__init__()

        self.widgets = []

        W = QtWidgets.QSpinBox()
        W.setMaximum(0xFFFF)
        self.widgets.append(('File ID:', W))

        W = QtWidgets.QComboBox()
        W.addItems(NEWER_DS_FILE_SLOTS)
        self.widgets.append(('Slot:', W))

        self.generateLayout()

    @classmethod
    def fromData(cls, data):
        cmd = cls()
        a, b = struct.unpack_from('<HB', data)
        cmd.widgets[0][1].setValue(a)
        cmd.widgets[1][1].setCurrentIndex(b)
        return cmd

    def asData(self):
        return struct.pack('<HB',
            self.widgets[0][1].value(),
            self.widgets[1][1].currentIndex())

    @property
    def dynamicDescription(self):
        return f'to the "{self.widgets[1][1].currentText()}" slot'


class UnloadFileCommand(Command):
    """
    Command which indicates that a file should be unloaded
    """
    name = 'Unload File'
    description = 'Causes a file to be unloaded.'

    def __init__(self):
        super().__init__()

        W = QtWidgets.QComboBox()
        W.addItems(NEWER_DS_FILE_SLOTS)
        self.widgets = [('Slot:', W)]
        self.generateLayout()

    @classmethod
    def fromData(cls, data):
        cmd = cls()
        cmd.widgets[0][1].setCurrentIndex(data[0])
        return cmd

    def asData(self):
        return [self.widgets[0][1].currentIndex()]

    @property
    def dynamicDescription(self):
        return f'from the "{self.widgets[0][1].currentText()}" slot'


class ExitStageCommand(Command):
    """
    Command which causes the stage to be exited
    """
    name = 'Exit Stage'
    description = 'Causes the stage to be exited.'

    def __init__(self):
        super().__init__()
        self.generateLayout()


CommandsById = {
    1:  DelayCommand,
    2:  SwitchSceneCommand,
    3:  FadeLogoInCommand,
    4:  DropLogoCommand,
    5:  FadeToBlackCommand,
    6:  FadeFromBlackCommand,
    7:  FadeToWhiteCommand,
    8:  FadeFromWhiteCommand,
    9:  ShowTextCommand,
    10: HideTextCommand,
    11: SetHeaderTextCommand,
    12: ShowHeaderTextCommand,
    13: HideHeaderTextCommand,
    14: SetBodyTextCommand,
    15: ShowBodyTextCommand,
    16: HideBodyTextCommand,
    17: DisablePlayerControlCommand,
    18: EnablePlayerControlCommand,
    19: EnableLowGravityPhysicsCommand,
    20: DisableLowGravityPhysicsCommand,
    21: UnlockInactiveCharacterCommand,
    22: SetPlayersFacingScreenCommand,
    23: LoadAndPlacePeachCommand,
    24: PlayCharacterWinAnimationsCommand,
    25: BeginFireworksCommand,
    26: EndFireworksCommand,
    27: ShowDarknessOverlayCommand,
    28: ShowTheEndCommand,
    29: HideTheEndCommand,
    30: ShowCoinCounterCommand,
    31: HideCoinCounterCommand,
    32: LoadFileCommand,
    33: UnloadFileCommand,
    34: ExitStageCommand,
    }


def CommandFromData(data):
    """
    Return a command from data
    """
    return CommandsById[data[0]].fromData(data[1:])


class CreditsSequenceBin():
    """
    Class which represents "2848 Credits_Sequence.bin"
    """
    def __init__(self, data=None):
        self.Commands = []
        if data is not None: self._initFromData(data)

    def _initFromData(self, data):
        """
        Initialise the CreditsSequenceBin from raw file data
        """

        # No headers. Iterate over the data until we've reached the EOF
        # command
        commands = []
        i = 0
        while True:
            # Get the command data
            datalen = data[i] - 1
            i += 1
            comdata = data[i:i+datalen]
            i += datalen

            if comdata[0] == 0: break

            # Make a command
            commands.append(CommandFromData(comdata))

        # Assign to self.commands
        self.Commands = commands


    def save(self):
        """
        Convert self.commands to bytes that can be saved
        """
        data = []

        coms = list(self.Commands)

        for com in coms:
            comdata = list(com.asData())
            while (len(comdata) + 2) % 4:
                comdata.append(0)
            data.append(len(comdata) + 2)

            for id, comType in CommandsById.items():
                if isinstance(com, comType):
                    data.append(id)
                    break
            else:
                raise ValueError(f'Could not find ID of command: {com}')

            for itm in comdata:
                if not isinstance(itm, int):
                    raise RuntimeError(f'{itm} is not an integer')
                data.append(itm)

        data.extend([2, 0]) # null command
        return bytes(data)



################################################################
################################################################
################################################################
######################### UI Classes ###########################


class HexSpinBox(QtWidgets.QDoubleSpinBox):
    """
    https://stackoverflow.com/a/34922919/4718769
    Only subclasses from QDoubleSpinBox to avoid the signed-integer
    limit. This very much only accepts integer values.
    """

    def __init__(self, length=8, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.length = length

        regex = QtCore.QRegExp(f'[0-9A-Fa-f]{{1,{length}}}')
        regex.setCaseSensitivity(Qt.CaseInsensitive)
        self.hexvalidator = QtGui.QRegExpValidator(regex, self)

    def validate(self, text, pos):
        return self.hexvalidator.validate(text, pos)

    def valueFromText(self, text):
        return int(text, 16)

    def textFromValue(self, value):
        return f'%0{self.length}X' % int(value)

    def value(self, *args, **kwargs):
        return int(super().value(*args, **kwargs))


class CreditsViewer(QtWidgets.QWidget):
    """
    Widget that allows you to view credits data
    """

    class DNDPicker(QtWidgets.QListWidget):
        """
        A list widget that emits a signal when an item has been moved
        """
        itemDropped = QtCore.pyqtSignal()

        def dropEvent(self, event):
            super().dropEvent(event)
            self.itemDropped.emit()

    def __init__(self):
        super().__init__()
        self.file = None

        # Create the command picker widgets
        PickerBox = QtWidgets.QGroupBox('Commands')
        self.picker = self.DNDPicker(self)
        self.picker.setDragDropMode(self.picker.InternalMove)
        self.picker.itemDropped.connect(self.handleDragDrop)
        self.picker.setMinimumWidth(384)
        self.ABtn = QtWidgets.QPushButton('Add')
        self.RBtn = QtWidgets.QPushButton('Remove')

        # Add some tooltips
        self.ABtn.setToolTip('<b>Add:</b><br>Adds a command after the currently selected command')
        self.RBtn.setToolTip('<b>Remove:</b><br>Removes the currently selected command')

        # Connect them to handlers
        self.picker.currentItemChanged.connect(self.handleComSel)
        self.ABtn.clicked.connect(self.handleAdd)
        self.RBtn.clicked.connect(self.handleRemove)

        # Disable them for now
        self.picker.setEnabled(False)
        self.ABtn.setEnabled(False)
        self.RBtn.setEnabled(False)

        # Set up the QGroupBox layout
        L = QtWidgets.QGridLayout()
        L.addWidget(self.picker, 0, 0, 1, 2)
        L.addWidget(self.ABtn, 1, 0)
        L.addWidget(self.RBtn, 1, 1)
        PickerBox.setLayout(L)

        # Create the command editor
        self.ComBox = QtWidgets.QGroupBox('Command')
        self.edit = CommandEditor()
        self.edit.dataChanged.connect(self.handleComDatChange)
        L = QtWidgets.QVBoxLayout()
        L.addWidget(self.edit)
        self.ComBox.setLayout(L)

        # Make the main layout
        L = QtWidgets.QHBoxLayout()
        L.addWidget(PickerBox)
        L.addWidget(self.ComBox)
        self.setLayout(L)

    # Ideally, we could just set the corresponding Command to each
    # QListWidgetItem's UserRole data. And that worked in old versions
    # of PyQt. Now, however, PyQt pickles the data upon starting a drag,
    # and Commands can't be pickled because they have widgets in their
    # attributes. Therefore, we have to maintain our own
    # item <-> command map that works even if an item is pickled and
    # unpickled. To do this, we set its UserRole data to a random UUID
    # that matches an attribute of its corresponding command. Then we
    # use that as the basis for associations between the two.

    _itemCommandMap = None
    def commandForItem(self, item):
        if self._itemCommandMap is None:
            self._itemCommandMap = {}
        return self._itemCommandMap.get(item.data(Qt.UserRole))
    def setCommandForItem(self, item, command):
        if self._itemCommandMap is None:
            self._itemCommandMap = {}
        item.setData(Qt.UserRole, command.uuid)
        self._itemCommandMap[command.uuid] = command

    def setFile(self, file):
        """
        Change the file to view
        """
        self.file = file
        self.picker.clear()
        self.setComEdit(CommandEditor()) # clears it

        # Enable widgets
        self.picker.setEnabled(True)
        self.ABtn.setEnabled(True)
        self.RBtn.setEnabled(False)

        # Add commands
        for com in file.Commands:
            item = QtWidgets.QListWidgetItem() # self.updateNames will add the name
            self.setCommandForItem(item, com)
            self.picker.addItem(item)

        self.updateNames()

    def saveFile(self):
        """
        Return the file in saved form
        """
        return self.file.save() # self.file does this for us

    def updateNames(self):
        """
        Update item names in the command picker
        """

        # This is apparently the best way to iterate over all items in
        # the list widget.
        for item in self.picker.findItems('', Qt.MatchContains):
            com = self.commandForItem(item)

            # Pick text and tooltips
            text = com.name
            tooltip = f'<b>{com.name}:</b><br>{com.description}'

            if com.dynamicDescription:
                text += f' ({com.dynamicDescription})'

            # Set text
            item.setText(text)
            item.setToolTip(tooltip)

    def handleDragDrop(self):
        """
        Handle dragging and dropping
        """
        # First, update the file
        newCommands = []
        for item in self.picker.findItems('', Qt.MatchContains):
            com = self.commandForItem(item)
            newCommands.append(com)
        self.file.Commands = newCommands

        # Then, update the names
        self.updateNames()

    def handleComDatChange(self):
        """
        Handle changes to the current message data
        """
        self.updateNames()

    def handleComSel(self):
        self.setComEdit(CommandEditor()) # clears it

        # Get the current item (it's None if nothing's selected)
        currentItem = self.picker.currentItem()

        # Update the Remove btn
        self.RBtn.setEnabled(currentItem is not None)

        # Get the command
        if currentItem is None: return
        com = self.commandForItem(currentItem)

        # Set up the command editor
        e = CommandEditor(com)
        self.setComEdit(e)

    def handleAdd(self):
        """
        Handle the user clicking Add
        """
        comT = getUserPickedCommand()
        if comT is None: return
        com = comT()

        # Add it to self.file and self.picker
        self.file.Commands.append(com)
        item = QtWidgets.QListWidgetItem()
        self.setCommandForItem(item, com)
        self.picker.addItem(item)
        self.picker.scrollToItem(item)
        item.setSelected(True)

        self.updateNames()

    def handleRemove(self):
        """
        Handle the user clicking Remove
        """
        item = self.picker.currentItem()
        com = self.commandForItem(item)

        # Remove it from file and the picker
        self.file.Commands.remove(com)
        self.picker.takeItem(self.picker.row(item))

        # Clear the selection
        self.setComEdit(CommandEditor())
        self.picker.clearSelection()
        self.picker.setCurrentItem(None)
        self.RBtn.setEnabled(False)

        self.updateNames()

    def setComEdit(self, e):
        """
        Change the current CommandEditor
        """
        x = self.ComBox.layout().takeAt(0)
        if x is not None: x.widget().delete()

        self.ComBox.layout().addWidget(e)
        e.dataChanged.connect(self.handleComDatChange)
        self.ComBox.update()



# NOTE: Due to Qt's limitations, this works differently
# than it did in my other tools. A new instance of this
# is created every time the selection changes.
class CommandEditor(QtWidgets.QWidget):
    """
    Widget that allows you to edit a command
    """
    dataChanged = QtCore.pyqtSignal()

    def __init__(self, com=None):
        super().__init__()
        self.com = Command() if com is None else com

        # Set the layout
        self.setLayout(self.com.layout)
        self.setMinimumWidth(384)

        # Connect each widget to the handler
        for i in range(self.com.layout.count()):
            w = self.com.layout.itemAt(i).widget()

            connectors = {
                QtWidgets.QCheckBox: 'stateChanged',
                QtWidgets.QComboBox: 'currentIndexChanged',
                QtWidgets.QDoubleSpinBox: 'valueChanged',
                QtWidgets.QLineEdit: 'textEdited',
                QtWidgets.QPlainTextEdit: 'textChanged',
                QtWidgets.QSpinBox: 'valueChanged',
                }
            for type, name in connectors.items():
                if isinstance(w, type):
                    getattr(w, name).connect(self.handleDataChanged)


    def delete(self):
        """
        Prepare to be deleted
        """
        self.hide()


    def handleDataChanged(self):
        """
        Handle data changes
        """
        self.dataChanged.emit()


def getNullLayout():
    """
    Return a layout with only "No settings"
    """
    NA = QtWidgets.QLabel('<i>No settings</i>')
    NA.setEnabled(False)
    L = QtWidgets.QVBoxLayout()
    L.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    L.addWidget(NA)
    return L


def getUserPickedCommand():
    """
    Return a command picked by the user
    """
    dlg = CommandPickDlg()
    if dlg.exec_() != dlg.Accepted: return

    return dlg.combo.itemData(dlg.combo.currentIndex())


class CommandPickDlg(QtWidgets.QDialog):
    """
    Dialog that lets the user pick a command type
    """
    def __init__(self):
        super().__init__()

        label = QtWidgets.QLabel('Choose a command type to insert:')

        # Make a combobox and add entries
        entries = [v for k, v in sorted(CommandsById.items(), key=lambda itm: itm[0])]

        self.combo = QtWidgets.QComboBox()
        items = []
        for com in entries:
            self.combo.addItem(com.name, com)

        # Make a buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # Add a layout
        L = QtWidgets.QVBoxLayout()
        L.addWidget(label)
        L.addWidget(self.combo)
        L.addWidget(buttonBox)
        self.setLayout(L)


################################################################
################################################################
################################################################
######################### Main Window ##########################


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.fp = None # file path

        # Create the viewer
        self.view = CreditsViewer()
        self.setCentralWidget(self.view)

        # Create the menubar and a few actions
        self.createMenubar()

        # Set window title and show the window
        self.setWindowTitle('Newer DS Credits Editor')
        self.show()

    def createMenubar(self):
        """
        Sets up the menubar
        """
        m = self.menuBar()

        # File Menu
        f = m.addMenu('&File')

        newAct = f.addAction('New File...')
        newAct.setShortcut('Ctrl+N')
        newAct.triggered.connect(self.handleNew)

        openAct = f.addAction('Open File...')
        openAct.setShortcut('Ctrl+O')
        openAct.triggered.connect(self.handleOpen)

        self.saveAct = f.addAction('Save File')
        self.saveAct.setShortcut('Ctrl+S')
        self.saveAct.triggered.connect(self.handleSave)
        self.saveAct.setEnabled(False)

        self.saveAsAct = f.addAction('Save File As...')
        self.saveAsAct.setShortcut('Ctrl+Shift+S')
        self.saveAsAct.triggered.connect(self.handleSaveAs)
        self.saveAsAct.setEnabled(False)

        f.addSeparator()

        exitAct = f.addAction('Exit')
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(self.handleExit)

        # Help Menu
        h = m.addMenu('&Help')

        aboutAct= h.addAction('About...')
        aboutAct.setShortcut('Ctrl+H')
        aboutAct.triggered.connect(self.handleAbout)


    def handleNew(self):
        """
        Handle creating a new file
        """
        f = CreditsSequenceBin()
        self.view.setFile(f)
        self.saveAsAct.setEnabled(True)

    def handleOpen(self):
        """
        Handle file opening
        """
        fp = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '', 'Binary Files (*.bin);;All Files (*)')[0]
        if fp == '': return
        self.fp = fp

        # Open the file
        with open(fp, 'rb') as f:
            data = f.read()

        M = CreditsSequenceBin(data)

        # Update the viewer with this data
        self.view.setFile(M)

        # Enable saving
        self.saveAct.setEnabled(True)
        self.saveAsAct.setEnabled(True)

    def handleSave(self):
        """
        Handle file saving
        """
        data = self.view.saveFile()

        try:
            with open(self.fp, 'wb') as f:
                f.write(data)
        except OSError as e:
            QtWidgets.QMessageBox.warning(
                self,
                'Unable to Save',
                f'There was an error while trying to save "{self.fp}".'
                f' (Specifically, "OSError: {e}".)\n'
                '\n'
                'If the file is open in another program, close that program and try again.'
                ' Otherwise, use Save As to save your work somewhere else.',
                )

    def handleSaveAs(self):
        """
        Handle saving to a new file
        """
        fp = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '', 'Binary Files (*.bin);;All Files (*)')[0]
        if fp == '': return
        self.fp = fp

        # Save it
        self.handleSave()

        # Enable saving
        self.saveAct.setEnabled(True)

    def handleExit(self):
        """
        Exit the editor
        """
        raise SystemExit

    def handleAbout(self):
        """
        Show the About dialog
        """
        try:
            with open('readme.md', 'r', encoding='utf-8') as f:
                readme = f.read()
        except FileNotFoundError:
            readme = f'Newer DS Credits Editor {version} by RoadrunnerWMC\n(No readme.md found!)\nLicensed under GNU GPL v3'

        txtedit = QtWidgets.QPlainTextEdit(readme)
        txtedit.setReadOnly(True)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(txtedit)
        layout.addWidget(buttonBox)

        dlg = QtWidgets.QDialog()
        dlg.setLayout(layout)
        dlg.setModal(True)
        dlg.setMinimumWidth(384)
        buttonBox.accepted.connect(dlg.accept)
        dlg.exec_()


################################################################
################################################################
################################################################
############################ main() ############################


def main(argv):
    """
    Main startup function
    """
    app = QtWidgets.QApplication(argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__': main(sys.argv)
