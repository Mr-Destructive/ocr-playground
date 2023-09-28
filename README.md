## OCR Playground

> This is a side project / assigment for understanding and learning OCRs/text extraction.

- Using [tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html) as the OCR.
- Using [PILLOW](https://pillow.readthedocs.io/en/stable/) for image processing.
- Using [flask](https://flask.palletsprojects.com/en/1.1.x/) for the API.


### Endpoints

- `/uploads`: to upload the image/pdf and get the OCR results.
- `/extract`: get text of rows related to particular column.
- `/rotate`: rotate the image/bounding box in the ocr provided with the angle.
- `/boxes`: get the bounding boxes in the entire document as a image.

### TODO

- Exploration of various concepts like OCRs, IDPs, OCDs, etc.
- Implement the rotation feature more accurately.
- Extract with the entire text resembling the document structure.
