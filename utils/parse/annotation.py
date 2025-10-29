from collections import UserDict
import xml.etree.ElementTree as ET
import os.path

from data import labels
from data import files


class MarkupLabels(UserDict):

    def __init__(self, element: ET.Element):
        super().__init__()
        for xml_label in element:
            id = xml_label.get('id')
            name = xml_label.get('name')
            color = xml_label.get('color')
            label = labels.append(name, color)
            self.data[id] = label        


class MarkupFiles(UserDict):

    def __init__(self, element: ET.Element, path: str):
        super().__init__()
        for xml_file in element:
            filename = xml_file.get('path')
            width = xml_file.get('width')
            height = xml_file.get('height')
            colored = xml_file.get('colored')
            sequence = xml_file.get('sequence')

            filepath = os.path.join(path, filename)
            file = files.append(
                filepath, 
                sequence=sequence, 
                width=width, 
                height=height, 
                colored=colored
            )

            self.data[file] = list()
            xml_objects = xml_file.findall('object')

            for xml_object in xml_objects:
                label = xml_object.get('label')
                points = xml_object.get('points')
                self.data[file].append((label, points))
        

class Annotation:

    @staticmethod
    def toXML(path):
        root = ET.Element("annotations", {"dims": files.dim})
        xml_labels = ET.Element("labels")
        for label in labels:
            xml_labels.append(label.toXML())
        if files.dim == '2D':
            xml_files = ET.Element("images")
            for img in files:
                xml_files.append(img.toXML(path))
        elif files.dim == '3D':
            xml_files = ET.Element("pointClouds" )
            for pcl in files:
                xml_files.append(pcl.toXML(path))
        root.append(xml_labels)
        root.append(xml_files)
        return root
    
    @staticmethod
    def fromXML(path):
        tree = ET.parse(path)
        root = tree.getroot()
        dims = root.get('dims')
        xml_labels = root.find("labels")
        if dims == '2D':
            xml_files = root.find("images")
        elif dims == '3D':
            xml_files = root.find("pointClouds")

        return MarkupLabels(xml_labels), \
               MarkupFiles(xml_files, os.path.dirname(path))