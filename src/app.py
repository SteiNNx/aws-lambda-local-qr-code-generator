import json
import base64
import qrcode
from io import BytesIO
from jsonschema import validate, ValidationError


# Definir el esquema JSON
QR_CODE_SCHEMA = {
    "type": "object",
    "properties": {
        "data": {"type": "string"},
        "size": {"type": "integer", "minimum": 1},
        "errorCorrectionLevel": {
            "type": "string",
            "enum": ["L", "M", "Q", "H"]
        },
        "margin": {"type": "integer", "minimum": 0},
        "color": {
            "type": "object",
            "properties": {
                "dark": {"type": "string"},
                "light": {"type": "string"}
            },
            "required": ["dark", "light"]
        }
    },
    "required": ["data", "size", "errorCorrectionLevel", "margin", "color"]
}

ERROR_CORRECTION_MAPPING = {
    'L': qrcode.constants.ERROR_CORRECT_L,
    'M': qrcode.constants.ERROR_CORRECT_M,
    'Q': qrcode.constants.ERROR_CORRECT_Q,
    'H': qrcode.constants.ERROR_CORRECT_H
}

def validate_event(event):
    """Valida el evento contra el esquema JSON."""
    try:
        validate(instance=event, schema=QR_CODE_SCHEMA)
    except ValidationError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }
    return None

def generate_qr_code(data, size, error_correction, margin, colors):
    """Genera un código QR basado en los parámetros proporcionados."""
    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECTION_MAPPING.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_M),
        box_size=size,
        border=margin
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=colors['dark'], back_color=colors['light'])
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def lambda_handler(event, context):
    """Manejador principal de la función Lambda."""
    validation_error = validate_event(event)
    if validation_error:
        return validation_error
    
    data = event.get('data')
    size = event.get('size')
    error_correction = event.get('errorCorrectionLevel')
    margin = event.get('margin')
    colors = event.get('color')
    
    qr_code_base64 = generate_qr_code(data, size, error_correction, margin, colors)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'qr_code': qr_code_base64
        })
    }
