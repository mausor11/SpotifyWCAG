import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("🎤 Powiedz komendę...")
    audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language="pl-PL")
        print("🔍 Rozpoznano:", command)
        # Tutaj możesz dodać ify np. if "następny" in command:
    except sr.UnknownValueError:
        print("❌ Nie rozpoznano mowy.")
