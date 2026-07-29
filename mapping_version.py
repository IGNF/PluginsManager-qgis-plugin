from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QTabBar,QMessageBox,QAbstractItemView,QListWidget

# QT6
try :
    Dialog = Qt.WindowType.Dialog
    WindowCloseButtonHint = Qt.WindowType.WindowCloseButtonHint
    WindowTitleHint = Qt.WindowType.WindowTitleHint
    WindowStaysOnTopHint = Qt.WindowType.WindowStaysOnTopHint
    WindowModal = Qt.WindowModality.WindowModal
    Checked = Qt.CheckState.Checked
    Unchecked = Qt.CheckState.Unchecked
    ItemIsEnabled = Qt.ItemFlag.ItemIsEnabled
    ItemIsEditable = Qt.ItemFlag.ItemIsEditable
    ItemIsUserCheckable = Qt.ItemFlag.ItemIsUserCheckable
    MatchExactly = Qt.MatchFlag.MatchExactly
    RightSide = QTabBar.ButtonPosition.RightSide
    LeftSide = QTabBar.ButtonPosition.LeftSide
    Warning = QMessageBox.Icon.Warning
    Information = QMessageBox.Icon.Information
    YesRole = QMessageBox.ButtonRole.YesRole
    NoRole = QMessageBox.ButtonRole.NoRole
    RejectRole = QMessageBox.ButtonRole.RejectRole
    AcceptRole = QMessageBox.ButtonRole.AcceptRole
    NoSelection = QAbstractItemView.SelectionMode.NoSelection
    AlignCenter = Qt.AlignmentFlag.AlignCenter
# QT5
except :
    Dialog = Qt.Dialog
    WindowCloseButtonHint = Qt.WindowCloseButtonHint
    WindowTitleHint = Qt.WindowTitleHint
    WindowStaysOnTopHint = Qt.WindowStaysOnTopHint
    WindowModal = Qt.WindowModal
    Checked = Qt.Checked
    Unchecked = Qt.Unchecked
    ItemIsEnabled = Qt.ItemIsEnabled
    ItemIsEditable = Qt.ItemIsEditable
    ItemIsUserCheckable = Qt.ItemIsUserCheckable
    MatchExactly = Qt.MatchFlag.MatchExactly
    RightSide = QTabBar.RightSide
    LeftSide = QTabBar.LeftSide
    Warning = QMessageBox.Warning
    Information = QMessageBox.Information
    YesRole = QMessageBox.YesRole
    NoRole = QMessageBox.NoRole
    RejectRole = QMessageBox.RejectRole
    AcceptRole = QMessageBox.AcceptRole
    NoSelection = QListWidget.NoSelection
    AlignCenter = Qt.AlignCenter