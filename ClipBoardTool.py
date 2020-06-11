# -*- coding: utf-8 -*-

import re
import sys
import sqlite3
import win32api
import win32gui
import win32con

from PyQt5.QtCore import Qt, QSize, QEvent
from PyQt5.QtGui import QFont, QCloseEvent, QKeyEvent, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QSpacerItem,
                             QToolButton, QTreeWidget, QVBoxLayout, QDialog,
                             QSizePolicy, QLineEdit, QMessageBox, QTreeWidgetItem,
                             QHeaderView, QLabel, QTextEdit, QComboBox, QPushButton,
                             QAbstractItemView, QMenu, QAction, QSystemTrayIcon)


# 退出选择对话框
class ExitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 状态，0表示取消，1表示退出，2表示托盘化
        self.status = 0

        font = QFont()
        font.setFamily('微软雅黑')
        self.setFont(font)
        self.setWindowIcon(QIcon('.\\clip.ico'))
        self.resize(250, 100)
        self.setWindowTitle('退出')
        self.verticalLayout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setText("确定要退出吗？")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QHBoxLayout()
        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacer_item)
        self.push_button_tray = QPushButton(self)
        self.push_button_tray.setText("托盘化")
        self.push_button_tray.setMinimumSize(QSize(0, 24))
        self.push_button_tray.setMaximumSize(QSize(16777215, 24))
        self.horizontalLayout.addWidget(self.push_button_tray)
        self.push_button_exit = QPushButton(self)
        self.push_button_exit.setText("退出")
        self.push_button_exit.setMinimumSize(QSize(0, 24))
        self.push_button_exit.setMaximumSize(QSize(16777215, 24))
        self.horizontalLayout.addWidget(self.push_button_exit)
        self.push_button_cancel = QPushButton(self)
        self.push_button_cancel.setText("取消")
        self.push_button_cancel.setMinimumSize(QSize(0, 24))
        self.push_button_cancel.setMaximumSize(QSize(16777215, 24))
        self.horizontalLayout.addWidget(self.push_button_cancel)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.push_button_tray.clicked.connect(self.tray)
        self.push_button_cancel.clicked.connect(self.reject)
        self.push_button_exit.clicked.connect(self.quit)

    def tray(self):
        self.status = 2
        self.accept()

    def quit(self):
        self.status = 1
        self.accept()


# 添加内容的对话框
class CreateContentDialog(QDialog):

    def __init__(self, parent=None, group_list=None, content=''):
        super().__init__(parent)

        self.add_content = None

        font = QFont()
        font.setFamily('微软雅黑')
        self.setFont(font)
        self.resize(350, 250)
        self.verticalLayout = QVBoxLayout(self)
        self.horizontalLayout = QHBoxLayout()
        self.label_sel_group = QLabel(self)
        self.label_sel_group.setMinimumSize(QSize(100, 24))
        self.label_sel_group.setMaximumSize(QSize(100, 24))
        self.horizontalLayout.addWidget(self.label_sel_group)
        self.combo_box_group = QComboBox(self)
        self.combo_box_group.addItems(group_list)
        self.combo_box_group.setEditable(True)
        self.combo_box_group.setMinimumSize(QSize(0, 24))
        self.combo_box_group.setMaximumSize(QSize(16777215, 24))
        self.horizontalLayout.addWidget(self.combo_box_group)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QHBoxLayout()
        self.label_key = QLabel(self)
        self.label_key.setMinimumSize(QSize(100, 24))
        self.label_key.setMaximumSize(QSize(100, 24))
        self.horizontalLayout_2.addWidget(self.label_key)
        self.line_edit_key = QLineEdit(self)
        self.line_edit_key.setMinimumSize(QSize(0, 24))
        self.line_edit_key.setMaximumSize(QSize(16777215, 24))
        self.horizontalLayout_2.addWidget(self.line_edit_key)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.text_edit_content = QTextEdit(self)
        self.text_edit_content.setText(content)
        self.verticalLayout.addWidget(self.text_edit_content)
        self.horizontalLayout_3 = QHBoxLayout()
        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacer_item)
        self.push_button_confirm = QPushButton(self)
        self.push_button_confirm.setMinimumSize(QSize(0, 24))
        self.push_button_confirm.setMaximumSize(QSize(16777215, 24))
        self.horizontalLayout_3.addWidget(self.push_button_confirm)
        self.push_button_cancel = QPushButton(self)
        self.push_button_cancel.setMinimumSize(QSize(0, 24))
        self.push_button_cancel.setMaximumSize(QSize(16777215, 24))
        self.horizontalLayout_3.addWidget(self.push_button_cancel)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.translate()

        self.push_button_confirm.clicked.connect(self.accept)
        self.push_button_cancel.clicked.connect(self.reject)

    def accept(self):
        group_name = self.combo_box_group.currentText()
        key_name = self.line_edit_key.text()
        content = self.text_edit_content.toPlainText()
        if group_name and key_name:
            self.add_content = (group_name, key_name, content)
            QDialog.accept(self)
        else:
            QMessageBox.information(self, '退出', '未输入组名和关键字！')

    def translate(self):
        self.setWindowTitle("添加内容")
        self.label_sel_group.setText("选择组")
        self.label_key.setText("设置关键字")
        self.push_button_confirm.setText("确定")
        self.push_button_cancel.setText("取消")


class EditContentDialog(CreateContentDialog):
    def __init__(self, parent=None, group_list=None, edit_content=None):
        group_name, key_name, content = edit_content

        super().__init__(parent, group_list, content)

        self.combo_box_group.setCurrentText(group_name)
        self.line_edit_key.setText(key_name)
        self.setWindowTitle('编辑内容')


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        # 定义主界面
        self.setWindowIcon(QIcon('.\\clip.ico'))
        # 主窗口的默认有右键菜单，默认的右键菜单不满足要求，因此采用以下语句停用
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setEnabled(True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet('QMainWindow { background-color: #F0F0F0 }'
                           'QWidget { font-family: \'Microsoft YaHei UI\' }')

        # 桌面控件
        desktop_widget = QApplication.desktop()
        desk_height = desktop_widget.height()
        desk_width = desktop_widget.width()
        self.window_width = 400
        self.window_height = 300
        self.setGeometry(int((desk_width - self.window_width) / 2),
                         int((desk_height - self.window_height) / 2),
                         self.window_width, self.window_height)
        # self.setWindowState(Qt.WindowMaximized)
        self.setMinimumSize(QSize(self.window_width, self.window_height))
        # 获得系统得剪切板
        self.clip_board = QApplication.clipboard()
        # 连接数据库
        self.db_conn = sqlite3.connect('clip_board_database.db')
        self.db_cursor = self.db_conn.cursor()
        # 是否置顶
        self.is_top = False
        # 是否移动
        self.on_move = False
        # 窗口状态
        self.window_status = ''
        # 记录鼠标的世界坐标
        self.mouse_start_point = None
        # 记录窗体的形状数据
        self.window_geo = None
        # 托盘图标
        self.tray_icon = QSystemTrayIcon(QIcon('.\\clip.ico'), self)
        self.tray_icon.setToolTip('自定义粘贴板')
        # 托盘菜单
        self.tray_icon_menu = QMenu(self)
        restore_action = QAction('还原', self)
        restore_action.triggered.connect(self.showNormal)
        quit_action = QAction('退出', self)
        quit_action.triggered.connect(QApplication.quit)
        self.tray_icon.activated.connect(self.restore_win)
        self.tray_icon_menu.addActions([restore_action, quit_action])
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.tray_icon.show()

        # 布局，创建子控件
        self.central_widget = QWidget(self)
        self.v_layout_main_window = QVBoxLayout(self.central_widget)
        self.v_layout_main_window.setContentsMargins(0, 0, 0, 0)
        self.v_layout_main_window.setSpacing(0)
        self.widget_title = QWidget(self.central_widget)
        self.horizontalLayout = QHBoxLayout(self.widget_title)
        spacer_item = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacer_item)
        self.horizontalLayout.setSpacing(0)
        self.tool_button_top = QToolButton(self.central_widget)
        self.tool_button_top.setIcon(QIcon('.\\top.ico'))
        self.tool_button_top.setIconSize(QSize(20, 20))
        self.tool_button_top.setStyleSheet('QToolButton { background-color: transparent;'
                                           'height: 20px; width: 20px; }')
        self.tool_button_top.setFocusPolicy(Qt.NoFocus)
        self.horizontalLayout.addWidget(self.tool_button_top)
        # self.tool_button_back = QToolButton(self.central_widget)
        # self.tool_button_back.setIcon(QIcon('.\\back.ico'))
        # self.tool_button_back.setIconSize(QSize(20, 20))
        # self.tool_button_back.setStyleSheet('QToolButton { background-color: transparent;'
        #                                     'height: 20px; width: 20px; }')
        # self.tool_button_back.setFocusPolicy(Qt.NoFocus)
        # self.horizontalLayout.addWidget(self.tool_button_back)
        self.tool_button_min = QToolButton(self.central_widget)
        self.tool_button_min.setIcon(QIcon('.\\min.ico'))
        self.tool_button_min.setIconSize(QSize(20, 20))
        self.tool_button_min.setStyleSheet('QToolButton { background-color: transparent;'
                                           'height: 20px; width: 20px; }')
        self.tool_button_min.setFocusPolicy(Qt.NoFocus)
        self.horizontalLayout.addWidget(self.tool_button_min)
        self.tool_button_max = QToolButton(self.central_widget)
        self.tool_button_max.setIcon(QIcon('.\\max.ico'))
        self.tool_button_max.setIconSize(QSize(20, 20))
        self.tool_button_max.setStyleSheet('QToolButton { background-color: transparent;'
                                           'height: 20px; width: 20px; }')
        self.tool_button_max.setFocusPolicy(Qt.NoFocus)
        self.horizontalLayout.addWidget(self.tool_button_max)
        self.tool_button_exit = QToolButton(self.central_widget)
        self.tool_button_exit.setIcon(QIcon('.\\close.ico'))
        self.tool_button_exit.setIconSize(QSize(20, 20))
        self.tool_button_exit.setStyleSheet('QToolButton { background-color: transparent;'
                                            'height: 20px; width: 20px; }')
        self.tool_button_exit.setFocusPolicy(Qt.NoFocus)
        self.horizontalLayout.addWidget(self.tool_button_exit)
        self.v_layout_main_window.addWidget(self.widget_title)
        self.v_layout_tree_view = QVBoxLayout()
        self.v_layout_tree_view.setContentsMargins(9, 0, 9, 9)
        self.v_layout_tree_view.setSpacing(6)
        self.h_layout_filter = QHBoxLayout()
        self.combo_box_group_name = QComboBox(self.central_widget)
        self.combo_box_group_name.setMinimumSize(QSize(120, 24))
        self.combo_box_group_name.setMaximumSize(QSize(120, 24))
        self.h_layout_filter.addWidget(self.combo_box_group_name)
        self.line_edit_key_filter = QLineEdit(self.central_widget)
        self.line_edit_key_filter.setMinimumSize(QSize(0, 24))
        self.line_edit_key_filter.setMaximumSize(QSize(16777215, 24))
        self.h_layout_filter.addWidget(self.line_edit_key_filter)
        self.combo_box_item_click_response = QComboBox(self.central_widget)
        self.combo_box_item_click_response.setMinimumSize(QSize(90, 24))
        self.combo_box_item_click_response.setMaximumSize(QSize(90, 24))
        self.combo_box_item_click_response.addItems(['复制', '复制并粘贴', '编辑'])
        self.h_layout_filter.addWidget(self.combo_box_item_click_response)
        self.v_layout_tree_view.addLayout(self.h_layout_filter)
        self.tree_widget_content_view = QTreeWidget(self.central_widget)
        self.tree_widget_content_view.header().setSectionResizeMode(QHeaderView.Stretch)
        self.tree_widget_content_view.setColumnCount(2)
        self.tree_widget_content_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.v_layout_tree_view.addWidget(self.tree_widget_content_view)
        self.v_layout_main_window.addLayout(self.v_layout_tree_view)
        self.setCentralWidget(self.central_widget)

        self.translate()

        self.tree_widget_content_view.itemClicked.connect(self.item_click_response)

        self.combo_box_group_name.currentIndexChanged.connect(self.group_filter)
        self.line_edit_key_filter.textChanged.connect(self.search_para)
        self.tool_button_top.clicked.connect(self.top_window)
        self.tool_button_max.clicked.connect(self.max_window)
        self.tool_button_min.clicked.connect(self.min_window)
        self.tool_button_exit.clicked.connect(self.close_window)

        self.display_clip_board_database()
        # self.create_clip_board_database()

    # 添加内容
    def add_clip_content(self):
        add_content = self.clip_board.text()
        if add_content:
            result = None
            try:
                result = self.db_cursor.execute(
                    '''SELECT KEY FROM CLIPBOARD WHERE CONTENT = \'%s\' ''' % add_content)
            except sqlite3.OperationalError as error:
                QMessageBox.information(self, '提示', str(error))
            if result:
                # 判断结果中是否有内容
                result_info = ''
                for row in result:
                    result_info += row[0] + '\n'
                if not result_info:
                    group_list = [gp for gp in self.get_database_dict()]
                    dialog = CreateContentDialog(self, group_list, add_content)
                    return_signal = dialog.exec_()
                    if return_signal == QDialog.Accepted:
                        group, key, content = dialog.add_content
                        self.add_clip_content_to_db(group, key, content)
                        self.display_clip_board_database()
                else:
                    result_info = '内容已存在以下关键字中：\n' + result_info
                    QMessageBox.information(self, '提示', result_info)

    # 添加内容到数据库
    def add_clip_content_to_db(self, group, key, content):
        self.db_cursor.execute(
            '''INSERT INTO CLIPBOARD (CONTENT_GROUP,KEY,CONTENT)
            VALUES (\'%s\', \'%s\', \'%s\')''' % (group, key, content))
        self.db_conn.commit()

    def close_window(self):
        QMainWindow.close(self)

    # 重载窗口关闭事件
    def closeEvent(self, event: QCloseEvent):
        if self.tray_icon.isVisible():
            origin_status_top = False
            if self.is_top:
                origin_status_top = True
                self.top_window()
            dialog = ExitDialog()
            dialog.exec_()
            if dialog.status == 1:
                QApplication.quit()
            elif dialog.status == 2:
                if origin_status_top:
                    self.top_window()
                self.hide()
                event.ignore()
            else:
                if origin_status_top:
                    self.top_window()
                event.ignore()
        # message = QMessageBox.warning(self, '退出', '''<p>确定要退出吗？''',
        #                               QMessageBox.Yes | QMessageBox.No)
        # if message == QMessageBox.Yes:
        #     event.accept()
        #     self.db_conn.close()
        # else:
        #     event.ignore()

    def create_clip_board_database(self):
        self.db_cursor.execute(
            '''CREATE TABLE CLIPBOARD(
            CONTENT_GROUP TEXT NOT NULL,
            KEY TEXT NOT NULL,
            CONTENT TEXT NOT NULL);''')
        self.db_conn.commit()
        self.db_cursor.execute(
            '''INSERT INTO CLIPBOARD (CONTENT_GROUP,KEY,CONTENT)
            VALUES (\'TEST_GROUP\', \'TEST_KEY\', \'TEST_CONTENT\')''')
        self.db_conn.commit()

    # 删除所选的内容
    def delete_contents(self):
        items = self.tree_widget_content_view.selectedItems()
        if items:
            message = QMessageBox.warning(self, '删除', '确定要删除所选组和内容吗？',
                                          QMessageBox.Yes | QMessageBox.No)
            if message == QMessageBox.Yes:
                for item in items:
                    if item.parent():
                        self.delete_content_in_database(item.parent().text(0),
                                                        item.text(0), item.text(1))
                    else:
                        self.delete_group_in_database(item.text(0))
                self.display_clip_board_database()

    # 删除数据库中的一条内容
    def delete_content_in_database(self, group, key, content):
        self.db_cursor.execute(
            '''DELETE FROM CLIPBOARD WHERE
            CONTENT_GROUP = \'%s\' AND
            KEY = \'%s\' AND 
            CONTENT = \'%s\'''' % (group, key, content))
        self.db_conn.commit()

    # 删除数据库中的组
    def delete_group_in_database(self, group_name):
        self.db_cursor.execute(
            '''DELETE FROM CLIPBOARD WHERE
            CONTENT_GROUP = \'%s\'''' % group_name)
        self.db_conn.commit()

    # 把数据库内容显示出来
    def display_clip_board_database(self):
        dict_content = self.get_database_dict()
        self.tree_widget_content_view.clear()
        self.combo_box_group_name.clear()
        if dict_content:
            grouplist = [gp for gp in dict_content]
            grouplist.insert(0, '全部组')
            self.combo_box_group_name.addItems(grouplist)
        for group_name in dict_content:
            top_item = QTreeWidgetItem(self.tree_widget_content_view)
            top_item.setText(0, group_name)
            for key_name, content in dict_content[group_name]:
                child_item = QTreeWidgetItem(top_item)
                child_item.setText(0, key_name)
                child_item.setText(1, content)
        if self.tree_widget_content_view.topLevelItemCount():
            self.tree_widget_content_view.expandAll()

    # 获得所有的数据存储在字典中
    def get_database_dict(self):
        dict_content = dict()
        data_rows = self.db_cursor.execute(
            '''SELECT CONTENT_GROUP,KEY,CONTENT FROM CLIPBOARD''')
        for row in data_rows:
            if row[0] not in dict_content:
                dict_content[row[0]] = list()
            dict_content[row[0]].append((row[1], row[2]))
        return dict_content

    # 按组过滤
    def group_filter(self, index):
        text = self.combo_box_group_name.itemText(index)
        count = self.tree_widget_content_view.topLevelItemCount()
        for i in range(count):
            item = self.tree_widget_content_view.topLevelItem(i)
            if text == '全部组':
                item.setHidden(False)
            else:
                if text != item.text(0):
                    item.setHidden(True)
                else:
                    item.setHidden(False)

    # 设置热键
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_V:
            if event.modifiers() == Qt.ControlModifier:
                self.add_clip_content()
                event.accept()
        if event.key() == Qt.Key_R:
            if event.modifiers() == Qt.ControlModifier:
                if self.tree_widget_content_view.topLevelItemCount():
                    self.tree_widget_content_view.collapseAll()
                event.accept()
        if event.key() == Qt.Key_E:
            if event.modifiers() == Qt.ControlModifier:
                if self.tree_widget_content_view.topLevelItemCount():
                    self.tree_widget_content_view.expandAll()
                event.accept()
        if event.key() == Qt.Key_Delete:
            self.delete_contents()
        else:
            event.ignore()

    # 最大化窗口
    def max_window(self):
        if self.isMaximized():
            self.showNormal()
            self.tool_button_max.setIcon(QIcon('.\\max.ico'))
        else:
            self.showMaximized()
            self.tool_button_max.setIcon(QIcon('.\\normal.ico'))

    # 最小化窗口
    def min_window(self):
        if not self.isMinimized():
            self.showMinimized()

    # 实现窗口拖动
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.on_move = True
            self.mouse_start_point = event.globalPos()
            self.window_geo = self.frameGeometry()
            if self.mouse_start_point.x() <= self.window_geo.left() + 9:
                if self.mouse_start_point.y() <= self.window_geo.top() + 9:
                    self.window_status = 'top_left'
                    self.setCursor(Qt.SizeFDiagCursor)
                elif self.mouse_start_point.y() >= self.window_geo.bottom() - 9:
                    self.window_status = 'bottom_left'
                    self.setCursor(Qt.SizeBDiagCursor)
                else:
                    self.window_status = 'left'
                    self.setCursor(Qt.SizeHorCursor)
            elif self.mouse_start_point.x() >= self.window_geo.right() - 9:
                if self.mouse_start_point.y() <= self.window_geo.top() + 9:
                    self.window_status = 'top_right'
                    self.setCursor(Qt.SizeBDiagCursor)
                elif self.mouse_start_point.y() >= self.window_geo.bottom() - 9:
                    self.window_status = 'bottom_right'
                    self.setCursor(Qt.SizeFDiagCursor)
                else:
                    self.window_status = 'right'
                    self.setCursor(Qt.SizeHorCursor)
            elif self.mouse_start_point.y() <= self.window_geo.top() + 9:
                self.window_status = 'top'
                self.setCursor(Qt.SizeVerCursor)
            elif self.mouse_start_point.y() >= self.window_geo.bottom() - 9:
                self.window_status = 'bottom'
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.window_status = 'move'
        QMainWindow.mousePressEvent(self, event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() and Qt.LeftButton and self.on_move:
            relative_pos = event.globalPos() - self.mouse_start_point
            if self.window_status == 'left':
                width = self.window_geo.right() - self.window_geo.left() - relative_pos.x()
                if width > self.window_width:
                    self.setGeometry(self.window_geo.left() + relative_pos.x(),
                                     self.window_geo.top(),
                                     width,
                                     self.window_geo.height())
            if self.window_status == 'right':
                width = self.window_geo.width() + relative_pos.x()
                if width > self.window_width:
                    self.setGeometry(self.window_geo.left(),
                                     self.window_geo.top(),
                                     width,
                                     self.window_geo.height())
            if self.window_status == 'top':
                height = self.window_geo.bottom() - self.window_geo.top() - relative_pos.y()
                if height > self.window_height:
                    self.setGeometry(self.window_geo.left(),
                                     self.window_geo.top() + relative_pos.y(),
                                     self.window_geo.width(),
                                     height)
            if self.window_status == 'bottom':
                height = self.window_geo.height() + relative_pos.y()
                if height > self.window_height:
                    self.setGeometry(self.window_geo.left(),
                                     self.window_geo.top(),
                                     self.window_geo.width(),
                                     height)
            if self.window_status == 'top_left':
                width = self.window_geo.right() - self.window_geo.left() - relative_pos.x()
                height = self.window_geo.bottom() - self.window_geo.top() - relative_pos.y()
                if width > self.window_width and height > self.window_height:
                    self.setGeometry(self.window_geo.left() + relative_pos.x(),
                                     self.window_geo.top() + relative_pos.y(),
                                     width,
                                     height)
            if self.window_status == 'top_right':
                width = self.window_geo.width() + relative_pos.x()
                height = self.window_geo.bottom() - self.window_geo.top() - relative_pos.y()
                if width > self.window_width and height > self.window_height:
                    self.setGeometry(self.window_geo.left(),
                                     self.window_geo.top() + relative_pos.y(),
                                     width,
                                     height)
            if self.window_status == 'bottom_right':
                width = self.window_geo.width() + relative_pos.x()
                height = self.window_geo.height() + relative_pos.y()
                if width > self.window_width and height > self.window_height:
                    self.setGeometry(self.window_geo.left(),
                                     self.window_geo.top(),
                                     width,
                                     height)
            if self.window_status == 'bottom_left':
                width = self.window_geo.right() - self.window_geo.left() - relative_pos.x()
                height = self.window_geo.height() + relative_pos.y()
                if width > self.window_width and height > self.window_height:
                    self.setGeometry(self.window_geo.left() + relative_pos.x(),
                                     self.window_geo.top(),
                                     width,
                                     height)
            if self.window_status == 'move':
                self.move(self.window_geo.topLeft() + relative_pos)
        QMainWindow.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # 改变移动状态
            self.window_status = ''
            self.on_move = False
            self.mouse_start_point = None
            self.window_geo = None
            self.setCursor(Qt.ArrowCursor)
        QMainWindow.mouseReleaseEvent(self, event)

    # 单击托盘时的响应
    def restore_win(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isHidden():
                self.show()
            self.activateWindow()

    # 搜索参数并显示在参数窗口里
    def search_para(self, key_name):
        text = self.combo_box_group_name.currentText()
        index = self.combo_box_group_name.currentIndex() - 1
        pattern = re.compile('.*' + key_name + '.*', re.I)
        if text == '全部组':
            count = self.tree_widget_content_view.topLevelItemCount()
            for i in range(count):
                num_key_in_show = 0
                item = self.tree_widget_content_view.topLevelItem(i)
                child_count = item.childCount()
                for child_index in range(child_count):
                    kn = item.child(child_index).text(0)
                    if re.match(pattern, kn):
                        item.child(child_index).setHidden(False)
                        num_key_in_show += 1
                    else:
                        item.child(child_index).setHidden(True)
                if num_key_in_show == 0:
                    item.setHidden(True)
                else:
                    item.setHidden(False)
        else:
            num_key_in_show = 0
            item = self.tree_widget_content_view.topLevelItem(index)
            child_count = item.childCount()
            for child_index in range(child_count):
                kn = item.child(child_index).text(0)
                if re.match(pattern, kn):
                    item.child(child_index).setHidden(False)
                    num_key_in_show += 1
                else:
                    item.child(child_index).setHidden(True)
            if num_key_in_show == 0:
                item.setHidden(True)
            else:
                item.setHidden(False)
        self.tree_widget_content_view.expandAll()

    # 将选中的内容添加到剪贴板中
    def item_click_response(self, item):
        if self.combo_box_item_click_response.currentText() == '编辑':
            if item.parent():
                group_list = [gp for gp in self.get_database_dict()]
                old_content = (item.parent().text(0), item.text(0), item.text(1))
                dialog = EditContentDialog(self, group_list, old_content)
                return_signal = dialog.exec_()
                if return_signal == QDialog.Accepted:
                    if old_content != dialog.add_content:
                        old_group, old_key, old_content = old_content
                        group, key, content = dialog.add_content
                        self.db_cursor.execute(
                            '''UPDATE CLIPBOARD SET CONTENT_GROUP = \'%s\', 
                            KEY = \'%s\', CONTENT = \'%s\' 
                            WHERE CONTENT_GROUP = \'%s\' AND 
                            KEY = \'%s\' AND 
                            CONTENT = \'%s\'''' % (group, key, content, old_group, old_key, old_content))
                        self.db_conn.commit()
                        self.display_clip_board_database()
        elif self.combo_box_item_click_response.currentText() == '复制':
            if item.parent():
                self.clip_board.setText(item.text(1))
        elif self.combo_box_item_click_response.currentText() == '复制并粘贴':
            if item.parent():
                self.clip_board.setText(item.text(1))
                focus_win_hwnd = xx = win32gui.GetFocus()
                hwnd_title = dict()

                def get_all_window(hwnd, mouse):

                    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and\
                            win32gui.IsWindowVisible(hwnd):
                        hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})
                win32gui.EnumWindows(get_all_window, 1)
                if hwnd_title:
                    hwnd_list = [h for h, t in hwnd_title.items()]
                    index = hwnd_list.index(focus_win_hwnd)
                    if self.is_top:
                        if index < len(hwnd_list) - 2:
                            focus_win_hwnd = hwnd_list[index + 2]
                            win32gui.SetForegroundWindow(focus_win_hwnd)
                            win32api.keybd_event(17, 0, 0, 0)
                            win32api.keybd_event(86, 0, 0, 0)
                            win32api.keybd_event(86, 0, win32con.KEYEVENTF_KEYUP, 0)
                            win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
                            win32api.keybd_event(13, 0, 0, 0)
                            win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
                    else:
                        if index < len(hwnd_list) - 1:
                            focus_win_hwnd = hwnd_list[index + 1]
                            win32gui.SetForegroundWindow(focus_win_hwnd)
                            win32api.keybd_event(17, 0, 0, 0)
                            win32api.keybd_event(86, 0, 0, 0)
                            win32api.keybd_event(86, 0, win32con.KEYEVENTF_KEYUP, 0)
                            win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
                            win32api.keybd_event(13, 0, 0, 0)
                            win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
        else:
            pass

    def top_window(self):
        if self.is_top:
            self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.MSWindowsOwnDC)
            self.show()
            self.is_top = False
            self.tool_button_top.setIcon(QIcon('.\\top.ico'))
        else:
            self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.show()
            self.is_top = True
            self.tool_button_top.setIcon(QIcon('.\\un_top.ico'))

    # 汉化
    def translate(self):
        self.setWindowTitle("MainWindow")
        self.tool_button_top.setToolTip('置顶')
        # self.tool_button_back.setToolTip('后台运行')
        self.tool_button_min.setToolTip('最小化')
        self.tool_button_max.setToolTip('最大化')
        self.tool_button_exit.setToolTip('关闭')
        self.line_edit_key_filter.setPlaceholderText("筛选器")
        self.tree_widget_content_view.headerItem().setText(0, '关键字')
        self.tree_widget_content_view.headerItem().setText(1, '内容')


def main():
    app = QApplication(sys.argv)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(QWidget(), '提示', '在这个操作系统上无法找到系统托盘')
        return app.exec_()

    QApplication.setQuitOnLastWindowClosed(False)

    # 创建主窗口
    main_window = MainWindow()
    # 显示主窗口
    main_window.show()
    return app.exec_()


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())