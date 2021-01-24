# -*- coding: utf-8 -*-
import sys, random
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer, QObject
from PyQt5 import QtCore


from threading import Timer
from time import time

APP_NAME = 'VeryCoolBall'
TICK_INTERVAL = 0.1

# 棋盘 9x9
CHESS_BOARD_ROW = 9
CHESS_BOARD_COLUMN = 9

# 棋盘里面球的颜色个数
NUM_OF_COLOR = 7

# 预测区域球的个数
NUM_OF_PRIDECT = 3

# 常量定义
DESK_WIDTH = 0
DESK_HEIGHT = 0


class UIType(object):
	InfoBoard = 'InfoBoard'
	ChessBoard = 'ChessBoard'
	StatisticBoard = 'StatisticBoard'

UI_CLS_MAPPING = {}

def register_ui_cls(name, bases, cls_dict):
	assert name not in UI_CLS_MAPPING
	klass = type(name, bases, cls_dict)
	UI_CLS_MAPPING[name] = klass
	return klass


def point_sub_xz(p1, p2):
	return p1[0] - p2[0], p1[-1] - p2[-1]

def point_add_xz(p1, p2):
	return p1[0] + p2[0], p1[-1] + p2[-1]


class GameWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.cur_width = int(DESK_WIDTH / 2)
		self.cur_height = int(2 * DESK_HEIGHT / 3)
		self.init_ui()
		self.paint_handle = []

		self.timer = Timer(TICK_INTERVAL, self.do_repaint)
		self.timer.start()

	def init_ui(self):
		self.setGeometry(0, 0, self.cur_width, self.cur_height)
		self.setWindowTitle("VeryCoolBall")
		self.show()

	def paintEvent(self, e):
		self.qp = QPainter()
		self.qp.begin(self)
		for func in self.paint_handle:
			func()
		self.qp.end()

	def do_repaint(self):
		self.update()
		self.timer = Timer(TICK_INTERVAL, self.do_repaint)
		self.timer.start()

	def append_paint_handle(self, func):
		self.paint_handle.append(func)

	def draw_point(self, pos, color=Qt.black):
		self.qp.setPen(color)
		self.qp.drawPoint(pos[0], pos[1])
		return True
	
	def draw_line(self, start_pos, end_pos, color=Qt.black):
		self.qp.setPen(color)
		self.qp.drawLine(start_pos[0], start_pos[1], end_pos[0], end_pos[1])
		return True

	def draw_box(self, left_up_pos, right_down_pos, color=Qt.black):
		self.qp.setPen(color)
		right_up_pos = right_down_pos[0], left_up_pos[1]
		left_down_pos = left_up_pos[0], right_down_pos[1]
		self.draw_line(left_up_pos, right_up_pos)
		self.draw_line(right_up_pos, right_down_pos)
		self.draw_line(right_down_pos, left_down_pos)
		self.draw_line(left_down_pos, left_up_pos)
		return True

	def draw_sphere(self, pos, radius, color=Qt.black):
		self.qp.setPen(color)
		# QT绘制单位就是1/16度，你必须单位换算
		self.qp.drawArc(pos[0], pos[-1], radius, radius, 0, 360 * 16)


class Game(object):

	def __init__(self, game_handle):
		super().__init__()
		self.game_handle = game_handle
		self.ui_manager = UIManager(self.game_handle)
		self.logic_manager = LogicManager()
		self.tick_timer = None
		self.has_init = False
		self.game_handle.append_paint_handle(self.game_tick)

	def init_game(self):
		assert self.has_init is False
		self.init_game_logic()
		self.init_game_ui()
		self.has_init = True

	def loop_game(self):
		self.ui_manager.refresh_ui()

	def game_tick(self):
		if not self.has_init:
			self.init_game()
		else:
			self.loop_game()

	def init_game_logic(self):
		# 初始化游戏逻辑，主要为确定七个小球的颜色，五到六个小球随机创建的位置和颜色，预测的小球颜色



	def init_game_ui(self):
		# 游戏UI分三块
		# 最上面一块放分数和接下来的球
		# 中间放整个棋盘
		# 最下面放每个球的数量统计

		handle_width = self.game_handle.cur_width
		handle_height = self.game_handle.cur_height
		print(handle_height, handle_width)
		self.ui_manager.craete_ui('InfoBoardUI', (0, 0), handle_width, handle_height * 0.15)
		self.ui_manager.craete_ui('ChessBoardUI', (0, handle_height * 0.15), handle_width, handle_height * 0.7)
		self.ui_manager.craete_ui('StatisticBoardUI', (0, handle_height * 0.85), handle_width, handle_height * 0.15)


class LogicManager(object):
	def __init__(self):
		self.logic_chess_panel = []

	def move_chess(self):
		# 处理
		pass

	def execute(self):
		# 进行一次对场上是否有联通棋子的判断
		pass

class LogicChessPanel(object):
	def __init__(self):
		self.width = CHESS_BOARD_COLUMN
		self.height = CHESS_BOARD_ROW


class LogicChess(object):
	def __init__(self):
		self.color = None
		self.pos = None
		self.is_visiable = False


class UIManager(object):

	def __init__(self, game_handle, create_pos=(0,0)):
		super().__init__()
		self.game_handle = game_handle
		self.ui = {}
		self.cur_ui_id = 0
		self.create_pos = create_pos

	def gen_ui_id(self):
		self.cur_ui_id += 1
		return self.cur_ui_id

	def craete_ui(self, ui_type, pos, width, height):
		ui_cls = UI_CLS_MAPPING[ui_type]
		ui_id = self.gen_ui_id()
		ui_obj = ui_cls(self, ui_id)
		assert ui_id not in self.ui
		self.ui[ui_id] = ui_obj
		chlid_ui_create_pos = point_add_xz(self.create_pos, pos)
		ui_obj.create(chlid_ui_create_pos, width, height)
		return ui_obj

	def refresh_ui(self):
		for ui_id, ui_inst in self.ui.items():
			ui_inst.refresh_ui()

class UIBase(object):
	
	def __init__(self, owner, ui_id):
		super().__init__()
		self.create_pos = None
		self.ui_id = ui_id
		self.width = None
		self.height = None
		self.owner = owner
		self.ui_view_cls = self.get_ui_view_cls()
		self.ui_logic_cls = self.get_ui_logic_cls()
		self.ui_view = self.ui_view_cls(self.owner.game_handle)
		self.ui_logic = self.ui_logic_cls()
		self.ui_manager = None

	def get_ui_view_cls(self):
		return UIView
	
	def get_ui_logic_cls(self):
		return UILogic

	def create(self, pos, width, height):
		self.create_pos = pos
		self.width = width
		self.height = height
		self.ui_manager = UIManager(self.owner.game_handle, create_pos=self.create_pos)
		self.ui_view.init_view_params(self.create_pos, self.width, self.height)

	def refresh_ui(self):
		self.ui_view.on_refresh()
		self.ui_manager.refresh_ui()

class UIView(object):
	def __init__(self, game_handle):
		super().__init__()
		self.game_handle = game_handle
		self.pos = None
		self.width = None
		self.height = None

	def init_view_params(self, pos, width, height):
		self.pos = pos
		self.width = width
		self.height = height

	def show_view(self):
		self.game_handle.draw_box(self.pos, (self.pos[0] + self.width, self.pos[1] + self.height))

	def on_refresh(self):
		return self.show_view()


class SphereUIView(UIView):
	def show_view(self):
		draw_pos = point_sub_xz(self.pos, (self.width / 2, self.width / 2))
		self.game_handle.draw_sphere(draw_pos, self.width)


class UILogic(object):
	pass

class InfoBoardUI(UIBase, metaclass=register_ui_cls):
	__metaclass__ = register_ui_cls

class ChessBoardUI(UIBase, metaclass=register_ui_cls):
	__metaclass__ = register_ui_cls

	def __init__(self, owner, ui_id):
		super(ChessBoardUI, self).__init__(owner, ui_id)
		self.chess_board_width = None
	
	def create(self, pos, width, height):
		super(ChessBoardUI, self).create(pos, width, height)
		self.chess_board_width = min(width, height)
		# 把棋盘居中摆放
		create_pos = (self.width - self.chess_board_width) / 2, (self.height - self.chess_board_width) / 2
		self.ui_manager.craete_ui('ChessBoardPanel', create_pos, self.chess_board_width, self.chess_board_width)


class ChessBoardPanel(UIBase, metaclass=register_ui_cls):
	def create(self, pos, width, height):
		super(ChessBoardPanel, self).create(pos, width, height)
		self.chess_block_width = width / CHESS_BOARD_COLUMN
		self.chess_block_height = height / CHESS_BOARD_ROW
		for row_num in range(CHESS_BOARD_ROW):
			for column_num in range(CHESS_BOARD_COLUMN):
				create_pos = self.chess_block_width * row_num, self.chess_block_height * column_num
				self.ui_manager.craete_ui('ChessBlock', create_pos, self.chess_block_width, self.chess_block_height)


class ChessBlock(UIBase, metaclass=register_ui_cls):
	def create(self, pos, width, height):
		super(ChessBlock, self).create(pos, width, height)
		# create_pos = self.width / 2, self.height / 2
		# self.ui_manager.craete_ui('Chess', create_pos, self.width * 0.9, 0)


class Chess(UIBase, metaclass=register_ui_cls):
	def get_ui_view_cls(self):
		return SphereUIView


class StatisticBoardUI(UIBase, metaclass=register_ui_cls):
	__metaclass__ = register_ui_cls
	


if __name__ == "__main__":
	app = QApplication(sys.argv)

	# 初始化屏幕长宽
	desktop = app.desktop()
	DESK_WIDTH = desktop.width()
	DESK_HEIGHT = desktop.height()

	game_window_handle = GameWidget()

	game = Game(game_window_handle)

	sys.exit(app.exec_())