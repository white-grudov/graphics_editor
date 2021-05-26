from tkinter import *
from tkinter import filedialog as fd, colorchooser, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageDraw, ImageFont, ImageFilter
import PIL.ImageOps
from copy import copy
import colorsys

root = Tk()
root.title('Графічний редактор')
root.geometry('1280x720')
root.resizable(width=False, height=False)
root.bind('<Control-q>', lambda event: root.destroy())

filename = None
pil_image = Image.new('RGB', (0, 0), color='white')
start_image = None
prev_image = None
image = None
region = None
scale = 100

x_coord, y_coord = 0, 0

default_width, default_height = 1105, 670
canvas_width, canvas_height = 1105, 670
d_top_margin, d_left_margin = 5, 150
top_margin, left_margin = 5, 150

start_crop_x, start_crop_y = 0, 0
temp_crop_x, temp_crop_y = 0, 0
end_crop_x, end_crop_y = 0, 0
crop_rect = None

do_blur = False
do_brightness = False
do_contrast = False
do_sharpness = False
do_histogram = False

do_draw = False
last_x, last_y = 0, 0
prev, start = None, None
tools, colors = None, None
enh_btn, line_btn, sqr_btn, crl_btn, sml_btn, color_ind, pipette = \
    Button(), Button(), Button(), Button(), Button(), Button(), Button()
brush_size = 5
brush_color = 'black'
brush_type = 'ENHANCED'

FILETYPES = (('All files', '*.*'),
             ('JPEG files', '*.jpg;*.jpeg'),
             ('PNG files', '*.png'),
             ('BMP files', '*.bmp'))


def resize(_):
    global region
    region = canvas.bbox(ALL)
    canvas.configure(scrollregion=region)


def key_pressed(event):
    global prev_image, pil_image
    if event.keysym == 'z':
        temp = pil_image
        pil_image = prev_image
        prev_image = temp
        load_image('')
    elif event.keysym == 's':
        save_image('')
    elif event.keysym == 'o':
        load_image('new')


def load_image(option: str):
    global filename, image, start_image, prev_image, pil_image, top_margin, left_margin

    if option == 'default':
        prev_image = pil_image
        pil_image = Image.new('RGB', (default_width, default_height), color='white')
        start_image = pil_image
    elif option == 'new':
        try:
            prev_image = pil_image
            filename = fd.askopenfilename(filetypes=FILETYPES)
            pil_image = Image.open(filename)
            start_image = pil_image
        except AttributeError:
            pass
    elif option == 'start':
        prev_image = pil_image
        pil_image = start_image
    elif option == 'prev':
        temp = pil_image
        pil_image = prev_image
        prev_image = temp
    else:
        pass

    canvas.delete(ALL)

    if scale != 100:
        w, h = pil_image.size
        scaled_image = pil_image.resize((int(w * scale / 100), int(h * scale / 100)), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(scaled_image)
    else:
        image = ImageTk.PhotoImage(pil_image)
    canvas.create_image(0, 0, anchor=NW, image=image)

    if image.width() < canvas_width:
        canvas.configure(width=image.width())
    else:
        canvas.configure(width=canvas_width)
    if image.height() < canvas_height:
        canvas.configure(height=image.height())
    else:
        canvas.configure(height=canvas_height)

    if image.width() < default_width:
        left_margin = d_left_margin + int((default_width - image.width()) / 2)
    else:
        left_margin = d_left_margin
    if image.height() < default_height:
        top_margin = d_top_margin + int((default_height - image.height()) / 2)
    else:
        top_margin = d_top_margin

    canvas.place(x=left_margin, y=top_margin)
    canvas.configure(scrollregion=canvas.bbox("all"))


def save_image(option: str):
    global filename
    if option == 'as' or filename is None:
        filename = fd.asksaveasfilename(filetypes=FILETYPES)
    if pil_image is not None:
        try:
            pil_image.save(filename)
        except ValueError:
            pass
    messagebox.showinfo(title='Повідомлення', message='Зображення збережено!')


def crop():
    crop_btn.config(background='light gray')

    canvas.bind('<ButtonPress-1>', lambda event: start_crop(event))
    canvas.bind('<B1-Motion>', lambda event: draw_crop(event))
    canvas.bind('<ButtonRelease-1>', lambda event: end_crop(event))
    root.bind('<Escape>', lambda event: suspend_crop(event))


def suspend_crop(_):
    global crop_rect
    canvas.delete(crop_rect)
    crop_btn.config(background='SystemButtonFace')

    canvas.unbind('<ButtonPress-1>')
    canvas.unbind('<B1-Motion>')
    canvas.unbind('<ButtonRelease-1>')
    root.unbind('<Escape>')


def start_crop(event):
    global start_crop_x, start_crop_y
    start_crop_x, start_crop_y = canvas.canvasx(event.x), canvas.canvasy(event.y)


def draw_crop(event):
    global temp_crop_x, temp_crop_y, crop_rect
    canvas.delete(crop_rect)
    temp_crop_x, temp_crop_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    crop_rect = canvas.create_rectangle(start_crop_x, start_crop_y,
                                        temp_crop_x, temp_crop_y,
                                        fill='gray', stipple='gray12', width=0)


def end_crop(event):
    global end_crop_x, end_crop_y

    end_crop_x, end_crop_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    root.bind('<Return>', lambda e: do_crop(e))


def do_crop(_):
    global pil_image, image, prev_image
    prev_image = pil_image
    pil_image = pil_image.crop((start_crop_x, start_crop_y,
                                end_crop_x, end_crop_y))
    canvas.delete(ALL)
    load_image('')
    crop_btn.config(background='SystemButtonFace')

    canvas.unbind('<ButtonPress-1>')
    canvas.unbind('<B1-Motion>')
    canvas.unbind('<ButtonRelease-1>')
    root.unbind('<Return>')


def rotate():
    global pil_image, prev_image
    prev_image = pil_image
    pil_image = pil_image.transpose(Image.ROTATE_270)
    load_image('')


def mirror():
    global pil_image, prev_image
    prev_image = pil_image
    pil_image = PIL.ImageOps.mirror(pil_image)
    load_image('')


def flip():
    global pil_image, prev_image
    prev_image = pil_image
    pil_image = PIL.ImageOps.flip(pil_image)
    load_image('')


def invert():
    global pil_image, prev_image
    prev_image = pil_image
    pil_image = PIL.ImageOps.invert(pil_image)
    load_image('')


def grayscale():
    global pil_image, prev_image
    prev_image = pil_image
    pil_image = PIL.ImageOps.grayscale(pil_image)
    load_image('')


def posterize():
    global pil_image, prev_image
    prev_image = pil_image
    pil_image = PIL.ImageOps.posterize(pil_image, 3)
    load_image('')


def solarize():
    global pil_image, prev_image
    prev_image = pil_image
    pil_image = PIL.ImageOps.solarize(pil_image, 64)
    load_image('')


def washout():
    global pil_image, prev_image
    prev_image = pil_image
    pil_image = pil_image.filter(ImageFilter.Color3DLUT.generate(17, do_washout))
    load_image('')


def do_washout(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    if 0.3 < h < 0.7:
        s = 0
    return colorsys.hsv_to_rgb(h, s, v)


def blur():
    global prev_image, pil_image, do_blur
    do_blur = True

    temp = prev_image
    prev_image = pil_image
    popup_win = Toplevel(root)
    popup_win.protocol("WM_DELETE_WINDOW", lambda: close_default(temp, popup_win))
    popup_win.title('Розмиття')
    popup_slider = Scale(popup_win, from_=0, to=100, orient=HORIZONTAL, length=200)
    popup_slider.pack()
    ok_btn = Button(popup_win, text='OK', command=lambda: end_blur(popup_win))
    ok_btn.pack(side=BOTTOM)
    change_blur(popup_win, popup_slider, 0)
    popup_slider.set(0)


def change_blur(popup_win: Toplevel, popup_slider: Scale, def_value: int):
    global prev_image, pil_image

    if do_blur:
        slider_value = def_value
        try:
            slider_value = popup_slider.get()
        except TclError:
            pass
        pil_image = prev_image
        pil_image = pil_image.filter(ImageFilter.GaussianBlur(slider_value))
        load_image('')
        canvas.after(200, lambda: change_blur(popup_win, popup_slider, slider_value))


def end_blur(popup_win: Toplevel):
    global do_blur
    do_blur = False
    popup_win.destroy()


def brightness():
    global prev_image, pil_image, do_brightness
    do_brightness = True

    temp = prev_image
    prev_image = pil_image
    popup_win = Toplevel(root)
    popup_win.protocol("WM_DELETE_WINDOW", lambda: close_default(temp, popup_win))
    popup_win.title('Яскравість')
    popup_slider = Scale(popup_win, from_=-100, to=100, orient=HORIZONTAL, length=200)
    popup_slider.pack()
    ok_btn = Button(popup_win, text='OK', command=lambda: end_brightness(popup_win))
    ok_btn.pack(side=BOTTOM)
    change_brightness(popup_win, popup_slider, 0)
    popup_slider.set(0)


def change_brightness(popup_win: Toplevel, popup_slider: Scale, def_value: int):
    global prev_image, pil_image

    if do_brightness:
        slider_value = def_value
        try:
            slider_value = popup_slider.get()
        except TclError:
            pass
        _scale = (slider_value + 100) / 100
        pil_image = prev_image
        enhancer = ImageEnhance.Brightness(pil_image)
        pil_image = enhancer.enhance(_scale)
        load_image('')
        canvas.after(200, lambda: change_brightness(popup_win, popup_slider, slider_value))


def end_brightness(popup_win: Toplevel):
    global do_brightness
    do_brightness = False
    popup_win.destroy()


def contrast():
    global prev_image, pil_image, do_contrast
    do_contrast = True

    temp = prev_image
    prev_image = pil_image
    popup_win = Toplevel(root)
    popup_win.protocol("WM_DELETE_WINDOW", lambda: close_default(temp, popup_win))
    popup_win.title('Контрастність')
    popup_slider = Scale(popup_win, from_=-100, to=100, orient=HORIZONTAL, length=200)
    popup_slider.pack()
    ok_btn = Button(popup_win, text='OK', command=lambda: end_contrast(popup_win))
    ok_btn.pack(side=BOTTOM)
    change_contrast(popup_win, popup_slider, 0)
    popup_slider.set(0)


def change_contrast(popup_win: Toplevel, popup_slider: Scale, def_value: int):
    global prev_image, pil_image

    if do_contrast:
        slider_value = def_value
        try:
            slider_value = popup_slider.get()
        except TclError:
            pass
        _scale = (slider_value + 100) / 100
        pil_image = prev_image
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(_scale)
        load_image('')
        canvas.after(200, lambda: change_contrast(popup_win, popup_slider, slider_value))


def end_contrast(popup_win: Toplevel):
    global do_contrast
    do_contrast = False
    popup_win.destroy()


def sharpness():
    global prev_image, pil_image, do_sharpness
    do_sharpness = True

    temp = prev_image
    prev_image = pil_image
    popup_win = Toplevel(root)
    popup_win.protocol("WM_DELETE_WINDOW", lambda: close_default(temp, popup_win))
    popup_win.title('Різкість')
    popup_slider = Scale(popup_win, from_=-100, to=100, orient=HORIZONTAL, length=200)
    popup_slider.pack()
    ok_btn = Button(popup_win, text='OK', command=lambda: end_sharpness(popup_win))
    ok_btn.pack(side=BOTTOM)
    change_sharpness(popup_win, popup_slider, 0)
    popup_slider.set(0)


def change_sharpness(popup_win: Toplevel, popup_slider: Scale, def_value: int):
    global prev_image, pil_image

    if do_sharpness:
        slider_value = def_value
        try:
            slider_value = popup_slider.get()
        except TclError:
            pass
        _scale = (slider_value + 100) / 100
        pil_image = prev_image
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(_scale)
        load_image('')
        canvas.after(200, lambda: change_sharpness(popup_win, popup_slider, slider_value))


def end_sharpness(popup_win: Toplevel):
    global do_sharpness
    do_sharpness = False
    popup_win.destroy()


def close_default(temp: Image, popup_win: Toplevel):
    global prev_image, pil_image, do_brightness, do_contrast, do_sharpness, do_histogram, do_blur
    do_brightness, do_contrast, do_sharpness, do_histogram, do_blur = False, False, False, False, False
    popup_win.destroy()
    pil_image = prev_image
    prev_image = temp
    load_image('')


def histogram():
    global prev_image, pil_image, do_histogram
    temp = prev_image
    prev_image = pil_image
    do_histogram = True

    hist_win = Toplevel(root)
    hist_win.title('Гістограма')
    hist_win.protocol("WM_DELETE_WINDOW", lambda: close_default(temp, hist_win))

    hist_cv = Canvas(hist_win, width=350, height=400, bg='white')
    hist_cv.pack()

    red = Scale(hist_win, from_=-100, to=100,
                orient=HORIZONTAL, label='Червоний', length=250)
    green = Scale(hist_win, from_=-100, to=100,
                  orient=HORIZONTAL, label='Зелений', length=250)
    blue = Scale(hist_win, from_=-100, to=100,
                 orient=HORIZONTAL, label='Синій', length=250)
    red.pack()
    green.pack()
    blue.pack()
    ok_btn = Button(hist_win, text='OK', command=lambda: end_histogram(hist_win))
    ok_btn.pack()

    RGB = (0, 0, 0)
    red.configure(command=lambda e: change_colors(red, green, blue, hist_cv, RGB))
    green.configure(command=lambda e: change_colors(red, green, blue, hist_cv, RGB))
    blue.configure(command=lambda e: change_colors(red, green, blue, hist_cv, RGB))
    change_colors(red, green, blue, hist_cv, RGB)


def change_colors(red: Scale, green: Scale, blue: Scale, hist_cv: Canvas, RGB: tuple):
    global prev_image, pil_image
    if do_histogram:
        pil_image = prev_image

        R, G, B, T = None, None, None, None
        try:
            R, G, B = Image.Image.split(pil_image)
        except ValueError:
            R, G, B, T = Image.Image.split(pil_image)

        r_var = red.get()
        g_var = green.get()
        b_var = blue.get()

        (r_prev, g_prev, b_prev) = RGB
        r_scale = (r_var - r_prev) / 100
        g_scale = (g_var - g_prev) / 100
        b_scale = (b_var - b_prev) / 100

        R = R.point(lambda i: i + int(round(i * r_scale)))
        G = G.point(lambda i: i + int(round(i * g_scale)))
        B = B.point(lambda i: i + int(round(i * b_scale)))

        try:
            pil_image = Image.merge(pil_image.mode, (R, G, B))
        except ValueError:
            pil_image = Image.merge(pil_image.mode, (R, G, B, T))
        load_image('')
        show_histogram(hist_cv)


def show_histogram(hist_cv: Canvas):
    global pil_image
    margin = 50
    height = 400
    hist_cv.delete(ALL)

    hist_cv.create_line(margin - 1, height - margin + 1, margin - 1 + 258, height - margin + 1)
    x_marker_start = margin - 1
    for i in range(0, 257, 64):
        x_marker = '%d' % i
        hist_cv.create_text(x_marker_start + i, height - margin + 7, text=x_marker)

    hist_cv.create_line(margin - 1, height - margin + 1, margin - 1, margin)
    y_marker_start = height - margin + 1
    for i in range(0, height - 2 * margin + 1, 50):
        y_marker = '%d' % i
        hist_cv.create_text(margin - 11, y_marker_start - i, text=y_marker)

    R, G, B = pil_image.histogram()[:256], pil_image.histogram()[256:512], pil_image.histogram()[512:768]
    for i in range(len(R)):
        pixel_no = R[i]
        hist_cv.create_oval(i + margin, height - pixel_no / 100 - 1 - margin,
                            i + 2 + margin, height - pixel_no / 100 + 1 - margin,
                            fill='red', outline='red')
    for i in range(len(G)):
        pixel_no = G[i]
        hist_cv.create_oval(i + margin, height - pixel_no / 100 - 1 - margin,
                            i + 2 + margin, height - pixel_no / 100 + 1 - margin,
                            fill='green', outline='green')
    for i in range(len(B)):
        pixel_no = B[i]
        hist_cv.create_oval(i + margin, height - pixel_no / 100 - 1 - margin,
                            i + 2 + margin, height - pixel_no / 100 + 1 - margin,
                            fill='blue', outline='blue')


def end_histogram(hist_win: Toplevel):
    global do_histogram
    do_histogram = False
    hist_win.destroy()


def draw_(_):
    global prev, start, prev_image, start_image, do_draw, scale
    do_draw = not do_draw
    brush_tools()

    if do_draw:
        scale = 100
        load_image('')
        scale_lbl.config(text=str(scale) + '%')
        canvas.unbind('<MouseWheel>')

        draw_btn.config(background='light gray')
        prev = copy(pil_image)
        start = copy(start_image)
        prev_image = pil_image

        canvas.bind('<Button-1>', xy)
        canvas.bind('<B1-Motion>', do_draw_)
        root.bind('<Return>', lambda event: draw_(event))
    else:
        prev_image = prev
        start_image = start
        draw_btn.config(background='SystemButtonFace')

        canvas.delete(ALL)
        load_image('')

        canvas.unbind('<Button-1>')
        canvas.unbind('<B1-Motion>')
        canvas.bind('<MouseWheel>', zoom)
        root.unbind('<Return>')


def xy(event):
    global last_x, last_y
    last_x, last_y = canvas.canvasx(event.x), canvas.canvasy(event.y)


def do_draw_(event):
    global last_x, last_y, prev_image, pil_image, brush_color, brush_size
    brush_size = int(brush_size)

    if do_draw:
        x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)

        pil_image = prev_image
        draw = ImageDraw.Draw(pil_image)

        if brush_type == 'ENHANCED':
            canvas.create_line((last_x, last_y, x, y),
                               fill=brush_color,
                               width=brush_size * 2)
            canvas.create_oval(x - brush_size, y - brush_size, x + brush_size, y + brush_size,
                               fill=brush_color,
                               outline=brush_color)
            draw.line((last_x, last_y, x, y),
                      fill=brush_color,
                      width=brush_size * 2)
            draw.ellipse((x - brush_size, y - brush_size, x + brush_size, y + brush_size),
                         fill=brush_color,
                         outline=brush_color)
        elif brush_type == 'LINE':
            canvas.create_line((last_x, last_y, x, y),
                               fill=brush_color,
                               width=brush_size * 2)
            draw.line((last_x, last_y, x, y),
                      fill=brush_color,
                      width=brush_size * 2)
        elif brush_type == 'SQUARE':
            canvas.create_rectangle(x - brush_size, y - brush_size, x + brush_size, y + brush_size,
                                    fill=brush_color,
                                    outline=brush_color)
            draw.rectangle((x - brush_size, y - brush_size, x + brush_size, y + brush_size),
                           fill=brush_color,
                           outline=brush_color)
        elif brush_type == 'CIRCLE':
            canvas.create_oval(x - brush_size, y - brush_size, x + brush_size, y + brush_size,
                               fill=brush_color,
                               outline=brush_color)
            draw.ellipse((x - brush_size, y - brush_size, x + brush_size, y + brush_size),
                         fill=brush_color,
                         outline=brush_color)
        elif brush_type == 'SMILE':
            canvas.create_text(x, y, font='Arial ' + str(brush_size * 2), fill=brush_color, text='=)')
            draw.text((x, y), font=ImageFont.truetype('arial.ttf', brush_size * 2), fill=brush_color, text='=)')

        last_x, last_y = x, y


def brush_tools():
    global tools, colors, enh_btn, line_btn, sqr_btn, crl_btn, sml_btn, color_ind, pipette

    if do_draw:
        tools = LabelFrame(root, text='Малювання')
        colors = Frame(tools)
        sizes = Frame(tools)
        slider = Frame(sizes)
        brushes = Frame(slider)

        black = color_button('#000000')
        black.grid(row=0, column=0, padx=2, pady=2)
        white = color_button('#FFFFFF')
        white.grid(row=0, column=1, padx=2, pady=2)
        azure4 = color_button('#838B8B')
        azure4.grid(row=1, column=0, padx=2, pady=2)
        gray = color_button('#808080')
        gray.grid(row=1, column=1, padx=2, pady=2)
        red4 = color_button('#8B0000')
        red4.grid(row=2, column=0, padx=2, pady=2)
        red = color_button('#FF0000')
        red.grid(row=2, column=1, padx=2, pady=2)
        orange = color_button('#FFA500')
        orange.grid(row=3, column=0, padx=2, pady=2)
        yellow = color_button('#FFFF00')
        yellow.grid(row=3, column=1, padx=2, pady=2)
        green = color_button('#008000')
        green.grid(row=4, column=0, padx=2, pady=2)
        l_green = color_button('#90EE90')
        l_green.grid(row=4, column=1, padx=2, pady=2)
        steelblue3 = color_button('#4F94CD')
        steelblue3.grid(row=5, column=0, padx=2, pady=2)
        l_blue = color_button('#ADD8E6')
        l_blue.grid(row=5, column=1, padx=2, pady=2)
        navy = color_button('#000080')
        navy.grid(row=6, column=0, padx=2, pady=2)
        blue = color_button('#0000FF')
        blue.grid(row=6, column=1, padx=2, pady=2)
        purple = color_button('#800080')
        purple.grid(row=7, column=0, padx=2, pady=2)
        pink = color_button('#FFC0CB')
        pink.grid(row=7, column=1, padx=2, pady=2)
        colors.grid(row=0, column=0)

        choose = Button(sizes, text='Інший колір', relief='ridge', command=lambda: color_change(None))
        choose.grid(row=0, column=0, padx=1, pady=1)
        size = Scale(slider, from_=1, to=50, length=205, relief='flat', command=brush_slider)
        size.set(brush_size)
        size.grid(row=0, column=0, padx=1, pady=1)
        sizes.grid(row=0, column=1)

        enh_btn = Button(brushes, text='🖌', width=2, command=lambda: change_brush('ENHANCED'),
                         relief='ridge', background='light gray')
        line_btn = Button(brushes, text='/', width=2, relief='ridge', command=lambda: change_brush('LINE'))
        sqr_btn = Button(brushes, text='■', width=2, relief='ridge', command=lambda: change_brush('SQUARE'))
        crl_btn = Button(brushes, text='●', width=2, relief='ridge', command=lambda: change_brush('CIRCLE'))
        sml_btn = Button(brushes, text='=)', width=2, relief='ridge', command=lambda: change_brush('SMILE'))
        color_ind = Button(brushes, width=2, relief='ridge', bg=brush_color, state=DISABLED)
        pipette = Button(brushes, text='💉', width=2, relief='ridge', bg='#D7E7E8', command=eyedropper)

        pipette.grid(row=0, column=0, padx=1, pady=2)
        enh_btn.grid(row=1, column=0, padx=1, pady=2)
        line_btn.grid(row=2, column=0, padx=1, pady=2)
        sqr_btn.grid(row=3, column=0, padx=1, pady=2)
        crl_btn.grid(row=4, column=0, padx=1, pady=2)
        sml_btn.grid(row=5, column=0, padx=1, pady=2)
        color_ind.grid(row=6, column=0, padx=1, pady=2)
        brushes.grid(row=0, column=1)
        slider.grid(row=1, column=0)

        tools.place(x=5, y=170)
    else:
        tools.destroy()


def eyedropper():
    pipette.config(bg='#B3D4D6')
    canvas.bind('<Button-1>', lambda event: take_color(event))


def take_color(event):
    pipette.config(bg='#D7E7E8')
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    canvas.unbind('<Button-1>')
    canvas.bind('<Button-1>', xy)
    r, g, b = pil_image.getpixel((x, y))
    color_change('#%02x%02x%02x' % (r, g, b))


def color_button(color: str):
    btn = Button(colors, background=color, width=2, relief='ridge', command=lambda: color_change(color))
    return btn


def color_change(color: str or None):
    global brush_color
    if color is None:
        (rgb, hx) = colorchooser.askcolor()
        brush_color = hx
    else:
        brush_color = color
    color_ind.config(bg=brush_color)


def brush_slider(size: int):
    global brush_size
    brush_size = size


def change_brush(new_type: str):
    global brush_type
    brush_type = new_type

    if brush_type == 'LINE':
        line_btn.config(background='light gray')
        sqr_btn.config(background='SystemButtonFace')
        crl_btn.config(background='SystemButtonFace')
        enh_btn.config(background='SystemButtonFace')
        sml_btn.config(background='SystemButtonFace')
    elif brush_type == 'SQUARE':
        line_btn.config(background='SystemButtonFace')
        sqr_btn.config(background='light gray')
        crl_btn.config(background='SystemButtonFace')
        enh_btn.config(background='SystemButtonFace')
        sml_btn.config(background='SystemButtonFace')
    elif brush_type == 'CIRCLE':
        line_btn.config(background='SystemButtonFace')
        sqr_btn.config(background='SystemButtonFace')
        crl_btn.config(background='light gray')
        enh_btn.config(background='SystemButtonFace')
        sml_btn.config(background='SystemButtonFace')
    elif brush_type == 'ENHANCED':
        line_btn.config(background='SystemButtonFace')
        sqr_btn.config(background='SystemButtonFace')
        crl_btn.config(background='SystemButtonFace')
        enh_btn.config(background='light gray')
        sml_btn.config(background='SystemButtonFace')
    elif brush_type == 'SMILE':
        line_btn.config(background='SystemButtonFace')
        sqr_btn.config(background='SystemButtonFace')
        crl_btn.config(background='SystemButtonFace')
        enh_btn.config(background='SystemButtonFace')
        sml_btn.config(background='light gray')


def change_size():
    global prev_image, pil_image

    temp = prev_image
    prev_image = pil_image
    popup_win = Toplevel(root)
    popup_win.protocol("WM_DELETE_WINDOW", lambda: close_default(temp, popup_win))
    popup_win.title('Змінити розмір')
    frame = Frame(popup_win)

    label1 = Label(frame, text='Ширина:', font=10)
    label2 = Label(frame, text='Висота:', font=10)
    field1 = Entry(frame, width=10, font=10)
    field2 = Entry(frame, width=10, font=10)
    field1.insert(0, pil_image.size[0])
    field2.insert(0, pil_image.size[1])

    label1.grid(row=0, column=0, padx=3, pady=3)
    label2.grid(row=1, column=0, padx=3, pady=3)
    field1.grid(row=0, column=1, padx=3, pady=3)
    field2.grid(row=1, column=1, padx=3, pady=3)

    ok_btn = Button(popup_win, text='OK')
    ok_btn.pack(side=BOTTOM, padx=3, pady=3)
    frame.pack()

    ok_btn.config(command=lambda: do_change_size(popup_win, int(field1.get()), int(field2.get())))


def do_change_size(popup_win: Toplevel, w: int, h: int):
    global prev_image, pil_image

    pil_image = prev_image
    pil_image = pil_image.resize((w, h), Image.ANTIALIAS)
    load_image('')
    popup_win.destroy()


def zoom(event):
    global scale
    if event.delta > 0:
        if scale < 150:
            scale += 10
        else:
            scale += 50
    elif event.delta < 0 and scale > 15:
        if scale < 150:
            scale -= 10
        else:
            scale -= 50
    scale_lbl.config(text=str(scale) + '%')
    load_image('')


def do_zoom():
    popup_win = Toplevel(root)
    popup_win.title('Масштабування')
    frame = Frame(popup_win)

    label1 = Label(frame, text='Масштаб:', font=10)
    field1 = Entry(frame, width=20, font=10)

    label1.grid(row=0, column=0, padx=3, pady=3)
    field1.grid(row=0, column=1, padx=3, pady=3)
    field1.insert(0, '100')

    ok_btn = Button(popup_win, text='OK')
    ok_btn.pack(side=BOTTOM, padx=3, pady=3)
    frame.pack()

    ok_btn.config(command=lambda: do_change_zoom(popup_win, int(field1.get())))


def do_change_zoom(popup_win: Toplevel, new_scale: int):
    global scale
    scale = new_scale
    scale_lbl.config(text=str(scale) + '%')
    load_image('')
    popup_win.destroy()


def coords(event):
    global x_coord, y_coord
    x_coord, y_coord = int(canvas.canvasx(event.x)), int(canvas.canvasy(event.y))

    x_crd.config(text=x_coord)
    y_crd.config(text=y_coord)


def text_popup(event):
    try:
        pop_menu.tk_popup(event.x_root, event.y_root)
    finally:
        pop_menu.grab_release()


def add_text():
    global prev_image, pil_image
    crd = (x_coord, y_coord)

    temp = prev_image
    prev_image = pil_image
    popup_win = Toplevel(root)
    popup_win.protocol("WM_DELETE_WINDOW", lambda: close_default(temp, popup_win))
    popup_win.title('Додати текст')
    frame = Frame(popup_win)

    label1 = Label(frame, text='Текст:', font=10)
    label2 = Label(frame, text='Розмір:', font=10)
    field1 = Entry(frame, width=50, font=10)
    field2 = Entry(frame, width=5, font=10)

    label1.grid(row=0, column=0, padx=3, pady=3)
    label2.grid(row=1, column=0, padx=3, pady=3)
    field1.grid(row=0, column=1, padx=3, pady=3, columnspan=2)
    field2.grid(row=1, column=1, padx=3, pady=3, sticky=W)
    field2.insert(0, '14')

    label_xy = Label(frame, text='X: ' + str(crd[0]) + ', Y: ' + str(crd[1]))
    label_xy.grid(row=1, column=2, padx=3, pady=3, sticky=E)

    ok_btn = Button(popup_win, text='OK')
    ok_btn.pack(side=BOTTOM, padx=3, pady=3)
    frame.pack()

    ok_btn.config(command=lambda: do_add_text(popup_win, field1.get(), int(field2.get()), crd))


def do_add_text(popup_win: Toplevel, string: str, text_size: int, crd: tuple):
    global prev_image, pil_image
    pil_image = prev_image

    draw = ImageDraw.Draw(pil_image)
    draw.text(crd, font=ImageFont.truetype('arial.ttf', text_size * 2), fill=brush_color, text=string)
    load_image('')
    popup_win.destroy()


def add_image():
    global prev_image, pil_image, start_image
    prev_image = copy(pil_image)
    temp = copy(start_image)

    new_filename = fd.askopenfilename(filetypes=FILETYPES)
    new_image = Image.open(new_filename)
    pil_image.paste(new_image, (x_coord, y_coord))
    load_image('')
    start_image = temp


root.bind('<Control-z>', key_pressed)
root.bind('<Control-o>', key_pressed)
root.bind('<Control-s>', key_pressed)
root.bind('<Control-S>', lambda e: save_image('as'))

scroll_x = Scrollbar(root, orient=HORIZONTAL)
scroll_y = Scrollbar(root, orient=VERTICAL)
canvas = Canvas(root,  # bg='white',
                width=canvas_width,
                height=canvas_height,
                xscrollcommand=scroll_x.set,
                yscrollcommand=scroll_y.set)
scroll_x.configure(command=canvas.xview)
scroll_y.configure(command=canvas.yview)

scroll_x.pack(side=BOTTOM, fill=X)
scroll_y.pack(side=RIGHT, fill=Y)
canvas.place(x=left_margin, y=top_margin)

canvas.bind('<MouseWheel>', zoom)
canvas.bind('<Button-3>', text_popup)
load_image('default')

main_frame = LabelFrame(root, text='Функції')

crop_btn = Button(main_frame, text='✂', font='Arial 20', width=3, relief='ridge', command=crop)
size_btn = Button(main_frame, text='🗚', font='Arial 20', width=3, relief='ridge', command=change_size)
draw_btn = Button(main_frame, text='✎', font='Arial 20', width=3, relief='ridge', command=lambda: draw_(None))
zoom_btn = Button(main_frame, text='🔍', font='Arial 20', width=3, relief='ridge', command=do_zoom)
crop_btn.grid(row=0, column=0, padx=3, pady=3)
size_btn.grid(row=0, column=1, padx=3, pady=3)
draw_btn.grid(row=1, column=0, padx=3, pady=3)
zoom_btn.grid(row=1, column=1, padx=3, pady=3)
main_frame.place(x=10, y=10)

coord_frame = LabelFrame(root, text='Координати')
x_lbl = Label(coord_frame, text='X: ')
y_lbl = Label(coord_frame, text='Y: ')
x_crd = Label(coord_frame, text='0')
y_crd = Label(coord_frame, text='0')
x_lbl.grid(row=0, column=0, padx=1, pady=1)
y_lbl.grid(row=1, column=0, padx=1, pady=1)
x_crd.grid(row=0, column=1, padx=1, pady=1, sticky=W)
y_crd.grid(row=1, column=1, padx=1, pady=1, sticky=W)
coord_frame.place(x=10, y=610)
canvas.bind('<Motion>', coords)

scale_frame = LabelFrame(text='М-таб')
scale_lbl = Label(scale_frame, text='100%')
scale_lbl.pack()
scale_frame.place(x=98, y=635)

root.bind("<Configure>", resize)
root.update_idletasks()
root.minsize(root.winfo_width(), root.winfo_height())

menu = Menu()

file_menu = Menu(tearoff=0)
file_menu.add_command(label='Відкрити зображення',
                      command=lambda: load_image('new'),
                      accelerator='Ctrl+O')
file_menu.add_command(label='Зберегти зображення',
                      command=lambda: save_image(''),
                      accelerator='Ctrl+S')
file_menu.add_command(label='Зберегти зображення як...',
                      command=lambda: save_image('as'),
                      accelerator='Ctrl+Shift+S')
file_menu.add_separator()
file_menu.add_command(label='Закрити програму',
                      command=lambda: root.destroy(),
                      accelerator='Ctrl+Q')

cor_menu = Menu(tearoff=0)
cor_menu.add_command(label='Яскравість', command=brightness)
cor_menu.add_command(label='Контрастність', command=contrast)
cor_menu.add_command(label='Різкість', command=sharpness)
cor_menu.add_separator()
cor_menu.add_command(label='Гістограма', command=histogram)
cor_menu.add_separator()
cor_menu.add_command(label='Повернути на 90°', command=rotate)
cor_menu.add_command(label='Віддзеркалити', command=mirror)
cor_menu.add_command(label='Перевернути', command=flip)

options_menu = Menu(tearoff=0)
options_menu.add_command(label='Відмінити дію',
                         command=lambda: load_image('prev'),
                         accelerator='Ctrl+Z')
options_menu.add_command(label='Скинути зображення', command=lambda: load_image('start'))

ef_menu = Menu(tearoff=0)
ef_menu.add_command(label='Інвертувати кольори', command=invert)
ef_menu.add_command(label='Зробити чорно-білим', command=grayscale)
ef_menu.add_command(label='Постеризація', command=posterize)
ef_menu.add_command(label='Соларизація', command=solarize)
ef_menu.add_command(label='Вицвітання (?)', command=washout)
ef_menu.add_separator()
ef_menu.add_command(label='Розмиття по Гаусу', command=blur)

menu.add_cascade(label='Файл', menu=file_menu)
menu.add_cascade(label='Опції', menu=options_menu)
menu.add_cascade(label='Корекція', menu=cor_menu)
menu.add_cascade(label='Ефекти', menu=ef_menu)
root.config(menu=menu)

pop_menu = Menu(tearoff=0)
pop_menu.add_command(label='Додати текст', command=add_text)
pop_menu.add_command(label='Вставити зображення', command=add_image)

root.mainloop()
