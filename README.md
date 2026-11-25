# AlmaSpa

## Segundo Parcial – Programación Web II

Sistema web desarrollado con Django para la gestión de solicitudes de tratamientos de un centro de bienestar y relajación.

## Funcionalidades

- Sitio web de presentación de AlmaSpa.
- Formulario de solicitud de turnos.
- Persistencia de datos mediante PostgreSQL y Django ORM.
- Clasificación automática de consultas.
- Panel administrativo con operaciones CRUD.
- Resumen de solicitudes por categoría.
- Registro de usuarios autorizados.
- Validación de cuentas mediante correo electrónico.
- Inicio y cierre de sesión.
- API propia de consultas mediante Django REST Framework.
- Integración con la API externa Open Beauty Facts.
- Envío de correos electrónicos mediante SMTP.

## Tecnologías utilizadas

- Python
- Django
- PostgreSQL
- Django REST Framework
- HTML, CSS y JavaScript
- Git y GitHub
- Render

## Repositorio GitHub

https://github.com/victoriaimo/AlmaSpa

## Sitio publicado

https://almaspa.onrender.com

## API externa

https://world.openbeautyfacts.org/

## Endpoints

- /api/consultas/
- /api/productos/

## Observaciones

El envío de correos electrónicos se probó en el entorno local. Se verificó la recepción del correo de validación de cuenta y la aceptación SMTP del correo de solicitud, aunque no se confirmó la recepción de este último.

El envío SMTP en Render queda sujeto a las restricciones de la plataforma.