import ssl
from pyral import Rally
import re

# Deshabilitar verificación SSL (solo para pruebas)
ssl._create_default_https_context = ssl._create_unverified_context

# Configuración de conexión a Rally
RALLY_SERVER = 'rally1.rallydev.com'
API_KEY = '_j4Iy2htQuCutXrGneZPit5tgyaeYkaDtRsLor7Rqgs'
WORKSPACE = 'Main'
PROJECT_NAME = 'Customer-Support-Tech'

# Constante para la fecha a ser utilizada en los tickets
FECHA_STR = "06-20-2024"

# Autenticación en Rally
try:
    rally = Rally(server=RALLY_SERVER, apikey=API_KEY, workspace=WORKSPACE)
    print("Conectado a Rally exitosamente.")
except Exception as e:
    print(f"Error al conectar a Rally: {e}")
    exit(1)

# ID del ticket principal
principal_ticket_id = 'US297793'

# Obtener el ticket principal
try:
    principal_ticket = rally.get('HierarchicalRequirement', query=f'FormattedID = "{principal_ticket_id}"', instance=True)
    if not principal_ticket:
        print(f"Error: No se encontró el ticket principal con ID {principal_ticket_id}")
        exit(1)
    principal_ticket_ref = principal_ticket._ref
    print(f"Principal Ticket Ref: {principal_ticket_ref}")
except Exception as e:
    print(f"Error al obtener el ticket principal: {e}")
    exit(1)

# Obtener los sucesores del ticket principal
try:
    sucesores_response = rally.get('HierarchicalRequirement', query=f'Predecessors = "{principal_ticket_ref}"')
    sucesores_tickets = list(sucesores_response)
    if not sucesores_tickets:
        print("No se encontraron sucesores para el ticket principal.")
        exit(1)
    print(f"Se encontraron {len(sucesores_tickets)} sucesores.")
except Exception as e:
    print(f"Error al obtener los sucesores: {e}")
    exit(1)

# Función para reemplazar la fecha en el nombre
def reemplazar_fecha(nombre, nueva_fecha):
    return re.sub(r'\d{2}-\d{2}-\d{4}', f'{nueva_fecha}', nombre)

# Actualizar el nombre y la descripción del ticket principal
nuevo_nombre_principal = reemplazar_fecha(principal_ticket.Name, FECHA_STR)
descripcion_principal = f"""
DEV:<br>
[{FECHA_STR}] Overarching L1 Deployment Salesforce Release<br><br>
QA:<br>
[QA-regression-{FECHA_STR}] PreProd regression<br>
[QA-regression-{FECHA_STR}] PreProd rollback<br>
[QA-regression-{FECHA_STR}] Production roll forward
"""
update_data_principal = {
    'ObjectID': principal_ticket.ObjectID,
    'Name': nuevo_nombre_principal,
    'Description': descripcion_principal
}
try:
    response = rally.update('HierarchicalRequirement', update_data_principal)
    print(f"Ticket principal {principal_ticket.FormattedID} actualizado con nuevo nombre: {nuevo_nombre_principal}")
    print(response)
except Exception as e:
    print(f"Error al actualizar el ticket principal {principal_ticket.FormattedID}: {e}")

# Actualizar los nombres de los sucesores que contienen "Overarching"
for ticket in sucesores_tickets:
    nuevo_nombre = reemplazar_fecha(ticket.Name, FECHA_STR)
    update_data = {
        'ObjectID': ticket.ObjectID,
        'Name': nuevo_nombre
    }
    try:
        response = rally.update('HierarchicalRequirement', update_data)
        print(f"Ticket {ticket.FormattedID} actualizado con nuevo nombre: {nuevo_nombre}")
        print(response)
    except Exception as e:
        print(f"Error al actualizar el ticket {ticket.FormattedID}: {e}")
