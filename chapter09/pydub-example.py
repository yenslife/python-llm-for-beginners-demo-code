from pydub import AudioSegment
song = AudioSegment.from_mp3("example.mp3")
two_minutes_segment = 2 * 60 * 1000 # 這邊是用毫秒
first_two_minutes = song[:two_minutes_segment]
# 輸出前兩分鐘的音訊
first_two_minutes.export("first_two_minutes.mp3", format="mp3")
