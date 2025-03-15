
from moviepy.video.VideoClip import TextClip

text = "GeeksforGeeks"
  
# creating a text clip 
# having font arial-bold 
# with font size = 70 
# and color = green 
clip = TextClip(text, font ="arial", fontsize = 70, color ="green") 
  
# showing  clip  
clip.ipython_display()  