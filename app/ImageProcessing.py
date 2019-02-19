import wand.display
from wand.image import Image

def save_thumbnail(image_name, frame_width, frame_height):
    """
    save thumbnail image (aspect ratio preserved) to thumbnails/image_name

    image_name (str): file name of the image in ./images
    frame_width, frame_height (int): width and height of specified frame
    """
    with wand.image.Image(filename='./images/' + image_name) as img:
        img.strip()
        img.sample(int(img.width/5), int(img.height/5))
        img.transform(resize='{}x{}>'.format(frame_width, frame_height))
        img.save(filename='thumbnails/' + image_name)

if __name__ == '__main__':
    save_thumbnail('duck.png', 160, 120)
