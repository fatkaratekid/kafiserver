from PIL import Image
from wand.image import Image as WandImage
import uuid
import numpy as np
import glob
from wand.color import Color
import pytesseract
import cv2
import os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


def convert_pdf_txt_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


def convert_scanned_pdf_to_image(filepdf):
    uuid_set = str(uuid.uuid4().fields[-1])[:5]
    with WandImage(filename=filepdf, resolution=300) as imgs:
        for page_id, img in enumerate(imgs.sequence):
            with WandImage(img) as pdf_img:
                pdf_img.format = 'png'
                pdf_img.background_color = Color("white") # Make background white
                pdf_img.alpha_channel = 'remove' # remove transparent channel -> jpg has no alpha
                pdf_img.save(filename="tmp_{}_p{}s.png".format(uuid_set, page_id))


        #search all image in temp path for temp file names containing uuid_set value
        list_im = glob.glob("tmp_{}*.png".format(uuid_set))
        list_im.sort() #sort the file before joining it
        imgs = [Image.open(i) for i in list_im]

        # Concatenating vertically all images
        min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
        imgs_comb = np.vstack(
            (np.asarray(i.resize(min_shape)) for i in imgs))
        # for horizontally  change the vstack to hstack
        imgs_comb = Image.fromarray(imgs_comb)
        pathsave = "menu_{}.png".format(uuid_set)

        imgs_comb.save(pathsave)

        # Removing temp images
        for i in list_im:
            os.remove(i)

        return pathsave


def ocr(path):
    print('and now OCR pipeline')

    print('reading')
    image = cv2.imread(path)
    gray = image
    print('grayscale')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print('thresholding')
    gray = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )[1]
    print('blur to denosie')
    gray = cv2.medianBlur(gray, 3)
    print('save')
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)

    #get text
    print('ocr')
    with Image.open(filename) as menu_img:

        text = pytesseract.image_to_string(menu_img)
        os.remove(filename)
    print('returning text')
    return text


def convert_scanned_pdf_to_text(filepdf):
    menu_image_path = convert_scanned_pdf_to_image(filepdf)
    text = ocr(menu_image_path)
    os.remove(menu_image_path)
    return text


def convert_pdf_to_text(filepdf):
    text = convert_pdf_txt_to_txt(filepdf)
    if len(text) < 21:
        text = convert_scanned_pdf_to_text(filepdf)
    return text


if __name__ == "__main__":
    text = convert_pdf_to_text('/home/giga/Downloads/m.pdf')
    print(text)
