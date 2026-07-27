TITRE = "PluginsManager"
MENU_IGN = "menu IGN "
PREFIXE_PLUGIN_IGN = "IGN_"

COLOR_MAJ = "#FFF176"
COLOR_COMBO = "#bababa"
COLOR_NON_INSTALLE = "#ff6e6e"

PLUGINS_IGN = {
    "IGN DigitizingDirection",
    "IGN ShortestPath",
    "MultiViewManager",
    "IGN_altibonne",
    "IGN_assistant-complexe",
    "IGN_assistant-dfci",
    "IGN_assistant-hydro-national",
    "IGN_assistant-liste",
    "IGN_assistant-odonyme",
    "IGN_assistant-route",
    "IGN_boite_outils",
    "IGN_jeux_attributs",
    "IGN_jeux_attributs_generique",
    "IGN_objets_preferes",
    # "IGN_requetes",
    "IGN_vueZ"
}

DOSSIER_ONGLET = "config_PluginsManager"
# liste des plugins à exclure du menu et de la barre d'outils (ex : plugin sans interface)
# EXCEPT_PLUGIN = ["IGN_Vues"]
EXCEPT_PLUGIN = [""]

PEFILE = ["pefile","pefile-2024.8.26-py3-none-any.whl"]
# DEFUSEDXML = ["defusedxml","defusedxml-0.7.1-py2.py3-none-any.whl"]
# PACKAGES = [PEFILE,DEFUSEDXML]
PACKAGES = [PEFILE]

# 0 : bouton "actualiser/sauvegarder"
# 1 : titre des barres d'outils
# 2 : tabwidget
CUSTOM_WIDGETS = (
    "background-color: #21d847; font-weight: bold;",
    """
    QLabel {background-color: #a9ffa1;font-weight: bold;border: 2px solid #4CAF50;
        border-radius: 8px;
    }
    QLabel:hover {background-color: #70e070;color: #000000}
    """,
    """
    QTabWidget {
    background-color: #f0f0f0;}
    QTabBar::tab {background: #d0d0d0;
        padding-left : 10px;
        margin-right: 5px;
        border: 1px solid #bbb;
        }
    QTabBar::tab:selected {
        background: #37c62f;
        color: black;}
    """
)