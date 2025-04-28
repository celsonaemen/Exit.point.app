import openrouteservice
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy_garden.mapview import MapView, MapMarker
from kivy.graphics import Line

client = openrouteservice.Client(key='5b3ce3597851110001cf624834402a3a6c6e4963a9ab1593a6d79c51')

class ApresentacaoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        texto = (
            "Bem-vindo ao ExitPoint!\n\n"
            "Já dormiu no ônibus e perdeu o ponto? Nunca mais!\n\n"
            "Com o ExitPoint, você:\n"
            "- Escolhe o ponto de desembarque no mapa\n"
            "- Configura um alarme para tocar antes de chegar\n"
            "- Dorme tranquilo durante a viagem\n\n"
            "Seu despertador de viagem chegou. Bora usar?"
        )

        label = Label(text=texto, halign="center", valign="middle", font_size='18sp')
        label.bind(size=label.setter('text_size'))

        botao = Button(text="Começar", size_hint=(1, 0.2), font_size='20sp')
        botao.bind(on_press=self.ir_para_proxima)

        layout.add_widget(label)
        layout.add_widget(botao)

        self.add_widget(layout)

    def ir_para_proxima(self, instance):
       
        self.manager.current = 'mapa'


class MapaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')

        
        self.mapview = MapView(zoom=10, lat=-20.2586, lon=-42.0267)  
        self.mapview.bind(on_touch_down=self.selecionar_pontos)

       
        botao_confirmar = Button(text="Confirmar Ponto", size_hint=(1, 0.1), font_size='20sp')
        botao_confirmar.bind(on_press=self.confirmar_ponto)

        layout.add_widget(self.mapview)
        layout.add_widget(botao_confirmar)

        self.add_widget(layout)

        
        self.pontos = []  

    def selecionar_pontos(self, instance, touch):
        if self.mapview.collide_point(*touch.pos):
         
            lat, lon = self.mapview.get_latlon_at(*touch.pos)

            if len(self.pontos) < 2:
                
                self.pontos.append((lat, lon))
                marcador = MapMarker(lat=lat, lon=lon, source="")
                self.mapview.add_widget(marcador)

                
                if len(self.pontos) == 2:
                    self.gerar_rota()

    def gerar_rota(self):
        
        origem = self.pontos[0]
        destino = self.pontos[1]

        
        route = client.directions(
            coordinates=[origem, destino],
            profile='driving-car',  
            format='geojson'
        )

        
        with self.mapview.canvas:
            for feature in route['features']:
                for coordinates in feature['geometry']['coordinates']:
                    Line(points=[(self.mapview.lonlat_to_pixel(lon, lat)) for lat, lon in coordinates], width=2, color=(0, 0, 1, 1))

        print(f"Rota gerada entre {origem} e {destino}")

    def confirmar_ponto(self, instance):
        if len(self.pontos) == 2:
            print(f"Ponto de partida: {self.pontos[0]}")
            print(f"Ponto de chegada: {self.pontos[1]}")
            
        else:
            print("Por favor, selecione ambos os pontos!")


class ExitPointApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ApresentacaoScreen(name='apresentacao'))
        sm.add_widget(MapaScreen(name='mapa'))
        return sm


if __name__ == '__main__':
    ExitPointApp().run()
