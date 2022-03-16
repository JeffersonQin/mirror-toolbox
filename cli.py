import click
from toolbox import ToolBox


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
@click.option('--inverse-effect-duration', default=0.05, type=float, help='inverse effect duration (second)')
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
	use_inverse_effect, inverse_effect_duration, inverse_effect_interval, 
	use_rgb_split_glitch, use_tiktok_style, 
	glitch_duration, glitch_interval, 
	glitch_rx_offset_mean, glitch_gx_offset_mean, glitch_bx_offset_mean,
	glitch_ry_offset_mean, glitch_gy_offset_mean, glitch_by_offset_mean,
	glitch_rx_offset_sd, glitch_gx_offset_sd, glitch_bx_offset_sd,
	glitch_ry_offset_sd, glitch_gy_offset_sd, glitch_by_offset_sd):
	'''
	Start toolbox
	'''
	
	toolbox_instance = ToolBox(hwnd)
	toolbox_instance.x1 = x1
	toolbox_instance.y1 = y1
	toolbox_instance.x2 = x2
	toolbox_instance.y2 = y2
	toolbox_instance.use_affine_rotate = use_affine_rotate
	toolbox_instance.affine_rotate_speed = affine_rotate_speed
	toolbox_instance.use_inverse_effect = use_inverse_effect
	toolbox_instance.inverse_switcher.duration = inverse_effect_duration
	toolbox_instance.inverse_switcher.interval = inverse_effect_interval
	toolbox_instance.use_rgb_split_glitch = use_rgb_split_glitch
	toolbox_instance.glitch_switcher.duration = glitch_duration
	toolbox_instance.glitch_switcher.interval = glitch_interval
	toolbox_instance.glitch_rx_offset_mean = glitch_rx_offset_mean
	toolbox_instance.glitch_gx_offset_mean = glitch_gx_offset_mean
	toolbox_instance.glitch_bx_offset_mean = glitch_bx_offset_mean
	toolbox_instance.glitch_ry_offset_mean = glitch_ry_offset_mean
	toolbox_instance.glitch_gy_offset_mean = glitch_gy_offset_mean
	toolbox_instance.glitch_by_offset_mean = glitch_by_offset_mean
	toolbox_instance.glitch_rx_offset_sd = glitch_rx_offset_sd
	toolbox_instance.glitch_gx_offset_sd = glitch_gx_offset_sd
	toolbox_instance.glitch_bx_offset_sd = glitch_bx_offset_sd
	toolbox_instance.glitch_ry_offset_sd = glitch_ry_offset_sd
	toolbox_instance.glitch_gy_offset_sd = glitch_gy_offset_sd
	toolbox_instance.glitch_by_offset_sd = glitch_by_offset_sd

	if use_tiktok_style:
		toolbox_instance.use_tiktok()

	while True:
		toolbox_instance.show(toolbox_instance.process_fps)
		print('fps: {:.2f}'.format(toolbox_instance.process_fps))


if __name__ == '__main__':
	cli()
