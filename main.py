__author__ = 'Chris'
TIMESTAMP__FORMAT = "{0:%Y.%m.%d.%H.%M.%S}"
WORK_TIME_INTERVAL = 1000 * 60 * 25


import wx
import win32con
import datetime
import os

import logging
log = logging.getLogger(__name__)
DEFAULT_LOG_FILE_DIR = os.getcwd()


class Config():
    def append_to_log(self, message):
        time = datetime.datetime.now()
        filename = self.get_log_filename_for_date(time, None)
        with open(filename, "a") as f:
            f.write("\"{}\", \"{}\" \n".format(TIMESTAMP__FORMAT.format(time), message))

        output_string = message

    def get_log_filename_for_date(self, date_time, logdir=None):
        import csv, os
        time = date_time
        filename = "{0:%Y-%m-%d}".format(time) + ".log"
        if logdir:
            filename = os.path.join(logdir, filename) #gat abspath
        else:
            filename = os.path.join(DEFAULT_LOG_FILE_DIR, filename) #gat abspath
        return filename
    def get_last_log_line_for_file(self, filename):
        with open(filename, 'rb') as fh:
            last = fh.readlines()[-1].decode()
        return ','.join(last.split(',')[1:]).strip().strip('"')

    def get_last_log_line_for_today(self):
        import csv
        filename = self.get_log_filename_for_date(datetime.datetime.now())
        if not os.path.exists(filename):
            return ""
        else:
            with open(filename, 'rb') as log_file:
                log_reader = csv.reader(log_file, delimiter=",", quotechar='"')
                log_items = list(log_reader)
                if len(log_items) == 0:
                    return ""
                else:
                    return log_items[-1][1].strip().strip('"')

            return "default"


config = Config()

class PopupFrame(wx.Frame):
    def __init__(self, title, pos, size):
        wx.Frame.__init__(self, None, -1, title, pos, size)

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame("Settings", (50, 60), (550, 340))
        #frame.Show()
        self.SetTopWindow(frame)
        return True

class MyIcon(wx.TaskBarIcon):
    TBMENU_RESTORE = wx.NewId()
    TBMENU_CLOSE = wx.NewId()
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        # Set the image
        self.tbIcon = wx.Icon("favicon.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(self.tbIcon, "Test")
        # bind some events
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnTaskBarOpenSettings, id=self.TBMENU_RESTORE)
        self.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.OnTaskBarRightClick)
    def OnTaskBarRightClick(self, evt):
        menu = self.CreatePopupMenu()
        self.PopupMenu(menu)
        menu.Destroy()

    def OnTaskBarOpenSettings(self, evt):
        log.debug("hi")
        self.frame.Show()
        pass

    def OnTaskBarClose(self, evt):
        self.RemoveIcon()
        exit(0)
        self.frame.Close()

    def CreatePopupMenu(self, evt=None):
        menu = wx.Menu()
        menu.Append(self.TBMENU_RESTORE, "Open Settings")
        menu.Append(self.TBMENU_CLOSE, "Close")
        return menu

class MyFrame(wx.Frame):
    def __init__(self, title, pos, size):
        wx.Frame.__init__(self, None, -1, title, pos, size)
        menuFile = wx.Menu()
        menuFile.Append(1, "&About...")
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, "&File")

        self.SetMenuBar(menuBar)
        #setup icon
        icon = wx.Icon("favicon.png", wx.BITMAP_TYPE_PNG)
        self.tbicon = MyIcon(self)
        self.tbicon.SetIcon(icon, "Work Notes")

        #setup hotkey
        self.regHotKey()
        self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotKeyId)

        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        h_box = wx.BoxSizer(wx.HORIZONTAL)
        m_text = wx.StaticText(panel, -1, "Hello, world!")
        m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        #
        #       message=DirSelectorPromptStr, pos=DefaultPosition, size=DefaultSize,
        #       style=DIRP_DEFAULT_STYLE, validator=DefaultValidator,
        #       name=DirPickerCtrlNameStr)
        DirSelectorPromptStr = "DirSelectorPromptStr"
        self.logfile_directory_picker_ctrl = wx.DirPickerCtrl(panel, id=wx.ID_ANY, path=DEFAULT_LOG_FILE_DIR,
               message=DirSelectorPromptStr, pos=wx.DefaultPosition, size=wx.DefaultSize,
               style=wx.DIRP_DEFAULT_STYLE, validator=wx.DefaultValidator,
               name=wx.DirPickerCtrlNameStr)
        h_box.Add(m_text, 1, wx.ALL, 10)
        h_box.Add(self.logfile_directory_picker_ctrl, 3, wx.ALL, 10)
        box.Add(h_box, 0, wx.ALL, 10)

        panel.SetSizer(box)
        panel.Layout()

        self.Bind(wx.EVT_MENU, self.OnAbout, id=1)
        self.info_timer = wx.Timer(self)

        self.Bind(wx.EVT_TIMER, self.OnTimerEvent, self.info_timer)
        self.info_timer.Start(WORK_TIME_INTERVAL)

        log.debug("timer running?: {}".format(self.info_timer.IsRunning()))
        log.debug("timer interval?: {}".format(self.info_timer.GetInterval()))
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    def OnCloseWindow(self, evt):
        self.Hide()
        evt.Veto()
    def OnTimerEvent(self, evt):
        log.debug("Time logged -")
        self.ShowStatusUpdateDialog()
    def regHotKey(self):
        self.hotKeyId = 100
        self.RegisterHotKey(self.hotKeyId, win32con.MOD_ALT, win32con.VK_F5)
    def ShowStatusUpdateDialog(self):
        self.info_timer.Stop()
        dialog = wx.TextEntryDialog(None, "Status update", "text entry", config.get_last_log_line_for_today(), style=wx.OK|wx.CANCEL)
        dialog.Raise()
        dialog.SetFocus()
        dialog.Show()
        if dialog.ShowModal() == wx.ID_OK:
            date_string = TIMESTAMP__FORMAT.format(datetime.datetime.now())
            config.append_to_log(dialog.GetValue())
            log.debug("entered {}".format(dialog.GetValue()))
        self.info_timer.Start(WORK_TIME_INTERVAL)
        dialog.Destroy()
    def handleHotKey(self, evt):
        self.ShowStatusUpdateDialog()

        #frame = PopupFrame("Popup", (50, 60), (450, 340))
        #frame.Show()
        #self.SetTopWindow(frame)
        log.debug("do hotkey stuff")
    def OnAbout(self, event):
        wx.MessageBox("This is a Hello world sample",
                      "About Hello world", wx.OK | wx.ICON_INFORMATION, self)
    def OnIconTaskBarRight(self, event):
        log.debug("Right up")


def main():
    log.debug('hello world')
    app = MyApp(False)
    app.MainLoop()

if __name__=='__main__':
    main()