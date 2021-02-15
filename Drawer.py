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


def divide_into_pastable_pieces(image):
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


def pad_array(array, subarray_shape, output_shape):
    right_col = array[:, -1, :]
    bottom_row = array[-1, :, :]
    padded_shape = tuple([subarray_shape[i] * output_shape[i] for i in range(2)])
    lacking_shape = tuple([padded_shape[i] - array.shape[i] for i in range(2)])

    padded_right_col = np.zeros((padded_shape[0], array.shape[2]))
    padded_bottom_row = np.zeros((padded_shape[1], array.shape[2]))

    padded_right_col[:right_col.shape[0], :] = right_col
    padded_bottom_row[:bottom_row.shape[0], :] = bottom_row

    new_array = np.zeros(padded_shape + tuple([array.shape[-1]]))
    new_array[:array.shape[0], :array.shape[1], :] = array

    for i in range(lacking_shape[0]):
        index = array.shape[0] + i
        new_array[index, :, :] = padded_bottom_row

    for i in range(lacking_shape[1]):
        index = array.shape[1] + i
        new_array[:, index, :] = padded_right_col

    return new_array


# def scale_down(array, shape):
    # output = np.zeros(shape + (array.shape[-1],))
    # shape_of_subarray = tuple([ceil(array.shape[i] / output.shape[i]) for i in range(2)])

    # lacking_size = sum([shape_of_subarray[i] * output.shape[i] - array.shape[i] for i in range(2)])
    # # if it's more affordable, add padding
    # if lacking_size > sum(shape_of_subarray)/2:
        # array = pad_array(array, shape_of_subarray, shape)
    # for x in range(shape[0]):
        # for y in range(shape[1]):
            # start_x = shape_of_subarray[0] * x
            # start_y = shape_of_subarray[1] * y
            # stop_x = shape_of_subarray[0] * (x + 1)
            # stop_y = shape_of_subarray[1] * (y + 1)
            # subarray = array[start_x:stop_x, start_y:stop_y].reshape(-1, array.shape[-1])
            # sum_vector = np.dot(np.ones(subarray.shape[0]), subarray)
            # average_vector = sum_vector / subarray.shape[0]
            # output[x][y] = average_vector
    # return output



def pad_along_axis(array: np.ndarray, target_length: int, axis: int = 0):
    pad_size = target_length - array.shape[axis]
    if pad_size <= 0:
        return array
    npad = [(0, 0)] * array.ndim
    npad[axis] = (0, pad_size)
    return np.pad(array, pad_width=npad, mode='constant', constant_values=0)


def scale_down(array, shape):
    # print("shape", shape)
    # output = np.zeros(shape + (array.shape[-1],))
    # print("array.shape", array.shape)
    # print("output.shape:", output.shape)
    # shape_of_subarray = tuple([array.shape[i] // output.shape[i] for i in range(2)])
    # print("shape_of_subarray", shape_of_subarray)
    # loss = [array.shape[i] - (output.shape[i] * shape_of_subarray[i]) for i in range(2)]
    # print("loss", loss)


    print("shape", shape)
    output = np.zeros(shape + (array.shape[-1],))
    print("array.shape", array.shape)
    print("output.shape:", output.shape)
    shape_of_subarray = tuple([array.shape[i] // output.shape[i] for i in range(2)])
    print("shape_of_subarray", shape_of_subarray)
    loss = [array.shape[i] - (output.shape[i] * shape_of_subarray[i]) for i in range(2)]
    print("loss", loss)

    size_to_add = [loss[i] // shape_of_subarray[i] for i in range(2)]
    # size_to_add = np.array(loss) / np.array(shape_of_subarray)
    shape = [shape[i] + size_to_add[i] for i in range(2)]
    print("shape", shape)
    output = np.zeros(tuple(shape) + (array.shape[-1],))

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
    shape = array.shape
    array = array.reshape((-1, shape[-1]))
    for i, rgba in enumerate(array):
        array[i] = find_closest_color(palette, rgba)
    return array.reshape(shape)


#######################


static_palette = generate_palette()


def encode_image(filename, shape):
    image_big = read_png(filename)
    if len(shape) == 1:
        shape = (shape[0], int(image_big.shape[0] / image_big.shape[1] * shape[0]))
    image_small = scale_down(image_big, (shape[1], shape[0]))
    image_small = normalize(image_small, static_palette)
    encoded_image = []
    for row in range(image_small.shape[0]):
        encoded_image.append('')
        for col in range(image_small.shape[1]):
            encoded_image[row] += static_palette[arr_to_tuple(image_small[row][col])]
    return divide_into_pastable_pieces(encoded_image)

# encode_image('temp.png', (20, ))