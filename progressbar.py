from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import QProgressDialog
from .constantes import *

class DownloadProgress:
    def __init__(self, parent,progress_bar = None, total=0,label = None,initialisation = False):

        self.label = label

        # dialogue de progression sans barre de progression intégrée, texte permanent
        if initialisation:
            self.dialog = QProgressDialog("Initialisation...",None,0,0,parent)
            self.dialog.setWindowTitle("Plugins IGN")
            self.dialog.setCancelButton(None)
            self.dialog.setMinimumDuration(0)
            self.dialog.setAutoClose(False)
            self.dialog.setAutoReset(False)
            self.progress = self.dialog
            self.dialog.show()

        # progress intégrée à l'interface
        elif progress_bar is not None:
            self.progress = progress_bar
            self.progress.setRange(0,total)
            self.progress.setValue(0)
            self.progress.show()
            self.dialog = None
            self.progress.setStyleSheet(PROGRESS)

        # progress dans la fenêtre indépendante
        else:
            self.dialog = QProgressDialog("Téléchargement en cours...",None, 0, total, parent)
            self.dialog.setAutoClose(False)
            self.dialog.setFixedSize(350, 50)
            self.dialog.show()
            self.progress = self.dialog

        QCoreApplication.processEvents()

    def setTitre(self,titre = ""):
        self.dialog.setWindowTitle(titre)

    def setValue(self, value,libelle = ""):
        self.progress.setValue(value)
        if libelle is not None:
            if self.label is not None:
                self.label.show()
                self.label.setText(libelle)
            elif self.dialog is not None:
                self.dialog.setLabelText(libelle)
        QCoreApplication.processEvents()

    def setLabel(self,libelle):
        if self.label is not None:
            self.label.show()
            self.label.setText(libelle)
        QCoreApplication.processEvents()

    def setClose(self):
        if self.dialog is not None:
            self.dialog.close()
        else:
            self.progress.hide()
        if self.label is not None:
            self.label.hide()
        QCoreApplication.processEvents()


