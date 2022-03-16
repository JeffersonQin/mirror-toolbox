from email.policy import default
import click
import cv2
from cv2 import rotate
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
g_fps = 60.0

def _cerr(caller: str, message: str):
	click.echo(click.style(f"[{caller}]", bg='magenta', fg='white'), nl=False)
	click.echo(click.style(f" {message}", fg = 'bright_red'))


def cerr(caller, *messages):
	val = ''
	for message in messages:
		val = val + ' ' + str(message)
	_cerr(caller, val)


def enum_callback(hwnd, params):
	if not str(win32gui.GetWindowText(hwnd)).startswith(window_name_prefix): return
	if win32gui.GetClassName(hwnd) != window_class: return
	global g_hwnd
	g_hwnd = hwnd	


def capture_screen(hwnd, x1, y1, x2, y2):
	# show window
	win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
	# get window position
	rect = win32gui.GetWindowRect(hwnd)
	cx = rect[0]
	cy = rect[1]
	cw = int((rect[2] - cx) * dpi_scale)
	ch = int((rect[3] - cy) * dpi_scale)
	# get screenshot param
	x = cx + x1 * dpi_scale
	y = cy + y1 * dpi_scale
	w = min((x2 - x1) * dpi_scale, cw)
	h = min((y2 - y1) * dpi_scale, ch)
	# take screenshot
	wDC = win32gui.GetWindowDC(hwnd)
	dcObj=win32ui.CreateDCFromHandle(wDC)
	cDC=dcObj.CreateCompatibleDC()
	dataBitMap = win32ui.CreateBitmap()
	dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
	cDC.SelectObject(dataBitMap)
	cDC.BitBlt((0, 0), (w, h) , dcObj, (x1, y1), win32con.SRCCOPY)
	dataBitMap.SaveBitmapFile(cDC, bmpfilenamename)
	# Free Resources
	dcObj.DeleteDC()
	cDC.DeleteDC()
	win32gui.ReleaseDC(hwnd, wDC)
	win32gui.DeleteObject(dataBitMap.GetHandle())


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
			if self.counter >= self.duration:
				self.status = False
				self.counter %= self.duration
		else:
			if self.counter >= self.interval:
				self.status = True
				self.counter %= self.interval


@click.group()
def cli():
	pass


@cli.command()
# hwnd
@click.option('--hwnd', default=None, help='hwnd of the window to capture')
# basic ROI
@click.option('--x1', default=None, type=int, help='top left horizontal coordinate of ROI')
@click.option('--y1', default=None, type=int, help='top left vertical coordinate of ROI')
@click.option('--x2', default=None, type=int, help='bottom right horizontal coordinate of ROI')
@click.option('--y2', default=None, type=int, help='bottom right vertical coordinate of ROI')
# affine rotate
@click.option('--use-affine-rotate', default=False, type=bool, help='use affining rotate')
@click.option('--affine-rotate-speed', default=10, type=float, help='affine rotate speed (% / second)')
# inverse effect
@click.option('--use-inverse-effect', default=False, type=bool, help='use inverse effect')
@click.option('--inverse-effect-interval', default=0.05, type=float, help='inverse effect interval (second)')
# rgb split glitch effect
@click.option('--use-rgb-split-glitch', default=False, type=bool, help='use rgb split glitch art effect')
@click.option('--use-tiktok-style', default=False, type=bool, help='use tiktok style rgb split glitch')
@click.option('--glitch-duration', default=0.5, type=float, help='rgb split glitch duration (second)')
@click.option('--glitch-interval', default=0.5, type=float, help='rgb split glitch interval (second)')
@click.option('--glitch-rx-offset-mean', default=5, type=float, help='glitch: mean X offset of R channel')
@click.option('--glitch-gx-offset-mean', default=-5, type=float, help='glitch: mean X offset of G channel')
@click.option('--glitch-bx-offset-mean', default=3, type=float, help='glitch: mean X offset of B channel')
@click.option('--glitch-ry-offset-mean', default=5, type=float, help='glitch: mean Y offset of R channel')
@click.option('--glitch-gy-offset-mean', default=-5, type=float, help='glitch: mean Y offset of G channel')
@click.option('--glitch-by-offset-mean', default=3, type=float, help='glitch: mean Y offset of B channel')
@click.option('--glitch-rx-offset-sd', default=2, type=float, help='glitch: sd of X offset of R channel')
@click.option('--glitch-gx-offset-sd', default=2, type=float, help='glitch: sd of X offset of G channel')
@click.option('--glitch-bx-offset-sd', default=2, type=float, help='glitch: sd of X offset of B channel')
@click.option('--glitch-ry-offset-sd', default=2, type=float, help='glitch: sd of Y offset of R channel')
@click.option('--glitch-gy-offset-sd', default=2, type=float, help='glitch: sd of Y offset of G channel')
@click.option('--glitch-by-offset-sd', default=2, type=float, help='glitch: sd of Y offset of B channel')
def start(
	hwnd, 
	x1, y1, x2, y2, 
	use_affine_rotate, affine_rotate_speed, 
	use_inverse_effect, inverse_effect_interval, 
	use_rgb_split_glitch, use_tiktok_style, 
	glitch_duration, glitch_interval, 
	glitch_rx_offset_mean, glitch_gx_offset_mean, glitch_bx_offset_mean,
	glitch_ry_offset_mean, glitch_gy_offset_mean, glitch_by_offset_mean,
	glitch_rx_offset_sd, glitch_gx_offset_sd, glitch_bx_offset_sd,
	glitch_ry_offset_sd, glitch_gy_offset_sd, glitch_by_offset_sd):
	'''
	Start toolbox
	'''
	global g_fps

	# hwnd
	if hwnd is None:
		win32gui.EnumWindows(enum_callback, None)
		if g_hwnd is None:
			raise Exception('No window found')
		hwnd = g_hwnd
	# shape
	width = x2 - x1
	height = y2 - y1

	# rotate top left
	rtl_side, rtl_pos = 0, 0.0
	# rotate top right
	rtr_side, rtr_pos = 1, 0.0

	# tiktok
	if use_tiktok_style:
		glitch_duration = 1
		glitch_interval = 0.00001
		glitch_rx_offset_mean = 0.0
		glitch_gx_offset_mean = 0.0
		glitch_bx_offset_mean = 0.0
		glitch_ry_offset_mean = 0.0
		glitch_gy_offset_mean = 0.0
		glitch_by_offset_mean = 0.0

	# inverse
	inverse_switcher = StatusSwitcher(False, inverse_effect_interval, inverse_effect_interval)

	# glitch
	glitch_switcher = StatusSwitcher(False, glitch_duration, glitch_interval)

	while True:
		# used to calculate fps
		start_time = time.time()

		try:
			capture_screen(hwnd, x1, y1, x2, y2)
		except Exception as e:
			cerr('capture_screen', repr(e))
			cerr('capture_screen', traceback.format_exc())
			continue

		img = cv2.imread(bmpfilenamename)
		img_processed = img

		if use_affine_rotate:
			rtl_side, rtl_pos = update_rotate(rtl_side, rtl_pos, affine_rotate_speed / g_fps)
			rtr_side, rtr_pos = update_rotate(rtr_side, rtr_pos, affine_rotate_speed / g_fps)

			rtl_x, rtl_y = calc_rotate(rtl_side, rtl_pos, width, height)
			rtr_x, rtr_y = calc_rotate(rtr_side, rtr_pos, width, height)

			affine_matrix = cv2.getAffineTransform(
				np.float32([[width / 2.0, height / 2.0], [0, 0], [width, 0]]),
				np.float32([[width / 2.0, height / 2.0], [rtl_x, rtl_y], [rtr_x, rtr_y]])
			)
			
			img_processed = cv2.warpAffine(img_processed, affine_matrix, (width, height))

		if use_inverse_effect:
			inverse_switcher.update()
			if inverse_switcher.status:
				img_processed = cv2.bitwise_not(img_processed)

		if use_rgb_split_glitch:
			glitch_switcher.update()
			if glitch_switcher.status:
				uxr = np.random.normal(glitch_rx_offset_mean, glitch_rx_offset_sd)
				uxg = np.random.normal(glitch_gx_offset_mean, glitch_gx_offset_sd)
				uxb = np.random.normal(glitch_bx_offset_mean, glitch_bx_offset_sd)
				uyr = np.random.normal(glitch_ry_offset_mean, glitch_ry_offset_sd)
				uyg = np.random.normal(glitch_gy_offset_mean, glitch_gy_offset_sd)
				uyb = np.random.normal(glitch_by_offset_mean, glitch_by_offset_sd)

				img_processed[:, :, 0] = cv2.warpAffine(img_processed[:, :, 0], 
					np.float32([[1, 0, uxr], [0, 1, uyr]]), (width, height))
				img_processed[:, :, 1] = cv2.warpAffine(img_processed[:, :, 1], 
					np.float32([[1, 0, uxg], [0, 1, uyg]]), (width, height))
				img_processed[:, :, 2] = cv2.warpAffine(img_processed[:, :, 2], 
					np.float32([[1, 0, uxb], [0, 1, uyb]]), (width, height))

		cv2.imshow('screenshot', img_processed)
		cv2.waitKey(1)

		# calculate fps
		end_time = time.time()
		g_fps = 1.0 / (end_time - start_time)

		print('fps: {:.2f}'.format(g_fps))


if __name__ == '__main__':
	cli()
