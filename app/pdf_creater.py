from fpdf import FPDF
import os
from PIL import Image
from tempfile import NamedTemporaryFile


class MyPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')


basedir = os.path.abspath(os.path.dirname(__file__))


def create_simple_pdf(name,text):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=text, ln=1, align="C")
    pdf.output(basedir+'/static/'+name+'.pdf', dest='F')


def create_pdf_from_images(name, image_list):
    print("creating pdf")
    pdf = MyPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font('Arial','B', 30)
    pdf.cell(80)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(30, 10, name, 0, 10, 'C')
    pdf.ln(20)
    for img in image_list:
        print(img)
        if os.path.exists(img):
            # print("exists")
            pdf.set_font("Arial", size=12)
            pdf.cell(25)
            pdf.image(img, w=150)
            pdf.ln(5)
            pdf.cell(200, 10, ln=1)
    print(basedir+'/static/Photo/'+name+'.pdf')
    pdf.output(basedir+'/static/Photo/'+name+'.pdf', dest='F')


def cut(image_path, left, top, right, bottom, name):
    im = Image.open(basedir+'/static/Photo/'+image_path)
    w, h = im.size
    # if ((left) and (top) and (right) and (bottom)):
    print(left,top,right,bottom)
    im1 = im.crop((w*left, h*top, w*right, h*bottom))
    # else:
        # im1=im
    im1.save(name)
    #im1.show()


def filename_gen(path: str, old_filename: str):
    ext = old_filename.split('.')[-1]
    tf = NamedTemporaryFile(dir=path)
    filename = tf.name+'.'+ext
    tf.close()
    while os.path.exists(filename):
        tf = NamedTemporaryFile(dir=path)
        filename = tf.name + '.' + ext
        tf.close()
    return filename


def save_copy(image_path, new_image_path):
    image = Image.open(image_path)
    new_image = image.copy()
    new_image.save(new_image_path)
