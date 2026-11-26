# CELL UPDATER-S3

Sistema de gestión asistido por IA para la sincronización de binarios y respaldo atómico en RPCS3.

[![Versión](https://img.shields.io/badge/Versión-v0.2.0_Alpha-blue)](https://github.com/SNTKida/CELL-Updater-S3/releases)
[![Python](https://img.shields.io/badge/Python-3.14+-yellow)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6_(Qt6)-green)](https://www.qt.io/product/qt6)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


---

## About

**CELL UPDATER-S3** trasciende la idea de un simple instalador de actualizaciones. Es un sistema de gestión autónomo impulsado por **AMAZONA**, un agente de IA diseñado para blindar y optimizar tu experiencia de emulación en RPCS3.

En lugar de limitarse a descargar archivos, AMAZONA orquesta todo el ciclo de vida de la actualización: monitorea tu hardware, ejecuta **respaldos atómicos** para garantizar que nunca pierdas una partida, y utiliza su **Cerebro Multi-IA** para traducir los cambios técnicos en resúmenes inteligentes, dinámicos e irrepetibles. 

Más que un script, es un asistente que cobra vida en tu dashboard, saludándote y adaptándose a tu entorno para que tú solo te preocupes por jugar.

---

## Status del Proyecto

Inspirado en el desarrollo transparente de grandes proyectos open-source. Estado actual de los módulos en la versión `v0.2.0`:

| Módulo | Estado | Progreso |
|--------|--------|----------|
| Respaldo Atómico (Zero Data Loss) | ✅ Operativo | 100% |
| Cerebro Multi-IA (Cascada) | ✅ Operativo | 100% |
| Telemetría de Hardware (WMI/psutil) | ✅ Operativo | 100% |
| GitHub BYOT (Bring Your Own Token) | 🚧 En desarrollo | 0% |
| Auto-actualización de Cell Updater | 🚧 En desarrollo | 0% |
| Soporte Multiplataforma (Linux/macOS) | 📋 Planificado | 0% |

---

##  Características Principales

-  **Zero Data Loss:** Copia de seguridad atómica de `dev_hdd0` `config` `config.yml` `Guiconfig` `input_configs` `dev_flash` y `cache` antes de cada actualización.
-  **Cerebro Multi-IA:** Fallback en cascada (DeepSeek ☁️(para dev)  → Ollama 🦙(para usuarios) → Texto Crudo 📄).
-  **Segundo Plano:** Timer interno de 2h y verificación inmediata al arranque.
-  **Telemetría Real:** Monitoreo de CPU, RAM, GPU y SO en el dashboard.
-  **Saludo Dinámico Contextual:** El dashboard cobra vida saludando al usuario por su nombre, idioma y adaptando el mensaje según la hora del día (mañana, tarde, noche), creando una experiencia personalizada y cercana.
-  **Mensajes Inteligentes Irrepetibles:** AMAZONA nunca repite el mismo saludo ni el mismo resumen. Cada interacción es única, generada en tiempo real con variación contextual, evitando la sensación de "plantilla fija" y creando una experiencia conversacional viva.
-  **Privacidad:** Credenciales nunca empaquetadas. Configuración desacoplada.

## 📋 Requisitos Previos

Antes de ejecutar CELL UPDATER-S3, asegúrate de cumplir con lo siguiente:

### 1. RPCS3 Instalado
El programa necesita encontrar tu emulador RPCS3. Debes tenerlo instalado y **al menos haberlo ejecutado una vez** para que genere su estructura de carpetas base.
- **Descarga oficial:** [rpcs3.net](https://rpcs3.net/download)
- **Ubicación recomendada:** `C:\Emulators\RPCS3\` (o cualquier ruta, recomiendo en documentos **sin caracteres especiales ni espacios**).
- **Importante:** El programa buscará automáticamente la carpeta `dev_hdd0` dentro del directorio de RPCS3.

### 2. Ollama
Para usar el resumen inteligente de cambios con IA local (sin costos de API):
- Instala [Ollama](https://ollama.com) desde su página oficial.
- Abre tu terminal y ejecuta: `ollama pull phi3`
- Asegúrate de que el servicio esté corriendo (ícono en la bandeja del sistema).
---

##  Ecosistema de IA

El proyecto implementa un sistema multi-agente para el procesamiento de datos:

- **AMAZONA** 🤖 — Agente principal. Genera resúmenes de changelog, gestiona la cascada de IA y monitorea la integridad.
- **CELL Updater** ⚙️ — Asistente técnico. Valida configuraciones, gestiona respaldos y supervisa el ciclo de vida del binario.

---

## 🛠️ Instalación

### Paso 1: Descargar el binario
1. Ve a la página de [Releases](https://github.com/SNTKida/CELL-Updater-S3/releases).
2. Descarga el archivo más reciente.
3. **No ejecutes el `.exe` directamente desde el `.zip`.** Extrae todo el contenido primero (recomiendo crear un acceso directo en escritorio).

### Paso 2: Extraer en una ubicación permanente
1. Crea una carpeta en tu PC, por ejemplo: `C:\Tools\CELL-Updater\`
2. Extrae el contenido del `.zip` dentro de esa carpeta.

---

## Ubicación de Archivos y Configuración

CELL UPDATER-S3 es transparente sobre dónde guarda tu información. Todos los archivos de usuario se almacenan en una carpeta dedicada llamada CellUpdaterS3 en Appdata, ahi dentro guardara registros de usuario e historial de actualizaciones, ambos en formato Json.

Dentro de esta carpeta encontrarás:

| Archivo/Carpeta | Descripción |
|-----------------|-------------|
| `user.json` | Tu configuración personal: nombre e idioma. |
| `logs/` | Historial de logs del sistema (útil para diagnosticar problemas). |
| `TempUpdate7z` | Respaldos atómicos de tus datos de RPCS3 (generados antes de cada actualización y se borran automaticamente una vez termine la actualizacion, protegiendo los datos mas importantes). |

> **Nota:** La carpeta `AppData` está oculta por defecto en Windows. Puedes acceder rápidamente presionando `Win + R` y escribiendo `%LOCALAPPDATA%\CELL-Updater-S3`.

##  Nota de Versión y Desarrollo

**CELL UPDATER-S3** es un proyecto en evolución continua. La versión actual (`v0.2.0 Alpha`) representa el núcleo funcional del sistema, pero el roadmap incluye características avanzadas como la auto-actualización del propio gestor y soporte multiplataforma. 

Si encuentras un error o tienes una sugerencia, no dudes en abrir un *Issue* en este repositorio. Tu feedback es vital para las próximas iteraciones.

---

