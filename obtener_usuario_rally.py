import ssl
from pyral import Rally

# Deshabilitar verificación SSL (solo para pruebas)
ssl._create_default_https_context = ssl._create_unverified_context

# Configuración de conexión a Rally
RALLY_SERVER = 'rally1.rallydev.com'
API_KEY = '_j4Iy2htQuCutXrGneZPit5tgyaeYkaDtRsLor7Rqgs'
WORKSPACE = 'Main'
USER_EMAIL = 'AArias@ancestry.com'  # Reemplaza con el correo electrónico del usuario si lo conoces

# Función para obtener una referencia de Rally
def obtener_referencia(rally, tipo, fetch, query, order=""):
    response = rally.get(tipo, fetch=fetch, query=query, order=order)
    for item in response:
        return item
    return None

# Autenticación en Rally
try:
    rally = Rally(server=RALLY_SERVER, apikey=API_KEY, workspace=WORKSPACE)
    print("Conectado a Rally exitosamente.")
except Exception as e:
    print(f"Error al conectar a Rally: {e}")
    exit(1)

# Obtener referencia del Usuario por correo electrónico
try:
    user_response = rally.get('User', fetch="ObjectID,UserName,EmailAddress,DisplayName,UserPermissions", query=f'EmailAddress = "{USER_EMAIL}"')
    user = next(user_response)
    user_ref = user._ref
    print(f"User Ref: {user_ref}")
    print(f"UserName: {user.UserName}")
    print(f"EmailAddress: {user.EmailAddress}")
    print(f"DisplayName: {user.DisplayName}")
    print(f"UserPermissions: {user.UserPermissions}")
except StopIteration:
    print(f"Error: No se encontró el usuario con EmailAddress = {USER_EMAIL}")
    exit(1)
except Exception as e:
    print(f"Error al obtener el User ID: {e}")
    exit(1)

# Alternativamente, si conoces el DisplayName del usuario:
USER_DISPLAY_NAME = 'Alfredo Arias (Alfredator)'  # Reemplaza con el display name correcto

# Obtener referencia del Usuario por DisplayName
try:
    user_response = rally.get('User', fetch="ObjectID,UserName,EmailAddress,DisplayName,UserPermissions", query=f'DisplayName = "{USER_DISPLAY_NAME}"')
    user = next(user_response)
    user_ref = user._ref
    print(f"User Ref: {user_ref}")
    print(f"UserName: {user.UserName}")
    print(f"EmailAddress: {user.EmailAddress}")
    print(f"DisplayName: {user.DisplayName}")
    print(f"UserPermissions: {user.UserPermissions}")
except StopIteration:
    print(f"Error: No se encontró el usuario con DisplayName = {USER_DISPLAY_NAME}")
    exit(1)
except Exception as e:
    print(f"Error al obtener el User ID: {e}")
    exit(1)