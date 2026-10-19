from pathlib import Path

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.uic import loadUi

from ..fonctions import affiche_doc_pluginsmanager
from ..constantes import TITRE

class DlgAProposDe(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_file = Path(__file__).parent.parent / "ui" / "aproposde.ui"
        loadUi(str(ui_file), self)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle(TITRE)
        self.label_suivi_version.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.pushButtonAffichedoc.clicked.connect(affiche_doc_pluginsmanager)

