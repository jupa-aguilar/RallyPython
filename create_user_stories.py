import ssl
from pyral import Rally
from datetime import datetime, timedelta
from slack_poster import post_to_slack

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

# Función para obtener el próximo jueves
def obtener_proximo_jueves():
    hoy = datetime.now()
    dias_para_jueves = (3 - hoy.weekday() + 7) % 7
    proximo_jueves = hoy + timedelta(days=dias_para_jueves)
    return proximo_jueves

def obtener_proximo_lunes():
    hoy = datetime.now()
    dias_para_lunes = (7 - hoy.weekday()) % 7
    proximo_lunes = hoy + timedelta(days=dias_para_lunes)
    return proximo_lunes

def obtener_dia_especifico(dia_solicitado):
    dias_semana = {
        "lunes": 0,
        "martes": 1,
        "miércoles": 2,
        "jueves": 3,
        "viernes": 4,
        "sábado": 5,
        "domingo": 6
    }

    hoy = datetime.now()
    dia_solicitado = dia_solicitado.lower()

    if dia_solicitado not in dias_semana:
        raise ValueError("El día solicitado no es válido. Usa: lunes, martes, miércoles, jueves, viernes, sábado o domingo.")
    
    dia_actual = hoy.weekday()
    dias_para_dia_solicitado = (dias_semana[dia_solicitado] - dia_actual + 7) % 7
    dia_especifico = hoy + timedelta(days=dias_para_dia_solicitado)

    return dia_especifico

# Función para obtener los detalles de los tickets desde Rally
def obtener_detalles_tickets(rally, ticket_ids):
    detalles_tickets = []
    for ticket_id in ticket_ids:
        ticket = rally.get('HierarchicalRequirement', query=f'FormattedID = "{ticket_id}"', instance=True)
        if ticket:
            detalles_tickets.append({
                'id': ticket.FormattedID,
                'name': ticket.Name,
                'url': f'https://rally1.rallydev.com/#/detail/userstory/{ticket.ObjectID}'
            })
    return detalles_tickets

# Fecha configurable
# fecha = obtener_proximo_jueves()
# obtener el próximo miercoles
fecha = obtener_dia_especifico("miércoles")
fecha_str = fecha.strftime("%m-%d-%Y")

# Función para obtener el nombre de la Release y la Iteration
def obtener_release_iteration(fecha):
    year = fecha.year
    trimestre = (fecha.month - 1) // 3 + 1
    release = f"PI-{year}_Q{trimestre}"

    # Encuentra la iteration correspondiente
    iteration_end_dates = {
        "Sprint_11_2024": datetime(2024, 6, 4),
        "Sprint_12_2024": datetime(2024, 6, 18),
        "Sprint_13_2024": datetime(2024, 7, 2),
        "Sprint_14_2024": datetime(2024, 7, 16),
        "Sprint_15_2024": datetime(2024, 7, 30),
        "Sprint_16_2024": datetime(2024, 8, 13),
        "Sprint_17_2024": datetime(2024, 8, 27),
        "Sprint_18_2024": datetime(2024, 9, 10),
        "Sprint_19_2024": datetime(2024, 9, 24),
        "Sprint_20_2024": datetime(2024, 10, 8),
        "Sprint_21_2024": datetime(2024, 10, 22),
        "Sprint_22_2024": datetime(2024, 11, 5),
        "Sprint_23_2024": datetime(2024, 11, 19),
        # Agrega aquí las demás iterations
    }

    iteration = min(iteration_end_dates, key=lambda k: abs(iteration_end_dates[k] - fecha))

    return release, iteration

# Obtener Release e Iteration actuales basados en la fecha
release_name, iteration_name = obtener_release_iteration(fecha)
print(f"Release Name: {release_name}")
print(f"Iteration Name: {iteration_name}")

# Correo electrónico del usuario principal
USER_EMAIL = 'jaguilar@ancestry.com'

# Correo electrónico del usuario adicional 1 (configurable)
ADDITIONAL_USER_EMAIL_1 = 'AArias@ancestry.com'

# Correo electrónico del usuario adicional 2 (configurable)
ADDITIONAL_USER_EMAIL_2 = 'slevita.contractor@ancestry.com'

# Configuración de nombres y descripciones
user_story_1_name = f"[{fecha_str}] L1 Deployment Salesforce Release"
user_story_2_name = f"[{fecha_str}] Overarching L1 Deployment Salesforce Release"
description_1 = f"""
DEV:<br>
[{fecha_str}] Overarching L1 Deployment Salesforce Release<br><br>
QA:<br>
[QA-regression-{fecha_str}] PreProd regression<br>
[QA-regression-{fecha_str}] PreProd rollback<br>
[QA-regression-{fecha_str}] Production roll forward
"""

# Nombres de las tres user stories adicionales
additional_story_names = [
    f"[QA-regression-{fecha_str}] PreProd regression",
    f"[QA-regression-{fecha_str}] PreProd rollback",
    f"[QA-regression-{fecha_str}] Production roll forward"
]

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

# Lista de IDs de tickets
ticket_ids = ['US282371', 'US290012', 'US297547', 'US303552', 'US306275']  # Actualiza esta lista con los IDs reales

# Obtener los detalles de los tickets
detalles_tickets = obtener_detalles_tickets(rally, ticket_ids)

# Crear la descripción dinámica
fecha_proxima = obtener_proximo_jueves().strftime("%m-%d-%Y")
paap_value = ""  # Actualiza este valor según sea necesario

description_2_template = f"""
<b>Salesforce</b><br>
{fecha_proxima} Deployment Checklist<br><br>
<b>Stories Ready</b><br><br>
<b>Planned</b><br>
<ul>
"""

for ticket in detalles_tickets:
    description_2_template += f'<li><a href="{ticket["url"]}">{ticket["id"]}</a>: {ticket["name"]}</li>\n'

# Agregar la tabla del PAAP y los pasos de pre-despliegue y post-despliegue
description_2_template += f"""
</ul>
<table border="1" cellpadding="5" cellspacing="0">
    <tr>
        <th>PAAP</th>
        <td>{paap_value}</td>
    </tr>
</table>
<b>Pre-Deployment Steps</b><br>
<ul>
    <li>Paso 1</li>
    <li>Paso 2</li>
</ul>
<b>Post-Deployment Steps</b><br>
<ul>
    <li>Paso 1</li>
    <li>Paso 2</li>
</ul>
"""

# Obtener referencia del Proyecto
project = obtener_referencia(rally, 'Project', "ObjectID,Name", f'Name = "{PROJECT_NAME}"')
if not project:
    print(f"Error: No se encontró el proyecto {PROJECT_NAME}")
    exit(1)
project_ref = project._ref
print(f"Project Ref: {project_ref}")

# Obtener referencia del Epic
epic = obtener_referencia(rally, 'PortfolioItem/EPIC', "ObjectID,FormattedID,Name,Project", f'FormattedID = "{EPIC_FORMATTED_ID}"')
if not epic:
    print(f"Error: No se encontró el Epic con FormattedID {EPIC_FORMATTED_ID}")
    exit(1)
epic_ref = epic._ref
print(f"Epic Ref: {epic_ref}")

# Obtener referencia de la Release actual
release = obtener_referencia(rally, 'Release', "ObjectID,Name", f'Project.Name = "{PROJECT_NAME}" and Name = "{release_name}"')
if not release:
    print(f"Error: No se encontró ninguna Release actual con nombre {release_name} para el proyecto {PROJECT_NAME}")
    exit(1)
release_ref = release._ref
print(f"Release Ref: {release_ref}")

# Obtener referencia de la Iteration actual
iteration = obtener_referencia(rally, 'Iteration', "ObjectID,Name", f'Project.Name = "{PROJECT_NAME}" and Name = "{iteration_name}"')
if not iteration:
    print(f"Error: No se encontró ninguna Iteration actual con nombre {iteration_name} para el proyecto {PROJECT_NAME}")
    exit(1)
iteration_ref = iteration._ref
print(f"Iteration Ref: {iteration_ref}")

# Obtener referencia del Usuario principal
try:
    user_response = rally.get('User', fetch="ObjectID,UserName,EmailAddress", query=f'EmailAddress = "{USER_EMAIL}"')
    user = next(user_response)
    user_ref = user._ref
    print(f"Owner Ref: {user_ref}, UserName: {user.UserName}")
except StopIteration:
    print(f"Error: No se encontró el usuario con EmailAddress = {USER_EMAIL}")
    exit(1)
except Exception as e:
    print(f"Error al obtener el User ID: {e}")
    exit(1)

# Obtener referencia del Usuario adicional 1
try:
    additional_user_response_1 = rally.get('User', fetch="ObjectID,UserName,EmailAddress", query=f'EmailAddress = "{ADDITIONAL_USER_EMAIL_1}"')
    additional_user_1 = next(additional_user_response_1)
    additional_user_ref_1 = additional_user_1._ref
    print(f"Additional Owner Ref 1: {additional_user_ref_1}, UserName: {additional_user_1.UserName}")
except StopIteration:
    print(f"Error: No se encontró el usuario con EmailAddress = {ADDITIONAL_USER_EMAIL_1}")
    exit(1)
except Exception as e:
    print(f"Error al obtener el User ID adicional 1: {e}")
    exit(1)

# Obtener referencia del Usuario adicional 2
try:
    additional_user_response_2 = rally.get('User', fetch="ObjectID,UserName,EmailAddress", query=f'EmailAddress = "{ADDITIONAL_USER_EMAIL_2}"')
    additional_user_2 = next(additional_user_response_2)
    additional_user_ref_2 = additional_user_2._ref
    print(f"Additional Owner Ref 2: {additional_user_ref_2}, UserName: {additional_user_2.UserName}")
except StopIteration:
    print(f"Error: No se encontró el usuario con EmailAddress = {ADDITIONAL_USER_EMAIL_2}")
    exit(1)
except Exception as e:
    print(f"Error al obtener el User ID adicional 2: {e}")
    exit(1)

# Crear la primera User Story con Release e Iteration como Unscheduled
user_story_1_data = {
    'Name': user_story_1_name,
    'Description': description_1,  # Descripción específica para la primera User Story
    'Project': project_ref,
    'PortfolioItem': epic_ref,  # Usar PortfolioItem en lugar de Parent
    'PlanEstimate': PLAN_ESTIMATE,
    'c_StoryType': STORY_TYPE,
    'Owner': user_ref  # Asignar a tu usuario
    # No incluir 'Release' ni 'Iteration' para que sea Unscheduled
}

try:
  user_story_1 = rally.put('HierarchicalRequirement', user_story_1_data)
  if user_story_1:
    print(f"Primera User Story creada con el ID: {user_story_1.ObjectID}")
  else:
    print("Error: No se pudo crear la primera User Story.")
    exit(1)
except Exception as e:
    print(f"Error al crear la primera User Story: {e}")
    exit(1)

# Crear la segunda User Story con dependencia de la primera
user_story_2_data = {
    'Name': user_story_2_name,
    'Description': description_2_template.format(story_1_id=user_story_1.ObjectID, story_2_id='placeholder', story_3_id='placeholder'),
    'Project': project_ref,
    'PortfolioItem': epic_ref,  # Usar PortfolioItem en lugar de Parent
    'Release': release_ref,
    'Iteration': iteration_ref,
    'PlanEstimate': PLAN_ESTIMATE,
    'c_StoryType': STORY_TYPE,
    'Owner': user_ref,  # Asignar a tu usuario
    'Predecessors': [user_story_1._ref]  # Usar la referencia correcta
}

try:
    user_story_2 = rally.put('HierarchicalRequirement', user_story_2_data)
    if user_story_2:
        print(f"Segunda User Story creada con el ID: {user_story_2.ObjectID}")
    else:
        print("Error: No se pudo crear la segunda User Story.")
except Exception as e:
    print(f"Error al crear la segunda User Story: {e}")

# Actualizar descripción de la segunda historia con el ID correcto
description_2 = description_2_template.format(story_1_id=user_story_1.ObjectID, story_2_id=user_story_2.ObjectID, story_3_id='placeholder')
user_story_2_data_update = {
    'Description': description_2
}

try:
    rally.update('HierarchicalRequirement', user_story_2.ObjectID, user_story_2_data_update)
    print("Descripción de la segunda User Story actualizada.")
except Exception as e:
    print(f"Error al actualizar la descripción de la segunda User Story: {e}")

# Crear las tres User Stories adicionales para el usuario 1
for story_name in additional_story_names:
    additional_story_data = {
        'Name': story_name,
        'Description': "",  # Descripción vacía
        'Project': project_ref,
        'PortfolioItem': epic_ref,  # Usar PortfolioItem en lugar de Parent
        'Release': release_ref,
        'Iteration': iteration_ref,
        'PlanEstimate': PLAN_ESTIMATE,
        'c_StoryType': STORY_TYPE,
        'Owner': additional_user_ref_1,  # Asignar al usuario adicional 1
        'Predecessors': [user_story_1._ref]  # Dependencia de la primera User Story
    }
    try:
        additional_story = rally.put('HierarchicalRequirement', additional_story_data)
        if additional_story:
            print(f"User Story adicional creada con el ID: {additional_story.ObjectID}")
        else:
            print(f"Error: No se pudo crear la User Story {story_name}.")
    except Exception as e:
        print(f"Error al crear la User Story {story_name}: {e}")

# Crear las tres User Stories adicionales para el usuario 2
for story_name in additional_story_names:
    additional_story_data = {
        'Name': story_name,
        'Description': "",  # Descripción vacía
        'Project': project_ref,
        'PortfolioItem': epic_ref,  # Usar PortfolioItem en lugar de Parent
        'Release': release_ref,
        'Iteration': iteration_ref,
        'PlanEstimate': PLAN_ESTIMATE,
        'c_StoryType': STORY_TYPE,
        'Owner': additional_user_ref_2,  # Asignar al usuario adicional 2
        'Predecessors': [user_story_1._ref]  # Dependencia de la primera User Story
    }
    try:
        additional_story = rally.put('HierarchicalRequirement', additional_story_data)
        if additional_story:
            print(f"User Story adicional creada con el ID: {additional_story.ObjectID}")
        else:
            print(f"Error: No se pudo crear la User Story {story_name}.")
    except Exception as e:
        print(f"Error al crear la User Story {story_name}: {e}")

# Mensaje para postear en Slack

# Formatear la lista de tickets
planned_tickets = ""
for ticket in detalles_tickets:
    formatted_ticket = f'<{ticket["url"]}|{ticket["id"]}>: {ticket["name"]}'
    planned_tickets += f"  - {formatted_ticket}\n"

# Crear el mensaje completo
message = f"""
*L1 Deployment plan for this Thursday*
<https://example.com/US297794|US297794>: [{fecha_str}] Overarching L1 Deployment Salesforce Release
*Checklist*: <https://example.com/checklist|{fecha_str} Deployment Checklist>
*PR*: {iteration_name}_{fecha.month}_{fecha.day} (TBD)
*PAAP*: TBD

*Stories Ready*
*Planned*
{planned_tickets}
*next steps*:
  1. make sure all stories ready to deploy are listed on the checklist
  2. deploy to preprod: regression testing
  3. validate checklist
  4. deploy to preprod: test after roll-forward
  5. file PAAP ticket
  6. deploy to production: test after roll-forward
"""

# Llamar a la función para postear el mensaje
post_to_slack(message)
