def objects_encoder(objectsToEncode, use_floats=True):
	'''
	Encode strings as a floating point number
	:param strings (list): A list of strings
	:return: A dictionary of strings: flaoting point number
	'''
	encoder = {}
	if use_floats: numeric_val, increment, decimal = 0.0, 0.1, 2
	else: numeric_val, increment, decimal = 0, 1, 0
	for index, objectToEncode in enumerate(objectsToEncode):
		numeric_val = round(increment*(index+1), decimal)
		encoder[objectToEncode] = numeric_val
	return encoder

def object_encoder(objectToEncode, encoder):
	'''
	Encode a text string using an encoder
	:param objectToEncode (str): A string to encode
	:param encoder: Encoder
	:return: String-Code tuple
	'''
	objectToEncode = tuple(objectToEncode)
	if objectToEncode in encoder.keys():
		object_code = encoder[objectToEncode]
	else:
		encoder_values = list(encoder.values())
		if type(encoder_values[0]) == float: decimal = 2
		else: decimal = 0
		increment = min(encoder_values)
		max_code = max(encoder_values)
		object_code = round(max_code+increment, decimal)
	return object_code

def build_decoder(encoder):
	'''
	Transform an encoder to a decoder
	:param encoder: Key-Value encoding dictionary
	:return: Value-Key decoding dictionary
	'''
	return {v: k for k, v in encoder.items()}