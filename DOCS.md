# base-template

Este repositorio proporciona una estructura base para la organización y gestión de problemas CMS, utilizando [TPS (Testcase Preparation System)](https://github.com/ioi-2017/tps), así como la importación de usuarios y administradores.

Su objetivo principal es estandarizar y automatizar el flujo de trabajo para la preparación y despliegue de problemas usando CMS.

## Estructura de directorios

A continuación, se describen los principales directorios del template:

### `scripts/`

Este directorio contiene los scripts necesarios para, importar usuarios, generar casos de prueba, empaquetar y comprimir los casos de prueba, visualizar y generar los statements de los problemas.

#### Scripts Disponibles

##### `task-prepare-folder.sh`
Inicializa la estructura básica de carpetas y archivos para un nuevo problema de CMS. Crea subdirectorios como `checker`, `gen`, `grader`, `public`, `scripts`, `solution`, `statement`y `validator`.

**Uso:**
```bash
./scripts/task-prepare-folder.sh nuevo_nombre_carpeta_del_problema
```
> Se recomienda que el `nuevo_nombre_carpeta_del_problema` sea el nombre corto del problema

##### `task-view-statement.sh`
Muestra en el navegador el enunciado del problema actual (`statement/es.md`) abriéndolo automáticamente si está disponible en la carpeta.

**Uso:**
```bash
./scripts/task-view-statement.sh nombre_carpeta_del_problema
```

##### `task-gen-statement.sh`
Genera el archivo `es.pdf` a partir de un archivo fuente `es.md` usando pyppeteer con python.

**Uso:**
```bash
./scripts/task-gen-statement.sh nombre_carpeta_del_problema nombre_corto_del_problema es
```

> cambiar `es` por `en` si esta disponible el archivo statement/en.md para asi generar el archivo en.pdf
> Nota.- Para tener soporte en multiples idiomas es necesario crear el statement en formato de codigo de lenguaje: es, en, etc 

##### `task-gen-cases.sh`
Ejecuta los generadores de casos ubicados en el directorio `gen/` y guarda los casos de entrada/salida generados en el directorio `tests/`.

**Uso:**
```bash
./scripts/task-gen-cases.sh nombre_carpeta_del_problema
```

### `task-gen-zip.sh`
Genera un archivo `.zip` listo para ser cargado al CMS. Este zip contiene el statement, los casos, y archivos de configuración.

**Uso:**
```bash
./task-gen-zip.sh nombre_carpeta_del_problema
```

### `cms-import-users.sh`
Importa usuarios al CMS.
> Usado por los workflows

### `cms-import-admins.sh`
Importa administradores al CMS.
> Usado por los workflows

### `tasks/`

En este directorio se encuentra todo lo relacionado con la creación de problemas.
Cada problema debe ubicarse dentro de la carpeta `tasks`.

### `users/`

Este directorio incluye dos archivos CSV:
- Uno destinado a los administradores.
- Otro para los usuarios.

### `.github`

# importProblemsMain.yml

Este archivo define dos flujos de trabajo de GitHub Actions para automatizar el manejo de tareas y usuarios en un sistema CMS orientado a competencias de programación.

## Descripción general

El archivo contiene dos workflows principales:

- **Importación de problemas (tasks) y sus enunciados**
- **Importación de usuarios y administradores**

Ambos workflows se activan automáticamente al hacer push a la rama `main` sobre los respectivos directorios (`tasks/**` y `users/**`), o pueden ejecutarse manualmente (`workflow_dispatch`).

---

## 1. Importación de Problemas

Este workflow automatiza la preparación y carga de problemas y sus casos de prueba en el servidor CMS.

### Disparadores
- Push a la rama `main` en cualquier archivo dentro de `tasks/`
- Ejecución manual

### Flujo de trabajo

1. **Preparación del entorno:**
   - Se configura la conexión SSH usando una llave privada almacenada en los secretos del repositorio.
   - Se agregan los hosts conocidos para la conexión segura.

2. **Clonación del repositorio:**
   - Se hace checkout del código fuente.

3. **Instalación de dependencias:**
   - Se instalan utilidades como `dos2unix` y `zip`.
   - Se instala el sistema de pruebas TPS.

4. **Generación y exportación de tareas:**
   - Para cada directorio de problema en `tasks/`, se preparan los casos de prueba y se empaquetan en archivos ZIP utilizando scripts del repositorio.
   - Los archivos ZIP se copian a una carpeta temporal `cms/`.

5. **Carga del artefacto:**
   - Se suben los ZIP generados como artefacto para ser reutilizados en la siguiente etapa.

6. **Importación en el servidor:**
   - Se descarga el artefacto en el runner.
   - Se transfiere la carpeta `cms/` al servidor remoto mediante SCP.
   - En el servidor, se descomprimen los ZIP y se importan los problemas y sus enunciados utilizando los comandos `cmsImportTask` y `cmsAddStatement`.

---

## 2. Importación de Usuarios

Este workflow automatiza la importación de usuarios y administradores al sistema CMS.

### Disparadores
- Push a la rama `main` en cualquier archivo dentro de `users/`
- Ejecución manual

### Flujo de trabajo

1. **Preparación del entorno:**
   - Se configura la conexión SSH y los hosts conocidos.
   - Se hace checkout del código fuente.

2. **Carga de archivos al servidor:**
   - Se transfieren los directorios `scripts/` y `users/` al servidor remoto mediante SCP.

3. **Importación de usuarios:**
   - En el servidor, se ejecutan los scripts para importar administradores (`cms-import-admins.sh`) y usuarios (`cms-import-users.sh`).
   - Ambos scripts se encuentran dentro del directorio `scripts/` y deben tener permisos de ejecución.

---

## Variables y secretos requeridos

- `secrets.DEV_SSH_SECRET`: Llave privada SSH para autenticación con el servidor remoto.
- `vars.DEV_SSH_HOST`: Dirección del servidor remoto.
- `vars.DEV_SSH_USERNAME`: Usuario para la conexión SSH.

---
