from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import time
import config

from array import array
import os
import PIL
from PIL import Image
import sys
import time
import random
import numpy as np
import pygame
import pickle


def get_random_monet():
    filename = random.choice(os.listdir("monet_landscape"))
    return "monet_landscape/"+ filename

def get_object(filename, predictor, publish_iteration_name):
    list_of_tags= []
    with open(filename, mode="rb") as test_data:
        results = predictor.detect_image(config.project_id, publish_iteration_name, test_data)
    for prediction in results.predictions:
        # tag name, probability, left, top, width, height
        if prediction.probability * 100 > 80:
            list_of_tags.append([prediction.tag_name, prediction.probability * 100, prediction.bounding_box.left, prediction.bounding_box.top, prediction.bounding_box.width, prediction.bounding_box.height])
    return list_of_tags

def get_random_sound(folder):
    while(1):
        filename = random.choice(os.listdir("tag_sounds/"+folder))
        if filename[0] != ".":
            if "mp3" or "wav" in filename:
                return "tag_sounds/"+folder+"/"+filename
    
def tag_to_sound(tags):
    tag_name= tags
    return get_random_sound(tag_name)


def get_random_music(com):
    while(1):
        folder= random.choice(os.listdir("classical/"+com))
        if ("DS_Store" not in folder):
            return "classical/"+com+"/"+folder

def in_box(box,rect,loc):
    left= box[2]
    top = box[3]
    width= box[4]
    height= box[5]
    w,h = rect.size
    left_image= w*left
    top_image= h*top
    right_image=left_image+(w*width)
    bottom_image=top_image+(h*height)
    if loc[0] >= left_image and loc[0]<= right_image and loc[1] >= top_image and loc[1] <= bottom_image:
        return True
    else:
        return False
      
def box_to_gamerect(box,rect):
    left= box[2]
    top = box[3]
    width= box[4]
    height= box[5]
    w,h = rect.size
    left_image= w*left
    top_image= h*top
    right_image=left_image+(w*width)
    bottom_image=top_image+(h*height)
    return pygame.Rect(left_image,top_image,w*width,h*height)

def previous_monetsounds(painting,music,tree,flower,grass,mountain,sky,structure, water, snow, boat, tag_box):
    
    current = [painting,music, tree, flower,grass,mountain,sky,structure, water, snow, boat,tag_box]
    pickle.dump(current, open("current_save.p","wb"))

def lood_save():
    try:
        return pickle.load(open("save.p","rb"))
    except:
        return False

def image_size(filename):
    picture = Image.open(filename)
    width, height = picture.size
    if height > 1000:
        scale = 1000.0/height
        scaled_h = int(scale*height)
        scaled_w = int(scale*width)
        scaled_pic = picture.resize((scaled_w,scaled_h))
        scaled_pic.save("temp_scaled.jpg", "JPEG")
        return "temp_scaled.jpg"
    else: 
        return filename 

def play_sound_no_volume(tags_in_image, channel_d):
    for i in tags_in_image:
        if i[0] in channel_d.keys():
            channel_d[i[0]][0].set_volume(0)
            channel_d[i[0]][0].play(channel_d[i[0]][1], loops =-1)

def main():
    prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": config.prediction_key})
    predictor = CustomVisionPredictionClient(config.ENDPOINT, prediction_credentials)

    publish_iteration_name = "Iteration2"
 
    OG_monet_file = get_random_monet()
    monet_file = image_size(OG_monet_file)

    tag_box= get_object(monet_file, predictor, publish_iteration_name)

    pygame.init()
    pygame.mixer.set_num_channels(12)
    game_monet = pygame.image.load(monet_file)
    screen = pygame.display.set_mode(game_monet.get_rect().size)

    game_monet_cp = pygame.Surface.copy(game_monet)
    pxarray = pygame.PixelArray(game_monet_cp)
    game_monet_rect = game_monet.get_rect()

    tree_file = tag_to_sound("tree")
    flower_file = tag_to_sound("flower")
    grass_file = tag_to_sound("grass")
    mountain_file = tag_to_sound("mountain")
    sky_file = tag_to_sound("sky")
    structure_file = tag_to_sound("structure")
    water_file = tag_to_sound("water")
    snow_file = tag_to_sound("snow")
    boat_file = tag_to_sound("boat")

    sound_tree = pygame.mixer.Sound(tree_file)
    sound_flower= pygame.mixer.Sound(flower_file)
    sound_grass = pygame.mixer.Sound(grass_file)
    sound_mountain= pygame.mixer.Sound(mountain_file)
    sound_sky= pygame.mixer.Sound(sky_file)
    sound_structure= pygame.mixer.Sound(structure_file)
    sound_water= pygame.mixer.Sound(water_file)
    sound_snow= pygame.mixer.Sound(snow_file)
    sound_boat = pygame.mixer.Sound(boat_file)

    music = "take-it-all-in.mp3" if random.randint(0,1) == 1 else "music_dave_miles_shades_of_orange.mp3"

    previous_monetsounds(OG_monet_file,music,tree_file,flower_file,grass_file,mountain_file,sky_file,structure_file,\
        water_file, snow_file, boat_file,tag_box)

    sound_music = pygame.mixer.Sound(music)
    channel_music = pygame.mixer.Channel(8)

    channel_d= {"tree":[pygame.mixer.Channel(0), sound_tree, False, 0], "flower":[pygame.mixer.Channel(1), sound_flower, False, 0], "grass":[pygame.mixer.Channel(2), sound_grass, False, 0],
                "mountain":[pygame.mixer.Channel(3), sound_mountain, False, 0], "sky":[pygame.mixer.Channel(4), sound_sky, False, 0], "structure":[pygame.mixer.Channel(5), sound_structure, False, 0],
                "water":[pygame.mixer.Channel(6), sound_water, False, 0], "snow":[pygame.mixer.Channel(7), sound_snow, False, 0], "boat":[pygame.mixer.Channel(9), sound_boat, False, 0]}

    rect_list=[]
    for i in tag_box:
        rect_list.append(box_to_gamerect(i,game_monet_rect))

    play_sound_no_volume(tag_box, channel_d)

    channel_music.play(sound_music,loops=-1)

    if music == "take-it-all-in.mp3":
        channel_music.set_volume(0.2)
    else:
        channel_music.set_volume(0.4)

    while 1:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                sys.exit()
            if (event.type == pygame.MOUSEBUTTONDOWN):
                 for i in tag_box:  
                    if in_box(i,game_monet_rect,loc):
                       pass
            loc = pygame.mouse.get_pos()
            color = pxarray[loc[0]][loc[1]]

            for i in tag_box:
                channel_d[i[0]][2] = False 

            for i in tag_box:
                if in_box(i,game_monet_rect,loc):
                    channel_d[i[0]][2]=True

            for i in tag_box:
                if channel_d[i[0]][2]== True:
                    if channel_d[i[0]][3] < 0.4:
                         channel_d[i[0]][3]+=0.005
                else: 
                    if channel_d[i[0]][3]> 0.0:
                        channel_d[i[0]][3] -=0.005

                channel_d[i[0]][0].set_volume(channel_d[i[0]][3]) 
                
            loc = pygame.mouse.get_pos()
            color = pxarray[loc[0]][loc[1]]
        
        screen.fill((0,0,0))
        screen.blit(game_monet, game_monet_rect)
        
        #Uncomment below to show bounding boxes
        #for i in rect_list:
            #pygame.draw.rect(game_monet,(0,0,0),i, 2)
        pygame.display.flip()

if __name__ == "__main__":
    main()