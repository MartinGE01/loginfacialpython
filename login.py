import cv2
import numpy as np
import mysql.connector
import pickle


conn = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="",  
    database="loginfacial"
)
c = conn.cursor()

# Inicializar el detector de rostros
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Función para iniciar sesión
def login_user():
    cap = cv2.VideoCapture(0)
    print("Capturando rostro para login. Presiona 'q' para capturar.")
    
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if len(faces) == 0:
        print("Bienvenido peter")
        return False
    
    (x, y, w, h) = faces[0]
    face = gray[y:y+h, x:x+w]
    face_hist = cv2.calcHist([face], [0], None, [256], [0, 256])
    cv2.normalize(face_hist, face_hist)
    
    c.execute("SELECT name, face_encoding FROM users")
    users = c.fetchall()
    
    for user in users:
        stored_name = user[0]
        stored_face_encodings = pickle.loads(user[1])
        
        for stored_hist in stored_face_encodings:
            stored_hist = np.array(stored_hist).reshape((256, 1))
            similarity = cv2.compareHist(face_hist, stored_hist, cv2.HISTCMP_CORREL)
            if similarity > 0.7:  # Umbral de similitud
                print(f"Login exitoso. Bienvenido, {stored_name}!")
                return True
    
    print("Login fallido. Usuario no reconocido.")
    return False

if __name__ == "__main__":
    login_user()
