import os
import zipfile
from xml.etree import ElementTree as ET

from qgis.PyQt.QtCore import QUrl, QEventLoop
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import Qgis,QgsNetworkAccessManager

from .constantes import *

class PluginsIGN:
    def __init__(self):
        self._plugins_xml = {"officiel": None,"github": None}
        self.list_plugins_github = []

    def load_xml(self,type_depot="officiel"):
        url = None
        if type_depot == "officiel":
            version = Qgis.QGIS_VERSION.split("-")[0]  # ex. "3.44.8"
            version_courte = ".".join(version.split(".")[:2])  # "3.44"
            url = QUrl(f"https://plugins.qgis.org/plugins/plugins.xml?qgis={version_courte}")
        elif type_depot == "github":
            url = QUrl(f"https://raw.githubusercontent.com/IGNF/collaboratif-plugins/main/plugins.xml?nocache=1")
        request = QNetworkRequest(url)
        reply = QgsNetworkAccessManager.instance().get(request)
        loop = QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec()
        try:
            if reply.error():
                print(reply.errorString())
                return None
            return bytes(reply.readAll())
        finally:
            reply.deleteLater()

    def get_plugins_ign_from_depot(self,type_depot) -> dict:
        if self._plugins_xml[type_depot] is None:
            self._plugins_xml[type_depot] = self.load_xml(type_depot)
        xml = self._plugins_xml[type_depot]
        if xml is None:
            return {}

        plugins = {}
        plugins_trouves = set()
        root = ET.fromstring(xml)
        for plugin in root.findall("pyqgis_plugin"):
            name = plugin.attrib.get("name")
            # plugin IGN dans le depot officiel
            if type_depot == "officiel":
                if name not in PLUGINS_IGN:
                    continue
                plugins_trouves.add(name)
            elif type_depot == "github":
                if name not in self.list_plugins_github:
                    continue

            plugins[name] = {"version": plugin.attrib.get("version"),
                                "download_url": plugin.findtext("download_url"),
                                "description": plugin.findtext("description"),
                                 }
        # Plugins IGN absents du dépôt officiel
        # ceux-ci seront à télécharger depuis github
        if type_depot == "officiel":
            self.list_plugins_github = set(PLUGINS_IGN) - plugins_trouves
        return plugins

    def download_plugins(self,download_url):
        request = QNetworkRequest(QUrl(download_url))
        reply = QgsNetworkAccessManager.instance().get(request)
        loop = QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec() # bloque jusqu'à la fin du telechargement
        try:
            if reply.error():
                print(reply.errorString())
                return None
            return bytes(reply.readAll()) # le fichier est telechargé sous forme de bytes
        finally:
            reply.deleteLater()

    def extract_zip(self,rep_dest,fic_zip):
        # Déziper dans le dossier des plugins
        try:
            with zipfile.ZipFile(fic_zip, 'r') as zip_ref:
                zip_ref.extractall(rep_dest)
        except zipfile.BadZipFile:
            print(f"ZIP corrompu : {fic_zip}")
        except FileNotFoundError:
            print(f"Fichier introuvable : {fic_zip}")
        except PermissionError:
            print(f"Permission refusée : {fic_zip}")
        except Exception as e:
            print(f"Erreur dézip : {e}")

        # Supprimer le fichier zip
        print(f"Suppression du fichier zip : {fic_zip}")
        os.remove(fic_zip)


