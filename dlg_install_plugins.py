
from qgis.PyQt.QtGui import QFont,QBrush, QColor
from qgis.PyQt.QtWidgets import QDialog, QTableWidgetItem
from qgis.PyQt.uic import loadUi

from .fonctions import *
from .plugins_ign import *
from.progressbar import DownloadProgress

class InstallerDialog(QDialog):
    def __init__(self,parent = None):
        super().__init__(parent)

        self.pluginsIGN = PluginsIGN()

        self.dossier_profil = None
        self.dico_plugin_from_xml = {}
        # aucun plugin n’est coché.
        self.ischeck = False

        # Charger le fichier .ui dans cette instance
        ui_file = Path(__file__).parent / "ui" / "installer.ui"
        loadUi(ui_file, self)

        self.pushButton_installer.clicked.connect(self.on_installe_plugin)
        self.pushButton_tout_rien.clicked.connect(self.on_tout_rien)

    def init_aspect_dialog(self):
        self.tablePlugins.clear()
        self.tablePlugins.setRowCount(0)
        self.label_non_installe.setStyleSheet(f"background-color: {COLOR_MAJ}")
        self.pushButton_tout_rien.setStyleSheet("font : bold ;background-color: #00b909; color: black;")
        self.pushButton_installer.setStyleSheet("font : bold ;background-color: #00b909; color: black;")

        self.setWindowFlags(WindowStaysOnTopHint | WindowCloseButtonHint)
        # tablewidget
        self.tablePlugins.horizontalHeader().setStyleSheet(
            "QHeaderView::section { color: white; background-color: #00a108; font-weight: bold; }")
        self.tablePlugins.setSelectionMode(NoSelection)
        self.tablePlugins.setColumnCount(5)
        self.tablePlugins.setHorizontalHeaderLabels(["Plugins disponibles","Dépôt", "Version disponible","Version installée", "Description"])
        self.tablePlugins.setColumnWidth(0, 220)
        self.tablePlugins.setColumnWidth(1, 150)
        self.tablePlugins.setColumnWidth(2, 130)
        self.tablePlugins.setColumnWidth(3, 120)
        self.tablePlugins.setColumnWidth(4, 350)
        self.tablePlugins.horizontalHeader().setStretchLastSection(True)

        self.tablePlugins.verticalHeader().setMinimumSectionSize(1)
        self.tablePlugins.verticalHeader().setDefaultSectionSize(20)

    def remplir_dlg_plugins(self):
        self.tablePlugins.setUpdatesEnabled(False)
        self.tablePlugins.setSortingEnabled(False)
        for depot in ("officiel", "github"):
            for name, infos in self.pluginsIGN.get_plugins_ign_from_depot(depot).items():
                version = infos["version"]
                description = infos["description"]
                version_installe = get_info_plugins_installe(name,"version")

                ligne = self.tablePlugins.rowCount()
                self.tablePlugins.insertRow(ligne)

                # NOM DU PLUGIN
                if version_installe != version:
                    check = "True"
                else:
                    check = "False"
                item_name = self.creer_item(name,check)
                item_name.setData(Qt.UserRole, infos)  # stocke le dictionnaire complet (name, url, version...) dans l'item
                self.tablePlugins.setItem(ligne, 0, item_name)

                # DEPOT
                nom_depot = ""
                if depot == "officiel":
                    nom_depot = "Dépôt officiel (qgis.org)"
                elif depot == "github":
                    nom_depot = "GitHub"
                item_depot = self.creer_item(nom_depot)
                self.tablePlugins.setItem(ligne, 1, item_depot)

                # VERSION DISPONIBLE
                item_version_dispo = self.creer_item(version)
                if version_installe != version:
                    item_version_dispo.setBackground(QBrush(QColor(COLOR_MAJ)))
                self.tablePlugins.setItem(ligne, 2, item_version_dispo)

                # VERSION INSTALLÉE
                item_version_installe = self.creer_item(version_installe)
                self.tablePlugins.setItem(ligne, 3, item_version_installe)

                # DESCRIPTION
                item_descr = self.creer_item(description)
                self.tablePlugins.setItem(ligne, 4, item_descr)
        # rafraichir l'affichage du tableau qu'a la fin du remplissage pour éviter les ralentissements
        self.tablePlugins.setUpdatesEnabled(True)
        self.tablePlugins.setSortingEnabled(True)

    def creer_item(self,texte,check = ""):
        font = QFont()
        font.setBold(True)
        if texte is None:
            item = QTableWidgetItem("Non Installé")
            item.setFont(font)
            item.setBackground(QBrush(QColor(COLOR_NON_INSTALLE)))
            return item

        item = QTableWidgetItem(texte)
        item.setFont(font)
        item.setFlags(item.flags() & ~ItemIsEditable)
        if check == "True":
            item.setCheckState(Checked)
        elif check == "False":
            item.setCheckState(Unchecked)
        else:
            pass
        return item

    def on_tout_rien(self):
        if self.ischeck:
            for row in range(self.tablePlugins.rowCount()):
                item = self.tablePlugins.item(row, 0)  # colonne Nom
                # if self.tablePlugins.item(row, 0).text() != PLUGIN_MAITRE:
                item.setCheckState(Unchecked)
                self.pushButton_tout_rien.setText("Tout sélectionner")
                self.ischeck = False
        else:
            for row in range(self.tablePlugins.rowCount()):
                item = self.tablePlugins.item(row, 0)  # colonne Nom
                item.setCheckState(Checked)
                self.pushButton_tout_rien.setText("Rien sélectionner")
                self.ischeck = True

    def get_plugins_checked(self):
        plugins_checked = []
        for row in range(self.tablePlugins.rowCount()):
            item = self.tablePlugins.item(row, 0)
            if item is not None and item.checkState() == Checked:
                plugin = item.data(Qt.UserRole).copy()  # Récupère le dictionnaire (copie) stocké dans l'item
                plugin["name"] = item.text()  # Ajoute le nom du plugin au dictionnaire
                plugins_checked.append(plugin)
        return plugins_checked

    def on_installe_plugin(self):
        list_plugin_to_install = self.get_plugins_checked()
        if len(list_plugin_to_install) == 0:
            return None
        print(f"Plugins à installer : {list_plugin_to_install}")
        progress = DownloadProgress(self, len(list_plugin_to_install))
        for idx,plugin in enumerate(list_plugin_to_install,start = 1):
            progress.update(idx, f"Téléchargement de : {plugin["name"]}")
            # téléchargement des plugins sous forme de bytes
            plugins_bytes = self.pluginsIGN.download_plugins(plugin['download_url'])

            # écriture physique du zip
            current_directory = os.path.dirname(__file__)
            # Remonter d'un niveau
            parent_directory = os.path.abspath(Path(current_directory, os.pardir))
            chemin_zip = os.path.join(parent_directory, f"{plugin['name']}.zip")
            print(f"Installation du plugin : {plugin['name']}-{chemin_zip}")
            with open(chemin_zip, "wb") as f:
                f.write(plugins_bytes)

            # extraction du zip
            self.pluginsIGN.extract_zip(parent_directory,chemin_zip)

        text = ("Installation terminé\n\n - Veuillez redémarrer QGIS pour prendre\n"
                "en compte les plugins")
        QMessageBox.information(self, "Installateur de plugins", text)
        return progress




