from fpdf import FPDF
import os
from PIL import Image


basedir = os.path.abspath(os.path.dirname(__file__))


def create_simple_pdf(name,text):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=text, ln=1, align="C")
    pdf.output(basedir+'/static/'+name+'.pdf', dest='F')


def create_pdf_from_images(name, image_list):
    print("creating pdf")
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    for img in image_list:
        print(img)
        if os.path.exists(img):
            print("exists")
            pdf.image(img, w=200)
            pdf.set_font("Arial", size=12)
            pdf.ln(10)
            pdf.cell(200, 10, txt="{}".format(img[img.rindex('/')+1:]), ln=1)
    print(basedir+'/static/Photo/'+name+'.pdf')
    pdf.output(basedir+'/static/Photo/'+name+'.pdf', dest='F')


def cut(image_path, left, top, right, bottom, name):
    im = Image.open(basedir+'/static/Photo/'+image_path)
    w, h = im.size
    im1 = im.crop((w*left, h*top, w*right, h*bottom))
    im1.save(name)
    #im1.show()
