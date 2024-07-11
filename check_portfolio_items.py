import ssl
from pyral import Rally

# Deshabilitar verificación SSL (solo para pruebas)
ssl._create_default_https_context = ssl._create_unverified_context

# Configuración de conexión a Rally
RALLY_SERVER = 'rally1.rallydev.com'
API_KEY = '_j4Iy2htQuCutXrGneZPit5tgyaeYkaDtRsLor7Rqgs'
WORKSPACE = 'Main'
PROJECT_NAME = 'Customer-Support-Tech'
EPIC_FORMATTED_ID = 'EPIC-32254'
STORY_TYPE = 'Operations Product Support'
PLAN_ESTIMATE = 1

# Función para obtener una referencia de Rally
def obtener_referencia(rally, tipo, fetch, query):
    response = rally.get(tipo, fetch=fetch, query=query)
    for item in response:
        return item.ref
    return None

# Autenticación en Rally
try:
    rally = Rally(server=RALLY_SERVER, apikey=API_KEY, workspace=WORKSPACE)
    print("Conectado a Rally exitosamente.")
except Exception as e:
    print(f"Error al conectar a Rally: {e}")
    exit(1)

# Obtener referencia del Proyecto
project_ref = obtener_referencia(rally, 'Project', "ObjectID,Name", f'Name = "{PROJECT_NAME}"')
if not project_ref:
    print(f"Error: No se encontró el proyecto {PROJECT_NAME}")
    exit(1)
print(f"Project Ref: {project_ref}")

# Intentar obtener algunos PortfolioItems para revisar los nombres de las entidades
try:
    portfolio_items_response = rally.get('PortfolioItem', fetch="ObjectID,FormattedID,Name,Project")
    print("PortfolioItems encontrados:")
    for item in portfolio_items_response:
        print(f"FormattedID: {item.FormattedID}, Name: {item.Name}, Type: {item._type}, ObjectID: {item.ObjectID}")
except Exception as e:
    print(f"Error al buscar PortfolioItems: {e}")
    exit(1)