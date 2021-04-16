from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

def tiling(im, columns, rows):
    result = Image.new("RGBA", (im.size[0]*columns, im.size[1]*rows))
    for x in range(columns):
        for y in range(rows):
            result.paste(im, (im.size[0]*x, im.size[1]*y))
    return result

class Skin:
    """A skin object from image at given location (path).
A skin image should consist of square tiles in a grid like this:
------------------------------------------...
tile out     stone         stone    
 of plan       1             2       ...

 empty       stone 1      stone 2    ...
  tile     highlighted  highlighted
------------------------------------------...
    See without_transparency.png.
Highlight tiles are drawn over stone tiles,
stone tiles are drawn over empty tiles,
empty tiles are drawn over out-of-plan tiles,
so you can make some partially transparent.
See example.png and example2.png.
Reloading a game with skin may take a while if there is a lot of tiles to draw
or the skin image is large.
"""
    def __init__(self, path, win_line_color="black"):
        """path: path to skin file"""
        sheet = Image.open(path)
        size = sheet.height//2
        columns = sheet.width//size
        if columns <= 0:
            raise ValueError("skin aspect ratio must be at least 1:2")
        self.tiles = []
        for x in range(columns):
            for y in range(2):
                self.tiles.append(sheet.crop((x*size, y*size, (x+1)*size, (y+1)*size)))
        self.mark_images = [{} for i in range(columns-1)]
        self.highlight_images = [{} for i in range(columns-1)]
        self.win_line_color = win_line_color

    def board(self, canvas, left, top, size, width, height):
        """this board method is a board function as described in tk_app.py"""
        canvas_columns = int(canvas.winfo_width()//size)+2
        canvas_rows = int(canvas.winfo_height()//size)+2
        self.bg_image = ImageTk.PhotoImage(
            tiling(self.tiles[0], canvas_columns, canvas_rows)
            .resize((round(size*canvas_columns),round(size*canvas_rows)))
            )
        self.plan_image = ImageTk.PhotoImage(
            tiling(self.tiles[1], width, height)
            .resize((round(size*width),round(size*height)))
            )

        x_min = left-size*(left//size+1.5)
        y_min = top-size*(top//size+1.5)
        canvas.create_image(x_min,y_min, image=self.bg_image, anchor="nw")
        canvas.create_image(left-size/2,top-size/2, image=self.plan_image, anchor="nw")

    def mark(self, i):
        """return the i-th mark function as described in tk_app.py"""
        def mark_func(canvas, x, y, half_size, i=i):
            size = int(round(2*half_size))
            if size not in self.mark_images[i]:
                self.mark_images[i][size] = ImageTk.PhotoImage(self.tiles[2*i+2].resize((size,size)))
                self.highlight_images[i][size] = ImageTk.PhotoImage(self.tiles[2*i+3].resize((size,size)))
            mark = canvas.create_image(x-half_size,y-half_size, image=self.mark_images[i][size], anchor="nw")
            highlight = canvas.create_image(x-half_size,y-half_size, image=self.highlight_images[i][size], anchor="nw")
            return ([mark], [highlight])
        return mark_func

    def marks(self):
        """return a list of all mark functions"""
        result = []
        for i in range(len(self.tiles)//2-1):
            result.append(self.mark(i))
        return result

    def __getitem__(self, i):
        """simulates the appearance tuple for `appearance_options`
dictionary in tk_app.py"""
        if i == 0: return self.board
        elif i == 1: return self.marks()
        else: return self.win_line_color
            
class CustomSkin(Skin):
    def __init__(self):
        self.tiles = None
        self.win_line_color = "black"
        
    def get_path(self, anyway=False):
        if self.tiles is None or anyway:
            path = filedialog.askopenfilename(initialdir="skins")
            super().__init__(path)
            
    def board(self, *args, **kwargs):
        self.get_path()
        return super().board(*args, **kwargs)

    def marks(self):
        self.get_path()
        return super().marks()

