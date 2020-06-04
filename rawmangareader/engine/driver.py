import os
import cv2
import functools
from rawmangareader.engine.predict import Predictor
from rawmangareader.engine.bubbletext import BubbleText
from rawmangareader.engine.ocr import extractTextFromBox
from rawmangareader.engine.translation import Translator
from configparser import ConfigParser

class Driver():
    CONFIG_FILE_NAME = 'config.ini'
    CONFIG_DEFAULT_SECTION = 'Default'
    CONFIG_SUBSCRIPTION_KEY = 'SubscriptionKey'
    CONFIG_USE_CUDA = 'UseCuda'

    @staticmethod
    def getSupportedLanguages():
        return Translator.getSupportedLanguages()

    def __init__(self):
        super().__init__()
        self.config = ConfigParser()
        self.config.read(Driver.CONFIG_FILE_NAME)

        useCuda = False
        subscriptionKey = None
        try:
            subscriptionKey = self.config.get(Driver.CONFIG_DEFAULT_SECTION, Driver.CONFIG_SUBSCRIPTION_KEY)
            useCuda = self.config.get(Driver.CONFIG_DEFAULT_SECTION, Driver.CONFIG_USE_CUDA) == '1'
        except:
            pass

        self.image_rgb = None
        self.imagePath = None
        self.bubbleTextBoxes = None
        self.currentDirectory = None
        self.predictor = Predictor(useCuda)
        self.translator = Translator(subscriptionKey)

    def hasSubscriptionKey(self):
        return self.translator.hasSubscriptionKey()

    def loadAndProcessImage(self, imagePath, fromLang, toLang):
        success = False
        try:
            image = cv2.imread(imagePath)
            if image is not None:
                self.imagePath = imagePath
                self.image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.loadBoxes()
                self.getOriginalTextForAllBoxes()
                self.translateTextForAllBoxes(fromLang, toLang)
                success = True
        except Exception  as ex:
            print("***", ex)
            success = False

        return success

    def loadBoxes(self):
        if self.imagePath is not None and self.imagePath != "":
            coordinates = self.predictor.predict(self.imagePath)
            sortedCoordinates = sorted(coordinates, key=functools.cmp_to_key(self.compareCoordinates))
            self.bubbleTextBoxes = { str(id):BubbleText(str(id), box, None, None) for id, box in enumerate(sortedCoordinates) }

    def compareCoordinates(self, coor1, coor2):
        """Compare coordinate for sorting purpose.

        Arguments:
            coor1 {list[float]} -- topLeft and bottomRight - [x1, y2, x2, y2]
            coor2 {list[float]} -- topLeft and bottomRight - [x1, y2, x2, y2]

        Returns:
            [int] -- negative if the first coordinate is less than the second coordinate.
                     0 if they are equal.
                     positive if the first coordinate is greater than the second coordinate.
        """
        ymin1 = coor1[1]
        ymin2 = coor2[1]
        if ymin1 < ymin2:
            return -1
        elif ymin1 > ymin2:
            return 1
        else:
            xmin1 = coor1[0]
            xmin2 = coor2[0]
            if xmin1 > xmin2:
                return -1
            elif xmin1 < xmin2:
                return 1
            else:
                return 0

    def getBoxes(self):
        """Return a cictionary of BubbleText.
        Key is a string of bubble text box id.
        Value is BubbleText box object.

        Returns:
            dict{BubbleText} -- Dictionary of BubbleText.
        """
        if self.bubbleTextBoxes is None:
            self.loadBoxes()

        return self.bubbleTextBoxes

    def getOriginalTextFromBox(self, boxId):
        return self.bubbleTextBoxes[boxId].text

    def getTranslatedTextFromBox(self, boxId):
        return self.bubbleTextBoxes[boxId].translation

    def getOriginalTextForAllBoxes(self):
        for bubbleText in self.bubbleTextBoxes.values():
            if bubbleText.text is None or bubbleText.text == '':
                text = extractTextFromBox(self.image_rgb, bubbleText.xmin, bubbleText.ymin, bubbleText.width, bubbleText.height)
                bubbleText.text = text

    def translateTextForAllBoxes(self, fromLang, toLang):
        listOfStrings = [ bubbleTextBox.text for bubbleTextBox in self.bubbleTextBoxes.values() ]
        translatedStrings = self.translator.translate(listOfStrings, fromLang=fromLang, toLang=toLang)

        for i, bubbleTextBox in enumerate(self.bubbleTextBoxes.values()):
            bubbleTextBox.translation = translatedStrings[i]

    def setText(self, boxId, text):
        self.bubbleTextBoxes[str(boxId)].text = text

    def setCurrentDirectory(self, currentDirectory):
        self.currentDirectory = currentDirectory.replace('/', '\\')

    def getImageFullPath(self, filename):
        return os.path.join(self.currentDirectory, filename)

    def getCurrentDirectoryFileList(self):
        files = os.listdir(self.currentDirectory)
        ret = []
        for file in files:
            if os.path.isfile(os.path.join(self.currentDirectory, file)):
                ret.append(file)

        return ret

    def getSubscriptionKey(self):
        return self.config.get(Driver.CONFIG_DEFAULT_SECTION, Driver.CONFIG_SUBSCRIPTION_KEY)

    def updateSettings(self, settings):
        for key, value in settings.items():
            self.config.set(Driver.CONFIG_DEFAULT_SECTION, key, str(value))

        with open(Driver.CONFIG_FILE_NAME, 'w') as configFile:
            self.config.write(configFile)

    def getSettings(self):
        return {
            Driver.CONFIG_SUBSCRIPTION_KEY : self.config.get(Driver.CONFIG_DEFAULT_SECTION, Driver.CONFIG_SUBSCRIPTION_KEY),
            Driver.CONFIG_USE_CUDA : self.config.get(Driver.CONFIG_DEFAULT_SECTION, Driver.CONFIG_USE_CUDA)
            }