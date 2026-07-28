import os
import webbrowser
from pathlib import Path

from qgis.core import QgsApplication
from .mapping_version import *
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
    msg.setWindowFlags(WindowStaysOnTopHint | WindowCloseButtonHint)
    msg.exec()

def affichemessageAvertissement( titre, text):
    msg = QMessageBox()
    msg.setIcon(Warning)

    msg.setWindowTitle(titre)
    msg.setText(text)
    btnAnnuler = msg.addButton("Annuler", YesRole)
    btnAnnuler.setStyleSheet("color:red ; font-weight: bold")
    btnValider = msg.addButton("Supprimer", AcceptRole)
    btnValider.setStyleSheet("color:green ; font-weight: bold")
    msg.setWindowFlags(WindowStaysOnTopHint | WindowCloseButtonHint)
    msg.exec()
    if msg.clickedButton() == btnAnnuler:
        return False
    if msg.clickedButton() == btnValider:
        return True
    return None

def afficheDoc():
    webbrowser.open("https://ignf.github.io/PluginsManager-qgis-plugin/")


def get_info_plugins_installe(plugin_name,info):
    rep_plugin_qgis  = QgsApplication.qgisSettingsDirPath() + "python/plugins/"
    plugin_name = plugin_name.replace("IGN ", PREFIXE_PLUGIN_IGN)
    fic_metadata = os.path.join(rep_plugin_qgis, plugin_name, "metadata.txt")
    if os.path.exists(fic_metadata):
        with open(fic_metadata, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{info}="):
                    return line.strip().split("=")[1]
    return None

# def load_profils_json():
#     url = QUrl(f"https://raw.githubusercontent.com/IGNF/collaboratif-plugins/main/profils.json?nocache=1")
#     with open(url, "r", encoding="utf-8") as f:
#         profils = json.load(f)
#     return profils
