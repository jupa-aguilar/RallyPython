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
STORY_TYPE = 'Operations Product Support'
PLAN_ESTIMATE = 1

# Autenticar con Rally
try:
    rally = Rally(server=RALLY_SERVER, apikey=API_KEY, workspace=WORKSPACE)
    print("Conectado a Rally exitosamente.")
except Exception as e:
    print(f"Error al conectar a Rally: {e}")
    exit(1)

# Obtener el ObjectID del Proyecto
try:
    project_response = rally.get('Project', fetch="ObjectID,Name", query=f'Name = "{PROJECT_NAME}"')
    project = project_response.next()
    project_ref = project.ref
    print(f"Project ID: {project.ObjectID}")
except Exception as e:
    print(f"Error al obtener el Project ID: {e}")
    exit(1)

# Buscar todos los Epics en el Proyecto
try:
    epics_response = rally.get('HierarchicalRequirement', fetch="ObjectID,FormattedID,Name", query=f'StoryType = "Epic" and Project.Name = "{PROJECT_NAME}"')
    epics = [epic for epic in epics_response]
    if not epics:
        print(f"Error: No se encontraron Epics en el proyecto {PROJECT_NAME}")
        exit(1)
    print("Epics encontrados en el proyecto:")
    for epic in epics:
        print(f"Epic ID: {epic.FormattedID}, Name: {epic.Name}, ObjectID: {epic.ObjectID}")
except Exception as e:
    print(f"Error al buscar Epics en el proyecto: {e}")
    exit(1)