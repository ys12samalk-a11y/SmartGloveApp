import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
import requests
import base64
import numpy as np
from PIL import Image as PILImage
from io import BytesIO
import tflite_runtime.interpreter as tflite

ESP32_IP = "http://192.168.4.1"
MODEL_PATH = "currency_model.tflite"
CLASS_NAMES = ["100", "10", "20", "200", "5", "50"]

class SmartGloveApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        self.status_label = Label(text="جاهز... المس الحساس", font_size=20)
        layout.add_widget(self.status_label)

        self.image_display = Image()
        layout.add_widget(self.image_display)

        self.result_label = Label(text="النتيجة: ", font_size=24)
        layout.add_widget(self.result_label)

        self.interpreter = tflite.Interpreter(model_path=MODEL_PATH)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        Clock.schedule_interval(self.check_touch, 1)
        return layout

    def check_touch(self, dt):
        try:
            response = requests.get(f"{ESP32_IP}/checkTouch", timeout=3)
            if response.status_code == 200 and "TOUCHED" in response.text:
                self.status_label.text = "تم لمس الحساس! جاري المعالجة..."
                Clock.unschedule(self.check_touch)
                self.capture_and_predict()
                Clock.schedule_once(self.restart_timer, 5)
        except Exception:
            pass

    def restart_timer(self, dt):
        self.status_label.text = "جاهز... المس الحساس"
        Clock.schedule_interval(self.check_touch, 1)

    def capture_and_predict(self):
        try:
            response = requests.get(f"{ESP32_IP}/getImage", timeout=15)
            if response.status_code == 200:
                base64_image = response.text
                self.status_label.text = "تم استقبال الصورة! جاري التحليل..."
                image_data = base64.b64decode(base64_image)
                image = PILImage.open(BytesIO(image_data)).convert('RGB')
                image.save('temp.jpg')
                self.image_display.source = 'temp.jpg'
                self.image_display.reload()
                image = image.resize((224, 224))
                image_array = np.array(image, dtype=np.float32)
                image_array = np.expand_dims(image_array, axis=0)
                image_array = image_array / 255.0
                self.interpreter.set_tensor(self.input_details[0]['index'], image_array)
                self.interpreter.invoke()
                output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
                predicted_class = np.argmax(output_data)
                confidence = output_data[0][predicted_class] * 100
                currency = CLASS_NAMES[predicted_class]
                self.result_label.text = f"النتيجة: {currency} جنيه ({confidence:.1f}%)"
                self.status_label.text = "تم التعرف!"
                requests.get(f"{ESP32_IP}/play?id={predicted_class + 1}", timeout=5)
            else:
                self.status_label.text = "فشل التصوير! حاول تاني."
        except Exception as e:
            self.status_label.text = f"خطأ: {str(e)}"

if __name__ == '__main__':
    SmartGloveApp().run() 
