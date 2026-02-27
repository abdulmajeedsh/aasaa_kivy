from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

Builder.load_string('''
<OrderHistoryScreen>:
    BoxLayout:
        orientation: "vertical"
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: [dp(10), 0]
            spacing: dp(10)
            canvas.before:
                Color:
                    rgba: 0.13, 0.59, 0.95, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                text: "<"
                size_hint_x: None
                width: dp(44)
                font_size: sp(22)
                background_color: 0,0,0,0
                background_normal: ""
                color: 1,1,1,1
                on_release: root.go_back()
            Label:
                text: "Order History"
                font_size: sp(18)
                bold: True
                color: 1,1,1,1
                halign: "left"
                text_size: self.size
                valign: "center"
        BoxLayout:
            id: tab_area
            orientation: "vertical"
''')


class OrderHistoryScreen(Screen):
    def on_enter(self):
        self.load_data()

    def load_data(self):
        app = App.get_running_app()
        tab_area = self.ids.tab_area
        tab_area.clear_widgets()

        tp = TabbedPanel(do_default_tab=False, tab_width=dp(150))

        # Synced tab
        synced_tab = TabbedPanelItem(text="Synced Orders")
        synced_scroll = ScrollView()
        synced_box = BoxLayout(orientation='vertical', size_hint_y=None)
        synced_box.bind(minimum_height=synced_box.setter('height'))
        history = app.db.get_order_history()
        # Group by order_id
        grouped = {}
        for h in history:
            oid = h.get('order_id', '')
            if oid not in grouped:
                grouped[oid] = []
            grouped[oid].append(h)

        if grouped:
            for oid, items in grouped.items():
                total = sum(float(i.get('total_amount', 0)) for i in items)
                first = items[0]
                row = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(10), dp(5)], spacing=dp(5))
                info = BoxLayout(orientation='vertical')
                nl = Label(text=f"Customer: {first.get('customer_code', '')}",
                           font_size='14sp', color=(0.13, 0.13, 0.13, 1), halign='left', bold=True)
                nl.bind(size=lambda *a: setattr(nl, 'text_size', (nl.width, None)))
                info.add_widget(nl)
                dl = Label(text=f"Order: {oid} | Rs. {total:.2f}",
                           font_size='11sp', color=(0.46, 0.46, 0.46, 1), halign='left')
                dl.bind(size=lambda *a: setattr(dl, 'text_size', (dl.width, None)))
                info.add_widget(dl)
                row.add_widget(info)
                detail_btn = Button(text="View", size_hint_x=None, width=dp(55),
                                     font_size='12sp', background_color=(0.13, 0.59, 0.95, 1),
                                     background_normal="", color=(1, 1, 1, 1))
                detail_items = list(items)
                detail_btn.bind(on_release=lambda inst, it=detail_items: self._show_detail(it))
                row.add_widget(detail_btn)
                synced_box.add_widget(row)
                sep = BoxLayout(size_hint_y=None, height=dp(1))
                with sep.canvas.before:
                    Color(0.9, 0.9, 0.9, 1)
                    sep._rect = Rectangle(pos=sep.pos, size=sep.size)
                sep.bind(pos=lambda s, v: setattr(s._rect, 'pos', v),
                         size=lambda s, v: setattr(s._rect, 'size', v))
                synced_box.add_widget(sep)
        else:
            synced_box.add_widget(Label(text="No synced orders", font_size='16sp',
                                        color=(0.46, 0.46, 0.46, 1), size_hint_y=None, height=dp(100)))
        synced_scroll.add_widget(synced_box)
        synced_tab.add_widget(synced_scroll)

        # Unsynced tab
        unsynced_tab = TabbedPanelItem(text="Unsynced Orders")
        unsynced_scroll = ScrollView()
        unsynced_box = BoxLayout(orientation='vertical', size_hint_y=None)
        unsynced_box.bind(minimum_height=unsynced_box.setter('height'))
        unsynced = app.db.get_unsynced_orders()

        if unsynced:
            # Sync All button
            sync_all_btn = Button(text="Sync All Orders", size_hint_y=None, height=dp(44),
                                   font_size='14sp', background_color=(0.30, 0.69, 0.31, 1),
                                   background_normal="", color=(1, 1, 1, 1))
            sync_all_btn.bind(on_release=lambda x: self._sync_all())
            unsynced_box.add_widget(sync_all_btn)

            u_grouped = {}
            for u in unsynced:
                oid = u.get('order_id', '')
                if oid not in u_grouped:
                    u_grouped[oid] = []
                u_grouped[oid].append(u)

            for oid, items in u_grouped.items():
                total = sum(float(i.get('total_amount', 0)) for i in items)
                first = items[0]
                row = BoxLayout(size_hint_y=None, height=dp(60), padding=[dp(10), dp(5)], spacing=dp(5))
                info = BoxLayout(orientation='vertical')
                nl = Label(text=f"Customer: {first.get('customer_code', '')}",
                           font_size='14sp', color=(0.13, 0.13, 0.13, 1), halign='left', bold=True)
                nl.bind(size=lambda *a: setattr(nl, 'text_size', (nl.width, None)))
                info.add_widget(nl)
                dl = Label(text=f"Order: {oid} | Rs. {total:.2f} | PENDING",
                           font_size='11sp', color=(0.96, 0.26, 0.21, 1), halign='left')
                dl.bind(size=lambda *a: setattr(dl, 'text_size', (dl.width, None)))
                info.add_widget(dl)
                row.add_widget(info)
                unsynced_box.add_widget(row)
        else:
            unsynced_box.add_widget(Label(text="All orders synced", font_size='16sp',
                                          color=(0.46, 0.46, 0.46, 1), size_hint_y=None, height=dp(100)))
        unsynced_scroll.add_widget(unsynced_box)
        unsynced_tab.add_widget(unsynced_scroll)

        tp.add_widget(synced_tab)
        tp.add_widget(unsynced_tab)
        tab_area.add_widget(tp)

    def _show_detail(self, items):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        first = items[0]
        box.add_widget(Label(text=f"Customer: {first.get('customer_code', '')}",
                              font_size='14sp', color=(0.13, 0.13, 0.13, 1),
                              size_hint_y=None, height=dp(25), bold=True))
        box.add_widget(Label(text=f"Order ID: {first.get('order_id', '')}",
                              font_size='12sp', color=(0.46, 0.46, 0.46, 1),
                              size_hint_y=None, height=dp(20)))

        total = 0
        for item in items:
            txt = f"{item.get('product_name', '')} | Qty: {item.get('quantity', 0)} | Rs. {item.get('net_amount', 0):.2f}"
            box.add_widget(Label(text=txt, font_size='12sp', color=(0.13, 0.13, 0.13, 1),
                                  size_hint_y=None, height=dp(22)))
            total += float(item.get('total_amount', 0))

        box.add_widget(Label(text=f"\nTotal: Rs. {total:.2f}", font_size='14sp',
                              color=(0.30, 0.69, 0.31, 1), size_hint_y=None, height=dp(30), bold=True))
        scroll.add_widget(box)
        content.add_widget(scroll)

        Popup(title="Order Details", content=content, size_hint=(0.9, 0.6)).open()

    def _sync_all(self):
        app = App.get_running_app()
        app.sync_service.force_sync(
            callback=lambda d: self._on_synced(),
            error_callback=lambda e: Popup(title="Error",
                                           content=Label(text=f"Sync failed: {e}"),
                                           size_hint=(0.8, 0.3)).open()
        )

    def _on_synced(self):
        Popup(title="Success", content=Label(text="Orders synced!"),
              size_hint=(0.8, 0.25)).open()
        self.load_data()

    def go_back(self):
        App.get_running_app().navigate_to('main_dashboard', direction='right')
