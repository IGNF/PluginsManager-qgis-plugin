import zipfile
from xml.etree import ElementTree as ET

from qgis.PyQt.QtCore import QEventLoop
from qgis.PyQt.QtNetwork import QNetworkRequest,QNetworkReply
from qgis.core import Qgis,QgsNetworkAccessManager
from .constantes import *


class PluginsIGN:
    def __init__(self):
        self._all_plugins_name_dispo = None
        self._plugins_officiel_trouves = set()
        self.list_plugins_github = []

        self._plugins_xml = {"officiel": None,"github": None}

    def get_url_depot_officiel(self):
        version = Qgis.QGIS_VERSION.split("-")[0]  # ex. "3.44.8"
        version_courte = ".".join(version.split(".")[:2])  # "3.44"
        return QUrl(f"https://plugins.qgis.org/plugins/plugins.xml?qgis={version_courte}")


    def load_fichier(self, url):
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"Cache-Control", b"no-cache, no-store, must-revalidate")
        request.setRawHeader(b"Pragma", b"no-cache")
        request.setRawHeader(b"Expires", b"0")
        reply = QgsNetworkAccessManager.instance().get(request)
        loop = QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec()
        try:
            err = reply.error()
            if err != QNetworkReply.NetworkError.NoError:
                return None
            data = bytes(reply.readAll())
            return data
        finally:
            reply.deleteLater()

    def get_xml(self, depot):
        if self._plugins_xml[depot] is None:
            if depot == "officiel":
                self._plugins_xml[depot] = self.load_fichier(self.get_url_depot_officiel())
            elif depot == "github":
                self._plugins_xml[depot] = self.load_fichier(URL_PLUGINS_GITHUB)
            else:
                return None
        return self._plugins_xml[depot]

    # recuperation du nom de tous les plugins dans all_plugins.xml de GitHub
    def get_all_plugins_name_dispo(self):
        if self._all_plugins_name_dispo is None:
            xml = self.get_xml("github")
            if not xml:
                return set()
            root = ET.fromstring(xml)
            self._all_plugins_name_dispo = []
            for plugin in root.findall("pyqgis_plugin"):
                self._all_plugins_name_dispo.append(plugin.attrib["name"])
        return self._all_plugins_name_dispo

    # retourne tous les plugins disponibles dans les dépots officiel et github, avec leurs infos (version, url de téléchargement, description, icône)
    def get_plugins_ign_from_depot(self,type_depot) -> dict:
        self.get_all_plugins_name_dispo()
        # print(f"all plugins dispo from all_plugins.xml = {self._all_plugins_name_dispo}")
        if self._plugins_xml[type_depot] is None:
            if type_depot == "officiel":
                url = self.get_url_depot_officiel()
                self._plugins_xml[type_depot] = self.load_fichier(url)
            elif type_depot == "github":
                self._plugins_xml[type_depot] = self.load_fichier(URL_PLUGINS_GITHUB)
        xml = self._plugins_xml[type_depot]
        if xml is None:
            return {}

        plugins = {}

        root = ET.fromstring(xml)
        for plugin in root.findall("pyqgis_plugin"):
            name = plugin.attrib.get("name")

            # plugin IGN dans le depot officiel
            if type_depot == "officiel":
                if name not in self._all_plugins_name_dispo:
                    continue
                self._plugins_officiel_trouves.add(name)
            elif type_depot == "github":
                if name not in self.list_plugins_github:
                    continue

            plugins[name] = {"version": plugin.attrib.get("version"),
                                "download_url": plugin.findtext("download_url"),
                                "description": plugin.findtext("description"),
                                "icon" : plugin.findtext("icon")
                                 }
        # Plugins IGN absents du dépôt officiel
        # ceux-ci seront à télécharger depuis github
        if type_depot == "officiel":
            self.list_plugins_github = set(self._all_plugins_name_dispo) - self._plugins_officiel_trouves
        return plugins

    def download_plugins(self,download_url):
        request = QNetworkRequest(QUrl(download_url))
        reply = QgsNetworkAccessManager.instance().get(request)
        loop = QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec() # bloque jusqu'à la fin du telechargement
        try:
            err = reply.error()
            if err != QNetworkReply.NetworkError.NoError:
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
        os.remove(fic_zip)


