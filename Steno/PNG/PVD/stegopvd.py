#Changer ch12.png par l'image

from PIL import Image
import math

def nextPixel():
  global x, y, dir
  if 0 <= x + dir < width:
    x += dir
  else:
    y += 1
    dir *= -1

im = Image.open("ch12.png")
width, height = im.size
x, y, dir = 0, 0, 1
R = [0, 8, 16, 32, 64, 128, 256]
P, B = "", ""
while y < 4:
  p1 = im.getpixel((x, y))
  nextPixel()
  p2 = im.getpixel((x, y))
  nextPixel()
  d = abs(p1 - p2) 
  for i in range(len(R) - 1):
    if R[i] <= d < R[i + 1]:
      n = int(math.log(R[i + 1] - R[i], 2))
      B += format(d - R[i], '0'+str(n)+'b')
      break
  while len(B) >= 8:
    P += chr(int(B[:8], 2))
    B = B[8:]

print(P)
