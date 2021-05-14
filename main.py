"""
Функції:
1) Меню
2) Вставка зображення
3) Збереження зображення
4) Скролл
5) Збільшення/зменшення

6) Вибір кольору
7) Вибір пензля
8) Зміна товщини пензля
9) Очищення полотна
10) Зміна розміру зображення в n разів
11) Зміна розміру зоображення в пікселях
12) Обрізання зображення
13) Інвертування зображення
14) Зробити чорно-білим
15) Віддзеркалення зображення
16) Погіршити якість зображення
17) Регулювання яскравості
18) Регулювання контрастності
19) Регулювання різкості
20) Додавання тексту
"""

import os
import time
from tkinter import *
from tkinter import filedialog as fd, ttk, colorchooser
from PIL import ImageGrab, ImageTk, Image, ImageEnhance
import PIL.ImageOps

# -------------------- Ініціалізація --------------------

# Налаштування вікна програми
root = Tk()
root.title('Графічний редактор')
root.state('zoomed')
root.iconphoto(False, PhotoImage(file='./icon.png'))

# Глобальні зміні та константи
brush_size = 10
brush_color = "black"
img = None
last_x, last_y = 0, 0
text_x, text_y = None, None
current_brush = 'ENHANCED'

FILETYPES = (('All files', '*.*'),
             ('JPEG files', '*.jpg;*.jpeg'),
             ('PNG files', '*.png'),
             ('BMP files', '*.bmp'))

# Налаштування області малювання та скролбарів
h = ttk.Scrollbar(root, orient=HORIZONTAL)
v = ttk.Scrollbar(root, orient=VERTICAL)
cv_x = 75
cv_y = 10
cv_w = 1420
cv_h = 740
canvas = Canvas(root, width=cv_w, height=cv_h,  # Розмір області в програмі
                bg='white', scrollregion=(0, 0, 1920, 1080),  # Загальний розмір
                xscrollcommand=h.set, yscrollcommand=v.set)  # Прив'язування скролбарів
h.configure(command=canvas.xview)
v.configure(command=canvas.yview)

canvas.place(x=cv_x, y=cv_y)
h.pack(side=BOTTOM, fill=X)
v.pack(side=RIGHT, fill=Y)


# -------------------- Основні функції --------------------

# Передавання останього значення положення миші на полотні
def xy(event):
    global last_x, last_y
    last_x, last_y = canvas.canvasx(event.x), canvas.canvasy(event.y)


# Малювання лінії
def draw(event):
    global brush_size, last_x, last_y
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)

    if current_brush == 'LINE':
        canvas.create_line((last_x, last_y, x, y), fill=brush_color, width=brush_size * 2)
    elif current_brush == 'SQUARE':
        canvas.create_rectangle(x - brush_size, y - brush_size, x + brush_size, y + brush_size,
                                fill=brush_color, outline=brush_color)
    elif current_brush == 'CIRCLE':
        canvas.create_oval(x - brush_size, y - brush_size, x + brush_size, y + brush_size,
                           fill=brush_color, outline=brush_color)
    elif current_brush == 'ENHANCED':
        canvas.create_line((last_x, last_y, x, y), fill=brush_color, width=brush_size * 2)
        canvas.create_oval(x - brush_size, y - brush_size, x + brush_size, y + brush_size,
                           fill=brush_color, outline=brush_color)
    elif current_brush == 'SMILE':
        canvas.create_text(x - brush_size, y - brush_size,
                           font='Arial ' + str(brush_size), fill=brush_color, text='=)')
    last_x, last_y = x, y


# Зміна пензля
def change_brush(new_brush: str):
    global current_brush
    current_brush = new_brush
    if current_brush == 'LINE':
        line_btn.config(background='light gray')
        sqr_btn.config(background='SystemButtonFace')
        crl_btn.config(background='SystemButtonFace')
        enh_btn.config(background='SystemButtonFace')
        sml_btn.config(background='SystemButtonFace')
    elif current_brush == 'SQUARE':
        line_btn.config(background='SystemButtonFace')
        sqr_btn.config(background='light gray')
        crl_btn.config(background='SystemButtonFace')
        enh_btn.config(background='SystemButtonFace')
        sml_btn.config(background='SystemButtonFace')
    elif current_brush == 'CIRCLE':
        line_btn.config(background='SystemButtonFace')
        sqr_btn.config(background='SystemButtonFace')
        crl_btn.config(background='light gray')
        enh_btn.config(background='SystemButtonFace')
        sml_btn.config(background='SystemButtonFace')
    elif current_brush == 'ENHANCED':
        line_btn.config(background='SystemButtonFace')
        sqr_btn.config(background='SystemButtonFace')
        crl_btn.config(background='SystemButtonFace')
        enh_btn.config(background='light gray')
        sml_btn.config(background='SystemButtonFace')
    elif current_brush == 'SMILE':
        line_btn.config(background='SystemButtonFace')
        sqr_btn.config(background='SystemButtonFace')
        crl_btn.config(background='SystemButtonFace')
        enh_btn.config(background='SystemButtonFace')
        sml_btn.config(background='light gray')


# Зміна кольору
def color_change(color):
    global brush_color
    if color is None:
        (rgb, hx) = colorchooser.askcolor()
        brush_color = hx
    else:
        brush_color = color


# Приближення/віддалення
def do_zoom(event):
    factor = 1.001 ** event.delta
    canvas.scale(ALL, event.x, event.y, factor, factor)


# Створення нової кнопки для зміни кольору
def color_button(color: str, x: int, y: int):
    btn = Button(background=color, width=2, command=lambda: color_change(color))
    btn.place(x=x, y=y)


# Обробка слайдеру зміни товщини пензля
def brush_slider(new_size):
    size_field.delete(0, END)
    size_field.insert(0, new_size)
    brush_size_change(int(new_size))


# Обробка текстового поля для введення товщини
def brush_textfield(_):
    new_size = size_field.get()
    size_slider.set(new_size)
    brush_size_change(int(new_size))


# Зміна товщини пензля
def brush_size_change(new_size: int):
    global brush_size
    brush_size = new_size


# Отримання поточних координат миші
def coordinates(event):
    x_crd.config(text=event.x)
    y_crd.config(text=event.y)


# Отримання зображення з полотна
def get_image() -> Image:
    time.sleep(0.5)
    x, y = root.winfo_rootx() + cv_x + 23, root.winfo_rooty() + cv_y + 16
    x1, y1 = x + int(cv_w * 1.25), y + int(cv_h * 1.25)
    return ImageGrab.grab().crop((x, y, x1, y1))


# Збереження зображення
def save_image():
    new_img = get_image()
    filename = fd.asksaveasfilename(filetypes=FILETYPES)
    new_img.save(filename)


# Вставка зображення
def paste_image():
    global img
    filename = fd.askopenfilename(filetypes=FILETYPES)
    img = ImageTk.PhotoImage(Image.open(filename))
    canvas.create_image(0, 0, anchor=NW, image=img)


# Вікно збільшення/зменшення зображення
def change_scale():
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)

    sw = Tk()
    sw.geometry('560x80+460+300')
    sw.wm_title('Збільшення/зменшення')

    sw_lbl = Label(sw, text='Введіть, у скільки разів збільшити зображення:', justify='left', font=10)
    sw_field = Entry(sw, width=40, font=10)
    sw_btn = Button(sw, text='Змінити розмір', width=15,
                    command=lambda: (scale(float(sw_field.get()), new_img), sw.destroy()))
    sw_lbl.place(x=10, y=10)
    sw_field.place(x=10, y=45)
    sw_btn.place(x=400, y=43)


# Збільшення/зменшення зображення
def scale(new_size: float, new_img: Image):
    global img
    new_w = int(cv_w * new_size)
    new_h = int(cv_h * new_size)

    new_img = new_img.resize((new_w, new_h), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(new_img)
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)


# Вікно зміни розміру зображення
def change_size():
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)

    sw = Tk()
    sw.geometry('400x80+460+300')
    sw.wm_title('Розмір')

    sw_lbl = Label(sw, text='Введіть нові розміри зображення:', justify='left', font=10)
    sw_width = Entry(sw, width=10, font=10)
    sw_x = Label(sw, text='x', font=10)
    sw_height = Entry(sw, width=10, font=10)
    sw_btn = Button(sw, text='Змінити розмір', width=15,
                    command=lambda: (size(int(sw_width.get()), int(sw_height.get()), new_img), sw.destroy()))
    sw_lbl.place(x=10, y=10)
    sw_width.place(x=10, y=45)
    sw_x.place(x=115, y=43)
    sw_height.place(x=140, y=45)
    sw_btn.place(x=280, y=43)


# Зміна розміру зображення
def size(width: int, height: int, new_img: Image):
    global img

    new_img = new_img.resize((width, height), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(new_img)
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)


# Вікно обрізання зображення
def crop_image():
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)

    sw = Tk()
    sw.geometry('400x110+460+300')
    sw.wm_title('Обрізка')

    sw_lbl = Label(sw, text='Введіть точки обрізання:', justify='left', font=10)
    sw_btn = Button(sw, text='Змінити розмір', width=15,
                    command=lambda: (crop(int(sw_ex1.get()), int(sw_ey1.get()),
                                          int(sw_ex2.get()), int(sw_ey2.get()), new_img),
                                     sw.destroy()))
    sw_x1 = Label(sw, text='x1:', font=10)
    sw_y1 = Label(sw, text='y1:', font=10)
    sw_x2 = Label(sw, text='x2:', font=10)
    sw_y2 = Label(sw, text='y2:', font=10)

    sw_ex1 = Entry(sw, width=5, font=10)
    sw_ey1 = Entry(sw, width=5, font=10)
    sw_ex2 = Entry(sw, width=5, font=10)
    sw_ey2 = Entry(sw, width=5, font=10)

    sw_lbl.place(x=10, y=10)
    sw_btn.place(x=250, y=73)

    sw_x1.place(x=10, y=45)
    sw_ex1.place(x=40, y=45)
    sw_y1.place(x=100, y=45)
    sw_ey1.place(x=140, y=45)
    sw_x2.place(x=10, y=75)
    sw_ex2.place(x=40, y=75)
    sw_y2.place(x=100, y=75)
    sw_ey2.place(x=140, y=75)


# Обрізання зображення
def crop(x1: int, y1: int, x2: int, y2: int, new_img=Image):
    global img

    new_img = new_img.crop((x1, y1, x2, y2))
    img = ImageTk.PhotoImage(new_img)
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)


# Інвертоване зображення
def invert():
    global img
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)
    new_img = PIL.ImageOps.invert(new_img)
    img = ImageTk.PhotoImage(new_img.resize((cv_w + 3, cv_h + 3), Image.ANTIALIAS))
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)


# Чорно-біле зображення
def grayscale():
    global img
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)
    new_img = PIL.ImageOps.grayscale(new_img)
    img = ImageTk.PhotoImage(new_img.resize((cv_w + 3, cv_h + 3), Image.ANTIALIAS))
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)


# Віддзеркалення вертикально
def flip():
    global img
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)
    new_img = PIL.ImageOps.flip(new_img)
    img = ImageTk.PhotoImage(new_img.resize((cv_w + 3, cv_h + 3), Image.ANTIALIAS))
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)


# Віддзеркалення горизонтально
def mirror():
    global img
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)
    new_img = PIL.ImageOps.mirror(new_img)
    img = ImageTk.PhotoImage(new_img.resize((cv_w + 3, cv_h + 3), Image.ANTIALIAS))
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)


# Погіршення якості
def lower():
    global img
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)
    new_img.save('./temp.jpg', quality=50)
    img = ImageTk.PhotoImage(Image.open('./temp.jpg').resize((cv_w + 3, cv_h + 3), Image.ANTIALIAS))
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)
    os.remove('./temp.jpg')


# Ще більше огіршення якості
def jpeg():
    global img
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)
    new_img.save('./temp.jpg', quality=1)
    img = ImageTk.PhotoImage(Image.open('./temp.jpg').resize((cv_w + 3, cv_h + 3), Image.ANTIALIAS))
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)
    os.remove('./temp.jpg')


# Вікно змінення яскравості
def brightness():
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)

    sw = Tk()
    sw.geometry('360x90+460+300')
    sw.wm_title('Яскравість')

    sw_scale = Scale(sw, from_=-100, to=100, length=340, orient=HORIZONTAL)
    sw_btn = Button(sw, text='Змінити', width=10,
                    command=lambda: (change_brightness(sw_scale.get(), new_img), sw.destroy()))
    sw_scale.place(x=10, y=10)
    sw_btn.place(x=145, y=60)


# Яскравість
def change_brightness(value: int, new_img: Image):
    global img

    value = (value + 100) / 100
    enhancer = ImageEnhance.Brightness(new_img)
    new_img = enhancer.enhance(value)

    img = ImageTk.PhotoImage(new_img.resize((cv_w + 3, cv_h + 3), Image.ANTIALIAS))
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)


# Вікно змінення контрастності
def contrast():
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)

    sw = Tk()
    sw.geometry('360x90+460+300')
    sw.wm_title('Контрастність')

    sw_scale = Scale(sw, from_=-100, to=100, length=340, orient=HORIZONTAL)
    sw_btn = Button(sw, text='Змінити', width=10,
                    command=lambda: (change_contrast(sw_scale.get(), new_img), sw.destroy()))
    sw_scale.place(x=10, y=10)
    sw_btn.place(x=145, y=60)


# Контрастність
def change_contrast(value: int, new_img: Image):
    global img

    value = (value + 100) / 100
    enhancer = ImageEnhance.Brightness(new_img)
    new_img = enhancer.enhance(value)

    img = ImageTk.PhotoImage(new_img.resize((cv_w + 3, cv_h + 3), Image.ANTIALIAS))
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)


# Вікно змінення різкості
def sharpness():
    new_img = get_image().resize((cv_w, cv_h), Image.ANTIALIAS)

    sw = Tk()
    sw.geometry('360x90+460+300')
    sw.wm_title('Різкість')

    sw_scale = Scale(sw, from_=-100, to=100, length=340, orient=HORIZONTAL)
    sw_btn = Button(sw, text='Змінити', width=10,
                    command=lambda: (change_sharpness(sw_scale.get(), new_img), sw.destroy()))
    sw_scale.place(x=10, y=10)
    sw_btn.place(x=145, y=60)


# Різкість
def change_sharpness(value: int, new_img: Image):
    global img

    value = (value + 100) / 100
    enhancer = ImageEnhance.Sharpness(new_img)
    new_img = enhancer.enhance(value)

    img = ImageTk.PhotoImage(new_img.resize((cv_w + 3, cv_h + 3), Image.ANTIALIAS))
    canvas.delete('all')
    canvas.create_image(0, 0, anchor=NW, image=img)


# Контекстне меню
def do_popup(event):
    global text_x, text_y
    try:
        pop_menu.tk_popup(event.x_root, event.y_root)
        text_x, text_y = event.x, event.y
    finally:
        pop_menu.grab_release()


# Форма додавання тексту
def add_text():
    sw = Tk()
    sw.geometry('360x90+' + str(text_x) + '+' + str(text_y))
    sw.wm_title('Текст')

    sw_text = Entry(sw, width=35, font=10)
    sw_text.bind('<Return>', lambda event: (text(sw_text.get(), int(sw_size.get())), sw.destroy()))
    sw_text.place(x=10, y=10)

    sw_lbl = Label(sw, text='Розмір:', font=10)
    sw_size = Entry(sw, width=5, font=10)
    sw_size.insert(0, '10')
    sw_lbl.place(x=10, y=48)
    sw_size.place(x=80, y=50)


# Додавання тексту
def text(string: str, text_size: int):
    global text_x, text_y
    canvas.create_text(text_x, text_y, text=string, font='Arial ' + str(text_size), fill=brush_color)


# -------------------- Прив'язування дій миші до області малювання --------------------

canvas.bind('<Button-1>', xy)
canvas.bind('<B1-Motion>', draw)
canvas.bind('<Motion>', coordinates)
canvas.bind('<MouseWheel>', do_zoom)
canvas.bind('<ButtonPress-2>', lambda event: canvas.scan_mark(event.x, event.y))
canvas.bind('<B2-Motion>', lambda event: canvas.scan_dragto(event.x, event.y, gain=1))
canvas.bind('<Button-3>', do_popup)

# -------------------- Елементи програми --------------------

# Кнопки кольорів для малювання
color_button('black', 10, 20)
color_button('white', 40, 20)
color_button('azure4', 10, 50)
color_button('gray', 40, 50)
color_button('red4', 10, 80)
color_button('red', 40, 80)
color_button('orange', 10, 110)
color_button('yellow', 40, 110)
color_button('green', 10, 140)
color_button('light green', 40, 140)
color_button('steelblue3', 10, 170)
color_button('light blue', 40, 170)
color_button('navy', 10, 200)
color_button('blue', 40, 200)
color_button('purple', 10, 230)
color_button('pink', 40, 230)

# Зміна кольору на довільний
color_btn = Button(text='Змінити\nколір', width=7, command=lambda: color_change(None))
color_btn.place(x=8, y=260)

# Зміна розміру пензля
size_slider = Scale(from_=1, to=50, showvalue=0, command=brush_slider, length=145)
size_slider.place(x=10, y=340)
size_slider.set(brush_size)
size_field = Entry(width=8)
size_field.bind('<Return>', brush_textfield)
size_field.place(x=10, y=495)
size_field.insert(0, brush_size)

# Кнопки зміни пензлів
line_btn = Button(text='/', width=2, command=lambda: change_brush('LINE'))
line_btn.place(x=40, y=430)
sqr_btn = Button(text='■', width=2, command=lambda: change_brush('SQUARE'))
sqr_btn.place(x=40, y=370)
crl_btn = Button(text='●', width=2, command=lambda: change_brush('CIRCLE'))
crl_btn.place(x=40, y=400)
enh_btn = Button(text='🖌', width=2, command=lambda: change_brush('ENHANCED'))
enh_btn.place(x=40, y=340)
sml_btn = Button(text='=)', width=2, command=lambda: change_brush('SMILE'))
sml_btn.place(x=40, y=460)
enh_btn.config(background='light gray')

# Кнопка очищення полотна
clear_btn = Button(text='Очистити', width=7, command=lambda: canvas.delete('all'))
clear_btn.place(x=8, y=550)

# Координати на полотні
x_lbl = Label(text='X:')
y_lbl = Label(text='Y:')
x_crd = Label(text='0')
y_crd = Label(text='0')
x_lbl.place(x=5, y=700)
y_lbl.place(x=5, y=720)
x_crd.place(x=25, y=700)
y_crd.place(x=25, y=720)

# -------------------- Налаштування меню --------------------

menu = Menu()

file_menu = Menu(tearoff=0)
file_menu.add_command(label='Вставити зображення', command=paste_image)
file_menu.add_command(label='Зберегти зображення', command=save_image)

edit_menu = Menu(tearoff=0)
edit_menu.add_command(label='Збільшити/зменшити', command=change_scale)
edit_menu.add_command(label='Змінити розмір', command=change_size)
edit_menu.add_command(label='Обрізати зображення', command=crop_image)
edit_menu.add_separator()
edit_menu.add_command(label='Інвертувати кольори', command=invert)
edit_menu.add_command(label='Зробити чорно-білим', command=grayscale)
edit_menu.add_separator()
edit_menu.add_command(label='Віддзеркалити вертикально', command=flip)
edit_menu.add_command(label='Віддзеркалити горизонтально', command=mirror)
edit_menu.add_separator()
edit_menu.add_command(label='Погіршити якість', command=lower)
edit_menu.add_command(label='Знищити зображення', command=jpeg)
edit_menu.add_separator()
edit_menu.add_command(label='Яскравість', command=brightness)
edit_menu.add_command(label='Контрастність', command=contrast)
edit_menu.add_command(label='Різкість', command=sharpness)

menu.add_cascade(label='Файл', menu=file_menu)
menu.add_cascade(label='Редагувати', menu=edit_menu)
root.config(menu=menu)

pop_menu = Menu(tearoff=0)
pop_menu.add_command(label='Додати текст', command=add_text)

# -------------------- Запуск програми --------------------

root.mainloop()
