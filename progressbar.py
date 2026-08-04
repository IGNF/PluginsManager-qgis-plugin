from qgis.PyQt.QtCore import Qt,QCoreApplication
from qgis.PyQt.QtWidgets import QProgressDialog

from .mapping_version import *

class DownloadProgress:
    def __init__(self, parent, total=0,titre = ""):
        self.progress = QProgressDialog("Téléchargement en cours...", None, 0, total, parent)
        self.progress.setWindowTitle(titre)
        self.progress.setWindowModality(WindowModal)
        self.progress.setWindowFlags(self.progress.windowFlags() | WindowStaysOnTopHint)
        self.progress.setMinimumDuration(0)  # Affiche immédiatement
        self.progress.setValue(0)
        self.progress.show()
        QCoreApplication.processEvents()

    def update(self, current, label=""):
        """Met à jour la barre avec l’index courant """
        self.progress.setValue(current)
        if label:
            self.progress.setLabelText(f"{label}")
        self.progress.repaint()
        QCoreApplication.processEvents()

    def getMaximum(self):
        return self.progress.maximum()

    def setlabel(self, label):
        self.progress.setLabelText(label)
        QCoreApplication.processEvents()

    def close(self):
        self.progress.close()
        QCoreApplication.processEvents()

