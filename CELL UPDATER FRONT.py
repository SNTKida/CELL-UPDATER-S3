import sys
import os
import json
import subprocess
import threading
import requests
import webbrowser
import winreg
import traceback
import win32com.client
import ctypes
from datetime import datetime, timedelta

from PySide6.QtWidgets import *
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush
from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *

def get_resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso. Funciona en VS Code y en Nuitka --onefile"""
    if getattr(sys, 'frozen', False):
        # En Nuitka --onefile, sys.executable apunta a la carpeta temporal de extracción
        base_path = os.path.dirname(sys.executable)
    else:
        # En VS Code, apunta a la carpeta del script
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ==========================================
# CAJA NEGRA: Captura errores en modo .exe
# ==========================================
def log_error_to_file(error_msg):
    try:
        if getattr(sys, 'frozen', False):
            log_path = os.path.join(os.path.dirname(sys.executable), "error_log.txt")
        else:
            log_path = os.path.join(os.path.dirname(__file__), "error_log.txt")
        
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Fecha: {datetime.now()}\n")
            f.write(f"Error: {error_msg}\n")
            f.write(f"{'='*50}\n")
    except:
        pass

def excepcion_global(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log_error_to_file(error_msg)
    print(f"ERROR CRÍTICO: {error_msg}")

sys.excepthook = excepcion_global

try:
    from AMAZONA_AGENTE_IA import AMAZONA
    AMAZONA_AVAILABLE = True
except ImportError:
    AMAZONA_AVAILABLE = False
    AMAZONA = None

SKINS = {
    "CELL Updater": {
        "bg_primary": "#0d1117", "bg_secondary": "#161b22", "bg_sidebar": "#010409", 
        "text_primary": "#f0f6fc", "text_secondary": "#8b949e", "accent": "#0070D1", 
        "accent_hover": "#0088ff", "border": "#30363d", "btn_bg": "#21262d", "btn_hover": "#30363d"
    },
    "PS3 Clásico": {
        "bg_primary": "#0a0a0a", "bg_secondary": "#1a1a1a", "bg_sidebar": "#050505", 
        "text_primary": "#ffffff", "text_secondary": "#b0b0b0", "accent": "#0066cc", 
        "accent_hover": "#0088ff", "border": "#333333", "btn_bg": "#2a2a2a", "btn_hover": "#3a3a3a"
    },
    "Modo Claro": {
        "bg_primary": "#f6f8fa", "bg_secondary": "#ffffff", "bg_sidebar": "#f0f2f5", 
        "text_primary": "#1f2328", "text_secondary": "#656d76", "accent": "#0969da", 
        "accent_hover": "#0550ae", "border": "#d0d7de", "btn_bg": "#f3f4f6", "btn_hover": "#e5e7eb"
    }
}

class AmazonaWorker(QThread):
    progress_updated = Signal(int)
    status_updated = Signal(str)
    task_finished = Signal(bool, str)
    log_received = Signal(str)
    hardware_received = Signal(dict)
    ia_message_received = Signal(str)
    error = Signal(str)

    

    def __init__(self, amazona_instance):
        super().__init__()
        self.amazona = amazona_instance

    def run(self):
        try:
            self.amazona.log_signal.connect(self.log_received.emit)
            self.amazona.hardware_detected_signal.connect(self.hardware_received.emit)
            self.amazona.ia_message_signal.connect(self.ia_message_received.emit)
            self.amazona.update_finished_signal.connect(self.task_finished.emit)
            self.amazona.progress_signal.connect(self._manejar_progreso)
            self.status_updated.emit("Iniciando verificación del sistema...")
            self.amazona.Activador_IGNICIÓN()
        except Exception as e:
            self.error.emit(f"{str(e)}\n\n{traceback.format_exc()}")
            self.task_finished.emit(False, str(e))

    def _manejar_progreso(self, porcentaje, mensaje):
        self.progress_updated.emit(porcentaje)
        self.status_updated.emit(mensaje)

class Sidebar(QWidget):
    section_changed = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)
        self.setObjectName("sidebar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(20, 30, 20, 30)
        
        logo_label = QLabel("CELL Updater-S3")
        logo_label.setObjectName("logo_label")
        logo_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #f0f6fc; letter-spacing: 0.5px;")
        logo_layout.addWidget(logo_label)
        
        subtitle = QLabel("Sistema de Gestión")
        subtitle.setStyleSheet("font-size: 11px; color: #8b949e; font-weight: 400;")
        logo_layout.addWidget(subtitle)
        
        layout.addWidget(logo_container)
        layout.addSpacing(10)
        
        self.nav_buttons = {}
        nav_items = [("Dashboard", "dashboard"), ("Hardware", "hardware"), ("Historial", "historial"), ("Configuración", "config"), ("Acerca de", "about")]
        
        for text, section_id in nav_items:
            btn = QPushButton(text)
            btn.setObjectName(f"nav_btn_{section_id}")
            btn.setCheckable(True)
            btn.setChecked(section_id == "dashboard")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, sid=section_id: self.on_nav_clicked(sid))
            self.nav_buttons[section_id] = btn
            layout.addWidget(btn)
            
        layout.addStretch()
        
        info_label = QLabel("v0.2.0 Alpha\nBy SNTKida")
        info_label.setObjectName("sidebar_info")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 10px; color: #8b949e; padding: 20px; border-top: 1px solid #30363d;")
        layout.addWidget(info_label)
    
    def on_nav_clicked(self, section_id):
        for btn_id, btn in self.nav_buttons.items(): 
            btn.setChecked(btn_id == section_id)
        self.section_changed.emit(section_id)

    def crear_icono_con_badge(icono_base: QIcon, color_badge=QColor(255, 0, 0), tamano_badge=10) -> QIcon:
        """Crea un ícono con un círculo rojo (badge) en la esquina superior derecha"""
        pixmap = icono_base.pixmap(32, 32)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(color_badge))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(pixmap.width() - tamano_badge - 2, 2, tamano_badge, tamano_badge)
        painter.end()
        return QIcon(pixmap)


class MainWindow(QMainWindow):
    def __init__(self, modo="full"):
        super().__init__()
        self.modo = modo
        self.is_updating = False
        self.drag_position = None
        self.tray_icon = None
        self.amazona = None
        self.worker = None
        self.current_section = "dashboard"

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.resize(1150, 750)
        self.setMinimumSize(1000, 650)
        try: 
            self.setWindowIcon(QIcon("resources/icon_main.png"))
        except: 
            pass
        
        # ✅ FIX: Usar PNG con get_asset_path (funciona en Nuitka --onefile)
        try:
            get_asset_path = lambda p: os.path.join(os.path.dirname(__file__), p)
            icon_path = get_asset_path("assets/icon_main.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                print(f"✅ [APP] Ícono de ventana configurado: {icon_path}")
        except Exception as e:
            print(f"⚠️ [APP] No se pudo cargar el ícono: {e}")


        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.section_changed.connect(self.switch_section)
        main_layout.addWidget(self.sidebar)

        content_widget = QWidget()
        content_widget.setObjectName("content_area")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        header = QWidget()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.breadcrumb = QLabel("Dashboard / Overview")
        self.breadcrumb.setObjectName("breadcrumb")
        header_layout.addWidget(self.breadcrumb)
        header_layout.addStretch()
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setObjectName("status_indicator")
        header_layout.addWidget(self.status_indicator)
        
        self.status_text = QLabel("Sistema Activo")
        self.status_text.setObjectName("status_text")
        header_layout.addWidget(self.status_text)
        
        style = QApplication.style()
        for icon_type, tooltip in [(QStyle.SP_TitleBarMinButton, "Minimizar"), (QStyle.SP_TitleBarMaxButton, "Maximizar"), (QStyle.SP_TitleBarCloseButton, "Cerrar")]:
            btn = QPushButton()
            btn.setIcon(style.standardIcon(icon_type))
            btn.setFixedSize(35, 35)
            btn.setToolTip(tooltip)
            btn.setObjectName("window_btn")
            header_layout.addWidget(btn)
        
        window_buttons = header.findChildren(QPushButton)
        if len(window_buttons) >= 3:
            window_buttons[0].clicked.connect(self.showMinimized)
            window_buttons[1].clicked.connect(self.toggle_maximize)
            window_buttons[2].clicked.connect(self.close)
        
        content_layout.addWidget(header)

        self.page_stack = QStackedWidget()
        self.page_stack.addWidget(self.create_dashboard_page())
        self.page_stack.addWidget(self.create_hardware_page())
        self.page_stack.addWidget(self.create_history_page())
        self.page_stack.addWidget(self.create_config_page())
        self.page_stack.addWidget(self.create_about_page())
        content_layout.addWidget(self.page_stack)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setSizeGripEnabled(True)
        self.status_label = QLabel("Inicializando núcleo...")
        self.status_bar.addWidget(self.status_label)
        
        main_layout.addWidget(content_widget)

        self.tema_actual = "CELL Updater"
        self.apply_theme(self.tema_actual)
        
        QTimer.singleShot(100, self.init_amazona_background)
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_ui_light)
        self.refresh_timer.start(60000)
        self.setup_tray()
        
        if "--start-minimized" in sys.argv:
            self.hide()
        else:
            self.show()


    def activar_badge(self):
        """Muestra el circulito rojo en la bandeja"""
        if self.tray_icon and hasattr(self, 'icono_badge'):
            self.tray_icon.setIcon(self.icono_badge)

    def desactivar_badge(self):
        """Quita el circulito rojo"""
        if self.tray_icon and hasattr(self, 'icono_base'):
            self.tray_icon.setIcon(self.icono_base)

    # def _abrir_link(self, key):
    #     url = self._get_link(key)
    #     if url:
    #         webbrowser.open(url)

    def _get_link(self, key):
        if not self.amazona or not hasattr(self.amazona, 'carpeta_user'): 
            return ""
        path = os.path.join(self.amazona.carpeta_user, "user.json")
        if os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f: 
                    data = json.load(f)
                    return data.get(f"link_{key}", "")
            except: 
                pass
        return ""

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(25)
        layout.setContentsMargins(0, 0, 0, 0)

        welcome_card = QFrame()
        welcome_card.setObjectName("welcome_card")
        welcome_card.setMinimumHeight(100)
        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(30, 20, 30, 20)
        
        welcome_title = QLabel("Bienvenido al Sistema")
        welcome_title.setObjectName("welcome_title")
        welcome_layout.addWidget(welcome_title)
        
        self.welcome_label = QLabel("Inicializando componentes...")
        self.welcome_label.setObjectName("welcome_text")
        self.welcome_label.setWordWrap(True)
        welcome_layout.addWidget(self.welcome_label)
        layout.addWidget(welcome_card)

        versions_container = QWidget()
        versions_layout = QHBoxLayout(versions_container)
        versions_layout.setSpacing(20)
        
        versions_layout.addWidget(self._create_modern_card("Versión Local", "Detectando...", "version_local"))
        versions_layout.addWidget(self._create_modern_card("Versión Remota", "Detectando...", "version_remota"))
        versions_layout.addStretch()
        layout.addWidget(versions_container)

        ia_card = QFrame()
        ia_card.setObjectName("ia_card_principal")
        ia_card.setMinimumHeight(220)
        ia_layout = QVBoxLayout(ia_card)
        ia_layout.setContentsMargins(35, 25, 35, 25)
        
        ia_title = QLabel("MENSAJE INTELIGENTE DE AMAZONA")
        ia_title.setObjectName("ia_card_title")
        ia_layout.addWidget(ia_title)
        
        self.ia_message_label = QLabel("Esperando datos del sistema...")
        self.ia_message_label.setObjectName("ia_message_display")
        self.ia_message_label.setWordWrap(True)
        self.ia_message_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        ia_layout.addWidget(self.ia_message_label)
        layout.addWidget(ia_card)

        update_section = QFrame()
        update_section.setObjectName("update_section")
        update_layout = QVBoxLayout(update_section)
        update_layout.setContentsMargins(30, 25, 30, 25)
        
        update_title = QLabel("Gestión de Actualizaciones")
        update_title.setObjectName("update_title")
        update_layout.addWidget(update_title)
        
        update_desc = QLabel("Verifica e instala la última versión estable del emulador RPCS3.")
        update_desc.setObjectName("update_desc")
        update_layout.addWidget(update_desc)
        
        self.btn_update = QPushButton("Buscar e Instalar Actualizaciones")
        self.btn_update.setObjectName("update_btn")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.setMinimumHeight(45)
        self.btn_update.clicked.connect(self.run_update_check)
        update_layout.addWidget(self.btn_update)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(25)
        update_layout.addWidget(self.progress_bar)
        
        layout.addWidget(update_section)
        layout.addStretch()
        return page

    def _create_modern_card(self, title, value, obj_name, wider=False):
        card = QFrame()
        card.setObjectName(f"modern_card_{obj_name}")
        card.setMinimumWidth(350 if wider else 250)
        card.setMinimumHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(8)
        
        title_label = QLabel(title.upper())
        title_label.setObjectName("card_title")
        layout.addWidget(title_label)
        
        val_label = QLabel(value)
        val_label.setObjectName(f"card_value_{obj_name}")
        val_label.setWordWrap(True)
        layout.addWidget(val_label)
        layout.addStretch()
        return card

    def create_hardware_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        hw_section = QFrame()
        hw_section.setObjectName("content_group")
        hw_section.setMinimumHeight(300)
        hw_layout = QVBoxLayout(hw_section)
        hw_layout.setContentsMargins(30, 25, 30, 25)
        
        hw_title = QLabel("Información del Hardware")
        hw_title.setObjectName("section_title")
        hw_layout.addWidget(hw_title)
        
        self.label_hardware = QLabel("Cargando información del sistema...")
        self.label_hardware.setObjectName("hardware_display")
        self.label_hardware.setWordWrap(True)
        hw_layout.addWidget(self.label_hardware)
        
        layout.addWidget(hw_section)
        layout.addStretch()
        return page

    def create_history_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        hist_section = QFrame()
        hist_section.setObjectName("content_group")
        hist_section.setMinimumHeight(400)
        hist_layout = QVBoxLayout(hist_section)
        hist_layout.setContentsMargins(30, 30, 30, 30)
        
        hist_title = QLabel("Historial de Actividad")
        hist_title.setObjectName("section_title")
        hist_layout.addWidget(hist_title)
        
        self.history_text = QTextEdit()
        self.history_text.document().setMaximumBlockCount(100)
        self.history_text.setObjectName("history_display")
        self.history_text.setReadOnly(True)
        hist_layout.addWidget(self.history_text)
        
        layout.addWidget(hist_section)
        return page

    def create_config_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        theme_section = QFrame()
        theme_section.setObjectName("content_group")
        theme_section.setMinimumHeight(120)
        theme_layout = QVBoxLayout(theme_section)
        theme_layout.setContentsMargins(30, 25, 30, 25)
        
        theme_title = QLabel("Apariencia")
        theme_title.setObjectName("section_title")
        theme_layout.addWidget(theme_title)
        
        skin_layout = QHBoxLayout()
        skin_layout.addWidget(QLabel("Tema Visual:"))
        self.skin_combo = QComboBox()
        self.skin_combo.addItems(list(SKINS.keys()))
        self.skin_combo.setMinimumWidth(200)
        self.skin_combo.setMinimumHeight(35)
        self.skin_combo.currentTextChanged.connect(self.change_skin)
        skin_layout.addWidget(self.skin_combo)
        skin_layout.addStretch()
        theme_layout.addLayout(skin_layout)
        layout.addWidget(theme_section)

        startup_section = QFrame()
        startup_section.setObjectName("content_group")
        startup_section.setMinimumHeight(100)
        startup_layout = QVBoxLayout(startup_section)
        startup_layout.setContentsMargins(30, 25, 30, 25)
        
        startup_title = QLabel("Sistema")
        startup_title.setObjectName("section_title")
        startup_layout.addWidget(startup_title)
        
        self.chk_auto_start = QCheckBox("Iniciar CELL Updater automáticamente con Windows")
        self.chk_auto_start.setObjectName("toggle_switch")
        self.chk_auto_start.setCursor(Qt.PointingHandCursor)
        startup_layout.addWidget(self.chk_auto_start)
         
        # ✅ Cargar estado guardado del auto-inicio
        if self.amazona and hasattr(self.amazona, 'carpeta_user'):
            path = os.path.join(self.amazona.carpeta_user, "user.json")
            if os.path.isfile(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get("auto_start", False):
                            self.chk_auto_start.setChecked(True)
                            print("✅ [AUTO-START] Estado cargado: ACTIVADO")
                        else:
                            self.chk_auto_start.setChecked(False)
                            print("✅ [AUTO-START] Estado cargado: DESACTIVADO")
                except:
                    self.chk_auto_start.setChecked(False)
            else:
                self.chk_auto_start.setChecked(False)
        else:
            self.chk_auto_start.setChecked(False)
        
        startup_layout.addWidget(self.chk_auto_start)
        layout.addWidget(startup_section)

        actions_section = QFrame()
        actions_section.setObjectName("content_group")
        actions_section.setMinimumHeight(100)
        actions_layout = QVBoxLayout(actions_section)
        actions_layout.setContentsMargins(30, 25, 30, 25)
        
        actions_title = QLabel("Acciones Rápidas")
        actions_title.setObjectName("section_title")
        actions_layout.addWidget(actions_title)
        
        self.btn_open_folder = QPushButton("Abrir Carpeta de RPCS3")
        self.btn_open_folder.setObjectName("secondary_btn")
        self.btn_open_folder.setCursor(Qt.PointingHandCursor)
        self.btn_open_folder.setFixedWidth(250)
        self.btn_open_folder.setFixedHeight(40)
        self.btn_open_folder.clicked.connect(self.open_rpcs3_folder)
        actions_layout.addWidget(self.btn_open_folder)
        actions_layout.addStretch()
        layout.addWidget(actions_section)
        layout.addStretch()
        return page

    def create_about_page(self):
        
        
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        about_section = QFrame()
        about_section.setObjectName("content_group")
        about_layout = QVBoxLayout(about_section)
        about_layout.setContentsMargins(40, 30, 40, 30)
        
        # ── 1. Header: Título + Versión ──
        header_layout = QHBoxLayout()
        titulo = QLabel("CELL Updater-S3")
        titulo.setObjectName("about_title")
        header_layout.addWidget(titulo)
        
        version_badge = QLabel("v0.2.0 Alpha")
        version_badge.setObjectName("version_badge")
        header_layout.addWidget(version_badge)
        header_layout.addStretch()
        about_layout.addLayout(header_layout)
        
        # ── 2. Autoría (Marca SNT Kida) ──
        autor = QLabel("Sistema creado por SNTKida")
        autor.setObjectName("about_text")
        autor.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(autor)
        
        # ── 3. Botones de Redes Sociales (Funcionales y con tus enlaces reales) ──
        enlaces_reales = {
            "GitHub": "https://github.com/SNTKida",
            "Patreon": "https://www.patreon.com/c/SNTKida",
            "LinkedIn": "https://www.linkedin.com/in/pedro-alejandro-rengel-torres-50240936b/"
        }
        
        redes_layout = QHBoxLayout()
        redes_layout.addStretch()
        for nombre, url in enlaces_reales.items():
            btn = QPushButton(nombre)
            btn.setObjectName("secondary_btn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(120, 40)
            # Esta línea hace que el botón abra el navegador al hacer clic
            btn.clicked.connect(lambda checked, link=url: webbrowser.open(link))
            redes_layout.addWidget(btn)
        redes_layout.addStretch()
        about_layout.addLayout(redes_layout)

        # ── 4. Telemetría Global ──
        telemetria_box = QFrame()
        telemetria_box.setObjectName("telemetria_box")
        telemetria_layout = QVBoxLayout(telemetria_box)
        telemetria_layout.setContentsMargins(20, 20, 20, 20)
        
        telemetria_title = QLabel("TELEMETRÍA GLOBAL (GITHUB API)")
        telemetria_title.setObjectName("card_title")
        telemetria_layout.addWidget(telemetria_title)
        
        # Si el repo es privado, esto no funcionará. Lo dejamos así o puedes cambiar el texto.
        self.label_descargas = QLabel("Consultando servidor...")
        self.label_descargas.setObjectName("label_descargas")
        telemetria_layout.addWidget(self.label_descargas)
        about_layout.addWidget(telemetria_box)
        
        # ── 5. Pie de página (Limpio, sin mención a UDO o Tesis) ──
        footer = QLabel("© 2026 SNT Kida. Todos los derechos reservados.")
        footer.setObjectName("disclaimer")
        footer.setAlignment(Qt.AlignCenter)
        footer.setWordWrap(True)
        footer.setStyleSheet("font-size: 13px; padding: 20px; margin-top: 20px;")
        about_layout.addWidget(footer)
        
        layout.addWidget(about_section)
        layout.addStretch()
        return page

    # def guardar_enlaces(self):
    #     if not self.amazona or not hasattr(self.amazona, 'carpeta_user'): return
    #     path = os.path.join(self.amazona.carpeta_user, "user.json")
    #     data = {}
    #     if os.path.isfile(path):
    #         try:
    #             with open(path, 'r', encoding='utf-8') as f: data = json.load(f)
    #         except: pass
        
    #     data["link_github"] = self.input_github.text().strip()
    #     data["link_patreon"] = self.input_patreon.text().strip()
    #     data["link_linkedin"] = self.input_linkedin.text().strip()
        
    #     with open(path, 'w', encoding='utf-8') as f:
    #         json.dump(data, f, indent=4)
    #     QMessageBox.information(self, "Éxito", "Enlaces guardados correctamente.")

    def on_auto_start_changed(self, is_checked):
        """Maneja el cambio de estado del switch (is_checked es True o False)"""
        print(f"🔧 [AUTO-START] Switch cambiado a: {'ACTIVADO' if is_checked else 'DESACTIVADO'}")
        
        # 1. Ejecutar la lógica de sistema (crear/borrar acceso directo)
        self.configurar_auto_inicio(activar=is_checked)
        
        # 2. Guardar el estado en el JSON
        if self.amazona and hasattr(self.amazona, 'carpeta_user'):
            path = os.path.join(self.amazona.carpeta_user, "user.json")
            data = {}
            if os.path.isfile(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f: 
                        data = json.load(f)
                except: pass
            
            data["auto_start"] = is_checked
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
            except Exception as e:
                print(f"⚠️ [AUTO-START] No se pudo guardar en JSON: {e}")

    def configurar_auto_inicio(self, activar=True):
        """Crea o elimina el acceso directo en la carpeta de Inicio de Windows"""
        try:
            # Determinar la ruta del ejecutable
            if getattr(sys, 'frozen', False):
                target_path = sys.executable
            else:
                target_path = os.path.abspath(__file__)
            
            # Carpeta de Inicio de Windows (Startup)
            startup_folder = os.path.join(
                os.getenv('APPDATA'), 
                'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
            )
            shortcut_path = os.path.join(startup_folder, 'CELL Updater-S3.lnk')
            
            if activar:
                # Red Team: Usamos comillas simples dentro del script de PowerShell 
                # para que los espacios en las rutas no rompan el comando.
                ps_script = f"""
                $WshShell = New-Object -ComObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
                $Shortcut.TargetPath = '{target_path}'
                $Shortcut.Arguments = '--start-minimized'
                $Shortcut.WorkingDirectory = '{os.path.dirname(target_path)}'
                $Shortcut.Description = 'CELL Updater-S3'
                $Shortcut.Save()
                """
                
                # Ejecutar PowerShell oculto
                
                subprocess.run(
                    ['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script], 
                    check=False, capture_output=True
                )
                
                # Verificación de seguridad
                if os.path.exists(shortcut_path):
                    QMessageBox.information(self, "Auto-inicio", "Activado correctamente. Se iniciará con Windows.")
                    return True
                else:
                    QMessageBox.warning(self, "Error", "No se pudo crear el acceso directo. Revisa permisos.")
                    return False
                    
            else:
                # Desactivar: Borrar el acceso directo
                if os.path.exists(shortcut_path):
                    os.remove(shortcut_path)
                    QMessageBox.information(self, "Auto-inicio", "Desactivado correctamente.")
                else:
                    QMessageBox.information(self, "Auto-inicio", "Ya estaba desactivado.")
                return True
                
        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Fallo en auto-inicio: {str(e)}")
            return False

    def cargar_enlaces(self):
        if not self.amazona or not hasattr(self.amazona, 'carpeta_user'): return
        path = os.path.join(self.amazona.carpeta_user, "user.json")
        if os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f: data = json.load(f)
                self.input_github.setText(data.get("link_github", ""))
                self.input_patreon.setText(data.get("link_patreon", ""))
                self.input_linkedin.setText(data.get("link_linkedin", ""))
            except: pass

    def switch_section(self, section_id):
        self.current_section = section_id
        page_map = {"dashboard": 0, "hardware": 1, "historial": 2, "config": 3, "about": 4}
        title_map = {"dashboard": "Dashboard / Overview", "hardware": "Hardware del Sistema", "historial": "Historial de Actividad", "config": "Configuración", "about": "Acerca de CELL Updater-S3"}
        self.page_stack.setCurrentIndex(page_map.get(section_id, 0))
        self.breadcrumb.setText(title_map.get(section_id, "Dashboard"))

    def init_amazona_background(self):
        self.status_label.setText("Inicializando núcleo AMAZONA...")
        if AMAZONA_AVAILABLE:
            try:
                self.amazona = AMAZONA()
                self.amazona.Config_Rutas()
                self.amazona.Crear_carpeta()
                
                # ==========================================
                # DIAGNÓSTICO COMPLETO
                # ==========================================
                print(f"\n{'='*70}")
                print(f"🔍 DIAGNÓSTICO DE INICIO - CELL UPDATER S3")
                print(f"{'='*70}")
                print(f"📁 carpeta_app: {self.amazona.carpeta_base}")
                print(f"📁 carpeta_user: {self.amazona.carpeta_user}")
                
                user_json_path = os.path.join(self.amazona.carpeta_user, "user.json")
                print(f"📄 Ruta esperada de user.json: {user_json_path}")
                print(f"✅ ¿Existe el archivo?: {os.path.isfile(user_json_path)}")
                
                # Verificar contenido si existe
                if os.path.isfile(user_json_path):
                    try:
                        with open(user_json_path, 'r', encoding='utf-8') as f:
                            contenido = f.read()
                            print(f"📝 Contenido del JSON:\n{contenido}")
                    except Exception as e:
                        print(f"❌ Error leyendo JSON: {e}")
                
                # Listar archivos en carpeta User
                if os.path.exists(self.amazona.carpeta_user):
                    archivos = os.listdir(self.amazona.carpeta_user)
                    print(f"📂 Archivos en User: {archivos}")
                else:
                    print(f"⚠️ La carpeta User NO existe")
                
                print(f"{'='*70}\n")
                
                # ==========================================
                # CARGAR MEMORIA DE AMAZONA
                # ==========================================
                self.amazona.Cargar_memoria()
                print(f"👤 Después de Cargar_memoria(): usuario='{self.amazona.usuario}'")
                
                self.amazona.hardware_detected_signal.connect(self.actualizar_tarjetas_hardware)
                self.amazona.ia_message_signal.connect(self.actualizar_mensaje_amazona)
                self.amazona.actualizacion_bg_exitosa_signal.connect(self.on_bg_update_finished)
                if hasattr(self.amazona, 'notificacion_signal'):
                    self.amazona.notificacion_signal.connect(self.mostrar_notificacion)
                
                # ==========================================
                # VERIFICACIÓN DIRECTA Y FORZADA DEL USUARIO
                # ==========================================
                usuario_existente = None
                
                # Intento 1: Leer directamente el JSON
                if os.path.isfile(user_json_path):
                    try:
                        with open(user_json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            print(f"🔑 Claves en user.json: {list(data.keys())}")
                            
                            # Buscar en múltiples campos posibles
                            usuario_existente = (
                                data.get("usuario", "") or 
                                data.get("nombre", "") or 
                                data.get("user", "")
                            )
                            
                            if usuario_existente:
                                self.amazona.usuario = usuario_existente
                                self.amazona.idioma = data.get("idioma", "es")
                                print(f"✅ Usuario encontrado: '{usuario_existente}'")
                            else:
                                print(f"⚠️ Campo de usuario vacío en JSON")
                    except Exception as e:
                        print(f"❌ Error parseando JSON: {e}")
                
                # Intento 2: Si no hay usuario, crear uno por defecto
                if not usuario_existente:
                    print(f"⚠️ No se encontró usuario, creando diálogo de bienvenida")
                
                print(f"👤 self.amazona.usuario final: '{self.amazona.usuario}'")
                print(f"{'='*70}\n")
                
                # ==========================================
                # MOSTRAR SALUDO O DIÁLOGO
                # ==========================================
                if usuario_existente:
                    try:
                        saludo = self.amazona.saludo_dinamico()
                    except:
                        saludo = f"¡Bienvenido de nuevo, {usuario_existente.capitalize()}!"
                    self.actualizar_saludo(saludo)
                else:
                    self.actualizar_saludo("Bienvenido a CELL Updater-S3.")
                    dialog = QDialog(self)
                    dialog.setWindowTitle("Configuración Inicial")
                    layout = QVBoxLayout(dialog)
                    layout.addWidget(QLabel("¿Cómo te llamas?"))
                    input_nombre = QLineEdit()
                    layout.addWidget(input_nombre)
                    layout.addWidget(QLabel("Idioma preferido:"))
                    combo_idioma = QComboBox()
                    combo_idioma.addItems(["Español", "English"])
                    layout.addWidget(combo_idioma)
                    btn_ok = QPushButton("Continuar")
                    btn_ok.clicked.connect(dialog.accept)
                    layout.addWidget(btn_ok)
                    
                    if dialog.exec() == QDialog.Accepted:
                        nombre = input_nombre.text().strip().lower()
                        idioma = 'es' if combo_idioma.currentText() == "Español" else 'en'
                        if nombre:
                            self.amazona.usuario = nombre
                            self.amazona.idioma = idioma
                            
                            # Guardar inmediatamente y verificar
                            self.amazona.guardar_memoria()
                            
                            # Verificar que se guardó
                            if os.path.isfile(user_json_path):
                                print(f"✅ user.json creado exitosamente en: {user_json_path}")
                                with open(user_json_path, 'r', encoding='utf-8') as f:
                                    print(f"📝 Contenido guardado:\n{f.read()}")
                            else:
                                print(f"❌ ERROR: user.json NO se creó en: {user_json_path}")
                            
                            self.actualizar_saludo(f"¡Hola, {nombre.capitalize()}!")
                
                # ==========================================
                # RESTO DE LA INICIALIZACIÓN
                # ==========================================
                self.amazona.Detector_Hardware()
                
                
                self.status_label.setText("Sistema listo.")
                if hasattr(self, 'history_text'):
                    self.history_text.append("Núcleo AMAZONA cargado en segundo plano.")
                    #self.limitar_historial_ui()
                    self.cargar_historial_real()
                    #self.cargar_enlaces()
                
                self.tema_actual = self.cargar_preferencia_tema()
                self.skin_combo.blockSignals(True)
                self.skin_combo.setCurrentText(self.tema_actual)
                self.skin_combo.blockSignals(False)

                # ✅ CIRUGÍA: Cargar estado del auto-inicio desde el JSON
                if hasattr(self, 'chk_auto_start') and self.amazona:
                    path = os.path.join(self.amazona.carpeta_user, "user.json")
                    auto_start_state = False
                    if os.path.isfile(path):
                        try:
                            with open(path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                auto_start_state = data.get("auto_start", False)
                        except: pass
                    
                    # 1. Forzamos el estado visual SIN disparar el evento
                    self.chk_auto_start.setChecked(auto_start_state)
                    # 2. AHORA SÍ conectamos el cable
                    self.chk_auto_start.toggled.connect(self.on_auto_start_changed)
                    print(f"✅ [AUTO-START] Estado inicial cargado: {auto_start_state}")
                self.apply_theme(self.tema_actual)
                    # ✅ 2. ACTIVADOR DEL TIMER DE FONDO (Aquí está la magia)
                    # Inicia el ciclo de 2 horas automáticamente al abrir el programa
                self.amazona.Mecanismo_Buscador_Binarios_Timer(intervalo_horas=2)
                    
                #self._log_ui("✅ Sistema iniciado. Monitor de actualizaciones en segundo plano activo (cada 2h).")
                     
                QTimer.singleShot(500, self.actualizar_contador_descargas_bg)
            except Exception as e:
                self.status_label.setText("Error al iniciar AMAZONA.")
                if hasattr(self, 'history_text'): 
                    self.history_text.append(f"Error crítico: {e}")
                print(f"❌ ERROR CRÍTICO: {e}")
                
                traceback.print_exc()
        else:
            self.status_label.setText("Modo Limitado (AMAZONA no encontrado).")
            if hasattr(self, 'history_text'): 
                self.history_text.append("Ejecutando en modo limitado.")
        self.update_ui_light()

    #def limitar_historial_ui(self, max_lineas=100):
        ##if hasattr(self, 'history_text'):
           #######cursor.removeSelectedText()

    def agregar_log(self, mensaje):
        self.history_text.append(mensaje)
        #self.limitar_historial_ui()  # ← Solo aquí, se aplica en todos lados
                
    def mostrar_notificacion(self, titulo, mensaje):
        if self.tray_icon and QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.showMessage(titulo, mensaje, QSystemTrayIcon.Information, 5000)
        if hasattr(self, 'history_text'):
            self.history_text.append(f"[NOTIFICACIÓN] {titulo}: {mensaje}")

    def configurar_auto_inicio(self, activar=True):
        """Crea o elimina el acceso directo en la carpeta de Inicio de Windows"""
        try:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            # Carpeta de Inicio de Windows
            startup_folder = os.path.join(
                os.getenv('APPDATA'), 
                'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
            )
            shortcut_path = os.path.join(startup_folder, 'CELL Updater-S3.lnk')
            
            print(f"🔧 [AUTO-START] Carpeta Startup: {startup_folder}")
            print(f"🔧 [AUTO-START] Ruta del acceso directo: {shortcut_path}")
            print(f"🔧 [AUTO-START] Modo: {'ACTIVAR' if activar else 'DESACTIVAR'}")
            
            if activar:
                # Método 1: Usar win32com si está disponible
                try:
                    
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(shortcut_path)
                    shortcut.Targetpath = exe_path
                    shortcut.Arguments = "--start-minimized"
                    shortcut.WorkingDirectory = os.path.dirname(exe_path)
                    shortcut.Description = "CELL Updater-S3"
                    shortcut.save()
                    print(f"✅ [AUTO-START] Acceso directo creado con win32com")
                except ImportError:
                    # Método 2: Usar subprocess con PowerShell
                    
                    ps_script = f'''
                    $WshShell = New-Object -comObject WScript.Shell
                    $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
                    $Shortcut.TargetPath = "{exe_path}"
                    $Shortcut.Arguments = "--start-minimized"
                    $Shortcut.WorkingDirectory = "{os.path.dirname(exe_path)}"
                    $Shortcut.Description = "CELL Updater-S3"
                    $Shortcut.Save()
                    '''
                    
                    resultado = subprocess.run(
                        ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script], 
                        capture_output=True, 
                        text=True
                    )
                    
                    if resultado.returncode != 0:
                        print(f"⚠️ [AUTO-START] PowerShell falló: {resultado.stderr}")
                    else:
                        print(f"✅ [AUTO-START] Acceso directo creado con PowerShell")
                
                # Verificar si se creó
                if os.path.exists(shortcut_path):
                    print(f"✅ [AUTO-START] Verificado: acceso directo existe")
                    QMessageBox.information(
                        self, 
                        "Auto-inicio activado", 
                        "El programa se iniciará automáticamente con Windows (en bandeja)."
                    )
                    return True
                else:
                    print(f"❌ [AUTO-START] ERROR: El acceso directo NO se creó")
                    QMessageBox.warning(
                        self, 
                        "Error", 
                        "No se pudo crear el acceso directo. Verifica permisos de administrador."
                    )
                    return False
            else:
                # Eliminar acceso directo
                if os.path.exists(shortcut_path):
                    os.remove(shortcut_path)
                    print(f"✅ [AUTO-START] Acceso directo eliminado")
                    QMessageBox.information(
                        self, 
                        "Auto-inicio desactivado", 
                        "El programa ya no se iniciará automáticamente con Windows."
                    )
                else:
                    print(f"ℹ️ [AUTO-START] No existía acceso directo para eliminar")
                    QMessageBox.information(
                        self, 
                        "Auto-inicio", 
                        "Ya estaba desactivado."
                    )
                return True
                
        except Exception as e: 
            print(f"❌ [AUTO-START] Error: {e}")
            
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"No se pudo configurar:\n{str(e)}")
            return False

    def cargar_historial_real(self):
        if not hasattr(self, 'history_text'): return
        if not self.amazona or not hasattr(self.amazona, 'carpeta_user'):
            self.history_text.append("📜 Esperando configuración...")
            return
        
        path = os.path.join(self.amazona.carpeta_user, "historial_actualizaciones.json")
        if not os.path.isfile(path):
            self.history_text.append("📜 Historial vacío. Las actualizaciones aparecerán aquí.")
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f: 
                historial = json.load(f)
            
            if historial:
                for entry in reversed(historial[-15:]):
                    fecha = entry.get('fecha', 'Fecha desconocida')
                    version = entry.get('version', 'Versión desconocida')
                    mensaje = entry.get('mensaje', 'Sin mensaje')
                    self.history_text.append(f"📅 {fecha} | Versión: {version}")
                    self.history_text.append(f"   💬 {mensaje}")
                    self.history_text.append("")
            else:
                self.history_text.append("📜 No hay actualizaciones previas registradas.")
                self.history_text.append("   Las actualizaciones futuras aparecerán aquí.")
        except Exception as e:
            self.history_text.append(f"⚠️ Error al leer historial: {e}")

    def actualizar_mensaje_amazona(self, mensaje):
        ia_message_label = self.findChild(QLabel, "ia_message_display")
        if ia_message_label:
            ia_message_label.setText(mensaje)
        
        ia_label = self.findChild(QLabel, "card_value_ia_status")
        if ia_label: 
            ia_label.setText(mensaje)

    def actualizar_saludo(self, mensaje):
        if hasattr(self, 'welcome_label'):
            self.welcome_label.setText(mensaje)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            widget = self.childAt(event.pos())
            if widget and not isinstance(widget, (QPushButton, QTextEdit, QComboBox, QScrollBar, QAbstractScrollArea)):
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def toggle_maximize(self):
        self.showMaximized() if not self.isMaximized() else self.showNormal()

    def setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable(): 
            print("ADVERTENCIA: Bandeja del sistema no disponible en este OS.")
            return
        
        icon = QIcon("assets/icon_main.ico")
        if icon.isNull():
            icon = self.windowIcon()
        
        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("CELL Updater-S3")
        get_asset_path = lambda relative_path: os.path.join(os.path.dirname(__file__), relative_path)
        icon_path = get_asset_path("assets/icon_main.png") 
        
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            # Fallback por si acaso
            icon = self.windowIcon() 

        tray_menu = QMenu()
        tray_menu.addAction("Abrir Panel", self.showNormal)
        tray_menu.addAction("Buscar Actualizaciones", self.run_update_check)
        tray_menu.addSeparator()
        tray_menu.addAction("Salir", self.exit_app)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
        
        self.update_check_timer = QTimer()
        self.update_check_timer.timeout.connect(self.verificar_actualizacion_bg)
        self.update_check_timer.start(7200000)  # 2 horas = 7,200,000 ms
        print("[LOG] ⏰ Timer de actualizaciones automáticas activado (cada 2h)")
        
    def on_tray_activated(self, reason):
        """Maneja los clics en el ícono de la bandeja del sistema"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.activateWindow()
                self.desactivar_badge()  # <--- ¡APAGAR BADGE AL ABRIR!
                
        elif reason == QSystemTrayIcon.Trigger:
            self.showNormal()
            self.activateWindow()
            self.desactivar_badge()  # <--- ¡APAGAR BADGE AL ABRIR!

    def verificar_actualizacion_bg(self):
        if not self.amazona:
            return
        try:
            self.amazona.Conectar_internet()
            self.amazona.Consultar_Release_GitHub()
            version_local = getattr(self.amazona, 'version_local', '0')
            version_remota = getattr(self.amazona, 'Version_Nube_GitHub', '0')
            
            if version_remota and version_local != version_remota:
                self.mostrar_notificacion_actualizacion(version_remota)
        except Exception:
            pass

    def mostrar_notificacion_actualizacion(self, version):
        if self.tray_icon and QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.setToolTip(f"CELL Updater-S3 - Actualización {version} disponible")
            self.tray_icon.showMessage(
                "Actualización Disponible",
                f"RPCS3 {version} está disponible. Haz clic para actualizar.",
                QSystemTrayIcon.Information,
                5000
            )
            if hasattr(self, 'history_text'):
                self.history_text.append(f"🔔 [BG] Actualización {version} detectada en segundo plano.\n")

    def closeEvent(self, event):
        """Intercepta el cierre de la ventana para minimizar a la bandeja"""
        # Red Team: Verificamos que la bandeja exista y esté visible antes de interceptar.
        # Si la bandeja falló al iniciar, debemos permitir que el programa se cierre normalmente.
        if hasattr(self, 'tray_icon') and self.tray_icon is not None and self.tray_icon.isVisible():
            event.ignore()  # Cancela el cierre nativo de la ventana
            self.hide()     # Oculta la ventana principal
            
            # Notificación sutil para confirmar al usuario
            self.tray_icon.showMessage(
                "CELL Updater-S3",
                "Ejecutándose en segundo plano.",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            # Si no hay bandeja, aceptamos el cierre y limpiamos recursos
            event.accept()
            self.exit_app()

    def exit_app(self):
        """Cierra la aplicación completamente y limpia recursos en memoria"""
        # 1. Detener el hilo de AMAZONA si está corriendo (evita procesos zombie)
        if hasattr(self, 'worker') and self.worker is not None and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(3000)  # Espera hasta 3 segundos para que termine gracefully
            
        # 2. Eliminar el ícono de la bandeja para que no quede "fantasma" en Windows
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            self.tray_icon.setVisible(False)
            self.tray_icon = None
            
        # 3. Cerrar la aplicación
        QApplication.quit()

    def change_skin(self, skin_name):
        self.tema_actual = skin_name
        self.guardar_preferencia_tema(skin_name)
        self.apply_theme(skin_name)

    def apply_theme(self, skin_name):
        skin = SKINS.get(skin_name, SKINS["CELL Updater"])
        app = QApplication.instance()
        qss = f"""
            QMainWindow, QWidget {{ background-color: {skin["bg_primary"]}; color: {skin["text_primary"]}; font-family: 'Segoe UI', 'Inter', sans-serif; }}
            #sidebar {{ background-color: {skin["bg_sidebar"]}; border-right: 1px solid {skin["border"]}; }}
            #logo_label {{ color: {skin["text_primary"]}; }}
            QPushButton {{ background-color: {skin["btn_bg"]}; border: 1px solid {skin["border"]}; border-radius: 6px; padding: 8px 16px; color: {skin["text_primary"]}; font-size: 13px; }}
            QPushButton:hover {{ background-color: {skin["btn_hover"]}; border-color: {skin["accent"]}; }}
            QPushButton:pressed {{ background-color: {skin["accent"]}; color: white; border-color: {skin["accent"]}; }}
            QPushButton#update_btn {{ background-color: {skin["accent"]}; border: none; border-radius: 6px; font-size: 14px; font-weight: 600; color: white; }}
            QPushButton#update_btn:hover {{ background-color: {skin["accent_hover"]}; }}
            QPushButton#window_btn {{ background: transparent; border: none; border-radius: 4px; }}
            QPushButton#window_btn:hover {{ background-color: {skin["btn_hover"]}; }}
            QPushButton#nav_btn_dashboard, QPushButton#nav_btn_hardware, QPushButton#nav_btn_historial, QPushButton#nav_btn_config, QPushButton#nav_btn_about {{ background: transparent; border: none; border-left: 3px solid transparent; text-align: left; padding-left: 20px; font-size: 14px; color: {skin["text_secondary"]}; }}
            QPushButton#nav_btn_dashboard:hover, QPushButton#nav_btn_hardware:hover, QPushButton#nav_btn_historial:hover, QPushButton#nav_btn_config:hover, QPushButton#nav_btn_about:hover {{ color: {skin["text_primary"]}; background-color: rgba(255,255,255,0.05); }}
            QPushButton#nav_btn_dashboard:checked, QPushButton#nav_btn_hardware:checked, QPushButton#nav_btn_historial:checked, QPushButton#nav_btn_config:checked, QPushButton#nav_btn_about:checked {{ background-color: rgba(0, 112, 209, 0.15); border-left: 3px solid {skin["accent"]}; color: {skin["accent"]}; font-weight: 600; }}
            #content_area {{ background-color: {skin["bg_primary"]}; }}
            #header {{ background-color: transparent; border-bottom: 1px solid {skin["border"]}; padding: 10px 0; }}
            #breadcrumb {{ font-size: 16px; font-weight: 600; color: {skin["text_primary"]}; }}
            #status_indicator {{ font-size: 12px; color: #2ea043; font-weight: bold; }}
            #status_text {{ font-size: 12px; color: {skin["text_secondary"]}; margin-right: 15px; }}
            QFrame#content_group, QFrame#welcome_card, QFrame#update_section {{ background-color: {skin["bg_secondary"]}; border: 1px solid {skin["border"]}; border-radius: 8px; }}
            QFrame#modern_card_version_local, QFrame#modern_card_version_remota {{ background-color: {skin["bg_secondary"]}; border: 1px solid {skin["border"]}; border-radius: 8px; }}
            QFrame#modern_card_version_local:hover, QFrame#modern_card_version_remota:hover {{ border: 1px solid {skin["accent"]}; }}
            QFrame#ia_card_principal {{ background-color: {skin["bg_secondary"]}; border: 2px solid {skin["accent"]}; border-radius: 10px; }}
            QLabel#ia_card_title {{ font-size: 14px; font-weight: 700; color: {skin["accent"]}; margin-bottom: 15px; letter-spacing: 1px; }}
            QLabel#ia_message_display {{ font-size: 16px; color: {skin["text_primary"]}; line-height: 1.6; background-color: {skin["bg_primary"]}; padding: 20px; border-radius: 6px; min-height: 120px; }}
            QLabel#welcome_title, QLabel#update_title, QLabel#section_title {{ font-size: 18px; font-weight: 600; color: {skin["text_primary"]}; margin-bottom: 10px; }}
            QLabel#welcome_text {{ font-size: 20px; font-weight: 600; color: {skin["accent"]}; margin-top: 5px; }}
            QLabel#update_desc {{ font-size: 13px; color: {skin["text_secondary"]}; margin-bottom: 15px; line-height: 1.5; }}
            #card_title {{ font-size: 11px; color: {skin["text_secondary"]}; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }}
            #card_value_version_local, #card_value_version_remota, #card_value_ia_status, #card_value_welcome {{ color: {skin["text_primary"]}; font-size: 18px; font-weight: 600; }}
            QComboBox {{ background-color: {skin["btn_bg"]}; border: 1px solid {skin["border"]}; border-radius: 6px; padding: 8px 12px; color: {skin["text_primary"]}; min-width: 150px; min-height: 35px; }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QLineEdit {{ background-color: {skin["btn_bg"]}; border: 1px solid {skin["border"]}; border-radius: 6px; padding: 8px 12px; color: {skin["text_primary"]}; min-height: 35px; }}
            QLineEdit:focus {{ border: 1px solid {skin["accent"]}; }}
            QTextEdit#history_display {{ background-color: {skin["bg_primary"]}; border: 1px solid {skin["border"]}; border-radius: 6px; padding: 15px; color: {skin["text_secondary"]}; font-family: 'Consolas', monospace; font-size: 12px; }}
            QLabel#hardware_display {{ background-color: {skin["bg_primary"]}; border: 1px solid {skin["border"]}; border-radius: 6px; padding: 20px; color: {skin["text_primary"]}; font-size: 14px; line-height: 1.8; }}
            QProgressBar {{ border: 1px solid {skin["border"]}; border-radius: 4px; text-align: center; background-color: {skin["btn_bg"]}; color: {skin["text_primary"]}; min-height: 25px; font-size: 12px; font-weight: 600; }}
            QProgressBar::chunk {{ background-color: {skin["accent"]}; border-radius: 3px; }}
            QStatusBar {{ background-color: {skin["bg_sidebar"]}; color: {skin["text_secondary"]}; border-top: 1px solid {skin["border"]}; font-size: 11px; }}
            #sidebar_info {{ color: {skin["text_secondary"]}; }}
            QCheckBox#toggle_switch {{ spacing: 12px; font-size: 14px; color: {skin["text_primary"]}; }}
            QCheckBox#toggle_switch::indicator {{ width: 44px; height: 24px; border-radius: 12px; background-color: {skin["btn_bg"]}; border: 2px solid {skin["border"]}; }}
            QCheckBox#toggle_switch::indicator:checked {{ background-color: {skin["accent"]}; border: 2px solid {skin["accent"]}; }}
            QCheckBox#toggle_switch::indicator:hover {{ border: 2px solid {skin["accent_hover"]}; }}
            QPushButton#btn_save_links {{ background-color: {skin["accent"]}; border: none; border-radius: 6px; padding: 10px 24px; color: white; font-size: 13px; font-weight: 600; }}
            QPushButton#btn_save_links:hover {{ background-color: {skin["accent_hover"]}; }}
            QLabel#about_title {{ font-size: 24px; font-weight: 700; color: {skin["accent"]}; }}
            QLabel#version_badge {{ background-color: {skin["accent"]}; color: white; padding: 6px 16px; border-radius: 6px; font-weight: 600; font-size: 12px; margin-left: 15px; }}
            QLabel#about_text {{ font-size: 14px; color: {skin["text_secondary"]}; margin-bottom: 20px; }}
            QFrame#telemetria_box {{ background-color: {skin["bg_primary"]}; border: 1px dashed {skin["border"]}; border-radius: 8px; margin-top: 20px; }}
            QLabel#disclaimer {{ color: {skin["text_primary"]}; font-size: 13px; padding: 20px; margin-top: 20px; line-height: 1.6; background-color: {skin["bg_primary"]}; border-radius: 8px; border: 1px solid {skin["border"]}; }}
        """
        app.setStyleSheet(qss)

    def run_update_check(self):
        if self.is_updating or not self.amazona:
            if not self.amazona: QMessageBox.warning(self, "Advertencia", "AMAZONA no está listo.")
            return
        self.is_updating = True
        self.btn_update.setEnabled(False)
        self.btn_update.setText("Procesando...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.worker = AmazonaWorker(self.amazona)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.status_updated.connect(self.status_label.setText)
        self.worker.task_finished.connect(self.on_update_task_finished)
        self.worker.log_received.connect(lambda msg: self.history_text.append(f"[LOG] {msg}") if hasattr(self, 'history_text') else None)
        self.worker.hardware_received.connect(self.actualizar_tarjetas_hardware)
        self.worker.ia_message_received.connect(self.actualizar_mensaje_amazona)  
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()

    def on_worker_error(self, error_msg):
        self.is_updating = False
        self.btn_update.setEnabled(True)
        self.btn_update.setText("Buscar e Instalar Actualizaciones")
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error en el proceso", error_msg)

    def on_update_task_finished(self, success, message):
        self.is_updating = False
        self.btn_update.setEnabled(True)
        self.btn_update.setText("Buscar e Instalar Actualizaciones")
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("Proceso completado exitosamente")
            if hasattr(self, 'history_text'): self.history_text.append(f"ÉXITO: {message}")
            
            # ✅ ¡AQUÍ ENCENDEMOS EL CIRCULITO ROJO!
            self.activar_badge() 
            
        else:
            self.status_label.setText("Error en el proceso")
            if hasattr(self, 'history_text'): self.history_text.append(f"ERROR: {message}")
            
        self.update_ui_light()
        self.cargar_historial_real()

    def actualizar_tarjetas_hardware(self, datos):
        hw_label = self.findChild(QLabel, "hardware_display")
        if hw_label:
            gpu_texto = datos.get('gpu', 'No detectada')
            if datos.get('igpu') and datos['igpu'] != 'No detectada':
                gpu_texto += f" + iGPU: {datos['igpu']}"
            
            hw_label.setText(
                f"Procesador: {datos.get('cpu', 'Desconocido')}\n"
                f"RAM: {datos.get('ram_total', '0.0')} GB ({datos.get('ram_uso', '0')}% en uso)\n"
                f"GPU Dedicada: {gpu_texto}\n"
                f"Almacenamiento: {datos.get('almacenamiento_usado', '0.0')} GB usados / {datos.get('almacenamiento_total', '0.0')} GB totales\n"
                f"Sistema Operativo: {datos.get('so', 'Desconocido')}"
            )

    def update_ui_light(self):
        if not self.amazona: return
        try:
            version_local = getattr(self.amazona, 'version_local', 'Desconocida')
            version_remota = getattr(self.amazona, 'Version_Nube_GitHub', version_local)
            for obj_name, val in [("version_local", version_local), ("version_remota", version_remota)]:
                label = self.findChild(QLabel, f"card_value_{obj_name}")
                if label: label.setText(str(val))
        except Exception as e:
            print(f"Error en update_ui_light: {e}")

    def open_rpcs3_folder(self):
        if not self.amazona.Ruta_rpcs3:
            self.amazona.Carpeta_RPCS3()
            
        if self.amazona.Ruta_rpcs3 and os.path.isdir(self.amazona.Ruta_rpcs3):
            try:
                os.startfile(self.amazona.Ruta_rpcs3)
                self.status_label.setText("Carpeta de RPCS3 abierta")
            except Exception as e:
                self.status_label.setText(f"No se pudo abrir la carpeta: {e}")
        else:
            self.status_label.setText("No se pudo localizar la carpeta de RPCS3")
            QMessageBox.warning(self, "Ruta no encontrada", "No se pudo localizar la carpeta de instalación de RPCS3.")

    def actualizar_contador_descargas_bg(self):
        def fetch():
            try:
                url = "https://api.github.com/repos/SNTKida/CELL-Updater-S3/releases"
                headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "CELL-Updater-S3/1.0"}
                response = requests.get(url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    total = sum(asset.get("download_count", 0) for release in response.json() for asset in release.get("assets", []))
                    QTimer.singleShot(0, lambda: self.label_descargas.setText(f"{total} Descargas Globales"))
                elif response.status_code == 404:
                    QTimer.singleShot(0, lambda: self.label_descargas.setText("Repositorio no creado"))
                else:
                    QTimer.singleShot(0, lambda: self.label_descargas.setText("Modo Offline"))
            except Exception:
                QTimer.singleShot(0, lambda: self.label_descargas.setText("Error de conexión"))
        threading.Thread(target=fetch, daemon=True).start()

    def cargar_preferencia_tema(self):
        if not self.amazona or not hasattr(self.amazona, 'carpeta_user'): return "CELL Updater"
        path = os.path.join(self.amazona.carpeta_user, "user.json")
        if os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f: return json.load(f).get("tema", "CELL Updater")
            except: pass
        return "CELL Updater"

    def guardar_preferencia_tema(self, tema):
        if not self.amazona or not hasattr(self.amazona, 'carpeta_user'): return
        path = os.path.join(self.amazona.carpeta_user, "user.json")
        data = {}
        if os.path.isfile(path):
            try:
                with open(path, 'r', encoding='utf-8') as f: data = json.load(f)
            except: pass
        data["tema"] = tema
        with open(path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)

    def on_bg_update_finished(self, success, message):
        """Se ejecuta automáticamente cuando el timer de fondo termina su trabajo"""
        if success:
            if hasattr(self, 'history_text'):
                self.history_text.append(f"🔔 [AUTO] {message}")
                #self.limitar_historial_ui() # Aprovechamos y limpiamos el log
            
            # Encender el circulito rojo
            self.activar_badge()
            
            # Notificación de Windows (opcional)
            if self.tray_icon:
                self.tray_icon.showMessage("Cell Updater-S3", "Actualización automática completada.", QSystemTrayIcon.Information, 3000)

def iniciar_frontend(modo="full"):
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    window = MainWindow(modo=modo)
    sys.exit(app.exec())

if __name__ == "__main__":
    iniciar_frontend(modo="full")