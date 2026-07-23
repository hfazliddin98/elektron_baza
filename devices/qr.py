from io import BytesIO

import qrcode


def qr_png(matn, olcham=8):
    """Matndan QR-kod PNG baytlarini qaytaradi."""
    kod = qrcode.QRCode(box_size=olcham, border=2)
    kod.add_data(matn)
    kod.make(fit=True)
    rasm = kod.make_image(fill_color='black', back_color='white')

    bufer = BytesIO()
    rasm.save(bufer, format='PNG')
    return bufer.getvalue()
