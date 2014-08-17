#!/usr/bin/python
# -*-coding:Latin-1 -*

import sys
import time
import os

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pygame
from hsaudiotag import auto

class MusicPlayer(QThread):
    notifyProgress = pyqtSignal(int)
    
    def __init__(self, path):
        QThread.__init__(self)
        # self.file will be used to get the file duration, and tags
        self.file = auto.File(path.replace('/', os.sep).replace('\\', os.sep))
        # pygame mixer will be used to play the file
        pygame.mixer.music.load(path.replace('/', os.sep).replace('\\', os.sep))
    
    def __del__(self):
        self.wait()
    
    def run(self):
        pygame.mixer.music.play()
        for i in range(self.file.duration + 1):
            self.notifyProgress.emit(i)
            time.sleep(1)
        
        while pygame.mixer.music.get_busy():
            pass
        
        self.exit()
        
    @property
    def duration(self):
        return self.file.duration

class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        
        self.music = MusicPlayer("C:\\LoginScreenIntro.mp3")
        self.music.notifyProgress.connect(self.onProgress)
        
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, self.music.duration)
        self.progressBar.setFormat("%vs - %ms")
        
        numberOfPlayersLabel = QLabel("Entrer le nombre de joueurs :")
        self.numberOfPlayersLine = QLineEdit()
        
        hostPresenceBox = QGroupBox("Y aura-t-il un animateur ?")
        self.hostPresence = QRadioButton("Oui")
        self.hostAbsence = QRadioButton("Non")
        self.hostPresence.setChecked(True)
        
        hostLayout = QHBoxLayout()
        hostLayout.addWidget(self.hostPresence)
        hostLayout.addWidget(self.hostAbsence)
        hostPresenceBox.setLayout(hostLayout)
        
        self.submitButton = QPushButton("&Valider")
        self.numberOfPlayersLine.returnPressed.connect(self.submitButton.click)
        
        configLayout = QVBoxLayout()
        configLayout.addWidget(self.progressBar)
        configLayout.addWidget(numberOfPlayersLabel)
        configLayout.addWidget(self.numberOfPlayersLine)
        configLayout.addWidget(hostPresenceBox)
        configLayout.addWidget(self.submitButton)
        
        self.submitButton.clicked.connect(self.submitConfiguration)
        
        mainLayout = QGridLayout()
        mainLayout.addLayout(configLayout, 0, 0)
        
        self.setLayout(mainLayout)
        self.setWindowTitle("Blind Test")
        
        self.music.start()
        
    def submitConfiguration(self):
        try:
            numberOfPlayers = int(self.numberOfPlayersLine.text())
            if numberOfPlayers <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.information(self, "Erreur de saisie", "Veuillez entrer un nombre positif")
        else:
            QMessageBox.information(self, "Config ok", "{0} joueur{1}{2}".format(numberOfPlayers, 
                                                                                "s" if numberOfPlayers > 1 else "", 
                                                                                " avec un animateur" if self.hostPresence.isChecked() else " sans animateur"))
        
    def onProgress(self, i):
        self.progressBar.setValue(i)

if __name__ == '__main__':
    pygame.mixer.pre_init()
    pygame.init()
    
    app = QApplication(sys.argv)
    
    interface = Form()
    interface.adjustSize()
    # Centering the window on screen
    interface.move(app.desktop().screen().rect().center() - interface.rect().center())
    interface.show()
    
    sys.exit(app.exec_())