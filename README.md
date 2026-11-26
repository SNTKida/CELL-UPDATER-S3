# CELL UPDATER-S3

Sistema de gestión asistido por IA para la sincronización de binarios y respaldo atómico en RPCS3.

[![Versión](https://img.shields.io/badge/Versión-v0.2.0_Alpha-blue)](https://github.com/SNTKida/CELL-Updater-S3/releases)
[![Python](https://img.shields.io/badge/Python-3.14+-yellow)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6_(Qt6)-green)](https://www.qt.io/product/qt6)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


---

## ℹ️ About

**CELL UPDATER-S3** trasciende la idea de un simple instalador de actualizaciones. Es un sistema de gestión autónomo impulsado por **AMAZONA**, un agente de IA diseñado para blindar y optimizar tu experiencia de emulación en RPCS3.

En lugar de limitarse a descargar archivos, AMAZONA orquesta todo el ciclo de vida de la actualización: monitorea tu hardware, ejecuta **respaldos atómicos** para garantizar que nunca pierdas una partida, y utiliza su **Cerebro Multi-IA** para traducir los cambios técnicos en resúmenes inteligentes, dinámicos e irrepetibles. 

Más que un script, es un asistente que cobra vida en tu dashboard, saludándote y adaptándose a tu entorno para que tú solo te preocupes por jugar.

---

## 📊 Status del Proyecto

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

## ✨ Características Principales

- 🛡️ **Zero Data Loss:** Copia de seguridad atómica de `dev_hdd0` `config` `config.yml` `Guiconfig` `input_configs` `dev_flash` y `cache` antes de cada actualización.
- 🧠 **Cerebro Multi-IA:** Fallback en cascada (DeepSeek ☁️(para dev)  → Ollama 🦙(para usuarios) → Texto Crudo 📄).
- ⚡ **Segundo Plano:** Timer interno de 2h y verificación inmediata al arranque.
- 📊 **Telemetría Real:** Monitoreo de CPU, RAM, GPU y SO en el dashboard.
- 🌅 **Saludo Dinámico Contextual:** El dashboard cobra vida saludando al usuario por su nombre, idioma y adaptando el mensaje según la hora del día (mañana, tarde, noche), creando una experiencia personalizada y cercana.
- 🗣️ **Mensajes Inteligentes Irrepetibles:** AMAZONA nunca repite el mismo saludo ni el mismo resumen. Cada interacción es única, generada en tiempo real con variación contextual, evitando la sensación de "plantilla fija" y creando una experiencia conversacional viva.
- 🔒 **Privacidad:** Credenciales nunca empaquetadas. Configuración desacoplada.

---

## 🧠 Ecosistema de IA

El proyecto implementa un sistema multi-agente para el procesamiento de datos:

- **AMAZONA** 🤖 — Agente principal. Genera resúmenes de changelog, gestiona la cascada de IA y monitorea la integridad.
- **CELL Updater** ⚙️ — Asistente técnico. Valida configuraciones, gestiona respaldos y supervisa el ciclo de vida del binario.

---

## 🛠️ Instalación


1. Descarga el último `.zip` desde [Releases](https://github.com/SNTKida/CELL-Updater-S3/releases).
2. Extrae en una carpeta (ej: `C:\Tools\CELL-Updater`).
3. Ejecuta `CELL_UPDATER_S3.exe`.

> **Nota:** Si Windows SmartScreen muestra una advertencia, haz clic en *"Más información"* → *"Ejecutar de todas formas"*.

---

## 📝 Nota de Versión y Desarrollo

**CELL UPDATER-S3** es un proyecto en evolución continua. La versión actual (`v0.2.0 Alpha`) representa el núcleo funcional del sistema, pero el roadmap incluye características avanzadas como la auto-actualización del propio gestor y soporte multiplataforma. 

Si encuentras un error o tienes una sugerencia, no dudes en abrir un *Issue* en este repositorio. Tu feedback es vital para las próximas iteraciones.

---

