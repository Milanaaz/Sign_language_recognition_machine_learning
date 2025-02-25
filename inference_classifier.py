import pickle
import cv2
import mediapipe as mp
import numpy as np

# Загрузка модели
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

cap = cv2.VideoCapture(0)  # Выбираем камеру

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.3)

labels_dict = {
    0: 'a', 1: 'b', 2: 'l'
}

while True:
    ret, frame = cap.read()
    if not ret:
        print("Не удалось захватить кадр с камеры")
        break  # Прерываем цикл, если кадр не захвачен

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Обработка изображения для распознавания рук
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            data_aux = []
            x_ = []
            y_ = []

            # Сбор координат landmarks для текущей руки
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                x_.append(x)
                y_.append(y)

            # Нормализация координат
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

            # Предсказание символа для текущей руки
            try:
                print("Нормализованные данные для предсказания:", data_aux)  # Отладочный вывод данных
                prediction = model.predict([np.asarray(data_aux)])
                print("Предсказание модели:", prediction)  # Отладочный вывод предсказания
                predicted_character = labels_dict[int(prediction[0])]

                # Рисуем прямоугольник вокруг руки
                x1 = int(min(x_) * W) - 10
                y1 = int(min(y_) * H) - 10
                x2 = int(max(x_) * W) + 10
                y2 = int(max(y_) * H) + 10

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, predicted_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            except Exception as e:
                print(f"Ошибка предсказания: {e}")

            # Отображаем landmarks текущей руки
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

    # Отображение кадра
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Нажмите 'q' для выхода
        break

# Освобождение ресурса камеры и закрытие окон
cap.release()
cv2.destroyAllWindows()
