import io

from flask import Flask, render_template, send_file, request

from barcode import Code39
from barcode.writer import ImageWriter
import qrcode

import pdb

app = Flask(__name__, static_url_path='', static_folder='./static', template_folder='./templates')

@app.route("/")
def hello_world():
    return render_template('index.html')

# https://github.com/lincolnloop/python-qrcode
@app.route("/qrcode/<data>")
def get_qrcode(data):
    #data = request.args.get('data', 'Hello, QR Code!')
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')

    img_buffer.seek(0)
    return send_file(img_buffer, mimetype='image/png')


# https://python-barcode.readthedocs.io/en/stable/getting-started.html
# alt: https://pythonhosted.org/pyBarcode/index.html
@app.route('/code39/<data>', methods=['GET'])
def generate_code39(data):
    """Generates a code 39 barcode as a PNG image
    :param data:
        data (str): data for the barcode
    :return:
        A code 39 barcode PNG image
    """
    code39 = Code39(data, writer=ImageWriter(), add_checksum=False)

    # Uncomment to save barcodes to local file system
    # filename = code39.save('barcode')
    # print(f"Barcode saved as {filename}")

    # Write to a byte buffer
    img_buffer = io.BytesIO()
    code39.write(img_buffer)

    # Send byte buffer as response
    img_buffer.seek(0)
    return send_file(img_buffer, mimetype='image/png')


    # @app.route('/barcode', methods=['GET'])
    # def generate_barcode():
    #     # Get data from the request, e.g., a URL or text
    #     data = request.args.get('data')
    #
    #     if not data:
    #         return "Data parameter is required", 400
    #
    #     # Generate the barcode (QR code in this example)
    #     img = qrcode.make(data)
    #
    #     # Save the barcode image to a buffer
    #     buffer = io.BytesIO()
    #     img.save(buffer, format='PNG')
    #     buffer.seek(0)
    #
    #     # Create a Flask response with the image
    #     response = make_response(buffer.getvalue())
    #     response.headers['Content-Type'] = 'image/png'
    #     response.headers['Content-Disposition'] = 'inline; filename=barcode.png'
    #     return response


if __name__ == '__main__':
    app.run(debug=True, port=4800, host='0.0.0.0')