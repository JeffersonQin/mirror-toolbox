import imgui
import glfw
import time
import OpenGL.GL as gl
import pickle
from imgui.integrations.glfw import GlfwRenderer
from toolbox import ToolBox


def impl_glfw_init():
    width, height = 880, 500
    window_name = 'Mirror Toolbox v0.1 by @JeffersonQin'

    if not glfw.init():
        print('Could not initialize OpenGL context')
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print('Could not initialize Window')
        exit(1)

    return window


def main():
	toolbox_instance = ToolBox(None)

	window = impl_glfw_init()
	imgui.create_context()
	impl = GlfwRenderer(window)

	total_fps = 0.0
	active = False

	while not glfw.window_should_close(window):
		start = time.time()

		glfw.poll_events()
		impl.process_inputs()

		imgui.new_frame()

		imgui.begin('Statistics')
		imgui.text('FPS: %.2f' % (total_fps))
		imgui.text('Process FPS: %.2f' % (toolbox_instance.process_fps))
		imgui.end()

		imgui.begin('Basic Settings')
		imgui.text('Capture Area')
		_, toolbox_instance.x1 = imgui.input_int(label='x1 [top left]', value=toolbox_instance.x1)
		_, toolbox_instance.y1 = imgui.input_int(label='y1 [top left]', value=toolbox_instance.y1)
		_, toolbox_instance.x2 = imgui.input_int(label='x2 [bottom right]', value=toolbox_instance.x2)
		_, toolbox_instance.y2 = imgui.input_int(label='y2 [bottom right]', value=toolbox_instance.y2)
		if toolbox_instance.x1 >= toolbox_instance.x2 or toolbox_instance.y1 >= toolbox_instance.y2:
			imgui.push_style_color(imgui.COLOR_TEXT, 255, 0, 0)
			imgui.text('Invalid capture area')
			imgui.pop_style_color()
		imgui.end()

		imgui.begin('Affine Rotate Effect')
		_, toolbox_instance.use_affine_rotate = imgui.checkbox(label='Use Affine Rotate', state=toolbox_instance.use_affine_rotate)
		imgui.text('Unit: % / second')
		_, toolbox_instance.affine_rotate_speed = imgui.input_float(label='Speed', value=toolbox_instance.affine_rotate_speed)
		imgui.end()

		imgui.begin('Inverse Effect')
		_, toolbox_instance.use_inverse_effect = imgui.checkbox(label='Use Inverse Effect', state=toolbox_instance.use_inverse_effect)
		imgui.text('Unit: second')
		_, toolbox_instance.inverse_switcher.duration = imgui.input_float(label='Duration', value=toolbox_instance.inverse_switcher.duration)
		_, toolbox_instance.inverse_switcher.interval = imgui.input_float(label='Interval', value=toolbox_instance.inverse_switcher.interval)
		imgui.end()

		imgui.begin('Glitch Effect')
		_, toolbox_instance.use_rgb_split_glitch = imgui.checkbox(label='Use Glitch Effect', state=toolbox_instance.use_rgb_split_glitch)
		if imgui.button(label='Use TikTok Style'):
			toolbox_instance.use_tiktok()
		if imgui.button(label='Use Default Style'):
			toolbox_instance.use_default_glitch()
		imgui.text('Unit: % / second')
		_, toolbox_instance.glitch_switcher.duration = imgui.input_float(label='Duration', value=toolbox_instance.glitch_switcher.duration)
		_, toolbox_instance.glitch_switcher.interval = imgui.input_float(label='Interval', value=toolbox_instance.glitch_switcher.interval)
		imgui.text('Unit: pixel')
		_, toolbox_instance.glitch_rx_offset_mean = imgui.input_float(label='Rx Offset Mean', value=toolbox_instance.glitch_rx_offset_mean)
		_, toolbox_instance.glitch_gx_offset_mean = imgui.input_float(label='Gx Offset Mean', value=toolbox_instance.glitch_gx_offset_mean)
		_, toolbox_instance.glitch_bx_offset_mean = imgui.input_float(label='Bx Offset Mean', value=toolbox_instance.glitch_bx_offset_mean)
		_, toolbox_instance.glitch_ry_offset_mean = imgui.input_float(label='Ry Offset Mean', value=toolbox_instance.glitch_ry_offset_mean)
		_, toolbox_instance.glitch_gy_offset_mean = imgui.input_float(label='Gy Offset Mean', value=toolbox_instance.glitch_gy_offset_mean)
		_, toolbox_instance.glitch_by_offset_mean = imgui.input_float(label='By Offset Mean', value=toolbox_instance.glitch_by_offset_mean)
		_, toolbox_instance.glitch_rx_offset_sd = imgui.input_float(label='Rx Offset SD', value=toolbox_instance.glitch_rx_offset_sd)
		_, toolbox_instance.glitch_gx_offset_sd = imgui.input_float(label='Gx Offset SD', value=toolbox_instance.glitch_gx_offset_sd)
		_, toolbox_instance.glitch_bx_offset_sd = imgui.input_float(label='Bx Offset SD', value=toolbox_instance.glitch_bx_offset_sd)
		_, toolbox_instance.glitch_ry_offset_sd = imgui.input_float(label='Ry Offset SD', value=toolbox_instance.glitch_ry_offset_sd)
		_, toolbox_instance.glitch_gy_offset_sd = imgui.input_float(label='Gy Offset SD', value=toolbox_instance.glitch_gy_offset_sd)
		_, toolbox_instance.glitch_by_offset_sd = imgui.input_float(label='By Offset SD', value=toolbox_instance.glitch_by_offset_sd)
		imgui.end()

		imgui.begin('General')
		_, active = imgui.checkbox(label='Active', state=active)
		imgui.text('Profile file: ./toolbox.bin')
		if imgui.button(label='Save Profile'):
			pickle.dump(toolbox_instance, open('toolbox.bin', 'wb+'))
		if imgui.button(label='Load Profile'):
			toolbox_instance: ToolBox = pickle.load(open('toolbox.bin', 'rb'))
			toolbox_instance.init_hwnd()
		imgui.end()

		gl.glClearColor(0., 0., 0., 0)
		gl.glClear(gl.GL_COLOR_BUFFER_BIT)

		imgui.render()
		impl.render(imgui.get_draw_data())
		glfw.swap_buffers(window)
		imgui.end_frame()

		if active:
			toolbox_instance.show(total_fps)

		end = time.time()
		total_fps = 1 / (end - start)

	impl.shutdown()
	glfw.terminate()


if __name__ == '__main__':
	main()
