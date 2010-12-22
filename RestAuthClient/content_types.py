class content_handler( object ):
	def get_str( self, body ):
		pass
	def get_dict( self, body, keys ):
		pass
	def get_list( self, body ):
		pass
	def get_bool( self, body ):
		pass

	def serialize_unicode( self, obj ):
		return self.serialize_str( str( obj ) )

	def serialize_str( self, obj ):
		pass
	def serialize_bool( self, obj ):
		pass
	def serialize_list( self, obj ):
		pass
	def serialize_dict( self, obj ):
		pass

class json_handler( content_handler ):
	mime = 'application/json'

	def __init__( self ):
		import json
		self.json = json

	def get_str( self, body ):
		return self.json.loads( body )

	def get_dict( self, body, encoding ):
		return self.json.loads( body, encoding )

	def get_list( self, body ):
		return self.json.loads( body )

	def get_bool( self, body ):
		return self.json.loads( body )

	def serialize_str( self, obj ):
		return self.json.dumps( obj )

	def serialize_bool( self, obj ):
		return self.json.dumps( obj )

	def serialize_list( self, obj ):
		return self.json.dumps( obj )

	def serialize_dict( self, obj ):
		return self.json.dumps( obj )

class xml_handler( content_handler ):
	mime = 'application/xml'

class form_handler( content_handler ):
	mime = 'application/x-www-form-urlencoded'

CONTENT_HANDLERS = { 'application/json': json_handler,
	'application/xml': xml_handler,
	'application/x-www-form-urlencoded': form_handler }
