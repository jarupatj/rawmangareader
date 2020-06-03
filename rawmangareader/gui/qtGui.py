import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from rawmangareader.engine.driver import Driver

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("PyQt")

        self.graphicView = GraphicsView()
        self.setCentralWidget(self.graphicView)

        self.createSpeechBoxDockPane()
        self.createFileListDockPane()
        self.createMenuBar()

        self.driver = Driver()

    def createFileListDockPane(self):
        self.fileListWidget = QListWidget()
        self.fileListWidget.itemClicked.connect(self.fileListItemClicked)
        self.fileListWidget.setMinimumHeight(300)
        self.fileListWidget.setSelectionMode(QAbstractItemView.SingleSelection)

        nextButton = QPushButton()
        nextButton.setText('Next Image')
        prevButton = QPushButton()
        prevButton.setText('Prev Image')

        hbox = QHBoxLayout()
        hbox.addWidget(prevButton)
        hbox.addWidget(nextButton)

        vbox = QVBoxLayout()
        vbox.addWidget(self.fileListWidget)
        vbox.addLayout(hbox)

        rightDockWidget = QWidget()
        rightDockWidget.setLayout(vbox)

        dock = QDockWidget('Filelist', self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        dock.setWidget(rightDockWidget)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def createSpeechBoxDockPane(self):
        self.boxListWidget = QListWidget()
        self.boxListWidget.itemClicked.connect(self.boxListItemClicked)
        self.boxListWidget.itemChanged.connect(self.boxListItemChanged)
        self.boxListWidget.setSelectionMode(QAbstractItemView.SingleSelection)

        self.fromLang = LanguageSelection("From", Driver.getSupportedLanguages())
        self.toLang = LanguageSelection("To", Driver.getSupportedLanguages())

        self.oriText = TextDisplay('Text')
        self.transText = TextDisplay('Translation')

        setTextButton = QPushButton()
        setTextButton.setText("Update text")
        setTextButton.clicked.connect(self.updateTextButtonClicked)

        translateButton = QPushButton()
        translateButton.setText("Translate all text")
        translateButton.clicked.connect(self.translateButtonClicked)

        vbox = QVBoxLayout()
        vbox.addWidget(self.boxListWidget)
        vbox.addWidget(self.oriText)
        vbox.addWidget(setTextButton)
        vbox.addWidget(self.transText)
        vbox.addWidget(self.fromLang)
        vbox.addWidget(self.toLang)
        vbox.addWidget(translateButton)

        rightDockWidget = QWidget()
        rightDockWidget.setLayout(vbox)

        dock = QDockWidget('Text boxes', self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        dock.setWidget(rightDockWidget)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def createMenuBar(self):
        """Create Menu bar.
        """
        exitAction = QAction("E&xit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip('Leave The App')
        exitAction.triggered.connect(self.exitApplicationAction)

        openFolderAction = QAction('&Open folder', self)
        openFolderAction.triggered.connect(self.openFolderAction)
        openFolderAction.setShortcut("Ctrl+O")

        settingAction = QAction('&Setting', self)
        settingAction.triggered.connect(self.settingAction)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(openFolderAction)
        fileMenu.addAction(settingAction)
        fileMenu.addAction(exitAction)

    def resizeEvent(self, qResizeEvent):
        """Resize window happened. Need to update the location of the boxes.

        Arguments:
            qResizeEvent {QResizeEvent} -- event information.
        """
        self.displayBoxesOnImage()
        QMainWindow.resizeEvent(self, qResizeEvent)

    def settingAction(self):
        """Popup dialog box asking user for subscription key.
        """
        text, ok = QInputDialog.getText(self, 'Setting', 'Microsoft Translator subscription key')

        if ok and text:
            self.driver.setTranslatorSubscriptionKey(text)

    def openFolderAction(self):
        """Open folder menu is selected. Open file dialog to ask the user the folder location.
        """
        currentDirectory = QFileDialog.getExistingDirectory(self)
        self.driver.setCurrentDirectory(currentDirectory)
        self.updateFileList()

    def updateFileList(self):
        """Folder is selected. Update the file list UI with the list of file under
           the directory.
        """
        self.fileListWidget.clear()

        fileList = self.driver.getCurrentDirectoryFileList()
        self.fileListWidget.addItems(fileList)

    def fileListItemClicked(self, item):
        filename = item.text()
        self.loadAndProcessImage(self.driver.getImageFullPath(filename))

    def exitApplicationAction(self):
        sys.exit()

    def boxListItemClicked(self, item):
        """Text box item selected. Need to update the text displayed
           in the text box from the box selected.

        Arguments:
            item {QListWidgetItem} -- Item selected.
        """
        boxId = item.text()
        originalText = self.driver.getOriginalTextFromBox(boxId)
        translatedText = self.driver.getTranslatedTextFromBox(boxId)

        self.oriText.editor.setPlainText(originalText)
        self.transText.editor.setPlainText(translatedText)

    def boxListItemChanged(self, item):
        """Box is checked or unchecked. Update the display to
           show box or not not show box respectively.

        Arguments:
            item {QListWidgetItem} -- Item selected.
        """
        boxId = item.text()
        if item.checkState() == Qt.Checked:
            self.graphicView.showBox(boxId)
        elif item.checkState() == Qt.Unchecked:
            self.graphicView.hideBox(boxId)

    def updateTextButtonClicked(self):
        """Set original text from the currently selected text box.
        """
        index = self.boxListWidget.currentIndex()
        boxId = index.row()
        if boxId != -1:
            text = self.oriText.editor.toPlainText()
            print(boxId, text)
            self.driver.setText(boxId, self.oriText.editor.toPlainText())

    def translateButtonClicked(self):
        """Translate all text selected by text box.
        """
        fromLang = self.fromLang.items.currentText()
        toLang = self.toLang.items.currentText()
        self.driver.translateTextForAllBoxes(fromLang, toLang)

    def loadAndProcessImage(self, imagePath):
        """ Load images and all information.

        Arguments:
            imagePath {string} -- Absolute path to the image.
        """
        if not self.driver.hasSubscriptionKey():
            QMessageBox.critical(self, 'No subscription key', 'Please set the subscription key in File->Setting.')
            return

        # Get the from and to language for translation.
        #
        fromLang = self.fromLang.items.currentText()
        toLang = self.toLang.items.currentText()
        loadImageSuccess = self.driver.loadAndProcessImage(imagePath, fromLang, toLang)

        if loadImageSuccess:
            # Clean up previous data.
            #
            self.clearData()

            # Add text boxes to list view.
            #
            self.updateBoxList()

            # Update image and display boxes.
            #
            self.graphicView.loadImage(imagePath)
            self.displayBoxesOnImage()

    def clearData(self):
        """Clear data from UI.
        """
        self.boxListWidget.clear()
        self.oriText.editor.clear()
        self.transText.editor.clear()

    def updateBoxList(self):
        """Update box list view with the actual boxes.
        """
        bubbleBoxes = self.driver.getBoxes()
        if bubbleBoxes is not None:
            for id, _ in bubbleBoxes.items():
                item = QListWidgetItem(str(id))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                self.boxListWidget.addItem(item)

    def displayBoxesOnImage(self):
        """ Display boxes on the image.
        """
        bubbleBoxes = self.driver.getBoxes()
        if bubbleBoxes is not None:
            for id, box in bubbleBoxes.items():
                self.graphicView.drawBox(id, box.xmin, box.ymin, box.width, box.height)

class LanguageSelection(QWidget):
    def __init__(self, labelText, languageList, parent=None):
        super(LanguageSelection, self).__init__(parent)

        self.label = QLabel(labelText)
        self.items = QComboBox()
        for lang in languageList:
            self.items.addItem(lang)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.items)
        self.setLayout(layout)

class TextDisplay(QWidget):
    def __init__(self, title, parent=None):
        super(TextDisplay, self).__init__(parent)

        self.label = QLabel(title)
        self.editor = QTextEdit()

        self.editor.setFontPointSize(16)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.editor)
        self.setLayout(layout)

class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.rubberBands = {}

        self.graphicsScene = QGraphicsScene()
        self.setScene(self.graphicsScene)
        self.setSceneRect(0,0,800,600)

        self.installEventFilter(self)

    def scrollContentsBy(self, dx, dy):
        for rubberBand in self.rubberBands.values():
            currentRect = rubberBand.geometry()
            currentRect.adjust(dx, dy, dx, dy)
            rubberBand.setGeometry(currentRect)

        QGraphicsView.scrollContentsBy(self, dx, dy)

    def showBox(self, id):
        self.rubberBands[id].show()

    def hideBox(self, id):
        self.rubberBands[id].hide()

    def drawBox(self, id, left, top, width, height):
        polygon = self.mapFromScene(left, top, width, height)
        rect = polygon.boundingRect()

        if (self.rubberBands.get(id) is not None):
            self.rubberBands[id].setGeometry(rect)
        else:
            rubberBand = RubberBand(id, QRubberBand.Rectangle, self)
            rubberBand.setGeometry(rect)
            rubberBand.show()
            self.rubberBands[id] = rubberBand

    def loadImage(self, imagePath):
        for rubberBand in self.rubberBands.values():
            rubberBand.close()

        self.rubberBands.clear()
        self.graphicsScene.clear()

        pixmap = QPixmap(imagePath)
        self.graphicsScene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))

    def eventFilter(self, obj, event):
        name = type(obj).__name__
        # print(name, event.type(), obj)
        return QGraphicsView.eventFilter(self, obj, event)

    def viewportEvent(self, event):
        # print("viewport", event.type())
        return QGraphicsView.viewportEvent(self, event)

class RubberBand(QRubberBand):
    def __init__(self, id, shape, parent=None):
        super(QRubberBand, self).__init__(shape, parent)
        self.id = id
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        name = type(obj).__name__
        # print(name, event.type(), obj)
        return QRubberBand.eventFilter(self, obj, event)

    def paintEvent(self, event):
        pen = QPen()
        pen.setStyle(Qt.SolidLine)
        pen.setColor(Qt.red)

        painter = QPainter(self)
        painter.setPen(pen)

        font = painter.font()
        font.setPointSize(20)
        painter.setFont(font)

        painter.drawText(event.rect(), Qt.AlignHCenter | Qt.AlignTop,  self.id)

        QRubberBand.paintEvent(self, event)


