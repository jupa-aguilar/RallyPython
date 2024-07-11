import ssl
from pyral import Rally

# Deshabilitar verificación SSL (solo para pruebas)
ssl._create_default_https_context = ssl._create_unverified_context

# Configuración de conexión a Rally
RALLY_SERVER = 'rally1.rallydev.com'
API_KEY = '_j4Iy2htQuCutXrGneZPit5tgyaeYkaDtRsLor7Rqgs'
WORKSPACE = 'Main'
PROJECT_NAME = 'Customer-Support-Tech'

# Constantes para configuración del script
QA_OWNER_EMAIL = 'AArias@ancestry.com'
# QA_OWNER_EMAIL = 'slevita.contractor@ancestry.com'
# QA_OWNER_EMAIL = 'mpatel@ancestry.com'

TICKET_PADRE_ID = 'US286169'

# Función para obtener una referencia de Rally
def obtener_referencia(rally, tipo, fetch, query):
    response = rally.get(tipo, fetch=fetch, query=query)
    for item in response:
        return item
    return None

# Función para crear una etiqueta
def crear_etiqueta(rally, etiqueta):
    tag_data = {'Name': etiqueta}
    tag = rally.put('Tag', tag_data)
    return tag

# Autenticación en Rally
try:
    rally = Rally(server=RALLY_SERVER, apikey=API_KEY, workspace=WORKSPACE)
    print("Conectado a Rally exitosamente.")
except Exception as e:
    print(f"Error al conectar a Rally: {e}")
    exit(1)

# Obtener referencia del Proyecto
project = obtener_referencia(rally, 'Project', "ObjectID,Name", f'Name = "{PROJECT_NAME}"')
if not project:
    print(f"Error: No se encontró el proyecto {PROJECT_NAME}")
    exit(1)
project_ref = project._ref
print(f"Project Ref: {project_ref}")

# Obtener referencia del Ticket Padre
ticket_padre = obtener_referencia(rally, 'HierarchicalRequirement', "ObjectID,Name,PlanEstimate,Release,Iteration,Owner,Description", f'FormattedID = "{TICKET_PADRE_ID}"')
if not ticket_padre:
    print(f"Error: No se encontró el ticket padre con ID {TICKET_PADRE_ID}")
    exit(1)
ticket_padre_ref = ticket_padre._ref
ticket_padre_name = ticket_padre.Name
plan_estimate_padre = ticket_padre.PlanEstimate
release_ref = ticket_padre.Release._ref if ticket_padre.Release else None
iteration_ref = ticket_padre.Iteration._ref if ticket_padre.Iteration else None
owner_ref = ticket_padre.Owner._ref if ticket_padre.Owner else None
description_padre = ticket_padre.Description

# Manejar la posible ausencia del campo 'c_Color'
color_padre = getattr(ticket_padre, 'c_Color', None)

print(f"Ticket Padre Ref: {ticket_padre_ref}, Name: {ticket_padre_name}")

# Obtener referencia del Usuario de QA
try:
    qa_user_response = rally.get('User', fetch="ObjectID,UserName,EmailAddress", query=f'EmailAddress = "{QA_OWNER_EMAIL}"')
    qa_user = next(qa_user_response)
    qa_user_ref = qa_user._ref
    print(f"QA Owner Ref: {qa_user_ref}, UserName: {qa_user.UserName}")
except StopIteration:
    print(f"Error: No se encontró el usuario con EmailAddress = {QA_OWNER_EMAIL}")
    exit(1)
except Exception as e:
    print(f"Error al obtener el User ID de QA: {e}")
    exit(1)

# Crear etiqueta 'L1 Deploy'
try:
    tag = crear_etiqueta(rally, 'L1 Deploy')
    tag_ref = tag._ref
    print(f"Etiqueta 'L1 Deploy' creada con Ref: {tag_ref}")
except Exception as e:
    print(f"Error al crear la etiqueta 'L1 Deploy': {e}")
    exit(1)

# Crear los tres tickets hijos
child_tickets = {
    'DEV': None,
    'QA': None,
    'L1 DEPLOY': None
}

# Ajustar el PlanEstimate del hijo DEV si el del padre no está configurado
plan_estimate_dev = plan_estimate_padre if plan_estimate_padre is not None else None

ticket_data = {
    'DEV': {
        'PlanEstimate': plan_estimate_dev,
        'Release': release_ref,
        'Iteration': iteration_ref,
        'Owner': owner_ref,
        'c_Color': color_padre,
        'Description': description_padre
    },
    'QA': {
        'Release': release_ref,
        'Iteration': iteration_ref,
        'Owner': qa_user_ref,
        'c_Color': color_padre,
        'Description': description_padre
    },
    'L1 DEPLOY': {
        'PlanEstimate': 1,
        'Owner': owner_ref,
        'Tags': [{"_ref": tag_ref}],
        'c_Color': color_padre,
        'Description': "PRE-DEPLOYMENT STEPS\n•\n\nPOST-DEPLOYMENT STEPS\n•"
    }
}

def crear_ticket_hijo(tipo, nombre, ticket_padre_ref, datos_adicionales):
    ticket_data = {
        'Name': nombre,
        'Project': project_ref,
        'Parent': ticket_padre_ref
    }
    ticket_data.update(datos_adicionales)
    if 'c_Color' in ticket_data and ticket_data['c_Color'] is None:
        del ticket_data['c_Color']
    return rally.put('HierarchicalRequirement', ticket_data)

# Crear el ticket DEV
try:
    dev_ticket = crear_ticket_hijo('DEV', f"[DEV] {ticket_padre_name}", ticket_padre_ref, ticket_data['DEV'])
    child_tickets['DEV'] = dev_ticket
    print(f"Ticket hijo 'DEV' creado con el ID: {dev_ticket.ObjectID}")
except Exception as e:
    print(f"Error al crear el ticket hijo 'DEV': {e}")

# Crear el ticket QA con dependencia del ticket DEV
try:
    if child_tickets['DEV']:
        qa_ticket_data = ticket_data['QA']
        qa_ticket_data['Predecessors'] = [child_tickets['DEV']._ref]
        qa_ticket = crear_ticket_hijo('QA', f"[QA] {ticket_padre_name}", ticket_padre_ref, qa_ticket_data)
        child_tickets['QA'] = qa_ticket
        print(f"Ticket hijo 'QA' creado con el ID: {qa_ticket.ObjectID}")
except Exception as e:
    print(f"Error al crear el ticket hijo 'QA': {e}")

# Crear el ticket L1 DEPLOY con dependencia del ticket QA
try:
    if child_tickets['QA']:
        l1_deploy_ticket_data = ticket_data['L1 DEPLOY']
        l1_deploy_ticket_data['Predecessors'] = [child_tickets['QA']._ref]
        l1_deploy_ticket = crear_ticket_hijo('L1 DEPLOY', f"[L1 DEPLOY] {ticket_padre_name}", ticket_padre_ref, l1_deploy_ticket_data)
        child_tickets['L1 DEPLOY'] = l1_deploy_ticket
        print(f"Ticket hijo 'L1 DEPLOY' creado con el ID: {l1_deploy_ticket.ObjectID}")
except Exception as e:
    print(f"Error al crear el ticket hijo 'L1 DEPLOY': {e}")