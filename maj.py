import os
import subprocess
import importlib
from pathlib import Path

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QDialog,QTableWidgetItem
from qgis.PyQt.uic import loadUi
from qgis.core import QgsNetworkContentFetcher,QgsApplication
from qgis.PyQt.QtCore  import QUrl
from zipfile import ZipFile
import requests
import xml.etree.ElementTree as ET

from .mapping_version import *

INSTALLATEUR = "PluginIGN_Installer"
XML_RACINE = "https://raw.githubusercontent.com/IGNF/collaboratif-plugins/main/"
PEFILE = ["pefile","pefile-2024.8.26-py3-none-any.whl"]
DEFUSEDXML = ["defusedxml","defusedxml-0.7.1-py2.py3-none-any.whl"]
PACKAGES = [PEFILE,DEFUSEDXML]

def log(message,reset=False):
    """
    Écrit un message dans le fichier de log avec un horodatage.
    Le fichier est ouvert en mode append pour ne pas écraser les données.
    """
    current_directory = os.path.dirname(__file__)
    # Remonter d'un niveau
    parent_directory = os.path.abspath(Path(current_directory, os.pardir))
    fichier = Path(parent_directory, "log_maitre.txt")
    mode = "w" if reset else "a"  # "w" pour écraser, "a" pour ajouter
    with open(fichier, mode, encoding="utf-8") as f:
        f.write(f"{message}\n")

class MajPlugins:
    def __init__(self,iface):
        self.package_manquants = [] # liste de couples (nom complet, nom simplifié)
        self.iface = iface
        self.installateur = None
        self.plugins_xml = None
        self.prefix = None
        self.path_xml_local = None
        self.current_dir = os.path.dirname(__file__)
        self.parent_dir = os.path.dirname(self.current_dir)
        self.path_exe = list(Path(self.parent_dir).glob(f"*{INSTALLATEUR}.exe"))

        prefix = Path(QgsApplication.prefixPath())
        install_root = prefix.parent.parent
        self.osgeo_bat = install_root / "OSGeo4W.bat"

    def download_file(self,type_file):
        url = None
        self.fetcher = QgsNetworkContentFetcher()
        # définir quel installateur est utilisé pour adapter le nom du XML à télécharger
        if type_file == "XML":
            if len(self.path_exe) == 0:
                log(f"Installateur non trouvé dans le dossier : {self.parent_dir}")
                return

            if len(self.path_exe) > 1:
                log("Plusieurs installateurs trouvés dans le dossier, impossible de déterminer lequel est utilisé :")
                return

            # formatage de l'url de téléchargement du XML en fonction du nom de l'installateur trouvé dans le dossier
            exe_ss_ext = self.path_exe[0].stem
            self.prefix = exe_ss_ext.replace(INSTALLATEUR, "")
            self.prefix = self.prefix.replace("_", "")
            self.prefix = self.prefix.lower()
            if self.prefix != "":
                self.prefix = f"_{self.prefix}"
            url = rf"{XML_RACINE}plugins{self.prefix}.xml?nocache=1"
            # formatage du chemin local du XML dans le dossier du plugin
            self.path_xml_local = Path(self.parent_dir) / f"plugins{self.prefix}.xml"
            log(f"Téléchargement du xml : {url}")
            self.fetcher.finished.connect(self.finish_download)

        elif type_file == "EXE":
            url = self.installateur.find("download_url").text
            log(f"\tTéléchargement de l'installateur : {url}")
            self.fetcher.finished.connect(self.finish_download_zip)

        self.fetcher.fetchContent(QUrl(url))

    def finish_download_zip(self):
        reply = self.fetcher.reply()
        from qgis.PyQt.QtNetwork import QNetworkReply
        if reply.error() != QNetworkReply.NetworkError.NoError:
            log(f"Erreur téléchargement zip : {reply.errorString()}")
            return
        try:
            data = reply.readAll().data()
            with open(self.zip_path, "wb") as f:
                f.write(data)
            log(f"\tZIP de l'installateur téléchargé : {self.zip_path}")
            # supprimer l'exe s'il existe déjà dans le dossier avant de dézipper le nouveau
            self.suppr_fichier(self.path_exe[0])
            # dézipper le fichier téléchargé
            self.dezippe_file(self.zip_path)

        except Exception as e:
            log(f"Erreur sauvegarde zip : {repr(e)}")

    def finish_download(self):
        reply = self.fetcher.reply()
        from qgis.PyQt.QtNetwork import QNetworkReply
        if reply.error() != QNetworkReply.NetworkError.NoError:
            log(f"Erreur de téléchargement du fichier : {reply.errorString()}")
            return
        data = self.fetcher.contentAsString()

        # enregistrement du fichier XML dans le dossier du plugin
        try:
            with open(self.path_xml_local, "w") as f:
                f.write(data)
            log(f"Enregistrement terminé de : {self.path_xml_local}")
            # liste des plugins trouvés dans le XML
            self.plugins_xml = self.getplugin_from_xml(self.path_xml_local)
            # y a-t-il une mise à jour de l'installateur à notifier ?
            if self.is_maj_installateur():
                self.installe_installateur()
            # y a-t-il des mises à jour de plugins à notifier ?
            self.is_maj_plugins()
        except Exception as e:
            log(f"Erreur du fichier XML : {e}")
            return

    def getplugin_from_xml(self,tmp_xml,all = False):
        tree = ET.parse(tmp_xml)
        root = tree.getroot()
        list_tmp = ""
        dico_plugin = {}
        # Parcourir les plugins
        for plugin in root.findall("pyqgis_plugin"):
            name = plugin.get("name")
            log(f"plugin trouvé dans le XML : {name}")
            # on ne prend pas en compte l'installateur pour la notification des mises à jour
            if not all:
                if INSTALLATEUR in name:
                    self.installateur = plugin
                    continue
            version = plugin.get("version")
            description = plugin.find("description")
            download_url = plugin.find("download_url").text
            dico_plugin[name] = [version, description.text,download_url]
            list_tmp += f"-{name}\n"
        return dico_plugin

    def dial_maj(self):
        self.dlgMaj = QDialog()
        loadUi(os.path.dirname(__file__) + "/maj.ui", self.dlgMaj)
        icon_path = Path(__file__).parent /"icons"/ "icon.png"
        self.dlgMaj.setWindowIcon(QIcon(str(icon_path)))
        self.dlgMaj.setWindowFlags(WindowCloseButtonHint)

        self.dlgMaj.tableWidget_maj.setSelectionMode(NoSelection)
        self.dlgMaj.tableWidget_maj.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.dlgMaj.tableWidget_maj.setColumnCount(2)
        self.dlgMaj.tableWidget_maj.setHorizontalHeaderLabels(["Plugin", "Version"])
        self.dlgMaj.tableWidget_maj.setShowGrid(False)
        self.dlgMaj.tableWidget_maj.verticalHeader().setDefaultSectionSize(15)


        self.dlgMaj.setWindowTitle("Mises à jour ...")
        self.dlgMaj.pushButton_executer_installateur.clicked.connect(self.execute_installeur)
        self.dlgMaj.pushButton_fermer.clicked.connect(self.dlgMaj.close)# self.dlgMaj.exec()

    def is_maj_plugins(self):
        # comparer les versions des plugins installés (lecture metadata.txt) avec celles du fichier XML téléchargé
        # et afficher une notification si une mise à jour est disponible
        self.dial_maj()
        is_maj = False
        for nom, (version, description, lien) in self.plugins_xml.items():
            version_local = self.get_info_plugins(nom, "version=")
            if version_local is None:
                log(f"Plugin {nom} non trouvé localement ou metadata.txt manquant, impossible de vérifier la version.")
                continue
            if version_local != version:
                log(f"Mise à jour disponible pour {nom} : version locale : {version_local}, version disponible : {version}")
                # self.dlgMaj.listWidget_maj.addItem(nom)
                self.dlgMaj.tableWidget_maj.insertRow(0)
                item_version = QTableWidgetItem(version)
                item_version.setTextAlignment(AlignCenter)
                self.dlgMaj.tableWidget_maj.setItem(0, 0, QTableWidgetItem(nom))
                self.dlgMaj.tableWidget_maj.setItem(0, 1, QTableWidgetItem(item_version))
                is_maj = True
        if is_maj:
            self.dlgMaj.tableWidget_maj.resizeColumnsToContents()
            self.dlgMaj.exec()

    def is_maj_installateur(self):
        # comparer la version de l'installateur (lecture metadata.txt) avec celle du fichier XML téléchargé
        # et afficher une notification si une mise à jour est disponible
        version_xml = self.installateur.get('version')
        version_local = self.get_version_installateur()
        if version_local is None:
            log(f"Installateur {INSTALLATEUR} non trouvé localement (ou pefile n'est pas installé), impossible de vérifier la version.")
            return False

        if version_local != version_xml:
            log(f"Mise à jour disponible pour {self.installateur.get('name')} : version locale : {version_local}, version disponible : {version_xml}")
            return True
        else:
            log(f"{self.installateur.get('name')} est à jour (version locale :{version_local} -- version_xml : {version_xml})")

    def installe_installateur(self):
        self.zip_path = Path(self.parent_dir) / f"{self.installateur.get('name')}.zip"
        # suppression du fichier zip s'il existe déjà
        self.suppr_fichier(self.zip_path)
        # téléchargement de l'installateur (zip) depuis le lien du XML
        self.download_file("EXE")

    def suppr_fichier(self, zip_path):
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
                log(f"\tSuppression de : \n\t\t{zip_path}")
            except Exception as e:
                log(f"\tErreur lors de la suppression du fichier  : \n\t\t{e}")

    # retourne les infos des plugins dans le dossier de QGIS
    def get_info_plugins(self, plugin_name, type_info):
        fic_metadata = os.path.join(self.parent_dir, plugin_name,"metadata.txt")
        if os.path.exists(fic_metadata):
            with open(fic_metadata, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith(type_info):
                        return line.strip().split("=")[1]
        return None

    def get_version_installateur(self):
        if self.need_package():
            return None # pefile dans ce cas
        import pefile
        if not self.path_exe:
            return None
        with pefile.PE(self.path_exe[0]) as pe:
            # Extraire les informations de version
            for fileinfo in pe.FileInfo:
                for entry in fileinfo:
                    if entry.Key.decode() == 'StringFileInfo':
                        for st in entry.StringTable:
                            for k, v in st.entries.items():
                                if k.decode() == "FileVersion":
                                    return v.decode()
        return None

    def download_exe(self, url, destination):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(destination, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            log(f"\tTéléchargement terminé : \n\t\t{destination}")

        except Exception as e:
            log(f"\tErreur de téléchargement : \n\t\t{e}")

    def dezippe_file(self,zip_path):
        # Chemin du fichier zip
        # Dossier de destination
        extract_to = Path(self.parent_dir)
        # Décompression
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            log(f"\tExtraction de : \n\t\t{zip_path}")
        # supprimer le fichier zip après extraction
        try:
            os.remove(zip_path)
            log(f"\tSuppression du zip : \n\t\t{zip_path}")
        except Exception as e:
            log(f"\tErreur lors de la suppression du fichier zip : \n\t\t{e}")

    def execute_installeur(self):
        # test si le dial de notification de mise à jour est ouvert et le fermer avant de lancer l'installateur
        try:
            if getattr(self, "dlgMaj", None):
                self.dlgMaj.close()
        except Exception:
            pass
        try:
            subprocess.Popen([str(self.path_exe[0])], cwd=str(self.parent_dir))
        except Exception as e:
            text = (f"Le programme de mise à jour est introuvable :"
                    f"Veuillez lancer l'installateur fournit (*_{INSTALLATEUR}.exe)")
            QMessageBox.warning(None, "Erreur", text)

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
            log(f"Fichier batch introuvable : {self.osgeo_bat}")
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
            cmd = f'start "" cmd /c call "{self.osgeo_bat}" && pip install "{archive}" && exit'
            result = subprocess.run(cmd, shell=True)

            if result.returncode != 0:
                echec_package += f"<br>{package[0]}"

        if echec_package != "<br>":
            QMessageBox.information(self.iface.mainWindow(),"echec",f"Echec de : <span style='color:red;'>{echec_package}</span>")

        else:
            texte = "Tous les packages ont été installés<br>"
            texte += f"Veuillez relancer QGIS et fermer toutes les fenetres shell"
            QMessageBox.information(self.iface.mainWindow(),"Succès",texte)




