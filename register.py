import cv2
import numpy as np
import mysql.connector
import pickle
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox


conn = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="",  
    database="loginfacial "
)
c = conn.cursor()

# Crear tabla si no existe
c.execute('''CREATE TABLE IF NOT EXISTS users (
             id INT AUTO_INCREMENT PRIMARY KEY,
             name VARCHAR(255),
             face_encoding BLOB)''')

# Inicializar el detector de rostros
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Función para registrar usuario
def register_user(name, face_samples):
    if len(face_samples) > 0:
        face_encodings = []
        for face in face_samples:
            hist = cv2.calcHist([face], [0], None, [256], [0, 256])
            cv2.normalize(hist, hist)
            face_encodings.append(hist.flatten())
        
        face_encoding_bytes = pickle.dumps(face_encodings)
        c.execute("INSERT INTO users (name, face_encoding) VALUES (%s, %s)", (name, face_encoding_bytes))
        conn.commit()
        messagebox.showinfo("Registro exitoso", f"Usuario {name} registrado correctamente.")
    else:
        messagebox.showerror("Error", "No se detectó ningún rostro.")

# Función para mostrar la imagen registrada
def mostrar_imagen(image):
    ventana_imagen = tk.Toplevel()
    ventana_imagen.title("Imagen Registrada")
    
    img = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    img = ImageTk.PhotoImage(image=Image.fromarray(img))
    
    img_label = tk.Label(ventana_imagen, image=img)
    img_label.image = img
    img_label.pack()

# Función para iniciar la interfaz gráfica
def iniciar_interfaz():
    root = tk.Tk()
    root.title("Registro de Usuario")
    
    # Variables globales para control de flujo
    global face_samples
    face_samples = []
    capturing = True
    
    # Función para registrar usuario desde la interfaz
    def registrar_desde_interfaz():
        nombre = nombre_entry.get()
        if nombre and face_samples:
            register_user(nombre, face_samples)
        else:
            messagebox.showerror("Error", "Por favor, introduce un nombre válido y captura una imagen.")
    
    # Función para salir de la aplicación
    def salir():
        cap.release()
        root.destroy()
    
    # Función para iniciar el registro de un nuevo usuario
    def registrar_nuevo_usuario():
        global face_samples
        face_samples = []
        nombre_entry.delete(0, tk.END)
        capturar_button.config(state=tk.NORMAL)
        registrar_button.config(state=tk.NORMAL)
        actualizar_vista()

    # Configuración de la interfaz
    nombre_label = tk.Label(root, text="Nombre:")
    nombre_label.grid(row=0, column=0, padx=10, pady=10)
    
    nombre_entry = tk.Entry(root)
    nombre_entry.grid(row=0, column=1, padx=10, pady=10)
    
    registrar_button = tk.Button(root, text="Registrar", command=registrar_desde_interfaz)
    registrar_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    
    # Vista previa de la cámara en la interfaz
    cap = cv2.VideoCapture(0)
    
    video_label = tk.Label(root)
    video_label.grid(row=2, column=0, columnspan=2)
    
    # Captura de rostro para el registro
    current_faces = []

    # Captura el rostro actual mostrado en la vista previa
    def capturar_rostro():
        nonlocal capturing
        if len(current_faces) > 0:
            global face_samples
            face_samples.clear()  # Limpiar muestras anteriores
            face_samples.extend(current_faces)  # Guardar las muestras actuales de rostros detectados
            capturing = False  # Detener la actualización en tiempo real
            capturar_button.config(state=tk.DISABLED)
            registrar_button.config(state=tk.NORMAL)

    # Botón para capturar rostro
    capturar_button = tk.Button(root, text="Capturar Rostro", command=capturar_rostro)
    capturar_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    
    # Botón para salir
    salir_button = tk.Button(root, text="Salir", command=salir)
    salir_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    # Botón para ver imagen capturada
    def ver_imagen():
        if face_samples:
            mostrar_imagen(face_samples[0])
        else:
            messagebox.showerror("Error", "No se ha capturado ninguna imagen aún.")
    
    ver_button = tk.Button(root, text="Ver Imagen Capturada", command=ver_imagen)
    ver_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
    
    # Botón para registrar nuevo usuario
    nuevo_usuario_button = tk.Button(root, text="Registrar Nuevo Usuario", command=registrar_nuevo_usuario)
    nuevo_usuario_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    # Actualizar la vista previa de la cámara en tiempo real y detectar rostros
    def actualizar_vista():
        if capturing:
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                # Limpiar la lista de caras actuales
                current_faces.clear()
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    current_faces.append(gray[y:y+h, x:x+w])
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (400, 300))
                img = ImageTk.PhotoImage(image=Image.fromarray(frame))
                video_label.configure(image=img)
                video_label.image = img
            
            video_label.after(10, actualizar_vista)
    
    actualizar_vista()
    
    root.mainloop()

if __name__ == "__main__":
    iniciar_interfaz()
