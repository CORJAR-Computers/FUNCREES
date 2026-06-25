import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from beneficiaries.models import Beneficiary
from events.models import Event, Ticket
from donations.models import Donation
from contact.models import ContactMessage


def populate():
    print("Borrando datos anteriores...")
    Beneficiary.objects.all().delete()
    Event.objects.all().delete()
    Donation.objects.all().delete()
    ContactMessage.objects.all().delete()
    Ticket.objects.all().delete()

    print("Creando 50 Beneficiarios...")
    nombres_hombres = [
        'Don José', 'Don Alberto', 'Don Roberto', 'Don Pedro', 'Don Luis',
        'Don Carlos', 'Don Manuel', 'Don Jorge', 'Don Antonio', 'Don Miguel',
        'Don Rafael', 'Don Francisco', 'Don Eduardo', 'Don Hernando', 'Don Mario',
        'Don Alfredo', 'Don Gustavo', 'Don Óscar', 'Don César', 'Don Fernando',
        'Don Rodrigo', 'Don Arturo', 'Don Gabriel', 'Don Enrique', 'Don Julio'
    ]
    nombres_mujeres = [
        'Doña María', 'Doña Carmen', 'Doña Ligia', 'Doña Beatriz', 'Doña Rosa',
        'Doña Ana', 'Doña Teresa', 'Doña Luz', 'Doña Marta', 'Doña Cecilia',
        'Doña Isabel', 'Doña Elena', 'Doña Gloria', 'Doña Matilde', 'Doña Sofía',
        'Doña Juana', 'Doña Leticia', 'Doña Amelia', 'Doña Patricia', 'Doña Clara',
        'Doña Dora', 'Doña Blanca', 'Doña Nelly', 'Doña Margarita', 'Doña Lucía'
    ]
    apellidos = [
        'Martínez', 'Suárez', 'De la Ossa', 'Arrieta', 'Contreras',
        'Pérez', 'García', 'Rodríguez', 'López', 'Hernández',
        'González', 'Díaz', 'Moreno', 'Álvarez', 'Romero',
        'Torres', 'Ramírez', 'Castillo', 'Ortiz', 'Silva',
        'Vargas', 'Mendoza', 'Cruz', 'Reyes', 'Morales'
    ]
    lugares = [
        'Sincelejo', 'Corozal', 'Sampués', 'Tolú', 'San Marcos',
        'Chinú', 'San Benito', 'San Onofre', 'Morroa', 'Palmito',
        'Ovejas', 'San Pedro', 'Since', 'El Roble', 'Sahagún',
        'La Unión', 'Ciénaga de Oro', 'Montería', 'Cereté', 'Planeta Rica',
        'Buenavista', 'San Antero', 'San Bernardo', 'Tuchín', 'Purísima'
    ]
    tipos_fotos_h = [
        'https://randomuser.me/api/portraits/men/{}.jpg',
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face',
        'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face',
        'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face'
    ]
    tipos_fotos_m = [
        'https://randomuser.me/api/portraits/women/{}.jpg',
        'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face',
        'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face',
        'https://images.unsplash.com/photo-1542596768-5d1d21f1cf98?w=400&h=400&fit=crop&crop=face'
    ]

    testimonios = [
        "Gracias a Funcrees tengo un plato de comida caliente todos los días.",
        "Aquí encontré una familia que me quiere y valora mi experiencia.",
        "Los talleres de memoria me han ayudado a sentirme más activo.",
        "Ya no me siento solo. Los voluntarios son como mis nietos.",
        "La atención médica preventiva me ha cambiado la vida.",
        "A mis 83 años aprendí a usar el celular para hablar con mis hijos.",
        "El huerto comunitario me devolvió las ganas de vivir.",
        "Bailar en las tardes de terapia me hace sentir joven otra vez.",
        "Nunca imaginé que a esta edad tendría tantos amigos.",
        "La comida del comedor es deliciosa y nos tratan con mucho cariño.",
        "El acompañamiento psicológico me ayudó a superar la depresión.",
        "Hacer manualidades me mantiene la mente despejada.",
        "Me encanta enseñarles a los jóvenes a tejer hamacas.",
        "La fisioterapia me devolvió la movilidad de mis piernas.",
        "Cantar en el coro de la fundación es mi momento favorito.",
        "Compartir con otros abuelitos me hace sentir acompañado.",
        "Los médicos nos revisan la presión y el azúcar cada mes.",
        "Agradezco a Dios por las personas que apoyan esta obra.",
        "Los paseos que organizan son el mejor regalo del año.",
        "Todavía puedo aprender cosas nuevas, aquí me lo demostraron.",
        "Mis hijos viven lejos, pero aquí tengo quien me abrace.",
        "El taller de cocina me recordó los sabores de mi infancia.",
        "Leer cuentos a los niños que visitan la fundación es mi alegría.",
        "El deporte adaptado me ha fortalecido el cuerpo y el alma.",
        "Donde hay amor, hay esperanza. Gracias Funcrees."
    ]

    historias = [
        "Vivió toda su vida en el campo trabajando la tierra. Al enviudar y perder su hogar, llegó a la fundación donde encontró un nuevo propósito liderando el huerto comunitario.",
        "Fue costurera durante 40 años en Sincelejo. Hoy enseña su oficio a madres cabeza de familia en los talleres de la fundación, manteniendo viva la tradición.",
        "Exdocente rural jubilado, dedica sus tardes a enseñarles a leer a otros abuelitos que no tuvieron la oportunidad de estudiar.",
        "Perdió su casa en las inundaciones. En la fundación encontró techo, comida y una nueva familia que la quiere y respeta.",
        "Fue músico tradicional de gaitas. Ahora dirige el coro de la fundación y alegra los eventos con su acordeón.",
        "Trabajó como enfermera en el hospital de Sincelejo. Hoy colabora como voluntaria en las jornadas de salud preventiva.",
        "Es el mejor jugador de dominó de la fundación. Organiza torneos semanales que son el momento más alegre de la semana.",
        "Nunca tuvo hijos, pero aquí ha encontrado decenas de nietos adoptivos que la visitan y la llenan de amor.",
        "Fue conductor de bus durante 30 años. Ahora disfruta de los paseos que organiza la fundación por los pueblos de Sucre.",
        "Su mayor orgullo es haber aprendido a leer a los 82 años en los talleres de alfabetización de Funcrees."
    ]

    beneficiarios = []
    for i in range(50):
        is_mujer = i < 25
        nombres = nombres_mujeres if is_mujer else nombres_hombres
        fotos = tipos_fotos_m if is_mujer else tipos_fotos_h
        nombre = f"{nombres[i % 25]} {random.choice(apellidos)}"
        edad = random.randint(68, 96)
        ciudad = random.choice(lugares)
        foto_template = random.choice(fotos)
        if 'randomuser' in foto_template:
            foto_url = foto_template.format(random.randint(1, 99))
        else:
            foto_url = foto_template
        testimonio = random.choice(testimonios)
        historia = random.choice(historias)

        b = Beneficiary.objects.create(
            nombre=nombre,
            historia=historia,
            testimonio=testimonio,
            edad=edad,
            ciudad=ciudad,
            foto_url=foto_url,
            apadrinado=random.random() < 0.3,  # 30% apadrinados
            apadrinadores_count=random.randint(0, 3)
        )
        beneficiarios.append(b)

        if (i + 1) % 10 == 0:
            print(f"  ... {i + 1} beneficiarios creados")

    print("Creando Eventos...")
    Event.objects.create(
        id='bingo-solidario-2026',
        titulo='Gran Bingo Solidario Pro-Aguinaldos',
        descripcion='Participa en nuestro gran bingo anual. Tendremos premios increíbles y todo lo recaudado será para la cena navideña de nuestros 50 abuelitos.',
        fecha=timezone.now().date() + timedelta(days=30),
        hora='14:00',
        lugar='Coliseo de Sincelejo',
        costo_bono=20000.00,
        cupo_maximo=1000,
        numeracion_min=1,
        numeracion_max=1000,
        permite_seleccion_numero=True,
        categoria='evento',
        imagen_url='https://images.unsplash.com/photo-1513151233558-d860c5398176?auto=format&fit=crop&q=80&w=800'
    )

    Event.objects.create(
        id='gran-rifa-esperanza',
        titulo='Gran Rifa de la Esperanza',
        descripcion='Participa por un espectacular combo tecnológico para el hogar y bonos de mercado. El 100% recaudado apoya la salud de nuestros abuelitos.',
        fecha=timezone.now().date() + timedelta(days=60),
        hora='10:00',
        lugar='Sorteo Oficial - Lotería del Sinuano',
        costo_bono=10000.00,
        cupo_maximo=5000,
        numeracion_min=1,
        numeracion_max=500,
        permite_seleccion_numero=True,
        categoria='evento',
        imagen_url='https://images.unsplash.com/photo-1577083552431-6e5fd01988ec?auto=format&fit=crop&q=80&w=800'
    )

    Event.objects.create(
        id='campania-panales',
        titulo='Campaña Permanente de Pañales para Adulto Mayor',
        descripcion='Dona el valor equivalente a un paquete de pañales para adulto mayor y ayúdanos a mantener la dignidad de nuestros abuelitos.',
        costo_bono=35000.00,
        permite_seleccion_numero=False,
        categoria='campania',
        imagen_url='https://images.unsplash.com/photo-1576086213369-97a306d36557?auto=format&fit=crop&q=80&w=800'
    )

    Event.objects.create(
        id='venta-libros-culturales',
        titulo='Venta de Libros Culturales - Donación',
        descripcion='Adquiere libros donados por la comunidad a precios de aporte solidario. Una oportunidad de aprender y apoyar a la vez.',
        costo_bono=5000.00,
        permite_seleccion_numero=False,
        categoria='campania',
        imagen_url='https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&q=80&w=800'
    )

    print("  Eventos creados: Bingo, Rifa, Campaña Pañales, Venta de Libros")

    print("Creando Donaciones de prueba...")
    for i in range(10):
        Donation.objects.create(
            referencia=f"DONA-TEST{i:04d}",
            tipo=random.choice(['general', 'apadrinamiento', 'boleta']),
            monto=random.choice([20000, 30000, 50000, 100000, 200000, 500000]),
            donante_nombre=f"Donante Solidario {i + 1}",
            donante_email=f"donante{i + 1}@ejemplo.com",
            estado=random.choice(['completado', 'completado', 'completado', 'pendiente']),
            metodo_pago=random.choice(['wompi', 'pse', 'bancolombia']),
            autorizacion_datos=True
        )

    print("Creando Mensajes de Contacto...")
    ContactMessage.objects.create(
        nombre="Empresa Aliada S.A.S.",
        email="contacto@empresaaliada.com",
        telefono="3001234567",
        tipo="alianza",
        mensaje="Nos gustaría establecer una alianza de responsabilidad social empresarial con la fundación. Somos una empresa del sector salud interesada en apadrinar a 5 adultos mayores.",
    )
    ContactMessage.objects.create(
        nombre="María José Pérez",
        email="mariaj@ejemplo.com",
        telefono="3107654321",
        tipo="voluntariado",
        mensaje="Soy psicóloga con experiencia en gerontología y me gustaría ofrecer mis servicios como voluntaria los fines de semana.",
    )

    print("✅ ¡Población de datos finalizada exitosamente!")
    print(f"   • {Beneficiary.objects.count()} beneficiarios")
    print(f"   • {Event.objects.count()} eventos")
    print(f"   • {Donation.objects.count()} donaciones de prueba")
    print(f"   • {ContactMessage.objects.count()} mensajes de contacto")


if __name__ == '__main__':
    populate()
