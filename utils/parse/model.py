import xml.etree.ElementTree as ET
import pathlib

class MarkupLabel:

    def __init__(self, element: ET.Element):
        self.id:int = int(element.get("id"))
        self.name:str = element.get("name")
        self.color:str = element.get("color")
    
class MarkupEpoch:

    def __init__(self, element: ET.Element):
        self.number:str = str(element.get("number"))
        self.epochPath:str = element.get("epochPath")
        self.default:bool = (element.get("default") == 'True')
        

class ModelInit:
    def __init__(self, element: ET.Element):
        self.architecture:str = element.find("architecture").get('value')
        self.labels: dict[str, MarkupLabel] = dict()
        
        xmlLabels = element.find('labels')
        for xmlLabel in xmlLabels:
            label = MarkupLabel(xmlLabel)
            self.labels[str(label.id)] = label

        
class ModelTrain:
    epochs: list[MarkupEpoch] = list()
    defaultEpoch: MarkupEpoch = None

    def __init__(self, element: ET.Element):
        savedEpochs = element.find('savedEpochs')
        for epoch in savedEpochs:
            epoch = MarkupEpoch(epoch)
            self.epochs.append(epoch)
            if epoch.default:
                self.defaultEpoch = epoch
        

class MarkupModel:

    def __init__(self, path):
        self.path = pathlib.Path(path)

        tree = ET.parse(path)
        element = tree.getroot()

        self.modelName:str = element.get("modelName")
        self.dims:str = element.get("dims")
        self.description:str = element.get("description")
        self.init:ModelInit = ModelInit(element.find('init'))
        self.train:ModelTrain = ModelTrain(element.find('train'))

