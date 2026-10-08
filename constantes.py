import os
from pathlib import Path

from qgis.PyQt.QtCore import QUrl

TITRE = "PluginsManager"
# sert à filtrer les plugins IGN des autres
PREFIXE_PLUGIN_IGN = "IGN "

TAILLE_DLG_SANS_ONGLET = 150
TAILLE_DLG_AVEC_ONGLET = 400

COLOR_MAJ = "#FFF176"
# COLOR_COMBO = "#bababa"
COLOR_NON_INSTALLE = "#99b9bc"
COLOR_HORS_PROFIL = "#f2f2f2"

URL_QGIS = "https://plugins.qgis.org"
REP_PLUGIN_GITHUB = f"https://raw.githubusercontent.com/IGNF/collaboratif-plugins/main/"
URL_PLUGINS_GITHUB = f"https://raw.githubusercontent.com/IGNF/collaboratif-plugins/main/all_plugins.xml"
URL_PROFIL_GITHUB = f"https://raw.githubusercontent.com/IGNF/collaboratif-plugins/main/profils.json"

ICON_INSTALL = Path(os.path.dirname(__file__)) / "icons" / "install_plugins.png"
ICON_NEW = Path(os.path.dirname(__file__)) / "icons" / "new_version.png"

DOSSIER_ONGLET = "config_PluginsManager"
XML_PLUGINS_COCHE_TOOLBAR = "tabwidget.xml"
PATH_PROFIL_ACTIF = Path(os.path.dirname(__file__), DOSSIER_ONGLET, "profil_actif.json")
# liste des plugins avec prefixe "IGN " à exclure du menu et de la barre d'outils
EXCEPT_PLUGIN = ["IGN PluginsManager"]
# plugins à prendre en compte même sans prefixe "IGN ", juste pour afficher la doc dans le menu IGN
PLUGINS_HORS_IGN = ["MultiViewManager"]

PLUGIN_VERSION = "version"
PLUGIN_REP = "repertoire"
PLUGIN_LIEN_DOC = "lien_doc"
PLUGIN_ICON = "icon"

# PEFILE = ["pefile","pefile-2024.8.26-py3-none-any.whl"]
# DEFUSEDXML = ["defusedxml","defusedxml-0.7.1-py2.py3-none-any.whl"]
# PACKAGES = [PEFILE,DEFUSEDXML]
# PACKAGES = [PEFILE]

# 0 : bouton "enregistrer les modifications"
# 1 : titre des barres d'outils
# 2 : tabwidget
# 3 : titre
# 4 : Qtablewidget
CUSTOM_WIDGETS = (
    "color:#FFFFFF;background-color: #486554; font-weight: bold;",

    "background-color: #a9ffa1;border: 2px solid #4CAF50;border-radius: 8px;font-weight: bold; ",

    """QTabWidget {background-color: #f0f0f0;}
    QTabBar::tab {background: #d0d0d0;padding-left : 10px;margin-right: 5px;border: 1px solid #bbb;}
    QTabBar::tab:selected {background: #5a7e69;color: #FFFFFF;}""",

"   font-weight: bold;background-color:  #cad0d7;border: 1px solid black;border-radius: 5px;padding: 2px;font-size: 20px;",

    "QHeaderView::section { font-size: 10pt ;font-weight: bold;background-color:  #a0a5ab }",

)

PROGRESS = """
    QProgressBar {
        border: 1px solid palette(mid);
        border-radius: 3px;
        background: palette(base);
        text-align: center;
        height: 16px;
    }

    QProgressBar::chunk {
        background: palette(highlight);
        border-radius: 2px;
    }
"""