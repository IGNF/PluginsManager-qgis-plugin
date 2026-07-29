import shutil

from qgis.PyQt.QtGui import QFont,QBrush, QColor
from qgis.PyQt.QtWidgets import QDialog, QTableWidgetItem
from qgis.PyQt.uic import loadUi

import json


from .fonctions import *
from .plugins_ign import *
from.progressbar import DownloadProgress

class InstallerDialog(QDialog):
    def __init__(self,parent = None):
        super().__init__(parent)

        self.profil_actif = None
        self.pluginsIGN = PluginsIGN()

        # self.dossier_profil = None
        self.dico_plugin_from_xml = {}
        # aucun plugin n’est coché.
        self.ischeck = False

        current_directory = os.path.dirname(__file__)
        # Remonter d'un niveau
        self.parent_directory = os.path.abspath(Path(current_directory, os.pardir))

        self._plugin_to_suppr = []

        # Charger le fichier .ui dans cette instance
        ui_file = Path(__file__).parent / "ui" / "installer.ui"
        loadUi(ui_file, self)

        self.pushButton_installer.clicked.connect(self.on_installe_plugin)
        self.comboBox_profils.currentIndexChanged.connect(self.on_profil_changed)

    def init_aspect_dialog(self):
        self.tablePlugins.clear()
        self.tablePlugins.setRowCount(0)
        self.label_non_installe.setStyleSheet(f"background-color: {COLOR_MAJ}")
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

        self.init_combo_profils()
        self.load_profil_actif()

    def init_combo_profils(self):
        self.comboBox_profils.blockSignals(True) # bloquer le signal car additem emet currentIndexChanged
        self.comboBox_profils.clear()
        # contenu = self.pluginsIGN.load_fichier("profils")
        contenu = self.pluginsIGN.load_fichier(URL_PROFIL_GITHUB)
        self.list_profils = json.loads(contenu.decode("utf-8"))
        for profil,fichier in self.list_profils.items():
            self.comboBox_profils.addItem(profil,fichier)
        self.comboBox_profils.blockSignals(False)
        self.comboBox_profils.setStyleSheet("""
        QComboBox {
            font-weight: bold;
            color: red;
        }
        """)


    def remplir_dlg_plugins(self):
        self.tablePlugins.setUpdatesEnabled(False)
        self.tablePlugins.setSortingEnabled(False)
        # construction de l'url pour le profil actif
        list_plugins_profil = self.get_plugins_profil()

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
                # si le plugin n'est pas dans la liste des plugins du profil actif on le grise
                if name not in list_plugins_profil:
                    item_name.setBackground(QBrush(QColor(200, 200, 200)))
                    item_name.setCheckState(Unchecked)
                    item_name.setFlags(item_name.flags() & ~Qt.ItemIsUserCheckable & ~Qt.ItemIsEnabled)
                    # formatage pour retrouver les dossiers de la forme "IGN_"
                    self._plugin_to_suppr.append(Path(self.parent_directory,name.replace("IGN ","IGN_")))
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
        self.tablePlugins.sortItems(0, Qt.AscendingOrder)

    def on_profil_changed(self,index):
        self._plugin_to_suppr.clear()
        texte = self.comboBox_profils.itemText(index)
        valeur = self.comboBox_profils.itemData(index)
        nouveau_profil = {'nom': texte,'fichier': valeur}
        # si pas de changement on reecrit pas le fichier
        if nouveau_profil == self.profil_actif:
            return
        self.profil_actif = nouveau_profil

        # sauvegarde du profil actif
        with open(PATH_PROFIL_ACTIF,"w",encoding="utf-8") as f:
            json.dump( self.profil_actif, f, indent=4, ensure_ascii=False)



        self.tablePlugins.clearContents()
        self.tablePlugins.setRowCount(0)
        self.remplir_dlg_plugins()

    def get_plugins_profil(self):
        if self.profil_actif is None:
            return []
        # recuperation de la liste des plugins correspondant au profil actif
        fic_xml = self.profil_actif['fichier']
        url = REP_PLUGIN_GITHUB.resolved(QUrl(fic_xml)) # construction de l'url
        xml = self.pluginsIGN.load_fichier(url)

        list_plugins = []
        root = ET.fromstring(xml)
        for plugin in root.findall("pyqgis_plugin"):
            list_plugins.append(plugin.attrib.get("name"))
        return list_plugins


    def load_profil_actif(self):
        if os.path.exists(PATH_PROFIL_ACTIF):
            with open(PATH_PROFIL_ACTIF, "r", encoding="utf-8") as f:
                self.profil_actif = json.load(f)
        else:
            # profil par défaut = premier profil du combobox si le fichier n'existe pas
            # cas de la premiere ouverture
            self.profil_actif = {
                "nom": self.comboBox_profils.itemText(0),
                "fichier": self.comboBox_profils.itemData(0)
            }
        # changement du combobox en fonction du profil actif
        self.comboBox_profils.blockSignals(True)
        self.comboBox_profils.setCurrentText(self.profil_actif['nom'])
        self.comboBox_profils.blockSignals(False)


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

    def get_plugins_checked(self):
        plugins_checked = []
        for row in range(self.tablePlugins.rowCount()):
            item = self.tablePlugins.item(row, 0)
            if item is not None and item.checkState() == Checked:
                plugin = item.data(Qt.UserRole).copy()  # Récupère le dictionnaire (copie) stocké dans l'item
                plugin["name"] = item.text()  # Ajoute le nom du plugin au dictionnaire
                plugins_checked.append(plugin)
        return plugins_checked

    def confirme_suppr(self,plugins):
        list_dossier_plugins = []
        for plugin in plugins:
            list_dossier_plugins.append(Path(plugin).name)

        msg = QMessageBox(self)
        msg.setWindowTitle("Installation...")
        msg.setIcon(Information)
        msg.setText(f"Plugins non inclus dans le profil souhaité :")
        msg.setInformativeText("\n".join(list_dossier_plugins))
        btn_supprimer = msg.addButton("-Installer les plugins cochés\n -Supprimer les plugins ci-dessus", YesRole)
        btn_conserver = msg.addButton("-Installer les plugins cochés\n -Garder les plugins ci-dessus", NoRole)
        btn_annuler = msg.addButton("Annuler", RejectRole)
        msg.setDefaultButton(btn_annuler)
        msg.exec()
        if msg.clickedButton() == btn_supprimer:
            return "supprimer"
        if msg.clickedButton() == btn_conserver:
            return "conserver"
        if msg.clickedButton() == btn_annuler:
            return "annuler"
        return None

    def on_installe_plugin(self):
        list_plugin_to_install = self.get_plugins_checked()
        if len(list_plugin_to_install) == 0:
            QMessageBox.warning(self,"Avertissement","Aucun plugin n'est sélectionné.")
            return None

        for plugin in self._plugin_to_suppr:
            # rep_plugin = Path(self.parent_directory, plugin)
            if not plugin.exists():
                # si le plugin n'est pas installé, pas la peine de supprimer, on retire donc de la liste
                if plugin in self._plugin_to_suppr:
                    self._plugin_to_suppr.remove(plugin)

        reponse = self.confirme_suppr(self._plugin_to_suppr)
        if reponse == "annuler":
            return None
        if reponse == "supprimer":
            for dossier in self._plugin_to_suppr:
                try:
                    shutil.rmtree(dossier)
                except Exception as e:
                    print(f"Erreur lors de la suppression de {dossier} : {e}")
        if reponse == "conserver":
            pass

        progress = DownloadProgress(self, len(list_plugin_to_install))
        for idx,plugin in enumerate(list_plugin_to_install,start = 1):
            progress.update(idx, f"Téléchargement de : {plugin["name"]}")
            # téléchargement des plugins sous forme de bytes
            plugins_bytes = self.pluginsIGN.download_plugins(plugin['download_url'])

            # écriture physique du zip
            chemin_zip = os.path.join(self.parent_directory, f"{plugin['name']}.zip")
            with open(chemin_zip, "wb") as f:
                f.write(plugins_bytes)

            # extraction du zip
            self.pluginsIGN.extract_zip(self.parent_directory,chemin_zip)

        text = ("Installation terminée\n\n - Veuillez redémarrer QGIS pour prendre\n"
                "en compte les plugins")
        QMessageBox.information(self, "Installation des plugins", text)
        return progress




