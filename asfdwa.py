from collections import deque

# Maximal erlaubte Länge der Datenstruktur
max_length = 5


# Erstelle eine deque mit der maximalen Länge
data_queue = deque((),max_length)
 
# Füge Elemente zur deque hinzu
data_queue.append(10)
data_queue.append(20)
data_queue.append(30)
data_queue.append(40)
data_queue.append(50)

# Wenn ein neues Element hinzugefügt wird und die maximale Länge erreicht ist,
# wird das älteste Element automatisch entfernt
data_queue.appendleft(60)



# Gib den aktuellen Inhalt der deque aus
print(data_queue.pop())
