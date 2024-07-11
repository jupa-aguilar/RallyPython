import ssl
from pyral import Rally

# Deshabilitar verificación SSL (solo para pruebas)
ssl._create_default_https_context = ssl._create_unverified_context

# Configura tu conexión a Rally
RALLY_SERVER = 'rally1.rallydev.com'  # Sin 'https://'
API_KEY = '_j4Iy2htQuCutXrGneZPit5tgyaeYkaDtRsLor7Rqgs'

# Autenticar con Rally
try:
    rally = Rally(server=RALLY_SERVER, apikey=API_KEY)
    print("Conectado a Rally exitosamente.")
except Exception as e:
    print(f"Error al conectar a Rally: {e}")
    exit(1)

# Obtener la lista de Workspaces
try:
    response = rally.get('Workspace')
    for workspace in response:
        print(f"Workspace: {workspace.Name}, ObjectID: {workspace.ObjectID}")
except Exception as e:
    print(f"Error al obtener Workspaces: {e}")