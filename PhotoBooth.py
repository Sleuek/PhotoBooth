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
LARGEUR_ECRAN     = 1920
HAUTEUR_ECRAN    = 1280
LARGEUR_PHOTO      = 1920 
HAUTEUR_PHOTO     = 1280
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
   # background = Image.open(archiveDir+"/"+fileName)
    #foreground = Image.open("/home/pi/LayerInDaSowce.png")
    #Image.alpha_composite(background, foreground).save(archiveDirWithLayer+"/layered_"+ fileName)

    
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
    addPreviewOverlay(150,200,100,"--> Merci !   :-)")
    #Sauvegarde de l'image
    camera.capture(imageName, resize=(LARGEUR_PHOTO, HAUTEUR_PHOTO))
    print("Image "+imageName+" enregistrée.")

def addPreviewOverlay(xcoord,ycoord,fontSize,overlayText):
    global overlay_renderer
    img = Image.new("RGB", (LARGEUR_ECRAN, HAUTEUR_ECRAN))
    draw = ImageDraw.Draw(img)
    draw.font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",fontSize)
    draw.text((xcoord,ycoord), overlayText, (0, 0, 0))

    if not overlay_renderer:
        overlay_renderer = camera.add_overlay(img.tobytes(),
                                              layer=3,
                                              size=img.size,
                                              alpha=128);
    else:
        overlay_renderer.update(img.tobytes())



#lancer une action complète pour 1 photo et impression
def play():
    print("Démarrage de la séquence '1 photo'")

    
        
    fileName = time.strftime("%H%M%S")+".jpg"
    fileName_Miroir = time.strftime("%H%M%S")+"_Miroir.jpg"
    print("Nom de fichier créé : "+fileName)

    #precapture1(fileName)
    #time.sleep(2)
    countdownFrom(PHOTO_DELAY)
    #precapture2(fileName)
   #time.sleep(2)
    captureImage(fileName)
    time.sleep(1)    
    archiveImage(fileName)
    deleteImages(fileName)
    

    camera.stop_preview()
    
    AfficherPhoto(archiveDir+"/"+fileName)
    addPreviewOverlay(150,200,100,"Your token : " +fileName )
    time.sleep(5)
    
    addPreviewOverlay(150,200,100,"Appuyez sur le bouton")
    initCamera(camera)
    print("Démarrage de l'aperçu")
    camera.start_preview()
    #AfficherPhoto("/home/pi/LayerInDaSowce.png")

    #AfficherPhoto("/home/pi/Photomaton_Prev/accueil.png")
    #addPreviewOverlay(20,200,55,"--> Appuyez sur le bouton Rouge")

    #os.system('lpr -h -PSamsung_Samsung_CLX-3300_Series -#1 -o media=A4 -o scaling=25 "/home/pi/Desktop/Photos_du_Photomaton/'+fileName+'"')
    #time.sleep(5)
    #print("Travail d'impression créé avec succès.")

    
def initCamera(camera):
    #camera settings
    camera.resolution            = (LARGEUR_ECRAN, HAUTEUR_ECRAN)
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
    


def AfficherPhoto(fileName): # affiche NomPhoto
    print("loading image: " + fileName)
    background = pygame.image.load(fileName);
    background.convert_alpha()
    background = pygame.transform.scale(background,(LARGEUR_ECRAN,HAUTEUR_ECRAN))
    screen.blit(background,(0,0),(0,0,LARGEUR_ECRAN,HAUTEUR_ECRAN))
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

