import ssl
from pyral import Rally

# Deshabilitar verificación SSL (solo para pruebas)
ssl._create_default_https_context = ssl._create_unverified_context

# Configura tu conexión a Rally
RALLY_SERVER = 'rally1.rallydev.com'  # Sin 'https://'
API_KEY = '_j4Iy2htQuCutXrGneZPit5tgyaeYkaDtRsLor7Rqgs'
WORKSPACE = 'Main'
PROJECT_NAME = 'Customer-Support-Tech'
EPIC_FORMATTED_ID = 'EPIC-32254'

# Autenticar con Rally
try:
    rally = Rally(server=RALLY_SERVER, apikey=API_KEY, workspace=WORKSPACE)
    print("Conectado a Rally exitosamente.")
except Exception as e:
    print(f"Error al conectar a Rally: {e}")
    exit(1)

# Buscar el Epic por FormattedID en PortfolioItem/Epic
try:
    epics_response = rally.get('PortfolioItem/Epic', fetch="ObjectID,FormattedID,Name,Project,Workspace", query=f'FormattedID = "{EPIC_FORMATTED_ID}"')
    epics = [epic for epic in epics_response]
    if not epics:
        print(f"Error: No se encontró el Epic con FormattedID {EPIC_FORMATTED_ID}")
        exit(1)
    print("Epic encontrado:")
    for epic in epics:
        print(f"Epic ID: {epic.FormattedID}, Name: {epic.Name}, ObjectID: {epic.ObjectID}, Project: {epic.Project.Name}, Workspace: {epic.Workspace.Name}")
        epic_ref = epic.ref
except Exception as e:
    print(f"Error al buscar el Epic: {e}")
    exit(1)