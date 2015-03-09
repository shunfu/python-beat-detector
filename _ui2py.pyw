# IMPORTANT: USE FILE NAMING "ui_about.ui"
#            USE HIGHESET LEVEL OBJECT NAMING "ui_about" (IDENTICAL)

import glob
import os

out="""
import sys

from PyQt4 import QtCore, QtGui

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    ### SET-UP WINDOWS
    """
showit=""
for pyc in glob.glob("*.pyc"):
    os.system("del %s"%pyc)
for ui in glob.glob("*.ui"):
    os.system ("pyuic4 -x %s -o %s"%(ui,ui.replace(".ui",".py")))
    out="import %s\n"%(ui.split(".")[0])+out
    uiname=ui.split("_")[1].split(".")[0]
    out+="""
    # WINDOW ~
    win_~ = ui_~.QtGui.QMainWindow()
    ui~ = ui_~.Ui_win_~()
    ui~.setupUi(win_~)\n""".replace("~",uiname)
    showit+="    win_~.show()\n".replace("~",uiname)

out+="\n    ### DISPLAY WINDOWS\n"+showit
out+="""
    #WAIT UNTIL QT RETURNS EXIT CODE
    sys.exit(app.exec_())"""
    
f=open("ui.py",'w')
f.write(out)
f.close()
print "DONE"