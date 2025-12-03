#!/usr/bin/env python3

import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import time 

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTextEdit, QTreeWidget, QTreeWidgetItem, QSplitter, 
    QLabel, QSizePolicy, QMessageBox, QHeaderView, QProgressBar, QFileDialog,
    QDialog, QListWidget, QMenuBar
)
# Gerekli kütüphaneler: QIcon, QPixmap (Logo), QDesktopServices, QUrl (Hiperlink)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDir, QSize, QUrl 
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices 

# --- 0. DİL VE ÇEVİRİLER ---

LANGUAGES = {
    'en': {
        # Başlıklar
        'app_title': "System Compare Tool",
        'label_before': "Initial State",
        'label_comparison': "Comparison Results",
        'dialog_scan_title': "Add Scan Path",
        'dialog_exclude_title': "Exclude Paths",
        'dialog_about_title': "About System Compare Tool",
        
        # Butonlar
        'btn_language': "Language", 
        'btn_snapshot': "Take Snapshot",
        'btn_compare': "Compare Systems",
        'btn_export': "Export to TXT",
        'btn_exclude': "Exclude Paths",
        'btn_scan_paths': "Add Scan Paths",
        'btn_add': "Add Path...",
        'btn_remove': "Remove Selected",
        'btn_save_close': "Save and Close",
        'btn_cancel': "Cancel",
        'btn_ok_close': "OK", # YENİ: Hakkında penceresi için
        
        # Menü
        'menu_help': "Help",
        'menu_about': "About",

        # Durum ve Bilgi Metinleri
        'status_default': "Status: Ready.",
        'status_loading_old': "Status: Old snapshot ({}) loaded. Ready to Compare.",
        'status_new_snapshot_info': "Status: Snapshot successful. Now perform a change and hit 'Compare Systems'.",
        'status_comparison_done': "Status: Comparison finished. Difference count: {}. Results on the right panel.",
        'status_busy_snapshot': "Status: Taking initial snapshot... Please wait. (Excluded paths will be skipped)",
        'status_busy_compare': "Status: Taking new snapshot and comparing... Please wait. (Excluded paths will be skipped)",
        'status_abort': "Status: New snapshot canceled by user.",
        'status_no_snapshot': "Initial Snapshot Not Taken.",
        'status_save_success': "Status: Results successfully saved: {}",
        
        'msg_confirm_overwrite': "An existing snapshot record is present. Taking a new one will overwrite the old one. Do you want to continue?",
        'msg_warn_first_snapshot': "You must click 'Take Snapshot' first.",
        'msg_err_snapshot_save': "Error saving snapshot: {}",
        'msg_err_snapshot': "Error during snapshot: {}",
        'msg_err_compare': "Unexpected error during comparison: {}",
        'msg_err_save_list': "Could not save {} list: {}",
        'msg_success_update_list': "{} list successfully updated and saved.",
        'msg_warn_path_change': "{} list changed. Please click **'Take Snapshot'** again for a correct comparison with the new settings.",
        'msg_err_load': "Could not load saved snapshot file:\n{}",
        'msg_err_file_save': "Error saving file: {}",
        
        # Snapshot Bilgi Panel
        'info_loaded': "***Previous Snapshot Loaded from File!***",
        'info_taken': "***Initial Snapshot Taken!***",
        'info_date': "Date/Time:",
        'info_total_items': "Total Item Count:",
        'info_json_file': "JSON File:",
        'info_scan_roots': "Scanned Root Directories:",
        'info_default': "  - (Default)",
        'info_user': "  - (User)",
        'info_no_user_path': "  - (No User-Added Scan Path)",
        'info_excluded_paths': "Excluded Paths ({})",
        'info_no_excluded': "  - (None)",
        'info_warning_scan_title': "Scan Paths",
        'info_warning_exclude_title': "Exclusion List",

        # Ağaç Görünümü (Tree View)
        'tree_col_type': "Type",
        'tree_col_path': "Path",
        'tree_col_desc': "Description",
        'tree_new_root': "NEW ({})",
        'tree_deleted_root': "DELETED ({})",
        'tree_modified_root': "MODIFIED ({})",
        'tree_type_new': "New",
        'tree_type_removed': "Removed",
        'tree_type_changed': "Changed",
        
        # TXT Rapor
        'report_title': "### System Change Report ###",
        'report_date': "Report Date:",
        'report_snapshot_date': "Initial Snapshot Date:",
        'report_scan_roots': "--- SCANNED ROOT DIRECTORIES ---",
        'report_default_paths': "Default Paths:",
        'report_user_paths': "User Defined Paths:",
        'report_none': "(None)",
        'report_excluded_paths': "--- EXCLUDED DIRECTORIES ---",
        'report_added': "--- 1. NEW ADDED ITEMS ({}) ---",
        'report_deleted': "--- 2. DELETED ITEMS ({}) ---",
        'report_modified': "--- 3. MODIFIED ITEMS ({}) ---",
        'report_no_new': "No new item found.",
        'report_no_deleted': "No deleted item found.",
        'report_no_modified': "No modified item found.",
        'report_path': "[{}] Path: {}, Type: {}, Size: {} bytes",
        'report_detail': "Detail: {}, Size Difference: {} bytes ({} -> {})",
        'report_detail_hash': "Content (Hash) Changed",
        'report_new_tag': "NEW",
        'report_deleted_tag': "DELETED",
        'report_changed_tag': "CHANGED",

        # Hakkında Penceresi
        'about_text': """
This program creates a record of your current system state, allowing you to track changes that occur after a modification (e.g., after installing a new package). It is a simple system monitoring software.

This program provides no warranty.
Copyright (c) A. Serhat KILIÇOĞLU - 2025
        """,
        'about_version': "Version: 1.0.0",
        'about_license': "License: GPLv3",
        'about_lang': "Programming Language: Python3",
        'about_gui': "GUI: Qt5",
        'about_dev': "Developer: A. Serhat KILIÇOĞLU (shampuan)",
        'about_github': "Github:",
    },
    'tr': {
        # Başlıklar
        'app_title': "Sistem Karşılaştırma Aracı",
        'label_before': "Başlangıç Durumu",
        'label_comparison': "Karşılaştırma Sonuçları",
        'dialog_scan_title': "Yeni Dizin Ekle",
        'dialog_exclude_title': "Hariç Tut",
        'dialog_about_title': "Sistem Karşılaştırma Aracı Hakkında",

        # Butonlar
        'btn_language': "Language", 
        'btn_snapshot': "İlk Kaydı Al",
        'btn_compare': "Karşılaştır",
        'btn_export': "TXT'ye Aktar",
        'btn_exclude': "Hariç Tut",
        'btn_scan_paths': "Yeni Dizin Ekle",
        'btn_add': "Yol Ekle...",
        'btn_remove': "Seçileni Kaldır",
        'btn_save_close': "Kaydet ve Kapat",
        'btn_cancel': "İptal",
        'btn_ok_close': "Tamam", # YENİ: Hakkında penceresi için
        
        # Menü
        'menu_help': "Yardım",
        'menu_about': "Hakkında",

        # Durum ve Bilgi Metinleri
        'status_default': "Durum: Hazır.",
        'status_loading_old': "Durum: Eski snapshot ({}) başarıyla yüklendi. Karşılaştırmaya Hazır.",
        'status_new_snapshot_info': "Durum: Snapshot başarılı. Şimdi bir değişiklik yapın ve 'Karşılaştır'a basın.",
        'status_comparison_done': "Durum: Karşılaştırma tamamlandı. Fark sayısı: {}. Sonuçlar sağ panelde.",
        'status_busy_snapshot': "Durum: Başlangıç snapshot'ı alınıyor... Lütfen bekleyin. (Hariç tutulan yollar atlanacak)",
        'status_busy_compare': "Durum: Yeni snapshot alınıyor ve karşılaştırma yapılıyor... Lütfen bekleyin. (Hariç tutulan yollar atlanacak)",
        'status_abort': "Durum: Yeni snapshot alma işlemi kullanıcı tarafından iptal edildi.",
        'status_no_snapshot': "Başlangıç Snapshot'ı Alınmadı.",
        'status_save_success': "Durum: Sonuçlar başarıyla kaydedildi: {}",

        'msg_confirm_overwrite': "Daha önce alınmış bir snapshot kaydı mevcut. Yeni bir snapshot almak, eski kaydı silip (üzerine yazıp) güncelleyecek.\n\nDevam etmek istiyor musunuz?",
        'msg_warn_first_snapshot': "Önce 'İlk Kaydı Al' düğmesine basmalısınız.",
        'msg_err_snapshot_save': "Snapshot kaydedilirken hata oluştu: {}",
        'msg_err_snapshot': "Snapshot sırasında hata oluştu: {}",
        'msg_err_compare': "Karşılaştırma sırasında beklenmeyen hata oluştu: {}",
        'msg_err_save_list': "{} listesi kaydedilemedi: {}",
        'msg_success_update_list': "{} listesi başarıyla güncellendi ve kaydedildi.",
        'msg_warn_path_change': "{} listesi değişti. Yeni ayarlarla doğru karşılaştırma yapmak için lütfen **yeniden 'İlk Kaydı Al'** düğmesine basın.",
        'msg_err_load': "Kaydedilmiş snapshot dosyası yüklenemedi:\n{}",
        'msg_err_file_save': "Dosya kaydedilirken hata oluştu: {}",

        # Snapshot Bilgi Panel
        'info_loaded': "***Önceki Snapshot Dosyadan Yüklendi!***",
        'info_taken': "***Başlangıç Snapshot'ı Alındı!***",
        'info_date': "Tarih/Saat:",
        'info_total_items': "Toplam Öğe Sayısı:",
        'info_json_file': "JSON Dosyası:",
        'info_scan_roots': "Taranan Kök Dizinler:",
        'info_default': "  - (Varsayılan)",
        'info_user': "  - (Kullanıcı)",
        'info_no_user_path': "  - (Kullanıcı Tarafından Eklenen Tarama Yolu Yok)",
        'info_excluded_paths': "Hariç Tutulan Dizinler ({})",
        'info_no_excluded': "  - (Yok)",
        'info_warning_scan_title': "Tarama Yolları",
        'info_warning_exclude_title': "Hariç Tutma Listesi",
        
        # Ağaç Görünümü (Tree View)
        'tree_col_type': "Tür",
        'tree_col_path': "Yol",
        'tree_col_desc': "Açıklama",
        'tree_new_root': "YENİ ({})",
        'tree_deleted_root': "SİLİNEN ({})",
        'tree_modified_root': "DEĞİŞEN ({})",
        'tree_type_new': "Yeni",
        'tree_type_removed': "Kaldırıldı",
        'tree_type_changed': "Değişti",

        # TXT Rapor
        'report_title': "### Sistem Değişiklik Raporu ###",
        'report_date': "Rapor Tarihi:",
        'report_snapshot_date': "Başlangıç Snapshot Tarihi:",
        'report_scan_roots': "--- TARANAN KÖK DİZİNLER ---",
        'report_default_paths': "Varsayılan Yollar:",
        'report_user_paths': "Kullanıcı Tanımlı Yollar:",
        'report_none': "(Yok)",
        'report_excluded_paths': "--- HARİÇ TUTULAN DİZİNLER ---",
        'report_added': "--- 1. YENİ EKLENEN ÖĞELER ({}) ---",
        'report_deleted': "--- 2. SİLİNEN ÖĞELER ({}) ---",
        'report_modified': "--- 3. DEĞİŞTİRİLEN ÖĞELER ({}) ---",
        'report_no_new': "Yeni öğe bulunamadı.",
        'report_no_deleted': "Silinen öğe bulunamadı.",
        'report_no_modified': "Değiştirilen öğe bulunamadı.",
        'report_path': "[{}] Yol: {}, Tip: {}, Boyut: {} bayt",
        'report_detail': "Detay: {}, Boyut Farkı: {} bayt ({} -> {})",
        'report_detail_hash': "İçerik (Hash) Değişti",
        'report_new_tag': "YENİ",
        'report_deleted_tag': "SİLİNDİ",
        'report_changed_tag': "DEĞİŞTİ",

        # Hakkında Penceresi
        'about_text': """
Bu program, şu anki sistem durumunuzun kaydını oluşturarak, bir değişiklik sonrası (örneğin yeni bir paket kurulumu sonrası) oluşan değişiklikleri takip etmenizi sağlar. Basit bir sistem takip yazılımıdır.

Bu program hiçbir garanti getirmez.
Telif hakkı (c) A. Serhat KILIÇOĞLU - 2025
        """,
        'about_version': "Sürüm: 1.0.0",
        'about_license': "Lisans: GPLv3",
        'about_lang': "Programlama Dili: Python3",
        'about_gui': "GUI: Qt5",
        'about_dev': "Geliştirici: A. Serhat KILIÇOĞLU (shampuan)",
        'about_github': "Github:",
    }
}

# --- 1. Sabitler ve Yardımcı Fonksiyonlar ---

DIRS_TO_CHECK = [
    "/etc", "/usr/bin", "/usr/share", "/usr/local/bin", "~/.config", "~/.local", "/opt"
]

SNAPSHOT_FILE = str(Path.home() / "compare.json")
EXCLUSION_FILE = Path.home() / ".config" / "system_monitor_exclude.json"
SCAN_PATHS_FILE = Path.home() / ".config" / "system_monitor_scan_paths.json"

EXCLUSION_FILE.parent.mkdir(parents=True, exist_ok=True) 
SCAN_PATHS_FILE.parent.mkdir(parents=True, exist_ok=True) 

CONFIG_EXTENSIONS = ['.conf', '.ini', '.json', '.yaml', '.xml', '.cfg']
LOGO_PATH = str(Path(__file__).parent / "compare0.png") 

def get_file_hash(filepath, block_size=65536):
    """Verilen dosyanın SHA256 özetini (hash) hesaplar."""
    try:
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while True:
                buf = f.read(block_size)
                if not buf:
                    break
                hasher.update(buf)
        return hasher.hexdigest()
    except Exception:
        return None 

def is_excluded(path_str, excluded_paths):
    """Verilen yolun hariç tutulan yollardan herhangi birinin altında olup olmadığını kontrol eder."""
    path = Path(path_str)
    for excluded in excluded_paths:
        if path == excluded or excluded in path.parents:
            return True
    return False

def take_snapshot(root_dirs, excluded_paths_str):
    """Belirtilen kök dizinleri özyinelemeli olarak tarar ve meta verileri toplar."""
    snapshot_data = {}
    excluded_paths = [Path(d).expanduser() for d in excluded_paths_str]

    for root_dir_str in root_dirs:
        root_dir = Path(root_dir_str).expanduser() 

        if not root_dir.exists():
            continue

        for entry in root_dir.rglob('*'):
            try:
                if is_excluded(str(entry), excluded_paths):
                    continue

                if entry.is_symlink():
                    continue

                stats = entry.stat()
                data = {
                    "type": "dir" if entry.is_dir() else "file",
                    "size": stats.st_size,
                    "mtime": stats.st_mtime,
                }
                
                if entry.is_file() and any(entry.name.endswith(ext) for ext in CONFIG_EXTENSIONS):
                    data["hash"] = get_file_hash(entry)

                snapshot_data[str(entry)] = data
            except Exception:
                continue
                
    return snapshot_data

def compare_snapshots(snap1, snap2):
    """İki snapshot verisini karşılaştırır ve farkları döndürür."""
    differences = {
        "added": {},
        "deleted": {},
        "modified": {}
    }

    for path, data1 in snap1.items():
        if path not in snap2:
            differences["deleted"][path] = data1
        else:
            data2 = snap2[path]
            is_modified = False
            
            if data1["type"] == "file" and data2["type"] == "file":
                if data1["size"] != data2["size"]:
                    is_modified = True
                elif "hash" in data1 and data1.get("hash") != data2.get("hash"):
                    is_modified = True
            
            if is_modified:
                differences["modified"][path] = {"before": data1, "after": data2}

    for path, data2 in snap2.items():
        if path not in snap1:
            differences["added"][path] = data2
            
    return differences

# ----------------------------------------------------
# --- Hakkında Penceresi (About Dialog) ---
# ----------------------------------------------------
class AboutDialog(QDialog):
    def __init__(self, parent=None, language='en'):
        super().__init__(parent)
        self.language = language
        self.texts = LANGUAGES[self.language]
        self.setWindowTitle(self.texts['dialog_about_title'])
        self.setFixedSize(400, 450)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # 1. Başlık ve Logo
        header_layout = QHBoxLayout()
        
        # Logo 
        logo_label = QLabel()
        if Path(LOGO_PATH).exists():
            pixmap = QPixmap(LOGO_PATH)
            # Boyutu küçültülmüş logo
            logo_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("(Logo Yok)") 
            
        header_layout.addWidget(logo_label, alignment=Qt.AlignLeft)
        
        title_label = QLabel(f"<h2>{self.texts['app_title']}</h2>")
        header_layout.addWidget(title_label, alignment=Qt.AlignLeft)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(10)
        
        # 2. Bilgiler
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        info_layout.addWidget(QLabel(self.texts['about_version']))
        info_layout.addWidget(QLabel(self.texts['about_license']))
        info_layout.addWidget(QLabel(self.texts['about_lang']))
        info_layout.addWidget(QLabel(self.texts['about_gui']))
        info_layout.addWidget(QLabel(self.texts['about_dev']))
        
        # GitHub Hiperlinki
        # HTML ve setOpenExternalLinks ile tıklanabilir link
        github_label = QLabel(f"{self.texts['about_github']} <a href='https://www.github.com/shampuan'>www.github.com/shampuan</a>")
        github_label.setTextFormat(Qt.RichText) # HTML içeriği etkinleştir
        github_label.setOpenExternalLinks(True) # Harici tarayıcıda aç
        info_layout.addWidget(github_label)
        
        main_layout.addWidget(info_widget)
        
        # 3. Açıklama
        description_text = QTextEdit()
        # Telif hakkı bilgisi buraya eklendi
        about_content = f"<h3>{self.texts['dialog_about_title']}</h3>" + self.texts['about_text'].replace('(c)', '©')
        description_text.setHtml(about_content.replace('\n', '<br>'))
        description_text.setReadOnly(True)
        description_text.setFixedHeight(200)
        main_layout.addWidget(description_text)
        
        # 4. Kapat Butonu (Düzeltildi)
        # Artık 'btn_save_close' yerine 'btn_ok_close' kullanılıyor
        close_button = QPushButton(self.texts['btn_ok_close']) 
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button)


# ----------------------------------------------------
# --- Tarama Yolu Yönetim Penceresi (ScanPath Dialog) ---
# ----------------------------------------------------
class ScanPathDialog(QDialog):
    def __init__(self, parent=None, initial_paths=None, language='en'):
        super().__init__(parent)
        self.language = language
        self.texts = LANGUAGES[self.language]
        self.setWindowTitle(self.texts['dialog_scan_title'])
        self.setGeometry(200, 200, 500, 400)
        self.paths = initial_paths if initial_paths is not None else []
        self._setup_ui()
        
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        main_layout.addWidget(QLabel(self.texts['dialog_scan_title'] + ":"))
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.paths)
        main_layout.addWidget(self.list_widget)
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(self.texts['btn_add'])
        self.add_button.clicked.connect(self._add_path)
        self.remove_button = QPushButton(self.texts['btn_remove'])
        self.remove_button.clicked.connect(self._remove_path)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        main_layout.addLayout(button_layout)
        
        dialog_buttons = QHBoxLayout()
        self.save_button = QPushButton(self.texts['btn_save_close'])
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton(self.texts['btn_cancel'])
        self.cancel_button.clicked.connect(self.reject)
        
        dialog_buttons.addWidget(self.save_button)
        dialog_buttons.addWidget(self.cancel_button)
        main_layout.addLayout(dialog_buttons)

    def _add_path(self):
        dialog = QFileDialog(self, self.texts['dialog_scan_title'], str(Path.home()))
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setFilter(QDir.Dirs | QDir.Hidden | QDir.NoDotAndDotDot)
        dialog.setOption(QFileDialog.DontResolveSymlinks, True)
        
        if dialog.exec_() == QDialog.Accepted:
            path = dialog.selectedFiles()[0]
            
            if path and path not in self.paths:
                try:
                    relative_path = Path(path).relative_to(Path.home())
                    path_to_save = str(Path('~') / relative_path)
                except ValueError:
                    path_to_save = path

                if path_to_save not in self.paths:
                    self.paths.append(path_to_save)
                    self.paths.sort()
                    self.list_widget.clear()
                    self.list_widget.addItems(self.paths)

    def _remove_path(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            item_text = self.list_widget.item(current_row).text()
            self.list_widget.takeItem(current_row)
            if item_text in self.paths:
                self.paths.remove(item_text)

    def get_paths(self):
        return self.paths

# ----------------------------------------------------
# --- Hariç Tutma Penceresi (Exclusion Dialog) ---
# ----------------------------------------------------
class ExclusionDialog(QDialog):
    def __init__(self, parent=None, initial_exclusions=None, language='en'):
        super().__init__(parent)
        self.language = language
        self.texts = LANGUAGES[self.language]
        self.setWindowTitle(self.texts['dialog_exclude_title'])
        self.setGeometry(200, 200, 500, 400)
        self.exclusions = initial_exclusions if initial_exclusions is not None else []
        self._setup_ui()
        
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        main_layout.addWidget(QLabel(self.texts['dialog_exclude_title'] + ":"))
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.exclusions)
        main_layout.addWidget(self.list_widget)
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(self.texts['btn_add'])
        self.add_button.clicked.connect(self._add_path)
        self.remove_button = QPushButton(self.texts['btn_remove'])
        self.remove_button.clicked.connect(self._remove_path)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        main_layout.addLayout(button_layout)
        
        dialog_buttons = QHBoxLayout()
        self.save_button = QPushButton(self.texts['btn_save_close'])
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton(self.texts['btn_cancel'])
        self.cancel_button.clicked.connect(self.reject)
        
        dialog_buttons.addWidget(self.save_button)
        dialog_buttons.addWidget(self.cancel_button)
        main_layout.addLayout(dialog_buttons)

    def _add_path(self):
        dialog = QFileDialog(self, self.texts['dialog_exclude_title'], str(Path.home()))
        
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setFilter(QDir.Dirs | QDir.Hidden | QDir.NoDotAndDotDot)
        dialog.setOption(QFileDialog.DontResolveSymlinks, True)
        
        if dialog.exec_() == QDialog.Accepted:
            path = dialog.selectedFiles()[0]
            
            if path and path not in self.exclusions:
                try:
                    relative_path = Path(path).relative_to(Path.home())
                    path_to_save = str(Path('~') / relative_path)
                except ValueError:
                    path_to_save = path

                if path_to_save not in self.exclusions:
                    self.exclusions.append(path_to_save)
                    self.exclusions.sort()
                    self.list_widget.clear()
                    self.list_widget.addItems(self.exclusions)

    def _remove_path(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            item_text = self.list_widget.item(current_row).text()
            self.list_widget.takeItem(current_row)
            if item_text in self.exclusions:
                self.exclusions.remove(item_text)

    def get_exclusions(self):
        return self.exclusions

# --- 2. Arka Plan Çalışanı ---

class WorkerThread(QThread):
    snapshot_finished = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, dirs_to_scan, excluded_paths):
        super().__init__()
        self.dirs_to_scan = dirs_to_scan
        self.excluded_paths = excluded_paths

    def run(self):
        try:
            snapshot = take_snapshot(self.dirs_to_scan, self.excluded_paths)
            self.snapshot_finished.emit(snapshot)
        except Exception as e:
            self.error_occurred.emit(f"Snapshot sırasında hata oluştu: {e}")

# --- 3. PyQt5 Ana Pencere ---

class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.current_language = 'en' 
        if Path(LOGO_PATH).exists():
            self.setWindowIcon(QIcon(LOGO_PATH)) 
            
        self.snapshot_before = None
        self.snapshot_time = None
        self.differences = None 
        
        self.excluded_paths = self._load_exclusions() 
        self.user_scan_paths = self._load_scan_paths() 
        
        self._setup_ui()
        self._setup_worker()
        self._translate_ui() 
        self.update_before_info_panel() 
        self.load_initial_snapshot() 
    
    # --- Dil ve Çeviri Metotları ---
    def _translate_ui(self):
        self.texts = LANGUAGES[self.current_language]
        
        # Ana Pencere Başlığı
        self.setWindowTitle(self.texts['app_title'])
        
        # Butonlar
        self.snapshot_button.setText(self.texts['btn_snapshot'])
        self.compare_button.setText(self.texts['btn_compare'])
        self.save_button.setText(self.texts['btn_export'])
        self.exclude_button.setText(self.texts['btn_exclude'])
        self.scan_path_button.setText(self.texts['btn_scan_paths'])
        self.language_button.setText(LANGUAGES['en']['btn_language']) 

        # Etiketler
        self.before_label.setText(self.texts['label_before'])
        self.comparison_label.setText(self.texts['label_comparison'])
        self.status_label.setText(self.texts['status_default'])
        
        # Ağaç Görünümü Başlıkları
        self.comparison_tree.setHeaderLabels([
            self.texts['tree_col_type'], 
            self.texts['tree_col_path'], 
            self.texts['tree_col_desc']
        ])
        
        # Menü Çubuğu
        self.help_menu.setTitle(self.texts['menu_help'])
        self.about_action.setText(self.texts['menu_about'])

        # Diğer Bilgiler
        self.update_before_info_panel() 
        if self.differences:
            self.display_differences(self.differences)

    def toggle_language(self):
        if self.current_language == 'en':
            self.current_language = 'tr'
        else:
            self.current_language = 'en'
        self._translate_ui()
        
    def show_about_dialog(self):
        dialog = AboutDialog(self, self.current_language)
        dialog.exec_()
        
    # --- Yolların Yönetimi ---
    
    def _load_scan_paths(self):
        if SCAN_PATHS_FILE.exists():
            try:
                with open(SCAN_PATHS_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_scan_paths(self):
        try:
            with open(SCAN_PATHS_FILE, 'w') as f:
                json.dump(self.user_scan_paths, f, indent=4)
            return True
        except Exception as e:
            QMessageBox.critical(self, self.texts['info_warning_scan_title'], self.texts['msg_err_save_list'].format(self.texts['info_warning_scan_title'], e))
            return False

    def open_scan_path_dialog(self):
        dialog = ScanPathDialog(self, initial_paths=list(self.user_scan_paths), language=self.current_language)
        if dialog.exec_() == QDialog.Accepted:
            self.user_scan_paths = dialog.get_paths()
            if self._save_scan_paths():
                QMessageBox.information(self, self.texts['info_warning_scan_title'], self.texts['msg_success_update_list'].format(self.texts['info_warning_scan_title']))
            self.update_before_info_panel() 
            
            if self.snapshot_before is not None:
                 QMessageBox.warning(self, self.texts['info_warning_scan_title'], self.texts['msg_warn_path_change'].format(self.texts['info_warning_scan_title']))

    def _load_exclusions(self):
        if EXCLUSION_FILE.exists():
            try:
                with open(EXCLUSION_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_exclusions(self):
        try:
            with open(EXCLUSION_FILE, 'w') as f:
                json.dump(self.excluded_paths, f, indent=4)
            return True
        except Exception as e:
            QMessageBox.critical(self, self.texts['info_warning_exclude_title'], self.texts['msg_err_save_list'].format(self.texts['info_warning_exclude_title'], e))
            return False

    def open_exclusion_dialog(self):
        dialog = ExclusionDialog(self, initial_exclusions=list(self.excluded_paths), language=self.current_language)
        if dialog.exec_() == QDialog.Accepted:
            self.excluded_paths = dialog.get_exclusions()
            if self._save_exclusions():
                QMessageBox.information(self, self.texts['info_warning_exclude_title'], self.texts['msg_success_update_list'].format(self.texts['info_warning_exclude_title']))
            self.update_before_info_panel() 
            
            if self.snapshot_before is not None:
                 QMessageBox.warning(self, self.texts['info_warning_exclude_title'], self.texts['msg_warn_path_change'].format(self.texts['info_warning_exclude_title']))

    # --- UI Kurulumu ---

    def _setup_ui(self):
        self.setGeometry(100, 100, 900, 600) 
        
        # Menü Çubuğu (Hakkında menüsü burada tanımlanır)
        menu_bar = QMenuBar()
        self.help_menu = menu_bar.addMenu('') 
        
        self.about_action = self.help_menu.addAction('') 
        self.about_action.triggered.connect(self.show_about_dialog) # Bağlantı doğru
        self.setMenuBar(menu_bar)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5) 
        main_layout.setContentsMargins(10, 10, 10, 10) 

        # Butonlar için Yatay Düzen
        button_layout = QHBoxLayout()
        
        self.snapshot_button = QPushButton()
        self.snapshot_button.clicked.connect(self.take_snapshot_before)
        
        self.compare_button = QPushButton()
        self.compare_button.clicked.connect(self.compare_snapshots_after)
        self.compare_button.setEnabled(False) 
        
        self.save_button = QPushButton() 
        self.save_button.clicked.connect(self.save_to_txt)
        self.save_button.setEnabled(False) 
        
        self.exclude_button = QPushButton()
        self.exclude_button.clicked.connect(self.open_exclusion_dialog)
        
        self.scan_path_button = QPushButton()
        self.scan_path_button.clicked.connect(self.open_scan_path_dialog)

        self.language_button = QPushButton() 
        self.language_button.clicked.connect(self.toggle_language)
        
        button_layout.addWidget(self.snapshot_button)
        button_layout.addWidget(self.compare_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch(1) 
        button_layout.addWidget(self.exclude_button)
        button_layout.addWidget(self.scan_path_button)
        button_layout.addWidget(self.language_button)
        
        main_layout.addLayout(button_layout)

        # Durum Etiketi
        self.status_label = QLabel()
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        main_layout.addWidget(self.status_label) 

        # İlerleme Çubuğu (Her zaman görünür)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100) 
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout.addWidget(self.progress_bar)
        
        # Splitter (Sol ve Sağ Paneller) 
        splitter = QSplitter(Qt.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 

        # Sol Panel (Önceki Durum Bilgisi)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0) 
        left_layout.setSpacing(5) 

        self.before_label = QLabel() 
        left_layout.addWidget(self.before_label)
        self.before_info = QTextEdit()
        self.before_info.setReadOnly(True)
        left_layout.addWidget(self.before_info)
        
        # Sağ Panel (Karşılaştırma Sonucu)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5) 

        self.comparison_label = QLabel() 
        right_layout.addWidget(self.comparison_label)
        self.comparison_tree = QTreeWidget()
        self.comparison_tree.setColumnCount(3)
        self.comparison_tree.header().setStretchLastSection(True) 
        
        self.comparison_tree.header().setSectionResizeMode(0, QHeaderView.Interactive)
        self.comparison_tree.header().setSectionResizeMode(1, QHeaderView.Interactive)
        self.comparison_tree.header().setSectionResizeMode(2, QHeaderView.Interactive) 
        self.comparison_tree.setColumnWidth(0, 150) 
        
        right_layout.addWidget(self.comparison_tree)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 750]) 
        
        main_layout.addWidget(splitter)
        self.setCentralWidget(central_widget)

    def _setup_worker(self):
        self.worker_thread = None

    def update_before_info_panel(self, is_loaded=False):
        # ... (Bu fonksiyon çeviri metinlerini kullanarak doğru çalışıyor)
        info_parts = []
        
        if self.snapshot_before is not None and self.snapshot_time is not None:
            status = self.texts['info_loaded'] if is_loaded else self.texts['info_taken']
            info_parts.append(status)
            info_parts.append(f"{self.texts['info_date']} {self.snapshot_time.strftime('%Y-%m-%d %H:%M:%S')}")
            info_parts.append(f"{self.texts['info_total_items']} {len(self.snapshot_before)}")
            info_parts.append(f"{self.texts['info_json_file']} {SNAPSHOT_FILE}")
        else:
            info_parts.append(self.texts['status_no_snapshot'])
        
        info_parts.append("\n" + "-"*30 + "\n")
        
        info_parts.append(self.texts['info_scan_roots'])
        info_parts.extend([f"{self.texts['info_default']} {d}" for d in DIRS_TO_CHECK])
        
        if self.user_scan_paths:
             info_parts.extend([f"{self.texts['info_user']} {d}" for d in self.user_scan_paths])
        else:
             info_parts.append(self.texts['info_no_user_path'])
        
        info_parts.append("\n")
        
        info_parts.append(self.texts['info_excluded_paths'].format(len(self.excluded_paths)))
        if self.excluded_paths:
            info_parts.extend([f"  - {d}" for d in self.excluded_paths])
        else:
            info_parts.append(self.texts['info_no_excluded'])
            
        self.before_info.setText('\n'.join(info_parts))
        
        self.compare_button.setEnabled(self.snapshot_before is not None and not self._is_busy())

    def load_initial_snapshot(self):
        snapshot_path = Path(SNAPSHOT_FILE)
        
        if snapshot_path.exists():
            try:
                with open(snapshot_path, 'r') as f:
                    self.snapshot_before = json.load(f)
                
                mtime = snapshot_path.stat().st_mtime
                self.snapshot_time = datetime.fromtimestamp(mtime)

                self.update_before_info_panel(is_loaded=True)

                self.compare_button.setEnabled(True)
                self.status_label.setText(self.texts['status_loading_old'].format(snapshot_path.name))
                
            except Exception as e:
                self.snapshot_before = None 
                self.status_label.setText(f"Durum: HATA - {self.texts['msg_err_load'].format(e)}")
                QMessageBox.warning(self, self.texts['app_title'], self.texts['msg_err_load'].format(e))

    def take_snapshot_before(self):
        if self.snapshot_before is not None:
            reply = QMessageBox.question(self, 
                                         self.texts['app_title'], 
                                         self.texts['msg_confirm_overwrite'],
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.No:
                self.status_label.setText(self.texts['status_abort'])
                return
        
        final_dirs = DIRS_TO_CHECK + self.user_scan_paths
        
        self.status_label.setText(self.texts['status_busy_snapshot']) 
        self._set_ui_busy(True)
        
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()

        self.worker_thread = WorkerThread(final_dirs, self.excluded_paths)
        self.worker_thread.snapshot_finished.connect(self._handle_before_snapshot_result)
        self.worker_thread.error_occurred.connect(self._handle_error)
        self.worker_thread.start()

    def _handle_before_snapshot_result(self, snapshot_data):
        self._set_ui_busy(False)
        self.snapshot_before = snapshot_data
        self.snapshot_time = datetime.now()
        
        try:
            with open(SNAPSHOT_FILE, 'w') as f:
                json.dump(self.snapshot_before, f, indent=4)
            
            self.update_before_info_panel() 

            self.status_label.setText(self.texts['status_new_snapshot_info']) 
            self.compare_button.setEnabled(True)
            
        except Exception as e:
            self._set_ui_busy(False)
            self._handle_error(self.texts['msg_err_snapshot_save'].format(e))

    def compare_snapshots_after(self):
        if not self.snapshot_before:
            QMessageBox.warning(self, self.texts['app_title'], self.texts['msg_warn_first_snapshot']) 
            return

        final_dirs = DIRS_TO_CHECK + self.user_scan_paths

        self.status_label.setText(self.texts['status_busy_compare']) 
        self._set_ui_busy(True)

        self.worker_thread = WorkerThread(final_dirs, self.excluded_paths)
        self.worker_thread.snapshot_finished.connect(self._handle_compare_snapshot_result)
        self.worker_thread.error_occurred.connect(self._handle_error)
        self.worker_thread.start()

    def _handle_compare_snapshot_result(self, snapshot_after):
        self._set_ui_busy(False)
        try:
            self.differences = compare_snapshots(self.snapshot_before, snapshot_after)
            self.display_differences(self.differences)
            
            total_diff_count = len(self.differences['added']) + len(self.differences['deleted']) + len(self.differences['modified'])
            self.status_label.setText(self.texts['status_comparison_done'].format(total_diff_count)) 
            
            self.save_button.setEnabled(True)
            
        except Exception as e:
            self._set_ui_busy(False)
            self._handle_error(self.texts['msg_err_compare'].format(e))

    def _format_differences_for_txt(self):
        # ... (Bu fonksiyon çeviri metinlerini kullanarak doğru çalışıyor)
        content = f"{self.texts['report_title']}\n" 
        content += f"{self.texts['report_date']} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"{self.texts['report_snapshot_date']} {self.snapshot_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += "\n"
        
        content += self.texts['report_scan_roots'] + "\n"
        content += self.texts['report_default_paths'] + "\n"
        for d in DIRS_TO_CHECK:
            content += f"- {d}\n"
        content += f"\n{self.texts['report_user_paths']}\n"
        if self.user_scan_paths:
            for d in self.user_scan_paths:
                content += f"- {d}\n"
        else:
            content += self.texts['report_none'] + "\n"
        content += "\n"
        
        content += self.texts['report_excluded_paths'] + "\n"
        if self.excluded_paths:
            for d in self.excluded_paths:
                content += f"- {d}\n"
        else:
            content += self.texts['report_none'] + "\n"
        content += "\n"
        
        added = self.differences.get('added', {})
        content += self.texts['report_added'].format(len(added)) + "\n"
        if added:
            for path, data in added.items():
                content += self.texts['report_path'].format(self.texts['report_new_tag'], path, data['type'].capitalize(), data['size']) + "\n"
        else:
            content += self.texts['report_no_new'] + "\n"
        content += "\n"
        
        deleted = self.differences.get('deleted', {})
        content += self.texts['report_deleted'].format(len(deleted)) + "\n"
        if deleted:
            for path, data in deleted.items():
                content += self.texts['report_path'].format(self.texts['report_deleted_tag'], path, data['type'].capitalize(), data['size']) + "\n"
        else:
            content += self.texts['report_no_deleted'] + "\n"
        content += "\n"

        modified = self.differences.get('modified', {})
        content += self.texts['report_modified'].format(len(modified)) + "\n"
        if modified:
            for path, data_pair in modified.items():
                data1 = data_pair["before"]
                data2 = data_pair["after"]
                
                detail = ""
                if data1["size"] != data2["size"]:
                    size_diff = data2["size"] - data1["size"]
                    # Sadece Boyut Farkı metnini al (Türkçe/İngilizce)
                    size_diff_text = self.texts['report_detail'].split(',')[1].split(':')[0].strip()
                    detail += f"{size_diff_text}: {size_diff} bayt ({data1['size']} -> {data2['size']})"
                
                if "hash" in data1 and data1.get("hash") != data2.get("hash"):
                    if detail: detail += " | "
                    detail += self.texts['report_detail_hash']

                content += f"[{self.texts['report_changed_tag']}] Yol: {path}, Detay: {detail}\n"
        else:
            content += self.texts['report_no_modified'] + "\n"
            
        return content


    def save_to_txt(self):
        if self.differences is None:
            QMessageBox.warning(self, self.texts['app_title'], self.texts['msg_warn_first_snapshot'])
            return

        filename, _ = QFileDialog.getSaveFileName(self, 
                                                  self.texts['btn_export'], 
                                                  "compare.txt", 
                                                  "Metin Dosyaları (*.txt);;Tüm Dosyalar (*)")
        
        if not filename:
            return

        content = self._format_differences_for_txt()
        
        try:
            with open(filename, 'w', encoding='utf-8', newline='\r\n') as f:
                f.write(content)
            
            self.status_label.setText(self.texts['status_save_success'].format(filename))
            QMessageBox.information(self, self.texts['app_title'], self.texts['status_save_success'].format(filename))
        except Exception as e:
            self._handle_error(self.texts['msg_err_file_save'].format(e))
            
    def _is_busy(self):
        return self.worker_thread is not None and self.worker_thread.isRunning()

    def _set_ui_busy(self, is_busy):
        self.snapshot_button.setEnabled(not is_busy)
        self.exclude_button.setEnabled(not is_busy) 
        self.scan_path_button.setEnabled(not is_busy) 
        self.language_button.setEnabled(not is_busy)
        self.about_action.setEnabled(not is_busy)

        self.compare_button.setEnabled(not is_busy and self.snapshot_before is not None) 
        self.save_button.setEnabled(not is_busy and self.differences is not None) 
        
        if is_busy:
            self.progress_bar.setRange(0, 0) # Belirleyici olmayan (indeterminate) mod
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0) 

    def _handle_error(self, message):
        self._set_ui_busy(False)
        self.status_label.setText(f"Durum: HATA - {message}")
        QMessageBox.critical(self, self.texts['app_title'], message)

    def display_differences(self, differences):
        # ... (Bu fonksiyon çeviri metinlerini kullanarak doğru çalışıyor)
        self.comparison_tree.clear()

        # 1. Eklenenler (Added)
        added_root = QTreeWidgetItem(self.comparison_tree, [self.texts['tree_new_root'].format(len(differences['added'])), "", ""]) 
        added_root.setBackground(0, Qt.darkGreen)
        added_root.setForeground(0, Qt.white)
        for path, data in differences['added'].items():
            detail = f"{data['type'].capitalize()}, Boyut: {data['size']} bayt"
            QTreeWidgetItem(added_root, [self.texts['tree_type_new'], path, detail])

        # 2. Silinenler (Deleted)
        deleted_root = QTreeWidgetItem(self.comparison_tree, [self.texts['tree_deleted_root'].format(len(differences['deleted'])), "", ""]) 
        deleted_root.setBackground(0, Qt.darkRed)
        deleted_root.setForeground(0, Qt.white)
        for path, data in differences['deleted'].items():
            detail = f"{data['type'].capitalize()}, Boyut: {data['size']} bayt"
            QTreeWidgetItem(deleted_root, [self.texts['tree_type_removed'], path, detail])

        # 3. Değiştirilenler (Modified)
        modified_root = QTreeWidgetItem(self.comparison_tree, [self.texts['tree_modified_root'].format(len(differences['modified'])), "", ""]) 
        modified_root.setBackground(0, Qt.darkYellow)
        modified_root.setForeground(0, Qt.black)
        for path, data_pair in differences['modified'].items():
            data1 = data_pair["before"]
            data2 = data_pair["after"]
            
            detail = ""
            if data1["size"] != data2["size"]:
                size_diff = data2["size"] - data1["size"]
                # Sadece Boyut Farkı metnini al (Türkçe/İngilizce)
                size_diff_text = self.texts['report_detail'].split(',')[1].split(':')[0].strip()
                detail += f"{size_diff_text}: {size_diff} bayt ({data1['size']} -> {data2['size']})"
            
            if "hash" in data1 and data1.get("hash") != data2.get("hash"):
                if detail: detail += " | "
                detail += self.texts['report_detail_hash']

            QTreeWidgetItem(modified_root, [self.texts['tree_type_changed'], path, detail])
            
        self.comparison_tree.expandAll() 


# --- 4. Programı Çalıştırma ---

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    window = SystemMonitor()
    window.show()
    sys.exit(app.exec_())
