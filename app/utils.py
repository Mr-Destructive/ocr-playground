import math

import fitz
import pytesseract
from PIL import Image, ImageDraw


def rotate_center(x, y, c1, c2, angle):
    rotation_matrix = [
        [math.cos(math.radians(angle)), -math.sin(math.radians(angle))],
        [math.sin(math.radians(angle)), math.cos(math.radians(angle))],
    ]
    x1 = (x - c1) * rotation_matrix[0][0] - (y - c2) * rotation_matrix[0][1] + c1
    y1 = (x - c1) * rotation_matrix[1][0] - (y - c2) * rotation_matrix[1][1] + c2
    return [x1, y1]


def rotate_box(x0, y0, h, w, angle):
    x1 = x0 + w
    y1 = y0 - h
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    a = [x0, y1]
    c = [x1, y0]
    b = [x1, y1]
    d = [x0, y0]
    a1 = rotate_center(a[0], a[1], cx, cy, angle)
    b1 = rotate_center(b[0], b[1], cx, cy, angle)
    c1 = rotate_center(c[0], c[1], cx, cy, angle)
    d1 = rotate_center(d[0], d[1], cx, cy, angle)
    return a1


def rotate_image(image_path, output_path, rotation_angle):
    img = Image.open(image_path)
    boxes = pytesseract.image_to_boxes(img)
    # TODO:
    # Explore OSD:   pytesseract.image_to_osd(img)
    new_img = img.copy()
    draw = ImageDraw.Draw(new_img)
    for box in boxes.splitlines():
        box = box.split()
        x, y, w, h = int(box[1]), int(box[2]), int(box[3]), int(box[4])
        x1, y1 = rotate_box(x, y, h, w, rotation_angle)
        draw.rectangle([x1, y1, h, w], outline="red", width=2)
    new_img.save(output_path)


def get_image_boxes(image_path, output_path):
    img = Image.open(image_path)
    boxes = pytesseract.image_to_boxes(img)
    new_img = img.copy()
    draw = ImageDraw.Draw(new_img)
    for box in boxes.splitlines():
        box = box.split()
        print(box[0], box[1], box[2], box[3], box[4])
        x, y, w, h = int(box[1]), int(box[2]), int(box[3]), int(box[4])
        draw.rectangle([x, y, w, h], outline="red", width=2)
    new_img.save(output_path)

def get_ocr_value_of_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    boundary_values = []
    for page in pdf_document:
        for text_block in page.get_text_blocks():
            boundary_values.append(text_block)
    return boundary_values

def avg_x(block):
    return (block[0] + block[2]) / 2

def avg_y(block):
    return (block[1] + block[3]) / 2


def identify_columns(ocr_result):
    columns = []
    curr_column = []
    for item in ocr_result:
        average_x = avg_x(item)
        average_y = avg_y(item)
        if curr_column and abs(average_x - avg_x(curr_column[-1])) < 5 and abs(average_y - avg_y(curr_column[-1])) < 5:
            curr_column.append(item)
        else:
            if curr_column:
                columns.append(curr_column)
            curr_column = [item]
    if curr_column:
        columns.append(curr_column)
    return columns

def extract_rows_from_column(columns, column_names):
    rows = []
    column_names_set = set(column_names)
    for column in columns:
        column_text = ' '.join([item[4] for item in column])
        if any(keyword in column_text for keyword in column_names_set):
            min_x = min(item[0] for item in column)
            max_x = max(item[2] for item in column)
            for next_column in columns[columns.index(column) + 1:]:
                next_column_item = next_column[0]
                next_column_item_x1, _, next_column_item_x2, _, _, _, _ = next_column_item
                next_column_item_avg_x = (next_column_item_x1 + next_column_item_x2) / 2
                if min_x <= next_column_item_avg_x <= max_x:
                    rows.append(next_column_item)
    return rows
