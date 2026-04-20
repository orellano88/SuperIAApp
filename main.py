import requests
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime

class SuperIAEngine:
    def __init__(self):
        self.sunat_api = "https://api.apis.net.pe/v1/ruc"
        self.onpe_api = "https://devapp.zaylar.com/api"

    def get_full_analysis(self, target_id, callback):
        def run():
            results = {"sunat": {}, "onpe": {}, "finanzas": {}, "error": None}
            try:
                # 1. SUNAT (Detección automática de RUC o DNI)
                prefix = "" if len(target_id) == 11 else "10"
                suffix = "" if len(target_id) == 11 else "2"
                final_id = f"{prefix}{target_id}{suffix}"
                
                res_sunat = requests.get(f"{self.sunat_api}?numero={final_id}", timeout=10)
                if res_sunat.status_code == 200:
                    results["sunat"] = res_sunat.json()
                else:
                    results["error"] = "DNI/RUC no válido o servidor no responde."
            except Exception as e:
                results["error"] = "Error de conexión con el núcleo SUNAT."

            try:
                # 2. ONPE (Estadísticas Regionales - Ejemplo Puno)
                res_onpe = requests.get(f"{self.onpe_api}/geographic/regions", timeout=10)
                if res_onpe.status_code == 200:
                    data_onpe = res_onpe.json()
                    results["onpe"] = data_onpe.get('regions', {})
            except Exception as e:
                pass
            
            # 3. Inteligencia Financiera Proyectada
            # Usando modelos predictivos base sobre S/ 5,000
            ingresos = 5000 
            itf_calculado = round(ingresos * (0.005/100), 2)
            renta_calculada = round(ingresos * 0.08, 2)
            
            results["finanzas"] = {
                "itf": itf_calculado,
                "renta": renta_calculada,
                "neto": round(ingresos - renta_calculada - itf_calculado, 2)
            }
            
            Clock.schedule_once(lambda dt: callback(results), 0)
        
        threading.Thread(target=run, daemon=True).start()

class DataCard(BoxLayout):
    def __init__(self, title, content, color=(0.1, 0.1, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 140
        self.padding = [15, 10, 15, 10]
        self.spacing = 8
        with self.canvas.before:
            Color(*color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.add_widget(Label(text=title, bold=True, font_size='15sp', size_hint_y=0.4, halign='left', color=(0.9,0.9,1,1)))
        self.add_widget(Label(text=content, font_size='14sp', halign='center', markup=True, color=(0.8,0.8,0.8,1)))

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class SuperIAVeronaUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        Window.clearcolor = (0.05, 0.05, 0.08, 1) # Ultra dark theme
        self.engine = SuperIAEngine()
        
        # --- Cabecera Cyber ---
        self.header = BoxLayout(size_hint_y=None, height=75, padding=[15, 10])
        with self.header.canvas.before:
            Color(0.12, 0.25, 0.55, 1) # Azul Inteligencia
            self.h_rect = RoundedRectangle(pos=self.header.pos, size=self.header.size, radius=[0,0,25,25])
        self.header.bind(pos=self.update_h_rect, size=self.update_h_rect)
        self.header.add_widget(Label(text="IA TRIBUTARIA", bold=True, font_size='22sp', color=(1,1,1,1)))
        self.add_widget(self.header)

        # --- Entrada Inteligente ---
        self.input_box = BoxLayout(size_hint_y=None, height=70, padding=[20, 15], spacing=10)
        self.target_input = TextInput(hint_text="[DNI o RUC]", multiline=False, background_color=(1,1,1,0.05), foreground_color=(1,1,1,1), cursor_color=(0, 0.8, 0.4, 1), font_size='16sp', halign='center')
        self.input_box.add_widget(self.target_input)
        self.add_widget(self.input_box)

        # --- Zona de Resultados Dinámicos ---
        self.scroll = ScrollView(do_scroll_x=False)
        self.container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=20, padding=[20, 10, 20, 20])
        self.container.bind(minimum_height=self.container.setter('height'))
        
        # Bienvenida
        self.container.add_widget(Label(text="Sistema Conectado.\n[b]Modo Stealth Activo.[/b]", markup=True, color=(0, 0.8, 0.4, 1), font_size='14sp', halign='center'))
        
        self.scroll.add_widget(self.container)
        self.add_widget(self.scroll)

        # --- Botón de Análisis ---
        self.footer = BoxLayout(size_hint_y=None, height=85, padding=[20, 10, 20, 20])
        self.btn = Button(text="EJECUTAR ANÁLISIS", background_color=(0, 0.6, 0.9, 1), bold=True, font_size='16sp', background_normal='')
        self.btn.bind(on_press=self.start_process)
        
        # Redondear botón
        with self.btn.canvas.before:
            Color(0, 0.6, 0.9, 1)
            self.btn.rect = RoundedRectangle(pos=self.btn.pos, size=self.btn.size, radius=[10])
        self.btn.bind(pos=lambda obj, val: setattr(self.btn.rect, 'pos', val), size=lambda obj, val: setattr(self.btn.rect, 'size', val))
        
        self.footer.add_widget(self.btn)
        self.add_widget(self.footer)

    def update_h_rect(self, instance, value):
        self.h_rect.pos = instance.pos
        self.h_rect.size = instance.size

    def start_process(self, instance):
        val = self.target_input.text.strip()
        if len(val) in [8, 11] and val.isdigit():
            self.btn.disabled = True
            self.btn.text = "CONECTANDO A MATRIZ..."
            self.container.clear_widgets()
            self.container.add_widget(Label(text="Analizando huella fiscal...", color=(1, 1, 0, 1)))
            self.engine.get_full_analysis(val, self.show_results)
        else:
            self.target_input.text = ""
            self.target_input.hint_text = "ERROR: Solo 8 o 11 dígitos"

    def show_results(self, results):
        self.btn.disabled = False
        self.btn.text = "NUEVA CONSULTA"
        self.container.clear_widgets()
        
        if results.get("error"):
            self.container.add_widget(DataCard("ALERTA DE SISTEMA", f"[color=ff3333]{results['error']}[/color]"))
            return

        # Modulo SUNAT
        sunat = results.get("sunat", {})
        if sunat and sunat.get("nombre"):
            cond = sunat.get("condicion", "N/A")
            color_tarjeta = (0.6, 0.1, 0.1, 1) if cond == "NO HABIDO" else (0.1, 0.5, 0.2, 1)
            estado_texto = f"[b]{sunat['nombre']}[/b]\n[color=ffffaa]RUC: {sunat.get('numeroDocumento')}[/color]\nEstado: {sunat['estado']}\nCondición: {cond}"
            self.container.add_widget(DataCard("NÚCLEO SUNAT", estado_texto, color=color_tarjeta))
        
        # Modulo Financiero (IA)
        fin = results.get("finanzas", {})
        texto_finanzas = f"[color=aaffaa]ITF Mensual (0.005%):[/color] S/ {fin['itf']}\n[color=ffaaaa]Renta (8%):[/color] S/ {fin['renta']}\n[color=aaffff]Liquidez Libre:[/color] S/ {fin['neto']}"
        self.container.add_widget(DataCard("INTELIGENCIA FINANCIERA", texto_finanzas, color=(0.2, 0.2, 0.3, 1)))
        
        # Log Timestamp
        self.container.add_widget(Label(text=f"Auditoría cerrada: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", size_hint_y=None, height=30, color=(0.4, 0.4, 0.5, 1), font_size='12sp'))

class SuperIAApp(App):
    def build(self):
        return SuperIAVeronaUI()

if __name__ == '__main__':
    SuperIAApp().run()
