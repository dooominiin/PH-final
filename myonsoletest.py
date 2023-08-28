import time

total_progress = 100

for progress in range(total_progress + 1):
    percentage = (progress / total_progress) * 100
    print(f"Fortschritt: {percentage:.2f}%", end='\r')
    time.sleep(0.1)  # Simuliere eine Aufgabe
   
print("\nFertig!")
