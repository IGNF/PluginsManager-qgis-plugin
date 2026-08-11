import shutil

from qgis.PyQt.QtGui import QFont,QBrush, QColor,QIcon,QPixmap
from qgis.PyQt.QtWidgets import QDialog,QAbstractItemView,QTableWidgetItem

import json

from .fonctions import *
from .plugins_ign import *
from .progressbar import DownloadProgress

class InstallerDialog(QDialog):
    def __init__(self,plugin_maitre,parent = None):
        super().__init__(parent)

        self.list_profils = None
        self.plugin_maitre = plugin_maitre
        self.profil_actif = None
        self.pluginsIGN = PluginsIGN()

        current_directory = os.path.dirname(__file__)
        # Remonter d'un niveau
        self.parent_directory = os.path.abspath(Path(current_directory, os.pardir))

        self._plugin_to_suppr = []

        # Charger le fichier .ui dans cette instance
        ui_file = Path(__file__).parent / "ui" / "installer.ui"
        loadUi(ui_file, self)

        self.label_progress.hide()
        self.progressBar.hide()

        self.pushButton_installer.clicked.connect(self.on_installe_plugin)
        self.comboBox_profils.currentIndexChanged.connect(self.on_profil_changed)

    def init_aspect_dialog(self):
        self.tablePlugins.clear()
        self.tablePlugins.setRowCount(0)
        self.label_non_installe.setStyleSheet(f"background-color: {COLOR_MAJ}")
        self.label_hors_profil.setStyleSheet(f"background-color: {COLOR_HORS_PROFIL}")
        self.pushButton_installer.setStyleSheet("font : bold ;background-color: #00b909; color: black;")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        # tablewidget
        self.tablePlugins.horizontalHeader().setStyleSheet(
            "QHeaderView::section { color: white; background-color: #00a108; font-weight: bold; }")
        self.tablePlugins.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
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
        self.comboBox_profils.blockSignals(True) # bloquer le signal car "additem" emet currentIndexChanged
        self.comboBox_profils.clear()
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

        nb_plugins = sum(
            len(self.pluginsIGN.get_plugins_ign_from_depot(depot))
            for depot in ("officiel", "github")
        )
        # progress = DownloadProgress(self,None, nb_plugins,"Initialisation de la liste des plugins")
        progress = DownloadProgress(parent=self,
                                    progress_bar=None,
                                    total=nb_plugins,
                                    label=None)
        progress.setTitre("Initialisation...")

        compt = 0
        for depot in ("officiel", "github"):
            for name, infos in self.pluginsIGN.get_plugins_ign_from_depot(depot).items():
                compt +=1
                progress.setValue(compt, f"{name}")
                version = infos["version"]
                description = infos["description"]
                icon = infos["icon"]
                # test du nom avec get(name) pour éviter l'erreur si le plugin n'est pas installé (nom absent de la liste des plugins installés)
                if self.plugin_maitre.plugins_installes().get(name) is None:
                    version_installe = None
                else:
                    version_installe = self.plugin_maitre.plugins_installes().get(name)[PLUGIN_VERSION]

                ligne = self.tablePlugins.rowCount()
                self.tablePlugins.insertRow(ligne)

                # NOM DU PLUGIN
                if version_installe != version:
                    check = "True"
                else:
                    check = "False"
                item_name = self.creer_item(name,check)
                item_name.setData(Qt.ItemDataRole.UserRole, infos)  # stocke le dictionnaire complet (name, url, version...) dans l'item

                # DEPOT
                nom_depot = ""
                url_icon = ""
                if depot == "officiel":
                    nom_depot = "Dépôt officiel (qgis.org)"
                    url_icon = f"{URL_QGIS}{icon}"
                elif depot == "github":
                    nom_depot = "GitHub"
                    url_icon = icon
                item_depot = self.creer_item(nom_depot)

                # ICON
                icon_bytes = self.pluginsIGN.load_fichier(url_icon)
                pixmap = QPixmap()
                pixmap.loadFromData(icon_bytes)
                item_name.setIcon(QIcon(pixmap))

                # VERSION DISPONIBLE
                item_version_dispo = self.creer_item(version)
                if version_installe != version:
                    item_version_dispo.setBackground(QBrush(QColor(COLOR_MAJ)))
                # VERSION INSTALLÉE
                item_version_installe = self.creer_item(version_installe)

                # DESCRIPTION
                item_descr = self.creer_item(description)

                # si le plugin n'est pas dans la liste des plugins du profil actif, on le grise
                if name not in list_plugins_profil:
                    item_name.setBackground(QBrush(QColor(COLOR_HORS_PROFIL)))
                    item_name.setCheckState(Qt.CheckState.Unchecked)
                    item_name.setFlags(item_name.flags() & ~Qt.ItemFlag.ItemIsUserCheckable & ~Qt.ItemFlag.ItemIsEnabled)

                    item_version_dispo.setBackground(QBrush(QColor(COLOR_HORS_PROFIL)))
                    item_version_dispo.setFlags(item_name.flags() & ~Qt.ItemFlag.ItemIsUserCheckable & ~Qt.ItemFlag.ItemIsEnabled)
                    item_version_installe.setBackground(QBrush(QColor(COLOR_HORS_PROFIL)))
                    item_version_installe.setFlags(item_name.flags() & ~Qt.ItemFlag.ItemIsUserCheckable & ~Qt.ItemFlag.ItemIsEnabled)
                    item_depot.setBackground(QBrush(QColor(COLOR_HORS_PROFIL)))
                    item_depot.setFlags(item_name.flags() & ~Qt.ItemFlag.ItemIsUserCheckable & ~Qt.ItemFlag.ItemIsEnabled)
                    item_descr.setBackground(QBrush(QColor(COLOR_HORS_PROFIL)))
                    item_descr.setFlags(item_name.flags() & ~Qt.ItemFlag.ItemIsUserCheckable & ~Qt.ItemFlag.ItemIsEnabled)

                    # formatage pour retrouver les dossiers de la forme "IGN_"
                    if self.plugin_maitre.plugins_installes().get(name) is not None:
                        self._plugin_to_suppr.append(Path(self.parent_directory, self.plugin_maitre.plugins_installes().get(name)[PLUGIN_REP]))

                self.tablePlugins.setItem(ligne, 0, item_name)
                self.tablePlugins.setItem(ligne, 1, item_depot)
                self.tablePlugins.setItem(ligne, 2, item_version_dispo)
                self.tablePlugins.setItem(ligne, 3, item_version_installe)
                self.tablePlugins.setItem(ligne, 4, item_descr)

        progress.setClose()
        # rafraichir l'affichage du tableau qu'a la fin du remplissage pour éviter les ralentissements
        self.tablePlugins.setUpdatesEnabled(True)
        self.tablePlugins.setSortingEnabled(True)
        self.tablePlugins.sortItems(0, Qt.SortOrder.AscendingOrder)

    def on_profil_changed(self,index):
        self._plugin_to_suppr.clear()
        texte = self.comboBox_profils.itemText(index)
        valeur = self.comboBox_profils.itemData(index)
        nouveau_profil = {'nom': texte,'fichier': valeur}
        # si pas de changement on réécrit pas le fichier
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
        url = QUrl(REP_PLUGIN_GITHUB).resolved(QUrl(fic_xml)) # construction de l'url
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
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if check == "True":
            item.setCheckState(Qt.CheckState.Checked)
        elif check == "False":
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            pass
        return item

    def get_plugins_checked(self):
        plugins_checked = []
        for row in range(self.tablePlugins.rowCount()):
            item = self.tablePlugins.item(row, 0)
            if item is not None and item.checkState() == Qt.CheckState.Checked:
                plugin = item.data(Qt.ItemDataRole.UserRole).copy()  # Récupère le dictionnaire (copie) stocké dans l'item
                plugin["name"] = item.text()  # Ajoute le nom du plugin au dictionnaire
                plugins_checked.append(plugin)
        return plugins_checked


    def on_installe_plugin(self):
        # ==========================================
        # PLUGINS à SUPPRIMER (grisés) : on vérifie si le plugin existe encore avant de le supprimer
        # liste intermediaire pour stocker les plugins à supprimer
        # pour ne pas modifier la liste self._plugin_to_suppr pendant l'itération
        plugins_a_supprimer = []
        for plugin in self._plugin_to_suppr:
            if plugin.exists():
                plugins_a_supprimer.append(plugin)
        self._plugin_to_suppr = plugins_a_supprimer

        # ==========================================


        # =================================================
        # PLUGINS à INSTALLER (cochés) : on vérifie si le plugin est déjà installé et si la version est identique
        list_plugin_to_install = self.get_plugins_checked()

        # conditions d'installation
        is_installok = True
        if self.checkBox_suppr_plugins.checkState() == Qt.CheckState.Checked:
            if len(list_plugin_to_install) == 0 and len(self._plugin_to_suppr) == 0:
                is_installok = False
        else:
            if len(list_plugin_to_install) == 0:
                is_installok = False


        if not is_installok:
            QMessageBox.warning(self, "Avertissement", "Aucun plugin à installer ou à supprimer.")
            return None

        # suppression des plugins grisés si la case est cochée
        if self.checkBox_suppr_plugins.checkState() == Qt.CheckState.Checked:
            for dossier in self._plugin_to_suppr:
                try:
                    shutil.rmtree(dossier)
                except Exception as e:
                    print(f"Erreur lors de la suppression de {Path(dossier).name} : {e}")

        progress = DownloadProgress(parent = self,
                                    progress_bar=self.progressBar,
                                    total=len(list_plugin_to_install),
                                    label=self.label_progress)


        for idx, plugin in enumerate(list_plugin_to_install, start=1):
            progress.setValue(idx)
            progress.setLabel(f"Téléchargement de : {plugin['name']}")
            # téléchargement des plugins sous forme de bytes
            plugins_bytes = self.pluginsIGN.download_plugins(plugin['download_url'])
            if plugins_bytes is None:
                continue

            # écriture physique du zip
            chemin_zip = os.path.join(self.parent_directory, f"{plugin['name']}.zip")
            with open(chemin_zip, "wb") as f:
                f.write(plugins_bytes)

            # extraction du zip
            self.pluginsIGN.extract_zip(self.parent_directory,chemin_zip)
        progress.setClose()

        # on rafraichit la liste des plugins installés
        self.plugin_maitre._plugins_installes = self.plugin_maitre.get_dico_plugin_installes()
        self.tablePlugins.clearContents()
        self.tablePlugins.setRowCount(0)
        self._plugin_to_suppr.clear()

        self.plugin_maitre.refresh_plugins()  # met à jour QGIS
        self.remplir_dlg_plugins()

        text = "Installation terminée<br>"
        text += "<span style='color:red; font-weight:bold;'>"
        text += "- Veuillez redémarrer QGIS pour activer les nouveaux plugins<br>"
        text += "- Veuillez lancer la configuration des barres d'outils des plugins dans le menu 'IGN' -> 'Configuration'"
        text += "</span>"
        QMessageBox.information(self, "Installation des plugins", text)







