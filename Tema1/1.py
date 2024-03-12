import json
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer

# Define global variables
XML_FILE = 'guitars.xml'

# Define helper functions
def load_data():
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        return root
    except FileNotFoundError:
        return ET.Element('guitars')

def save_data(root):
    tree = ET.ElementTree(root)
    tree.write(XML_FILE)

def find_guitar_by_id(guitars, guitar_id):
    for guitar in guitars.findall('guitar'):
        if guitar.find('id').text == guitar_id:
            return guitar
    return None

def generate_response(status_code, data=None):
    response = {
        'status': status_code,
        'data': data
    }
    return json.dumps(response).encode('utf-8')

# Define request handler class
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        guitars = load_data()
        if self.path == '/guitars':
            guitars_list = [{'id': guitar.find('id').text, 'type': guitar.find('type').text, 'brand': guitar.find('brand').text}
                            for guitar in guitars.findall('guitar')]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(generate_response(200, guitars_list))
        elif self.path.startswith('/guitars/'):
            guitar_id = self.path.split('/')[-1]
            guitar = find_guitar_by_id(guitars, guitar_id)
            if guitar:
                guitar_data = {'id': guitar.find('id').text, 'type': guitar.find('type').text, 'brand': guitar.find('brand').text}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(generate_response(200, guitar_data))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(generate_response(404, {'message': 'Guitar not found'}))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        new_guitar = json.loads(post_data.decode('utf-8'))
        guitars = load_data()

        # Check if the request data has the required structure
        if 'brand' not in new_guitar or 'type' not in new_guitar:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(generate_response(400, {'message': 'Missing required fields: "brand" and "type"'}))
            return

        # Check if a guitar with the same brand and type already exists
        for guitar in guitars.findall('guitar'):
            if guitar.find('brand').text == new_guitar['brand'] and guitar.find('type').text == new_guitar['type']:
                self.send_response(409)
                self.end_headers()
                self.wfile.write(generate_response(409, {'message': 'Guitar with the same brand and type already exists'}))
                return
    
        # Generate a new ID by incrementing the maximum existing ID
        max_id = 0
        for guitar in guitars.findall('guitar'):
            guitar_id = int(guitar.find('id').text)
            max_id = max(max_id, guitar_id)
        new_id = max_id + 1

        # Add the new guitar with the generated ID
        new_guitar['id'] = str(new_id)
        new_guitar_elem = ET.SubElement(guitars, 'guitar')
        for key, value in new_guitar.items():
            ET.SubElement(new_guitar_elem, key).text = str(value)

        save_data(guitars)
        self.send_response(201)
        self.end_headers()
        self.wfile.write(generate_response(201, new_guitar))



    def do_PUT(self):
        if self.path == '/guitars':
            self.send_response(405)  # Method Not Allowed
            self.end_headers()
            self.wfile.write(generate_response(405, {'message': 'Updating the entire collection is not allowed'}))
            return

        content_length = int(self.headers['Content-Length'])
        put_data = self.rfile.read(content_length)
        updated_guitar = json.loads(put_data.decode('utf-8'))

        # Check if the request body has the appropriate structure
        if 'brand' not in updated_guitar or 'type' not in updated_guitar:
            self.send_response(400)  # Bad Request
            self.end_headers()
            self.wfile.write(generate_response(400, {'message': 'Request body must contain "brand" and "type"'}))
            return

        guitars = load_data()
        guitar_id = self.path.split('/')[-1]  # Extract the ID from the URL path
        guitar = find_guitar_by_id(guitars, guitar_id)
        if guitar:
            # Ensure 'id' is present in the updated_guitar dictionary
            updated_guitar['id'] = guitar_id
            for key, value in updated_guitar.items():
                guitar.find(key).text = str(value)
            save_data(guitars)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(generate_response(200, updated_guitar))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(generate_response(404, {'message': 'Guitar not found'}))



    def do_DELETE(self):
        if self.path == '/guitars':
            self.send_response(405)  # Method Not Allowed
            self.end_headers()
            self.wfile.write(generate_response(405, {'message': 'Deleting the entire collection is not allowed'}))
            return

        guitars = load_data()
        guitar_id = self.path.split('/')[-1]
        guitar = find_guitar_by_id(guitars, guitar_id)
        if guitar:
            guitars.remove(guitar)
            save_data(guitars)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(generate_response(200, {'message': 'Guitar deleted successfully'}))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(generate_response(404, {'message': 'Guitar not found'}))


# Define main function
def main():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Starting server...')
    httpd.serve_forever()

if __name__ == '__main__':
    main()

