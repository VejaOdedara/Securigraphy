import streamlit as st
from PIL import Image
import base64
from io import BytesIO

class PlayfairCipher:
    def __init__(self, key):
        self.key = key
        self.matrix = self.generate_matrix()

    def generate_matrix(self):
        letters = "abcdefghiklmnopqrstuvwxyz"  # Skipping 'j'
        key_processed = "".join([char for char in self.key if char in letters])
        key_without_duplicates = "".join(dict.fromkeys(key_processed))

        matrix = []
        for char in key_without_duplicates + letters:
            if char not in matrix:
                matrix.append(char)
        matrix = [matrix[i:i + 5] for i in range(0, 25, 5)]
        return matrix

    def find_position(self, char):
        for r_idx, row in enumerate(self.matrix):
            if char in row:
                return r_idx, row.index(char)
        return -1, -1

    def encrypt(self, text):
        text = text.replace("j", "i").replace("J", "I")  # Replace 'j' with 'i'
        text = [text[i:i+2] for i in range(0, len(text), 2)]
        encrypted_text = ""

        for pair in text:
            if len(pair) == 1:  # If there's only one character left
                pair += 'X'  # Add an 'X' to form a pair

            row1, col1 = self.find_position(pair[0])
            row2, col2 = self.find_position(pair[1])

            if row1 == row2:
                encrypted_text += self.matrix[row1][(col1 + 1) % 5] + self.matrix[row2][(col2 + 1) % 5]
            elif col1 == col2:
                encrypted_text += self.matrix[(row1 + 1) % 5][col1] + self.matrix[(row2 + 1) % 5][col2]
            else:
                encrypted_text += self.matrix[row1][col2] + self.matrix[row2][col1]

        return encrypted_text

    def decrypt(self, encrypted_text):
        decrypted_text = ""
        encrypted_text = [encrypted_text[i:i+2] for i in range(0, len(encrypted_text), 2)]

        for pair in encrypted_text:
            row1, col1 = self.find_position(pair[0])
            row2, col2 = self.find_position(pair[1])

            if row1 == row2:
                decrypted_text += self.matrix[row1][(col1 - 1) % 5] + self.matrix[row2][(col2 - 1) % 5]
            elif col1 == col2:
                decrypted_text += self.matrix[(row1 - 1) % 5][col1] + self.matrix[(row2 - 1) % 5][col2]
            else:
                decrypted_text += self.matrix[row1][col2] + self.matrix[row2][col1]

        return decrypted_text


class VigenereCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, text):
        encrypted_text = ""
        key_repeated = self.key * (len(text) // len(self.key)) + self.key[:len(text) % len(self.key)]

        for i in range(len(text)):
            char = text[i]
            if char.isalpha():
                shift = ord(key_repeated[i].lower()) - 97
                if char.isupper():
                    encrypted_text += chr(((ord(char) - 65 + shift) % 26) + 65)
                else:
                    encrypted_text += chr(((ord(char) - 97 + shift) % 26) + 97)
            else:
                encrypted_text += char

        return encrypted_text

    def decrypt(self, encrypted_text):
        decrypted_text = ""
        key_repeated = self.key * (len(encrypted_text) // len(self.key)) + self.key[:len(encrypted_text) % len(self.key)]

        for i in range(len(encrypted_text)):
            char = encrypted_text[i]
            if char.isalpha():
                shift = ord(key_repeated[i].lower()) - 97
                if char.isupper():
                    decrypted_text += chr(((ord(char) - 65 - shift) % 26) + 65)
                else:
                    decrypted_text += chr(((ord(char) - 97 - shift) % 26) + 97)
            else:
                decrypted_text += char

        return decrypted_text

class CaesarCipher:
    def __init__(self, shift):
        self.shift = shift

    def encrypt(self, text):
        encrypted_text = ""
        for char in text:
            if char.isalpha():
                if char.isupper():
                    encrypted_text += chr(((ord(char) - 65 + self.shift) % 26) + 65)
                else:
                    encrypted_text += chr(((ord(char) - 97 + self.shift) % 26) + 97)
            else:
                encrypted_text += char
        return encrypted_text

    def decrypt(self, encrypted_text):
        decrypted_text = ""
        for char in encrypted_text:
            if char.isalpha():
                if char.isupper():
                    decrypted_text += chr(((ord(char) - 65 - self.shift) % 26) + 65)
                else:
                    decrypted_text += chr(((ord(char) - 97 - self.shift) % 26) + 97)
            else:
                decrypted_text += char
        return decrypted_text

# Convert encoding data into 8-bit binary form using ASCII value of characters
def genData(data):
    new_data = [format(ord(i), '08b') for i in data]
    return new_data

# Modify pixels according to the 8-bit binary data
def modifyPixels(pixels, data):
    data_list = genData(data)
    data_length = len(data_list)
    pixel_data = iter(pixels)

    for i in range(data_length):
        pixel = [value for value in pixel_data.__next__()[:3] +
                         pixel_data.__next__()[:3] +
                         pixel_data.__next__()[:3]]

        for j in range(0, 8):
            if data_list[i][j] == '0' and pixel[j] % 2 != 0:
                pixel[j] -= 1
            elif data_list[i][j] == '1' and pixel[j] % 2 == 0:
                if pixel[j] != 0:
                    pixel[j] -= 1
                else:
                    pixel[j] += 1

        if i == data_length - 1:
            if pixel[-1] % 2 == 0:
                if pixel[-1] != 0:
                    pixel[-1] -= 1
                else:
                    pixel[-1] += 1
        else:
            if pixel[-1] % 2 != 0:
                pixel[-1] -= 1

        pixel = tuple(pixel)
        yield pixel[0:3]
        yield pixel[3:6]
        yield pixel[6:9]

# Encode data into the image
def encodeData(image, text, cipher):
    new_image = image.copy()
    encrypted_text = cipher.encrypt(text)
    pixels = modifyPixels(new_image.getdata(), encrypted_text)
    new_image.putdata(list(pixels))
    return new_image

# Encode image to base64 for download
def getBase64Image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# Decode the hidden data from the image
def decodeData(image, cipher):
    pixels = iter(image.getdata())
    binary_data = ""

    while True:
        pixels_list = [value for value in pixels.__next__()[:3] +
                       pixels.__next__()[:3] +
                       pixels.__next__()[:3]]

        binary_string = ""

        for pixel in pixels_list[:8]:
            if pixel % 2 == 0:
                binary_string += '0'
            else:
                binary_string += '1'

        binary_data += chr(int(binary_string, 2))

        if pixels_list[-1] % 2 != 0:
            decrypted_text = cipher.decrypt(binary_data)
            return decrypted_text

# Streamlit UI
st.title("Image Steganography: Hide your words in an image!")

option = st.selectbox("Choose an option:", ("Encode", "Decode"))

if option == "Encode" or option == "Decode":
    st.write("Please select a cipher technique:")
    selected_cipher = st.selectbox("Choose a cipher technique:", ("Playfair", "Vigenère", "Caesar"))

    if option == "Encode":
        st.write("Please provide the text to hide:")
        text = st.text_input("Enter the text:")
        key = st.text_input("Enter the key or shift value:")

        uploaded_image = st.file_uploader("Upload an image (PNG or JPEG)", type=["png", "jpg", "jpeg"])

        if st.button("Encode"):
            if text and uploaded_image and key:
                image = Image.open(uploaded_image)

                if selected_cipher == "Playfair":
                    cipher = PlayfairCipher(key)
                elif selected_cipher == "Vigenère":
                    cipher = VigenereCipher(key)
                else:  # Caesar Cipher
                    cipher = CaesarCipher(int(key))

                new_img = encodeData(image, text, cipher)
                st.image(new_img, caption='Encoded Image', use_column_width=True)

                buffered = BytesIO()
                new_img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                href = f'<a href="data:file/png;base64,{img_str}" download="encoded_image.png">Download Encoded Image</a>'
                st.markdown(href, unsafe_allow_html=True)
                

    elif option == "Decode":
        st.write("Please upload an image to decode:")
        decode_image = st.file_uploader("Upload the image", type=["png", "jpg", "jpeg"])
        key = st.text_input("Enter the key or shift value:")

        if st.button("Decode"):
            if decode_image and key:
                image = Image.open(decode_image)

                if selected_cipher == "Playfair":
                    cipher = PlayfairCipher(key)
                elif selected_cipher == "Vigenère":
                    cipher = VigenereCipher(key)
                else:  # Caesar Cipher
                    cipher = CaesarCipher(int(key))

                decoded_text = decodeData(image, cipher)
                st.write("Decoded Text:", decoded_text)
                key = ""  # Clear the key value for practicality
               
