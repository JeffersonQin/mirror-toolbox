import click
import cv2
import win32api
import win32con
import win32ui
import win32gui
import time
import traceback
import numpy as np

window_class = 'Qt5151QWindowIcon'
window_name_prefix = 'Classroom_'
window_exe = 'ClassIn.exe'

# TODO: 以后写 win32api 自动检测
dpi_scale = 1
bmpfilenamename = "screenshot.bmp"

g_hwnd = None


def _cerr(caller: str, message: str):
	click.echo(click.style(f"[{caller}]", bg='magenta', fg='white'), nl=False)
	click.echo(click.style(f" {message}", fg = 'bright_red'))


def cerr(caller, *messages):
	val = ''
	for message in messages:
		val = val + ' ' + str(message)
	_cerr(caller, val)


def enum_callback(hwnd, _):
	if not str(win32gui.GetWindowText(hwnd)).startswith(window_name_prefix): return
	if win32gui.GetClassName(hwnd) != window_class: return
	global g_hwnd
	g_hwnd = hwnd	


def update_rotate(side, pos, delta):
	pos += delta
	if pos > 1:
		pos -= 1
		side = (side + 1) % 4
	return side, pos


def calc_rotate(side, pos, width, height):
	if side == 0:
		return width * pos, 0
	if side == 1:
		return width, height * pos
	if side == 2:
		return width * (1 - pos), height
	if side == 3:
		return 0, height * (1 - pos)


class StatusSwitcher:

	def __init__(self, status, duration, interval):
		'''Constructor of StatusSwitcher
		===============================
		* :param: status: initial status
		* :param: duration: duration of status (True)
		* :param: interval: interval (False) between status
		'''
		self.status = status
		self.duration = duration
		self.interval = interval
		self.counter = 0.0
		self.last_time = time.time()


	def update(self):
		now_time = time.time()
		self.counter += now_time - self.last_time
		self.last_time = now_time

		if self.status is True:
			comparer = self.interval if self.duration is None else self.duration
			if self.counter >= comparer:
				self.status = False
				self.counter %= self.duration
		else:
			comparer = self.duration if self.interval is None else self.interval
			if self.counter >= comparer:
				self.status = True
				self.counter %= self.interval


class ToolBox:

	hwnd: int = None

	x1: int = 0
	y1: int = 0
	x2: int = 10
	y2: int = 10
	
	use_affine_rotate: bool = False
	affine_rotate_speed: float = 10.0
	
	use_inverse_effect: bool = False
	
	use_rgb_split_glitch: bool = False
	glitch_rx_offset_mean: float = 5.0
	glitch_gx_offset_mean: float = -5.0
	glitch_bx_offset_mean: float = 3.0
	glitch_ry_offset_mean: float = 5.0
	glitch_gy_offset_mean: float = -5.0
	glitch_by_offset_mean: float = 3.0
	glitch_rx_offset_sd: float = 2.0
	glitch_gx_offset_sd: float = 2.0
	glitch_bx_offset_sd: float = 2.0
	glitch_ry_offset_sd: float = 2.0
	glitch_gy_offset_sd: float = 2.0
	glitch_by_offset_sd: float = 2.0

	process_fps = 0.00000001


	def capture_screen(self):
		# show window
		win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
		# get window position
		rect = win32gui.GetWindowRect(self.hwnd)
		cx = rect[0]
		cy = rect[1]
		cw = int((rect[2] - cx) * dpi_scale)
		ch = int((rect[3] - cy) * dpi_scale)
		# get screenshot param
		x = cx + self.x1 * dpi_scale
		y = cy + self.y1 * dpi_scale
		w = min((self.x2 - self.x1) * dpi_scale, cw)
		h = min((self.y2 - self.y1) * dpi_scale, ch)
		# take screenshot
		wDC = win32gui.GetWindowDC(self.hwnd)
		dcObj=win32ui.CreateDCFromHandle(wDC)
		cDC=dcObj.CreateCompatibleDC()
		dataBitMap = win32ui.CreateBitmap()
		dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
		cDC.SelectObject(dataBitMap)
		cDC.BitBlt((0, 0), (w, h) , dcObj, (self.x1, self.y1), win32con.SRCCOPY)
		dataBitMap.SaveBitmapFile(cDC, bmpfilenamename)
		# Free Resources
		dcObj.DeleteDC()
		cDC.DeleteDC()
		win32gui.ReleaseDC(self.hwnd, wDC)
		win32gui.DeleteObject(dataBitMap.GetHandle())


	def init_hwnd(self):
		win32gui.EnumWindows(enum_callback, None)
		if g_hwnd is None:
			raise Exception('No window found')
		self.hwnd = g_hwnd


	def __init__(self, hwnd):
		if hwnd is None:
			self.init_hwnd()
		else:
			self.hwnd = hwnd

		# rotate top left
		self.rtl_side, self.rtl_pos = 0, 0.0
		# rotate top right
		self.rtr_side, self.rtr_pos = 1, 0.0

		self.glitch_switcher = StatusSwitcher(False, 0.5, 0.5)
		self.inverse_switcher = StatusSwitcher(False, 0.05, 0.05)


	def use_tiktok(self):
		self.glitch_switcher.duration = 1
		self.glitch_switcher.interval = 0.00001
		self.glitch_rx_offset_mean = 0.0
		self.glitch_gx_offset_mean = 0.0
		self.glitch_bx_offset_mean = 0.0
		self.glitch_ry_offset_mean = 0.0
		self.glitch_gy_offset_mean = 0.0
		self.glitch_by_offset_mean = 0.0


	def use_default_glitch(self):
		self.glitch_switcher.duration = 0.5
		self.glitch_switcher.interval = 0.5
		self.glitch_rx_offset_mean = 5.0
		self.glitch_gx_offset_mean = -5.0
		self.glitch_bx_offset_mean = 3.0
		self.glitch_ry_offset_mean = 5.0
		self.glitch_gy_offset_mean = -5.0
		self.glitch_by_offset_mean = 3.0
		self.glitch_rx_offset_sd = 2.0
		self.glitch_gx_offset_sd = 2.0
		self.glitch_bx_offset_sd = 2.0
		self.glitch_ry_offset_sd = 2.0
		self.glitch_gy_offset_sd = 2.0
		self.glitch_by_offset_sd = 2.0


	def show(self, fps):
		# used to calculate fps
		process_start = time.time()

		# shape
		width = self.x2 - self.x1
		height = self.y2 - self.y1

		# capture screen
		try:
			self.capture_screen()
		except Exception as e:
			cerr('capture_screen', repr(e))
			cerr('capture_screen', traceback.format_exc())
			return

		img = cv2.imread(bmpfilenamename)
		img_processed = img

		if self.use_affine_rotate:
			self.rtl_side, self.rtl_pos = update_rotate(self.rtl_side, self.rtl_pos, self.affine_rotate_speed / fps)
			self.rtr_side, self.rtr_pos = update_rotate(self.rtr_side, self.rtr_pos, self.affine_rotate_speed / fps)

			rtl_x, rtl_y = calc_rotate(self.rtl_side, self.rtl_pos, width, height)
			rtr_x, rtr_y = calc_rotate(self.rtr_side, self.rtr_pos, width, height)

			affine_matrix = cv2.getAffineTransform(
				np.float32([[width / 2.0, height / 2.0], [0, 0], [width, 0]]),
				np.float32([[width / 2.0, height / 2.0], [rtl_x, rtl_y], [rtr_x, rtr_y]])
			)
			
			img_processed = cv2.warpAffine(img_processed, affine_matrix, (width, height))

		if self.use_inverse_effect:
			self.inverse_switcher.update()
			if self.inverse_switcher.status:
				img_processed = cv2.bitwise_not(img_processed)

		if self.use_rgb_split_glitch:
			self.glitch_switcher.update()
			if self.glitch_switcher.status:
				uxr = np.random.normal(self.glitch_rx_offset_mean, self.glitch_rx_offset_sd)
				uxg = np.random.normal(self.glitch_gx_offset_mean, self.glitch_gx_offset_sd)
				uxb = np.random.normal(self.glitch_bx_offset_mean, self.glitch_bx_offset_sd)
				uyr = np.random.normal(self.glitch_ry_offset_mean, self.glitch_ry_offset_sd)
				uyg = np.random.normal(self.glitch_gy_offset_mean, self.glitch_gy_offset_sd)
				uyb = np.random.normal(self.glitch_by_offset_mean, self.glitch_by_offset_sd)

				img_processed[:, :, 0] = cv2.warpAffine(img_processed[:, :, 0], 
					np.float32([[1, 0, uxr], [0, 1, uyr]]), (width, height))
				img_processed[:, :, 1] = cv2.warpAffine(img_processed[:, :, 1], 
					np.float32([[1, 0, uxg], [0, 1, uyg]]), (width, height))
				img_processed[:, :, 2] = cv2.warpAffine(img_processed[:, :, 2], 
					np.float32([[1, 0, uxb], [0, 1, uyb]]), (width, height))

		cv2.imshow('screenshot', img_processed)
		cv2.waitKey(1)

		# calculate fps
		process_end = time.time()
		self.process_fps = 1.0 / (process_end - process_start)
