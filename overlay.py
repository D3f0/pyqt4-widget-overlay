from PyQt4 import QtCore, QtGui
from Queue import Queue

#    Building deployment manifest files
#    Estimating remaining time to complete bear production
#    Recognizing QR codes
#    Parsing XML Files
#    Building java path
#    Decafeinatting coffee for thirsty programmers 
#    Reconstructing sources from binaries
#    Downloading stage
TEST_TEXT = '''
    Formatting <b>local devices</b>
    This is a <a href="pmx://pepe">link</a> to pmx://pepe
'''

test_messages = map(lambda s: s.strip(), TEST_TEXT.strip().split('\n')) # text -> text list
print test_messages

class PMXMessageOverlay(object):
    messageFadedOut = QtCore.pyqtSignal()
    messageFadedIn = QtCore.pyqtSignal()
    ''' 
    NOTE: All subclasses should call updateMessagePosition on its resize event
    '''
    def __init__(self):
        
        self.messages = Queue()
        self.messageOverlay = LabelOverlayWidget(text = "", parent = self)
        
        self.messageOverlay.alpha = .1
        # Signals
        self.messageOverlay.fadedIn.connect(self.messageFadedIn)
        self.messageOverlay.fadedOut.connect(self.messageFadedOut)
        self.messageOverlay.linkActivated.connect(self.messageLinkActivated)
        
    def messageFadedIn(self):
        pass
    
    def messageFadedOut(self):
        pass
    
    def messageLinkActivated(self, link):
        print "Message link activated", link
        
    def showMessage(self, message, timeout = None, icon = None ):
        self.messageOverlay.setText(message)
        self.messageOverlay.updatePosition()
        self.messageOverlay.adjustSize()
        if unicode(message):
            self.messageOverlay.fadeIn()
        else:
            self.messageOverlay.fadeOut()
            print "No text"
    
    def updateMessagePosition(self):
        self.messageOverlay.updatePosition()

        
        
class LabelOverlayWidget(QtGui.QLabel):
    ''' 
    Inner message QLabel
    Don't use this widget separately, please use PMXMessageOverlay API
    '''
    fadedOut = QtCore.pyqtSignal()
    fadedIn = QtCore.pyqtSignal()
    
    
    STYLESHEET = '''
    QLabel {
        background-color: rgba(248, 240, 200, 30%);
        border: 1px solid;
        border-color: rgba(173, 114, 47, 30%);
        border-radius: 5px;
        padding: 2px;
    }
    '''
    
    def __init__(self, text="", parent=None):
        super(LabelOverlayWidget, self).__init__(text, parent)
        self.paddingLeft = 10
        self.paddingBottom = 10
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(32)
        self.timer.timeout.connect(self.updateAlpha)
        self.speed = 0
        self.setStyleSheet(self.STYLESHEET)
        self.hide()
    
    ALPHA_MAX = 255
    
    @property
    def alpha(self):
        return self.palette().color(QtGui.QPalette.WindowText).alpha() / float(self.ALPHA_MAX)
    
    @alpha.setter
    def alpha(self, value):
        if value < 0:
            value = 0
        value *= self.ALPHA_MAX
        self._updatePaletteAlpha([QtGui.QPalette.WindowText, 
                                  QtGui.QPalette.Background], value)
    
    
    
    def _updatePaletteAlpha(self, colorRole, alphaValue):
        '''
        @param palette: QtGui.QPalette instance
        '''
        palette = self.palette()
        if isinstance(colorRole, basestring):
            colorRole = [colorRole, ]
        for role in colorRole:
            color = palette.color(role)
            color.setAlpha(alphaValue)
            palette.setColor(role, color)
        self.setPalette(palette)
        
    def setParent(self, parent):
        self.updatePosition()
        return super(OverlayLabel, self).setParent(parent)
  
    def updatePosition(self):
        parentGeo = self.parent().geometry()
        if not parentGeo:
          return
        
        myGeo = self.geometry()
        #print parentGeo.width(), parentGeo.height()
        x = parentGeo.width() - self.width() - self.paddingLeft
        y = parentGeo.height() - self.height() - self.paddingBottom
        self.setGeometry(x, y, self.width(), self.height())
    
    def _setText(self, *args, **kwargs):
        retval = QtGui.QLabel.setText(self, *args, **kwargs)
        self.updatePosition()
    #    return retval
    
    def resizeEvent(self, event):
        super(LabelOverlayWidget, self).resizeEvent(event)
        self.updatePosition()
    
    def showEvent(self, event):
        self.updatePosition()
        return super(LabelOverlayWidget, self).showEvent(event)
  
    def enterEvent(self, event):
        print "Move"
        print self.styleSheet()
    
    FULL_THERSHOLD = 0.7
    DEFAULT_FADE_SPEED = 0.12
    
    def fadeIn(self, force = False):
        self.alpha = 0
        self.speed = self.DEFAULT_FADE_SPEED
        self.timer.start()
        
    def fadeOut(self, force = False):
        self.alpha = self.FULL_THERSHOLD
        self.speed = -self.DEFAULT_FADE_SPEED
        self.timer.start()
    
    def updateAlpha(self):
        
        if self.speed > 0:
            if self.isHidden():
                self.show()
            if self.alpha <= self.FULL_THERSHOLD:
                self.alpha += self.speed
            else:
                self.timer.stop()
                self.fadedOut.emit()
                
        elif self.speed < 0:
            if self.alpha >= 0:
                self.alpha += self.speed
            else:
                self.timer.stop()
                self.fadedIn.emit()
                self.hide()
                
    __backgroundColor = QtGui.QColor(248, 240, 200)
    @property
    def backgroundColor(self):
        return self.__backgroundColor
    
    @backgroundColor.setter       
    def backgroundColor(self, value):
            self.__backgroundColor = value
    
    
    __borderColor = QtGui.QColor(173, 114, 47)
    @property
    def borderColor(self):
        return self.__borderColor
    
    @borderColor.setter       
    def borderColor(self, value):
            self.__borderColor = value
            
    __opacity = 1.0
    @property
    def opacity(self):
        return self.__opacity
    
    @opacity.setter       
    def opacity(self, value):
            self.__opacity = value
                
            
#---------------------------------------------------------------------- 
# Example
#------------------------------------------------------------------------------ 

class ExampleOverlayedText(QtGui.QTextEdit, PMXMessageOverlay):
    def __init__(self, parent = None):
        QtGui.QTextEdit.__init__(self, parent)
        PMXMessageOverlay.__init__(self)
              
    def resizeEvent(self, event):
        
        super(ExampleOverlayedText, self).resizeEvent(event)
        self.updateMessagePosition()
        
    def messageLinkActivated(self, link):
        QtGui.QMessageBox.information(self, "Link activated", "You just clicked on %s" % link)

class Window(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi()
        
        self.lineedit.textChanged.connect(self.plaintext.showMessage)
        self.plaintext.setPlainText("Please type here...")
        
        
    def setupUi(self):
        self.setLayout(QtGui.QVBoxLayout())
        self.plaintext = ExampleOverlayedText()
        #self.plaintext = QtGui.QTextEdit()
        self.layout().addWidget(self.plaintext)
        self.lineedit = QtGui.QLineEdit()
        self.layout().addWidget(QtGui.QLabel("Test messages here:"))
        self.layout().addWidget(self.lineedit)
        
        
        

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
