#!/usr/bin/python3
# -*- coding: utf-8 -*

import picamera
import itertools
import subprocess
import os
from shutil import copyfile
import sys
import time
from datetime import datetime
import logging
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import pygame
from pygame.locals import *


CurrentWorkingDir= "/var/www/html/photos/Photomaton_Prev/"
archiveDir       = "/var/www/html/photos/PhotosduPhotomaton"
archiveDirWithLayer = "/var/www/html/photos/PhotosduPhotomatonWithLayer"
LARGEUR_ECRAN     = 1680
HAUTEUR_ECRAN    = 1050
LARGEUR_PHOTOPREV      = 1080 
HAUTEUR_PHOTOPREV     = 720
LARGEUR_PHOTO      = 1080 
HAUTEUR_PHOTO     = 720
PHOTO_DELAY      = 3 #délai en secondes avant prise de la photo
overlay_renderer = None
buttonEvent      = False

pygame.init()
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((1920,1080),RESIZABLE)
width, height = screen.get_size()


#on initialise les GPIO en écoute
#Attention au choix des ports ; référez-vous au site https://fr.pinout.xyz/
#J'ai pris BCM24(GPIO18) et la masse qui est à côté
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Supprimer les pré-images (on ne les garde que dans le dossier du bureau)
def deleteImages(fileName):
    logging.info("Suppression des anciennes images.")
    if os.path.isfile(fileName):
        os.remove(fileName);

def cleanUp():
    GPIO.cleanup()
    
def archiveImage(fileName):
    logging.info("Sauvegarde de l'image : "+fileName)
    copyfile(fileName,archiveDir+"/"+fileName)

    #watermark_with_transparency(archiveDir+"/"+fileName, archiveDirWithLayer+"/"+fileName+ '.png',
                    #            '/home/pi/LayerInDaSowce.png', position=(0,0))
  

    
def countdownFrom(secondsStr):
    secondsNum = int(secondsStr)
    if secondsNum >= 0 :
        while secondsNum > 0 :
            addPreviewOverlay(300,100,240,str(secondsNum))
            time.sleep(1)
            secondsNum=secondsNum-1

def precapture1(imageName):
    addPreviewOverlay(150,200,100,"--> Photo dans 5 secondes !   :-)")
    
def precapture2(imageName):
    addPreviewOverlay(150,200,100,"--> Souriez !!!")
    
    
def captureImage(imageName):
    #addPreviewOverlay(150,200,100,"--> Merci !   :-)")
    #Sauvegarde de l'image
    camera.capture(imageName, resize=(LARGEUR_PHOTO, HAUTEUR_PHOTO))

    print("Image "+imageName+" enregistrée.")

def addPreviewOverlay(xcoord,ycoord,fontSize,overlayText):
    #global overlay_renderer
    img = Image.new("RGB", (LARGEUR_PHOTOPREV, HAUTEUR_PHOTOPREV))
    draw = ImageDraw.Draw(img)
    draw.font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",fontSize)
    draw.text((xcoord,ycoord), overlayText, (255, 20, 147))


    camera.add_overlay(img.tobytes(),layer=3,size=img.size,alpha=255);


def overlayOnPreview():


    # Load the arbitrarily sized image
    img = Image.open('/home/pi/LayerInDaSowceScreen.png')
    # Create an image padded to the required size with
    # mode 'RGB'
    valueL = ((img.size[0] + 31) // 32) * 32
    valueH = ((img.size[1] + 15) // 16) * 16
    print(valueL)
    print(valueH)


    pad = Image.new('RGBA', (valueL,valueH))
   
    # Paste the original image into the padded one
    pad.paste(img, (0, 0))

    # Add the overlay with the padded image as the source,
    # but the original image's dimensions
    o = camera.add_overlay(pad.tobytes(), size=img.size)
    # By default, the overlay is in layer 0, beneath the
    # preview (which defaults to layer 2). Here we make
    # the new overlay semi-transparent, then move it above
    # the preview
    o.alpha = 255
    o.layer = 3

def printOnPreview(text):

    img = Image.new('RGBA', (1696  ,1696))
    #fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 15)
    d = ImageDraw.Draw(img)
    d.text((10,10), text, fill=(255, 255, 0))



    # Add the overlay with the padded image as the source,
    # but the original image's dimensions
    o = camera.add_overlay(img.tobytes(), size=img.size)
    # By default, the overlay is in layer 0, beneath the
    # preview (which defaults to layer 2). Here we make
    # the new overlay semi-transparent, then move it above
    # the preview
    o.alpha = 255
    o.layer = 2

def watermark_with_transparency(input_image_path,
                                output_image_path,
                                watermark_image_path,
                                position):
    base_image = Image.open(input_image_path)
    watermark = Image.open(watermark_image_path)
    width, height = base_image.size
    watermark.thumbnail((width, height), Image.ANTIALIAS)
    transparent = Image.new('RGBA', (width, height), (0,0,0,0))
    transparent.paste(base_image, (0,0))
    transparent.paste(watermark, position, mask=watermark)
    transparent.show()
    transparent.save(output_image_path)



#lancer une action complète pour 1 photo et impression
def play():
    print("Démarrage de la séquence '1 photo'")

    
        
    token = time.strftime("%H%M%S")
    fileName = token +".jpg"
    fileName_Miroir = token +"_Miroir.jpg"
    print("Nom de fichier créé : "+fileName)

    #precapture1(fileName)
    time.sleep(2)
    #countdownFrom(PHOTO_DELAY)
    #precapture2(fileName)
   #time.sleep(2)
    #printOnPreview("3")
    #time.sleep(1)
    #printOnPreview("2")
    #time.sleep(1)
    #printOnPreview("1")
    #time.sleep(1)
    captureImage(fileName)
    time.sleep(1)    
    archiveImage(fileName)
    deleteImages(fileName)
    

    camera.stop_preview()
    AfficherPhoto(archiveDir+"/"+fileName, token)
    #printOnPreview("filename")
    watermark_with_transparency(archiveDir+"/"+fileName, archiveDirWithLayer+"/"+fileName.replace('.jpg' , '.png'),
                                '/home/pi/LayerInDaSowce.png', position=(0,0))
    #addPreviewOverlay(150,200,100,"Your token : " +fileName )
    #printOnPreview("filename");
    

    #time.sleep(5)
    
    #addPreviewOverlay(150,200,100,"Appuyez sur le bouton")
    initCamera(camera)
    print("Démarrage de l'aperçu")
    camera.start_preview()
    overlayOnPreview()
    #AfficherPhoto("/home/pi/LayerInDaSowce.png")

    #AfficherPhoto("/home/pi/Photomaton_Prev/accueil.png")
    #addPreviewOverlay(20,200,55,"--> Appuyez sur le bouton Rouge")

    #os.system('lpr -h -PSamsung_Samsung_CLX-3300_Series -#1 -o media=A4 -o scaling=25 "/home/pi/Desktop/Photos_du_Photomaton/'+fileName+'"')
    #time.sleep(5)
    #print("Travail d'impression créé avec succès.")

    
def initCamera(camera):
    #camera settings
    camera.resolution            = (LARGEUR_PHOTOPREV, HAUTEUR_PHOTOPREV)
    camera.framerate             = 24
    camera.sharpness             = 0
    camera.contrast              = 0
    camera.brightness            = 50
    camera.saturation            = 0
    camera.ISO                   = 0
    camera.video_stabilization   = False
    camera.exposure_compensation = 0
    camera.exposure_mode         = 'auto'
    camera.meter_mode            = 'average'
    camera.awb_mode              = 'auto'
    camera.image_effect          = 'none'
    camera.color_effects         = None
    camera.rotation              = 180
    camera.hflip                 = False
    camera.vflip                 = False
    camera.crop                  = (0.0, 0.0, 1.0, 1.0)


def onButtonPress():
    print("Demande faite pour 1 photo !")
    play()
    #reset the initial welcome message
    #addPreviewOverlay(20,200,55,"--> Appuyez sur le bouton Rouge")


def onButtonDePress():
    print("Bouton Rouge n'est plus pressé (donc, il a le temps ???) ;-)")
    


def AfficherPhoto(fileName,text): # affiche NomPhoto
    print("loading image: " + fileName)
    background = pygame.image.load(fileName);
    background.convert_alpha()
    background = pygame.transform.scale(background,(LARGEUR_ECRAN,HAUTEUR_ECRAN))
    screen.blit(background,(0,0),(0,0,LARGEUR_ECRAN,HAUTEUR_ECRAN))


    red = (255, 0 , 0) 
    black = (255, 255, 255) 
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(text, True, black, red)
    textRect = text.get_rect() 
    textRect.center = (400 // 2, 200 // 2) 
    screen.blit(text, textRect) 
    
    pygame.display.flip()

#Flux initial
with picamera.PiCamera() as camera:
    os.chdir(CurrentWorkingDir)

    try:
        #addPreviewOverlay(20,200,55,"--> Appuyez sur le bouton Rouge")
        #AfficherPhoto("/home/pi/Photomaton_Prev/accueil.png")
        initCamera(camera)
        print("Démarrage de l'aperçu")
        camera.start_preview()
        overlayOnPreview()
        #AfficherPhoto("/home/pi/LayerInDaSowce.png")

    

        print("Démarrage de la boucle du programme")
        while True:
            input_state = GPIO.input(24)

            if input_state == False :
                if buttonEvent == False :
                    buttonEvent = True
                    onButtonPress()
            elif buttonEvent == True :
                    buttonEvent = False
                    onButtonDePress()
        

                    
    except BaseException:
        print("Heu ... Exception non gérée : " , exc_info=True)
        camera.close()
        cleanUp()
    finally:
        print("Au revoir ...")
        cleanUp()
        camera.close()

#end

