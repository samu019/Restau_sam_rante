# restaurant/emails.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def enviar_email_solicitud_recibida(solicitud):
    """Envía email al usuario cuando su solicitud es recibida/verificada"""
    subject = f'✅ Pago Verificado - {solicitud.nombre_restaurante}'
    
    html_message = render_to_string('restaurant/emails/solicitud_recibida.html', {
        'solicitud': solicitud,
        'usuario': solicitud.usuario
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[solicitud.usuario.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

def enviar_email_solicitud_aprobada(solicitud, restaurante):
    """Envía email al usuario cuando su solicitud es aprobada"""
    subject = f'🎉 ¡Felicidades! Tu restaurante ha sido aprobado - {solicitud.nombre_restaurante}'
    
    html_message = render_to_string('restaurant/emails/solicitud_aprobada.html', {
        'solicitud': solicitud,
        'restaurante': restaurante,
        'usuario': solicitud.usuario
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[solicitud.usuario.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

def enviar_email_solicitud_rechazada(solicitud, motivo):
    """Envía email al usuario cuando su solicitud es rechazada"""
    subject = f'❌ Actualización sobre tu solicitud - {solicitud.nombre_restaurante}'
    
    html_message = render_to_string('restaurant/emails/solicitud_rechazada.html', {
        'solicitud': solicitud,
        'motivo': motivo,
        'usuario': solicitud.usuario
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[solicitud.usuario.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

def enviar_notificacion_admin_nueva_solicitud(solicitud):
    """Envía email al admin cuando hay una nueva solicitud"""
    subject = f'📋 Nueva Solicitud de Restaurante - {solicitud.nombre_restaurante}'
    
    html_message = render_to_string('restaurant/emails/notificacion_admin.html', {
        'solicitud': solicitud
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False