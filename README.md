# Dreamy Tunes #

Highly inspired by https://www.youtube.com/@math-floyd/shorts, tried exploring the same in Python!

**Sample Video**
https://github.com/athishaves/dreamyTunes/assets/47027954/7efe6629-22af-42f4-8bbc-9b47e45350c4

**Instructions**
1. Requires python3, pygame and cv2
2. Get audio and midi files of the song
3. Use https://www.visipiano.com/midi-to-json-converter/ to convert midi to json
4. Run the program
   ````python3 animate.py <inputPath> <bgImagePath> <logoImagePath>````  
   inputPath -> make sure input json is saved as ````inputPath.json```` and audio file is saved as ````inputPath.wav````
5. If you had changed the TEMPO of the audio, then set the TEMPO.  
   Default is 1.0
6. Then the program will ask for the TRACK number.  
   audio might have many tracks and the same would have reflected in the json file.  
   Select the right track (0-indexed).
7. You can also set the resolution of the output video by changing ````SCREEN_WIDTH```` and ````SCREEN_HEIGHT````.  
   By default ````SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080````.  
   Time to render the video mainly depends on this factor
