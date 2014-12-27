#!/usr/bin/python
# -*- coding:utf8 -*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sip

class FocusEdit(QTextEdit):
    def __init__(self, parent=None):
        super(FocusEdit, self).__init__(parent)
        self.heightMin=60
        self.heightMax=1000
        self.document().contentsChanged.connect(self.sizeChange)
        
    def sizeChange(self):
        docHeight=self.document().size().height()
#         print docHeight
        if self.heightMin<=docHeight<=self.heightMax:
            self.setMaximumHeight(docHeight)
            self.emit(SIGNAL("change(int)"),docHeight)
        
    def focusOutEvent(self, event):
        self.emit(SIGNAL("EditFinish"))
    
    def mouseDoubleClickEvent(self, event):
        self.emit(SIGNAL("editing"))
        
class NoteLabel(QWidget):
    def __init__(self, memodata=None, parent=None):
        super(NoteLabel, self).__init__(parent)
        self.initObjects()
        self.setObjects(memodata)
        self.setMySizePolicy()
        self.setStyle()
        self.setEffects()
        self.content = memodata
        self.connect(self.contentEdit,SIGNAL("editing"),self.editing)
        self.connect(self.contentEdit, SIGNAL("EditFinish"),self.editFinish)
        
    def initObjects(self):
        self.palette = QPalette()
        self.layout = QHBoxLayout()
        self.timeLabel = QLabel()
        self.contentEdit = FocusEdit()
        
        pix = QPixmap(16, 16)
        pix.fill(Qt.black)
        self.actionTextColor = QAction(QIcon(pix), "&Color", self, \
                triggered=self.textColor)
        self.actionTextFont = QAction(QIcon('./img/font.png'), "&Font", self, \
                triggered=self.textFont)
        
    def setAllLabel(self, memodata):
        string = memodata['content']
        if string:
            self.contentEdit.setText(string)
        else:
            self.contentEdit.setText(u'内容为空')
        self.timeLabel.setText(memodata['deadline'])
        
    def setObjects(self, memodata):
        self.setAllLabel(memodata)
#         self.setPalette(self.palette)
        self.setTextDefaultFont()
        self.timeLabel.setMargin(10)
#         self.timeLabel.setPalette(self.palette)
#         self.timeLabel.setWordWrap(True)

        self.layout.addWidget(self.contentEdit)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.contentEdit.setReadOnly(True)
        self.layout.addSpacing(3)
        self.layout.addSpacing(3)
        self.layout.addWidget(self.timeLabel)
        self.setLayout(self.layout)
        
    def setMySizePolicy(self):
        self.setMinimumWidth(460)
        self.timeLabel.setMinimumWidth(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.contentEdit.setMaximumHeight(60)
        self.contentEdit.setMinimumHeight(60)
        self.contentEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.contentEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.contentEdit.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
#         self.contentEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def setStyle(self):
            label = '''
                QLabel{
                    border-radius: 4px;
                    background-color: #CCCCCC;
                    }
                QLabel:Hover{
                    border: 2px solid #DDDDDD;
                    }
            '''
            edit = '''
                QTextEdit{
                    border-top-left-radius: 4px;
                    border-bottom-left-radius: 4px;
                    background-color: #CCCCCC;
                    selection-color: #CCCCCC;
                    selection-background-color: #222222;
                    color: black;
                    }
            '''
    
    
            self.contentEdit.setStyleSheet(edit)
            self.timeLabel.setStyleSheet(label)
    def setFocus(self):
        self.textEdit.setFocus()
        
    def setText(self, text):
        self.textEdit.setText(text)
        
    def document(self):
        return self.textEdit.document()
    
    def save(self):
        self.textEdit.setDocument(self.textEdit.document())
        
    def setTextDefaultFont(self):
        font = QFont()
        font.setFamily('Microsoft YaHei')
        font.setPointSize(10)
        self.contentEdit.setFont(font)
        self.timeLabel.setFont(font)
        
    def setEffects(self):
        self.opacity = QGraphicsOpacityEffect()
        self.opacity.setOpacity(0.7)
        self.setGraphicsEffect(self.opacity)

    def changeEffects(self):
        self.opacity = QGraphicsOpacityEffect()
        self.opacity.setOpacity(0.9)
        self.setGraphicsEffect(self.opacity)
        
    def contextMenuEvent(self, event):
        self.menu = QMenu()
        self.menu.addAction(self.actionTextFont)
        self.menu.addAction(self.actionTextColor)

        self.menu.move(self.cursor().pos())
        self.menu.show()
        
    def textColor(self):
        currentColor = self.palette.color(QPalette.WindowText)
        color = QColorDialog.getColor(currentColor, self)
 
        if not color.isValid():
            return
        else:
            self.contentEdit.setTextColor(color)
            self.contentEdit.setEnabled(True)
            self.contentEdit.setFocus()
            self.contentEdit.setEnabled(False)
            
    def textFont(self):
        currentFont = self.contentEdit.font()
        font = QFontDialog.getFont(currentFont, self)
        if font[1]:
            self.contentEdit.setFont(font[0])
            self.timeLabel.setFont(font[0])
            self.actionTextFont.setFont(font[0])
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.pos()
            event.accept()
            
    def mouseMoveEvent(self, QMouseEvent):
        pw = self.parentWidget() # 获取父widget，也就是本程序中的主widget
        widget1 = pw.getTrashRect() # 获取主widget 的 垃圾箱widget（函数名没有改过来）
        flag = self.isCollide(widget1, self) # 检测两个widget的碰撞
        if flag:
            self.emit(SIGNAL('collideTrash'), True) # 碰撞就发射collideTrash信号
        else:
            self.emit(SIGNAL('collideTrash'), False)
        # 以下代码用于进行widget的拖拽
        if QMouseEvent.buttons() == Qt.LeftButton:
            self.move(QMouseEvent.globalPos() - self.dragPos)
            QMouseEvent.accept()

        if QMouseEvent.buttons() == Qt.RightButton:
            QMouseEvent.ignore()
            
    def mouseReleaseEvent(self, QMouseEvent):
        # 拖拽动作完成之后检测是否碰撞以确定该widget是否被删除
        pw = self.parentWidget()
        widget1 = pw.getTrashRect()
        flag = self.isCollide(widget1, self)
        if flag:
            self.emit(SIGNAL('collideTrash'), True)
            self.content['finished'] = True
            self.emit(SIGNAL('OneMemoFinish'), self.content['content'])
            print "emit meomofinish"
            sip.delete(self)
#             self.hide()
        else:
            self.emit(SIGNAL('collideTrash'), False)
            self.hide()
            self.show()
            
    def enterEvent(self, event):
        self.changeEffects()
        
    def leaveEvent(self, event):
        self.setEffects()
        
    def editdone(self):
        text = self.contentEdit.document()
        self.content['content'] = unicode(text.toPlainText())
        self.contentEdit.setText(text.toPlainText())
        datetime = self.currentData()
        self.content['deadline'] = unicode(datetime)
        self.contentEdit.setEnabled(False)
        self.timeLabel.setText(datetime)
        
    def editFinish(self):
        self.contentEdit.setReadOnly(True)
        self.timeUpdate()
        
    
    def timeUpdate(self):
        self.timeLabel.setText(QDateTime.currentDateTime().toString("yyyy/MM/dd hh:mm:ss"))
        
    def isCollide(self, widget1, widget2):
        dict1 = {}
        dict1['size'] = widget1.size()
        dict1['pos'] = widget1.pos()

        dict2 = {}
        dict2['size'] = widget2.size()
        dict2['pos'] = widget2.pos()

        r1TopRightX = dict1['pos'].x() + dict1['size'].width()
        r1TopRightY = dict1['pos'].y()
        r1BottomLeftX = dict1['pos'].x()
        r1BottomLeftY = dict1['pos'].y() + dict1['size'].height()

        r2TopRightX = dict2['pos'].x() + dict2['size'].width()
        r2TopRightY = dict2['pos'].y()
        r2BottomLeftX = dict2['pos'].x()
        r2BottomLeftY = dict2['pos'].y() + dict2['size'].height()
        if r1TopRightX > r2BottomLeftX and r1TopRightY < r2BottomLeftY \
                and r2TopRightX > r1BottomLeftX and r2TopRightY < r1BottomLeftY:
                    return True
        else:
            return False
        
    def getContent(self):
        return self.content
    
    def changelabelheight(self,height):
        self.deadlineLabel.setFixedHeight(height)
    
    def editing(self):
        self.contentEdit.setReadOnly(False)
