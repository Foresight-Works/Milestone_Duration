def strings_encoder(strings, use_floats=True):
	'''
	Encode strings as a floating point number
	:param strings (list): A list of strings
	:return: A dictionary of strings: flaoting point number
	'''
	mapping = {}
	if use_floats: numeric_val, increment, decimal = 0.0, 0.1, 2
	else: numeric_val, increment, decimal = 0, 1, 0
	for string in strings:
		numeric_val = round(numeric_val + increment, decimal)
		mapping[string] = numeric_val
	return mapping

def strings_encoder(text_strings, use_floats=True):
	'''
	Encode strings as a floating point number
	:param strings (list): A list of strings
	:return: A dictionary of strings: flaoting point number
	'''
	mapping = {}
	if use_floats: numeric_val, increment, decimal = 0.0, 0.1, 2
	else: numeric_val, increment, decimal = 0, 1, 0
	for index, text_string in enumerate(text_strings):
		numeric_val = round(increment*(index+1), decimal)
		mapping[text_string] = numeric_val
	return mapping

def string_encoder(text_string, mapping):
	'''
	Encode a text string using an encoder
	:param text_string (str): A string to encode
	:param mapping: Encoder
	:return: String-Code tuple
	'''
	increment = min(list(mapping.values()))
	max_code = max(list(mapping.values()))
	return (text_string, max_code+increment)

def update_encoder(encoder, text_string_code):
	'''
	Update an encoder with a string: code pair
	:param encoder(dict): An encoder to update 
	:param text_string_code(tuple): The string-code pair to add to encoder  
	:return: Updated encoder dictionary
	'''
	text_string, code = text_string_code
	encoder[text_string] = code
	return encoder

def build_decoder(encoder):
	'''
	Transform an encoder to a decoder
	:param encoder: Key-Value encoding dictionary
	:return: Value-Key decoding dictionary
	'''
	return {v: k for k, v in encoder.items()}