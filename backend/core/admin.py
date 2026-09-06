from django.contrib import admin

# El índice del admin usa nuestra plantilla que añade el panel "Resumen de la
# Fundación" encima del listado de apps (ver templates/admin/funcrees_index.html).
admin.site.index_template = 'admin/funcrees_index.html'
