from dataclasses import dataclass
from PIL import Image as PIL_Image 
from drafter import *
from bakery import assert_equal
from typing import Optional
import os
import io

set_site_information(
    author="Andrew Tsomik (personal_email:andrew.tsomik@gmail.com, school_email:atsomik@udel.edu)",
    description="""The website, upon user input, encrypts a message provided by the user into the image they inputted or,
    decodes a secret message that was encoded into an image inputted by the user.
    """,
    sources=[],
    planning=["steg.jpg"],
    links=["https://github.com/UD-F25-CS1/cs1-website-f25-andrewtsomik", "https://drive.google.com/drive/folders/1GRGBKvu955KnXYGo0F0WKjDh2IBdrBy-?usp=sharing"]
)
hide_debug_information()
set_website_title("Secret Messages")
set_website_framed(False)

def even_or_odd_bit(num : int) -> str:
    """
    Function returns "0" if the input "num" is even and "1" if it's odd
    
    Args:
        num (int): an integer

    Returns:
        str: Whether the integer in odd("1") or even("0")
    """
    if num % 2 == 0:
        return "0"
    else:
        return "1"

assert_equal(even_or_odd_bit(26), "0")
assert_equal(even_or_odd_bit(23), "1")
assert_equal(even_or_odd_bit(101), "1")
assert_equal(even_or_odd_bit(223432432), "0")

def decode_single_char(color_intensities : list[int]) -> str:
    """
    Converts color intensities into 1's and 0's based on if they are odd or even (1 if odd, 0 if even) which is the list of intensities in binary and 
    then converts it base 2 form and converts that value into its corresponding ASCII value

    Args:
        color_intensities list[int]: list of color intensities for a single character

    Returns:
        str: Decoded version of the list color intensities
    """
    if len(color_intensities) != 8:
        return ""
    binary_form = ""
    for intensity in color_intensities:
        binary_form += even_or_odd_bit(intensity)
    return chr(int(binary_form, 2))

assert_equal(decode_single_char([46, 47, 46, 46, 47, 44, 46, 44]), "H")
assert_equal(decode_single_char([46, 46, 47, 44, 46, 44]), "")
assert_equal(decode_single_char([46, 47, 46, 46, 47, 44, 46, 44, 43]), "")
assert_equal(decode_single_char([]), "")
assert_equal(decode_single_char([22, 22, 23, 23, 22, 22, 23, 22]), "2")

def decode_chars(color_intensities : list[int], character_count : int) -> Optional[str]:
    """
    Converts color intensities into 1's and 0's based on if they are odd or even (1 if odd, 0 if even) which is the list of intensities in binary and 
    then converts it base 2 form and converts that value into its corresponding ASCII value for all set of 8 integers in the color_intensities list and then combines them
    
    Args:
        color_intensities (list[int]): list of color intensities for character(s)
        character_count (int): how many characters need to be decoded

    Returns:
        str: Decoded version of the list color intensities
    """
    if len(color_intensities) != (8 * character_count):
        return None
    decoded_characters = ""
    intensity = []
    for index in range(len(color_intensities)):
        intensity.append(color_intensities[index])
        if len(intensity) == 8:
            decoded_characters += decode_single_char(intensity)
            if index == len(color_intensities) - 1:
                return decoded_characters
            intensity = []
    return decoded_characters

assert_equal(decode_chars([22, 22, 23, 23, 22, 22, 23, 22, 26, 26, 27, 27, 26, 27, 26, 27, 42, 42, 43, 43, 44, 44, 40, 42], 3), "250")
assert_equal(decode_chars([22, 22, 23, 23, 22, 22, 23, 22, 26, 26, 27, 27, 26, 27, 26, 27, 42, 42, 43, 43, 44, 44, 40], 3), None)
assert_equal(decode_chars([22, 22, 23, 23, 22, 22, 23, 22, 26, 26, 27, 27, 26, 27, 26, 27, 42, 42, 43, 43, 44, 44, 40, 42, 46, 47, 46, 46, 47, 44, 46, 44], 4), "250H")

def get_message_length(color_intensities : list[int], header_character_count : int) -> int:
    """
    Calculates the remaining length of the secret message by decoding and only keeping the values that are integers within the range of the header

    Args:
        color_intensities (list[int]): list of color intensities for character(s)
        header_charcter_count (int): The length of the header
    
    Returns:
        int: The length of the secret message remaining
    """
    decoded_message = decode_chars(color_intensities, header_character_count)
    if decoded_message == None:
        return 0
    message_length = ""
    for character in decoded_message:
        if character in "1234567890":
            message_length += character
    if message_length == "" or len(message_length) != header_character_count:
        return 0
    return int(message_length)

assert_equal(get_message_length([20, 254, 45, 95, 40, 90, 20, 40, 200, 254, 45, 95, 40, 95, 20, 45,220, 250, 45, 95, 48, 95, 24, 44], 3), 54)
assert_equal(get_message_length([22, 22, 23, 23, 22, 22, 23, 22, 26, 26, 27, 27, 26, 27, 26, 27, 42, 42, 43, 43, 44, 44, 40, 42], 3), 250)
assert_equal(get_message_length([22, 22, 23, 23, 22, 22, 23, 22, 26, 26, 27, 27, 26, 27, 26, 27, 42, 42, 43, 43, 44, 44, 40], 3), 0)
assert_equal(get_message_length([22, 22, 23, 23, 22, 22, 23, 22, 26, 26, 27, 27, 26, 27, 26, 27, 42, 42, 43, 43, 44, 44, 40, 42, 46, 47, 46, 46, 47, 44, 46, 44], 4), 0)

def get_encoded_message(color_intensities : list[int]) -> Optional[str]:
    """
    Gets the length of the remaining message from the first 24 color intensities then decodes the appropriate amount of intensities to decode the message
    
    Args:
        color_intensities (list[int]): list of color intensities for character(s)
        
    Returns:
        str: decoded message
    """
    message_length = get_message_length(color_intensities[:24], 3)
    if message_length == 0:
        return None
    message = decode_chars(color_intensities[24:(24 + 8 * message_length)], message_length)
    return message

assert_equal(get_encoded_message([254, 254, 255, 255, 254, 254, 254, 254, 
                           254, 254, 255, 255, 254, 254, 254, 254, 
                           254, 254, 255, 255, 254, 254, 255, 254, 
                           254, 255, 254, 254, 255, 254, 254, 254, 
                           254, 255, 255, 254, 255, 254, 254, 255, 
                           254, 254, 254, 254, 254, 254, 254, 254, 
                           254, 254, 254, 254, 254, 254, 254, 254, 
                           254, 254, 254, 254, 254, 254, 254, 254, 
                           254, 254, 254, 254, 254, 254, 254, 254, 
                           254, 254, 254, 254, 254, 254, 254, 254, 
                           252]), "Hi" )

def get_color_values(image : PIL_Image, channel_index : int) -> list[int]:
    '''
    This function obtains the color intensities of a certain channel(red, green, or blue) of an image and outputs them as a list of integers
    
    Args:
        image(PIL_Image) : An image
        channel_index(int) : Integers 0, 1, or 2 that correspond to a given channel of an image, red, green, and blue respectively
    
    Returns:
        list[int] : list of color intensities
    '''
    length, width = image.size       
    color_intensities = []
    for x in range(length):
        for y in range(width):
            pixel = image.getpixel((x, y))
            color_intensities.append(pixel[channel_index])

    return color_intensities

def get_message(max_characters : int) -> str:
    """
    Function requests the user input there secret message and will only stop asking until the message's length is under that of the max_characters allowed
    Function cannot be unit tested
    Args:
        max_characters (int): maximum characters allowed in the secret message
    
    Returns:
        str: secret message
    """
    secret_message = input("Input your secret message")
    while len(secret_message) > max_characters:
        secret_message = input("Input your secret message again, your previous message exceeded the maximum character count.")
    return secret_message



def prepend_header(secret_message : str) -> str:
    """
    Function adds the length of the secret message to the beginning of the secret message, always with 3 characters, 0's to fill in missing number spots to make it 3 characters
    
    Args:
        secret_message (str): secret message from user
        
    Returns:
        str: secret message prepended with its length
    """
    message_length = str(len(secret_message))
    if len(message_length) == 2:
        message_length = "0" + message_length
    elif len(message_length) == 1:
        message_length = "00" + message_length
    return message_length + secret_message

assert_equal(prepend_header("Hi!"), "003Hi!")
assert_equal(prepend_header("S o S"), "005S o S")
assert_equal(prepend_header("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), "026ABCDEFGHIJKLMNOPQRSTUVWXYZ")
assert_equal(prepend_header("Hello World!"), "012Hello World!")

def message_to_binary(ascii_string : str) -> str:
    """
    Function converts the characters of a string of ascii values into binary
    
    Args:
        ascii_string (str): string of ascii chracters
        
    Returns:
        str: string of ascii characters converted to binary
    """
    binary_string = ""
    for characters in ascii_string:
        binary_string += format(ord(characters), '08b')
    return binary_string

assert_equal(message_to_binary("Hi"), "0100100001101001")
assert_equal(message_to_binary("058"),"001100000011010100111000")
assert_equal(message_to_binary("005"), "001100000011000000110101")
assert_equal(message_to_binary("S o S"), "0101001100100000011011110010000001010011")

def new_color_value(color_intensity : int, hidden_bit : str) -> int:
    """
    Function changes the value of the color intensity based on if the bit you are hiding is '1' or '0' and if your color intensity is even or odd
    
    Args:
        color_intensity (int): a base 10 color intensity
        hidden_bit (str): bit you are hiding, either '1' or '0'
        
    Returns:
        int: new or unchanged color intensity
    """
    if hidden_bit == '1':
        if color_intensity % 2 == 0:
            color_intensity += 1
    elif hidden_bit == '0':
        if color_intensity % 2 == 1:
            color_intensity -= 1
    return color_intensity

assert_equal(new_color_value(250, '1'), 251)
assert_equal(new_color_value(250, '0'), 250)
assert_equal(new_color_value(251, '1'), 251)
assert_equal(new_color_value(251, '0'), 250)

def hide_bits(image : PIL_Image, hidden_bit : str) -> PIL_Image:
    """
    Function hides a message in the form of bits into an image
    Function cannot be unit tested
    Args:
        image (PIL_Image): inputted image
        hidden_bit (str): a bit, '0' or '1'
    
    Returns:
        PIL_Image: encrypted image
    """
    i = 0
    length, width = image.size
    for x in range(length):
        for y in range(width):
            if i < len(hidden_bit):
                red, green, blue = image.getpixel((x, y))
                green = new_color_value(green, hidden_bit[i])
                image.putpixel((x, y), (red, green, blue))
                i += 1
    return image

@dataclass
class State:
    image: Optional[PIL_Image]
    encoding: str
    message_to_encode: str
    secret_message: str
    encoding_count: int
    decoding_count: int

@route
def index(state: State) -> Page:
    """ Use FileUpload to allow user to select only png files """
    
    return Page(state, [
        "Select a 'png' file.",       
        FileUpload("new_image", accept="image/png"),
        Button("Display", display_image)
        ])

@route
def display_image(state : State, new_image: bytes) -> Page:
    """ open the file and assign to State field """
    state.image = PIL_Image.open(io.BytesIO(new_image)).convert('RGB')
    return Page(state, [
        Image(state.image),
        "Would you like to encode or decode your image?",
        "If encoding, please input your message you want encrypted",
        TextBox("message"),
        Button("Encode", encode),
        Button("Decode", decode)
        ])

@route
def encode(state : State, message="") -> Page:
    """ will encode images """
    state.encoding_count += 1
    state.message_to_encode = message
    users_message = state.message_to_encode
    message_with_header = prepend_header(users_message)
    binary_string = message_to_binary(message_with_header)   
    new_image = hide_bits(state.image, binary_string)
    state.encoding = "Here is your encoded image!"
    state.image = new_image
    state.image.save(str(state.encoding_count) + "_encoded_file.png")
    state.secret_message = binary_string
    return Page(state, [
        state.encoding,
        "Message hidden in file encoded: " + state.secret_message,
        Image(state.image),
        "Would you like to encode again or decode another image, or go back to the start?",
        "If encoding, please input your message you want encrypted",
        Button("Back to start page", index),
        TextBox("message"),
        Button("Encode another", input_image_encoding),
        Button("Decode another", input_image_decoding),
        FileUpload("new_image", accept="image/png")
        ])

@route
def decode(state : State) -> Page:
    """ will decode images """
    state.decoding_count += 1
    if state.image is None:
        return Page(state, [
            "Error: No image loaded. Please upload an image first.",
            Button("Back to start page", index)
            ])
    
    decoded_message = get_encoded_message(get_color_values(state.image, 1))
    if decoded_message is not None:
        state.encoding = "Here is your decoded image's secret message!"
        state.secret_message = decoded_message
        state.image.save(str(state.decoding_count) + "_decoded_file.png")
        return Page(state, [
            state.encoding,
            "Secret Message: " + state.secret_message,
            "Would you like to decode again or encode another image, or go back to the start?",
            "If encoding, please input your message you want encrypted",
            Button("Back to start page", index),
            TextBox("message"),
            Button("Encode another", input_image_encoding),
            Button("Decode another", input_image_decoding),
            FileUpload("new_image", accept="image/png")
            ])
    
    state.encoding = "There is no encoded message in this image"
    return Page(state, [
        state.encoding,
        "Would you like to decode again or encode another image, or go back to the start?",
        "If encoding, please input your message you want encrypted",
        Button("Back to start page", index),
        TextBox("message"),
        Button("Encode another", input_image_encoding),
        Button("Decode another", input_image_decoding),
        FileUpload("new_image", accept="image/png")
        ])

@route
def input_image_encoding(state : State, new_image: bytes, message: str) -> Page:
    """allows user to input image for encoding"""
    state.image = PIL_Image.open(io.BytesIO(new_image)).convert('RGB')
    state.message_to_encode = message
    return Page(state, [
        "Image:",
        Image(state.image),
        Button("Proceed to encoding", encode)
        ])

@route
def input_image_decoding(state : State, new_image: bytes, message="") -> Page:
    """allows user to input image for decoding"""
    state.image = PIL_Image.open(io.BytesIO(new_image)).convert('RGB')
    return Page(state, [
        "Image:",
        Image(state.image),
        Button("Proceed to decoding", decode)
        ])
    
start_server(State(None, "", "", "", 0, 0))
