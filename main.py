from fastapi import FastAPI, Request
from env import ENDPOINT, ACCESS_ID, ACCESS_KEY, USERNAME, PASSWORD, DEVICE_ID
from tuya_connector.openapi import TuyaOpenAPI

app = FastAPI()

# Method to connect to Tuya OpenAPI
def connect_to_tuya():
    """
    Connects to Tuya OpenAPI using credentials from env.py
    Returns the openapi instance if successful, otherwise None.
    """
    try:
        openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
        openapi.login(USERNAME, PASSWORD)
        return openapi
    except Exception as e:
        # Log the error if needed
        print(f"Connection error: {e}")
        return None

@app.post("/device/on")
def turn_on_device():
    """
    Endpoint to turn ON the Tuya device
    """
    openapi = connect_to_tuya()
    if not openapi:
        return {"status": "Device not connected"}
    commands = {'commands': [{'code': 'switch_1', 'value': True}]}
    openapi.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', commands)
    return {"status": "Device turned ON"}

@app.post("/device/off")
def turn_off_device():
    """
    Endpoint to turn OFF the Tuya device
    """
    openapi = connect_to_tuya()
    if not openapi:
        return {"status": "Device not connected"}
    commands = {'commands': [{'code': 'switch_1', 'value': False}]}
    openapi.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', commands)
    return {"status": "Device turned OFF"} 

# Conversión de color a HSV para Tuya
def get_color_hsv(color):
    colores = {
        "rojo": {"h": 0, "s": 1000, "v": 1000},
        "verde": {"h": 120, "s": 1000, "v": 1000},
        "azul": {"h": 240, "s": 1000, "v": 1000},
        "amarillo": {"h": 60, "s": 1000, "v": 1000},
        "blanco": {"h": 0, "s": 0, "v": 1000},
        "morado": {"h": 280, "s": 1000, "v": 1000},
    }
    return colores.get(color.lower(), {"h": 0, "s": 0, "v": 1000})

@app.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()
        intent = body['queryResult']['intent']['displayName']
        parameters = body['queryResult'].get('parameters', {})

        tuya = connect_to_tuya()
        if not tuya:
            return {"fulfillmentText": "No se pudo conectar con el dispositivo."}

        if intent == "EncenderFoco":
            tuya.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands',
                    {'commands': [{'code': 'switch_1', 'value': True}]})
            return {"fulfillmentText": "Foco encendido."}

        elif intent == "ApagarFoco":
            tuya.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands',
                    {'commands': [{'code': 'switch_1', 'value': False}]})
            return {"fulfillmentText": "Foco apagado."}

        elif intent == "CambiarColorFoco":
            color = parameters.get("color")
            if not color:
                return {"fulfillmentText": "No entendí el color que deseas."}
            color_data = get_color_hsv(color)
            tuya.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands',
                    {'commands': [{'code': 'colour_data_v2', 'value': color_data}]})
            return {"fulfillmentText": f"Color cambiado a {color}."}

        elif intent == "IntensidadFoco":
            intensidad = parameters.get("intensidad")
            try:
                intensidad = int(intensidad)
                if not (10 <= intensidad <= 1000):
                    intensidad = max(10, min(intensidad, 1000))
                tuya.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands',
                        {'commands': [{'code': 'bright_value_v2', 'value': intensidad}]})
                return {"fulfillmentText": f"Intensidad ajustada a {intensidad}."}
            except:
                return {"fulfillmentText": "No entendí la intensidad que deseas."}

        return {"fulfillmentText": "No entendí el comando."}
    except Exception as e:
        print("Error general en webhook:", e)
        return {"fulfillmentText": "Hubo un error interno."}