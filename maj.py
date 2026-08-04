
import subprocess # nosec B404
import importlib

from qgis.PyQt.QtGui import QIcon

from .dlg_install_plugins import *

from .mapping_version import *
from .constantes import *

class MajPlugins:
    def __init__(self,iface,installer):
        self.dlgMaj = None
        self.package_manquants = [] # liste de couples (nom complet, nom simplifié)
        self.iface = iface
        self.installer = installer
        self.plugins_xml = None
        self.prefix = None
        self.path_xml_local = None
        self.current_dir = os.path.dirname(__file__)
        self.parent_dir = os.path.dirname(self.current_dir)

        prefix = Path(QgsApplication.prefixPath())
        install_root = prefix.parent.parent
        self.osgeo_bat = install_root / "OSGeo4W.bat"

    def init_dial_maj(self):
        self.dlgMaj = QDialog()
        ui_file = Path(__file__).parent / "ui" / "maj.ui"
        loadUi(str(ui_file), self.dlgMaj)
        icon_path = Path(__file__).parent /"icons"/ "icon.png"
        self.dlgMaj.setWindowIcon(QIcon(str(icon_path)))
        self.dlgMaj.setWindowFlags(WindowCloseButtonHint | WindowStaysOnTopHint)

        self.dlgMaj.tableWidget_maj.setSelectionMode(NoSelection)
        self.dlgMaj.tableWidget_maj.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.dlgMaj.tableWidget_maj.setColumnCount(2)
        self.dlgMaj.tableWidget_maj.setHorizontalHeaderLabels(["Plugin", "Version"])
        self.dlgMaj.tableWidget_maj.setShowGrid(False)
        self.dlgMaj.tableWidget_maj.verticalHeader().setDefaultSectionSize(15)


        self.dlgMaj.setWindowTitle("Mises à jour ...")
        self.dlgMaj.pushButton_executer_installateur.clicked.connect(self.on_installe_maj_plugins)
        self.dlgMaj.pushButton_fermer.clicked.connect(self.fermeture_dialogue)

    def fermeture_dialogue(self):
        if self.dlgMaj:
            self.dlgMaj.close()
            self.dlgMaj = None

    def show_dial_maj_plugins(self,dico_plugins):
        # comparer les versions des plugins installés (lecture metadata.txt) avec celles du fichier XML téléchargé
        # et afficher une notification si une mise à jour est disponible
        self.init_dial_maj()
        is_maj = False
        # for nom, (version, description, lien) in self.plugins_xml.items():
        for nom, info in dico_plugins.items():
            print(f"{nom}-{info["version"]}")
            version_local = get_info_plugins_installe(nom, "version")
            if version_local != info["version"]:
                print(f"Mise à jour disponible pour {nom} : version locale : {version_local}, version disponible : {info["version"]}")
                # self.dlgMaj.listWidget_maj.addItem(nom)
                self.dlgMaj.tableWidget_maj.insertRow(0)
                item_version = QTableWidgetItem(info["version"])
                item_version.setTextAlignment(AlignCenter)
                self.dlgMaj.tableWidget_maj.setItem(0, 0, QTableWidgetItem(nom))
                self.dlgMaj.tableWidget_maj.setItem(0, 1, QTableWidgetItem(item_version))
                is_maj = True
        if is_maj:
            self.dlgMaj.tableWidget_maj.resizeColumnsToContents()
            self.dlgMaj.show()

    def on_installe_maj_plugins(self):
        self.fermeture_dialogue()
        self.installer.init_aspect_dialog()
        self.installer.remplir_dlg_plugins()
        self.installer.exec()

    def need_package(self):
        # test si les packages necessaires sont installés
        list_package_txt = "<br>"
        for package in PACKAGES:
            try:
                importlib.import_module(package[0]) # nom du module
            except ImportError:
                self.package_manquants.append([package[0],package[1]]) # nom simplifié ET nom complet du module
                list_package_txt += package[0]
                list_package_txt += "<br>"

                #  tout est OK
        if not self.package_manquants:
            return False

        texte = f"Les plugin IGN nécessitent les packages :<span style='color:red;'>{list_package_txt}</span><br><br>"
        texte += "Voulez vous les installer maintenant?"
        reponse = QMessageBox.question(
            self.iface.mainWindow(),
            "Package manquant",
            texte,
            QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
        if reponse == QMessageBox.Yes:
            if not self.isOSGeo4W_existe():
                return False
            texte = "L'installation va commencer, veuillez attendre le message de fin d'installation du package"
            QMessageBox.information(self.iface.mainWindow(), "Installation du package", texte)
            self.install_package(self.package_manquants)

            return True
        else:
            texte = f"package manquant : <span style='color:red;'>{list_package_txt}</span><br>"
            texte += "Certains plugins risquent de ne pas fonctionner"
            QMessageBox.warning(self.iface.mainWindow(),"Avertissement",texte)
        return True

    def isOSGeo4W_existe(self):
        if not self.osgeo_bat.exists():
            # log(f"Fichier batch introuvable : {self.osgeo_bat}")
            text = f"Fichier batch introuvable : {self.osgeo_bat}\n"
            text += f"Impossible de lancer l'installation"
            QMessageBox.critical(self.iface.mainWindow(), "Erreur", text)
            return False
        return True

    def install_package(self,packages):
        plugin_dir = Path(os.path.dirname(__file__))
        echec_package = "<br>"
        for package in packages:
            archive = Path(plugin_dir/"packages-requis"/package[1])

            cmd = [
                "cmd.exe",
                "/c",
                f'call {self.osgeo_bat} && python -m pip install {archive}'
            ]
            result = subprocess.run(cmd, capture_output=True,text=True,encoding="cp850") # nosec B603

            if result.returncode != 0:
                echec_package += f"<br>{package[0]}"

        if echec_package != "<br>":
            QMessageBox.information(self.iface.mainWindow(),"echec",f"Echec de : <span style='color:red;'>{echec_package}</span>")

        else:
            texte = "Tous les packages ont été installés<br>"
            texte += f"Veuillez relancer QGIS"
            QMessageBox.information(self.iface.mainWindow(),"Succès",texte)




