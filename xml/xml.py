from xml.etree import ElementTree as ET # nosec B405
from ..constantes import *


# ==================================================
# creation du dossier et du tabwidget.xml s'ils n'existent pas (premiere utilisation)
# tabwidget.xml : configuration des onglets
def initXML_toolbar(path_xml):
    dossier_plugin = Path(__file__).parent.parent
    dossier_config = dossier_plugin / DOSSIER_ONGLET
    # Créer le dossier s'il n'existe pas
    dossier_config.mkdir(parents=True, exist_ok=True)

    # Racine uniquement
    root = ET.Element("tabwidget")
    # Écriture dans le fichier
    tree = ET.ElementTree(root)
    tree.write(path_xml, encoding="utf-8", xml_declaration=True)

# ==================================================
# retourne une liste contenant tous les onglets du xml
def get_onglet_fromXML(path_xml):
    tree = ET.parse(path_xml) # nosec B314
    root = tree.getroot()
    onglets = root.findall(".//onglet")
    liste_onglet = []
    for onglet in onglets:
        liste_onglet.append(onglet.get("id"))
    return liste_onglet

# ==================================================
# retourne une liste de tous les plugins du xml pour un onglet donné
def get_plugins_from_onglet_xml(path_xml, onglet):
    # charge le XML existant
    tree = ET.parse(path_xml) # nosec B314
    root = tree.getroot()
    onglet_xml = root.find(f".//onglet[@id='{onglet}']")
    list_coche = []
    if onglet_xml is not None:
        for plugin in onglet_xml.findall("plugin"):
            list_coche.append(plugin.text)
    return list_coche

# ==================================================
# ajout onglet et plugins cochés dans le xml
def add_onglet_from_XML(path_xml,nom):
    # charge le XML existant
    tree = ET.parse(path_xml) # nosec B314
    root = tree.getroot()
    # creation nouvel onglet
    new_onglet = ET.Element("onglet",id = nom)
    root.append(new_onglet)
    # mise en page : indentation
    ET.indent(root, "    ")
    tree.write(path_xml, encoding='utf-8', xml_declaration=True)

# ==================================================
# suppression d'un onglet dans le xml
def suppr_onglet_from_XML(path_xml,id_onglet):
    tree = ET.parse(path_xml) # nosec B314
    root = tree.getroot()
    for onglet in root.findall(".//onglet"):
        if onglet.get("id") == id_onglet:
            root.remove(onglet)
    tree.write(path_xml, encoding='utf-8', xml_declaration=True)

# ==================================================
# suppression de tous les plugins dependant d'un onglet du xml
def suppr_all_plugins_from_onglet(path_xml, onglet):
    tree = ET.parse(path_xml) # nosec B314
    root = tree.getroot()
    onglet_xml = root.find(f".//onglet[@id='{onglet}']")
    if onglet_xml is not None:
        for plugin in onglet_xml.findall("plugin"):
            onglet_xml.remove(plugin)
        tree.write(path_xml, encoding='utf-8', xml_declaration=True)

# ==================================================
# re-initialise : tabwidget_xml
def clean_tabwidget_xml(path_xml,plugins_installes):
    tree = ET.parse(path_xml) # nosec B314
    root = tree.getroot()
    for onglet in root.findall("onglet"):
        for plugin in list(onglet.findall("plugin")):
            if plugin.text not in plugins_installes:
                onglet.remove(plugin)
    ET.indent(root, "    ")
    tree.write(path_xml, encoding="utf-8", xml_declaration=True)

# ==================================================
# écriture du xml avec tous les plugins cochés en fonction de l'onglet
def ecrire_plugin_coche_toXML(path_xml,onglet,list_plugin_coche):
    tree = ET.parse(path_xml) # nosec B314
    root = tree.getroot()
    ongletXml = root.find(f".//onglet[@id='{onglet}']")
    for plugin in list_plugin_coche:
        pluginXml = ET.SubElement(ongletXml,"plugin")
        pluginXml.text = plugin
    ET.indent(root, "    ")
    tree.write(path_xml,encoding='utf-8', xml_declaration=True)

def renomme_onglet_xml(path_xml,ancien_nom,nouveau_nom):
    tree = ET.parse(path_xml) # nosec B314
    root = tree.getroot()
    ongletXml = root.find(f".//onglet[@id='{ancien_nom}']")
    if ongletXml is None:
        return
    # Modifier l’attribut id
    ongletXml.set("id", nouveau_nom)
    ET.indent(tree, "    ")
    tree.write(path_xml, encoding="utf-8", xml_declaration=True)