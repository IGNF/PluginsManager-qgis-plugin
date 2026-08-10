import webbrowser
from configparser import ConfigParser

from qgis.PyQt.uic import loadUi
from qgis.PyQt.QtWidgets import QMessageBox,QDialog
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsApplication
from .constantes import *

def log(message,reset=False):
    """
    Écrit un message dans le fichier de log avec un horodatage.
    Le fichier est ouvert en mode append pour ne pas écraser les données.
    """
    current_directory = os.path.dirname(__file__)
    # Remonter d'un niveau
    parent_directory = os.path.abspath(Path(current_directory, os.pardir))
    fichier = Path(parent_directory, "log_PluginsManager.txt")
    mode = "w" if reset else "a"  # "w" pour écraser, "a" pour ajouter
    with open(fichier, mode, encoding="utf-8") as f:
        f.write(f"{message}\n")

def affiches_spec_bdtopo():
    webbrowser.open("https://bdtopoexplorer.ign.fr/")

def afficheerreur(titre,text):
    msg = QMessageBox()
    msg.setWindowTitle(titre)
    msg.setText(text)
    msg.setIcon(Warning)
    msg.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowCloseButtonHint)
    msg.exec()

def affichemessageAvertissement( titre, text):
    msg = QMessageBox()
    msg.setIcon(Warning)

    msg.setWindowTitle(titre)
    msg.setText(text)
    btnAnnuler = msg.addButton("Annuler", QMessageBox.ButtonRole.YesRole)
    btnAnnuler.setStyleSheet("color:red ; font-weight: bold")
    btnValider = msg.addButton("Supprimer", QMessageBox.ButtonRole.AcceptRole)
    btnValider.setStyleSheet("color:green ; font-weight: bold")
    msg.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowCloseButtonHint)
    msg.exec()
    if msg.clickedButton() == btnAnnuler:
        return False
    if msg.clickedButton() == btnValider:
        return True
    return None

def afficheDoc():
    webbrowser.open("https://ignf.github.io/PluginsManager-qgis-plugin/")


# ==================================================
# ouverture du dialogue "à propos de..."
def apropos(self):
    dlgAProposDe = QDialog()
    ui_file = Path(__file__).parent / "ui" / "aproposde.ui"
    loadUi(ui_file, dlgAProposDe)
    dlgAProposDe.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
    dlgAProposDe.setWindowTitle(f"{TITRE}")
    dlgAProposDe.pushButtonAffichedoc.clicked.connect(afficheDoc)
    dlgAProposDe.exec()

