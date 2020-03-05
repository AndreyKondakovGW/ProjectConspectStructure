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
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    for img in image_list:
        pdf.image(img,w=200)
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, txt="{}".format(img[img.rindex('/')+1:]), ln=1)
    print(basedir+'/static/Photo/'+name+'.pdf')
    pdf.output(basedir+'/static/Photo/'+name+'.pdf', dest='F')


def cut(image_path,left,top,right,bottom):
    im = Image.open(basedir+'/static/Photo/'+image_path)
    width, height = im.size
    im1 = im.crop((left, top, right, bottom))
    im1.save(basedir + '/static/Photo/'+'new1.pdf',)
    #im1.show()
