from PIL import Image
from collections import defaultdict
import numpy as np
from math import inf


def arr_to_tuple(array):
    return tuple(array.flatten())


def generate_palette():
    disco_colors = [':blue_square:',
                    ':orange_square:',
                    ':yellow_square:',
                    ':white_large_square:',
                    ':black_large_square:',
                    ':brown_square:',
                    ':green_square:',
                    ':purple_square:',
                    ':red_square:',
                    '      ']
    palette_png = read_png('palette.png')
    palette = defaultdict(lambda: ':question:')
    for i, color in enumerate(palette_png[0]):
        palette[arr_to_tuple(color)] = disco_colors[i]
    return palette


def image_needs_prefix(image):
    counter = 0
    for row in image:
        if counter + len(row) + 2 > 2000:
            if row[0] == ' ':
                return True
            counter = 0
        counter += len(row) + 2
    return False


def divide_into_pasteable_pieces(image):
    prefix = '.' if image_needs_prefix(image) else ''
    messages = [prefix]
    for row in image:
        if len(messages[-1]) + len(row) + 2 > 2000:
            messages.append(prefix)
        messages[-1] += row + '\n' + ' ' * len(prefix)
    return messages


def read_png(filename):
    im = Image.open(filename)
    pix = im.load()
    img = []
    for i in range(im.size[1]):
        img.append([])
        for j in range(im.size[0]):
            img[i].append(list(pix[j, i]))
    return np.array(img)


def scale_down(array, shape):
    output_shape = shape + [array.shape[-1]]
    shape_of_subarray = [array.shape[i] // output_shape[i] for i in range(2)]
    loss = [array.shape[i] - (output_shape[i] * shape_of_subarray[i]) for i in range(2)]

    size_to_add = [loss[i] // shape_of_subarray[i] for i in range(2)]
    shape = [shape[i] + size_to_add[i] for i in range(2)]
    output = np.zeros(shape + [array.shape[-1]])

    for x in range(shape[0]):
        for y in range(shape[1]):
            start_x = shape_of_subarray[0] * x
            start_y = shape_of_subarray[1] * y
            stop_x = shape_of_subarray[0] * (x + 1)
            stop_y = shape_of_subarray[1] * (y + 1)
            subarray = array[start_x:stop_x, start_y:stop_y].reshape(-1, array.shape[-1])
            sum_vector = np.dot(np.ones(subarray.shape[0]), subarray)
            average_vector = sum_vector / subarray.shape[0]
            output[x][y] = average_vector
    return output


def find_closest_color(palette, color):
    difference = inf
    closest = None
    for rgba in palette:
        if np.linalg.norm(color - np.array(rgba)) < difference:
            closest = np.array(rgba)
            difference = np.linalg.norm(color - np.array(rgba))
    return closest


def normalize(array, palette):
    array = array.reshape((-1, array.shape[-1]))
    for i, rgba in enumerate(array):
        array[i] = find_closest_color(palette, rgba)
    return array.reshape(array.shape)


static_palette = generate_palette()


def encode_image(filename, shape):
    image_big = read_png(filename)
    if len(shape) == 1:
        shape = (shape[0], int(image_big.shape[0] / image_big.shape[1] * shape[0]))
    image_small = scale_down(image_big, [shape[1], shape[0]])
    image_small = normalize(image_small, static_palette)
    encoded_image = []
    for row in range(image_small.shape[0]):
        encoded_image.append('')
        for col in range(image_small.shape[1]):
            encoded_image[row] += static_palette[arr_to_tuple(image_small[row][col])]
    return divide_into_pasteable_pieces(encoded_image)
