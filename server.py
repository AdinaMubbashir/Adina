import cgi
import io
import json
import sys
import MolDisplay
import molecule
from molsql import Database
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib


public_files = ['/index.html', '/style.css',
                '/script.js', '/home.html', '/upload.html', '/display.html']
db = Database(reset=True)
db.create_tables()


class MyHandler(BaseHTTPRequestHandler):
    pointX = 0
    pointY = 0
    pointZ = 0
    mol_here = "Nothing present"

    def do_GET(self):
        print(self.path)
        if self.path in public_files:
            self.send_response(200)
            self.send_header("Content-type", "text/html")

            fp = open(self.path[1:])
            page = fp.read()
            fp.close()

            self.send_header("Content-length", len(page))
            self.end_headers()

            self.wfile.write(bytes(page, "utf-8"))

        elif self.path == '/grabMol':
            # Get molecule
            mole = db.obtainMol()
            if not mole:
                # If no molecule is found
                self.send_response(204)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                return

            # Mole is converted into Json string
            molej = json.dumps(mole)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", str(len(molej)))
            self.end_headers()

            self.wfile.write(molej.encode("utf-8"))

        elif self.path == '/fileFormat':
            # If molecule is empty
            if MyHandler.mol_here == "Empty":
                self.send_response(204)
                self.send_header("Content-type", "image/svg+xml")
                self.end_headers()
                return

            # Molecule exists and modify settings to display
            if MyHandler.pointX != 0 or MyHandler.pointY != 0 or MyHandler.pointZ != 0:
                MolDisplay.radius = db.radius()
                MolDisplay.element_name = db.element_name()
                MolDisplay.header += db.radial_gradients()
                mol = db.load_mol(MyHandler.mol_here)

                # Transformations to molecules
                if MyHandler.pointX != 0:
                    num = molecule.mx_wrapper(int(MyHandler.pointX), 0, 0)
                    mol.xform(num.xform_matrix)
                if MyHandler.pointY != 0:
                    num = molecule.mx_wrapper(0, int(MyHandler.pointY), 0)
                    mol.xform(num.xform_matrix)
                if MyHandler.pointZ != 0:
                    num = molecule.mx_wrapper(0, 0, int(MyHandler.pointZ))
                    mol.xform(num.xform_matrix)
                # Sort atoms
                mol.sort()
            else:
                mol = None

            self.send_response(200)
            self.send_header("Content-type", "image/svg+xml")
            self.end_headers()

            if mol is not None:
                self.wfile.write(bytes(mol.svg(), "utf-8"))

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))

    def do_POST(self):

        if self.path == "/elementAdd.html":
            # Parse value
            content_length = int(self.headers['Content-Length'])
            value = urllib.parse.parse_qs(
                self.rfile.read(content_length).decode('utf-8'))

            # Elements are saved in the database
            db['Elements'] = (int(value['ElementNumber'][0]),
                              value['ElementCode'][0],
                              value['ElementName'][0],
                              value['colour1'][0][1:],
                              value['colour2'][0][1:],
                              value['colour3'][0][1:],
                              int(value['radius'][0]))

            # Response message
            update = "All Elements got added"
            message = update.encode('utf-8')

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Content-length', len(message))
            self.end_headers()
            self.wfile.write(message)

        elif (self.path == "/elementRemove.html"):
            content_length = int(self.headers['Content-Length'])
            # Read data
            figure = self.rfile.read(content_length)
            # Parse data
            value = urllib.parse.parse_qs(figure.decode('utf-8'))
            given = str(value['remove'][0])

            # Function for removing given element
            db.test(given)
            update = "Content has been collected"

            # Response message
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Content-length', len(update))
            self.end_headers()
            self.wfile.write(bytes(update, "utf-8"))

        elif (self.path == "/fileUpload"):
            # Uploading file
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            # Get content
            molN = form['molecule-name'].value
            fileVersion = form['fileSdf'].value

            # Check file to see if it is sdf file
            content = form['fileSdf'].headers['Content-Disposition']
            filename = cgi.parse_header(content)[1]['filename']
            if not filename.endswith('.sdf'):
                self.send_error(400, 'Invalid file format')
                return

            # Molecule is added to Database
            pFile = io.BytesIO(fileVersion)
            with io.TextIOWrapper(pFile) as file:
                db.add_molecule(molN, file)

            getMessage = "Everything was added"
            # Response message
            response_length = str(len(getMessage))
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", response_length)
            self.end_headers()
            self.wfile.write(getMessage.encode('utf-8'))

        elif self.path == "/inspectMolecule":
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            # Parse the content
            value = urllib.parse.parse_qs(data.decode('utf-8'))
            call = value['nameMole'][0]

            MyHandler.mol_here = call
            # Sort the molecule from Database
            mol = MolDisplay.Molecule()
            mol = db.load_mol(call)
            mol.sort()

            # Set radius and element name
            MolDisplay.radius = db.radius()
            MolDisplay.element_name = db.element_name()
            MolDisplay.header += db.radial_gradients()

            # Get SVG of molecule
            svg = mol.svg()

            response = bytearray(svg.encode('utf-8'))
            response_length = len(response)
            # Response message
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", response_length)
            self.end_headers()
            self.wfile.write(response)

        elif self.path == '/rotate':
            content_length = int(self.headers['Content-Length'])
            # Parse the data
            value = urllib.parse.parse_qs(
                self.rfile.read(content_length).decode('utf-8'))

            # Get axis values
            angleRot = value.get('axis', [None])[0]
            if angleRot:
                if angleRot in ('x', 'y', 'z'):
                    # Increment angle
                    angleAxis = getattr(
                        MyHandler, f'point{angleRot.upper()}')
                    angleAxis = (angleAxis + 10) % 360
                    setattr(
                        MyHandler, f'point{angleRot.upper()}', angleAxis)
                    # Message informing user the error
                    getMessage = 'Degree changed incremented successfully'
                else:
                    # Message informing user the error
                    getMessage = f'Error: Invalid axis {angleRot}'
            else:
                # Message informing user the error
                getMessage = 'Error: No axis specified'

            # Response message
            message = len(getMessage.encode('utf-8'))
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Content-length', message)
            self.end_headers()
            self.wfile.write(getMessage.encode('utf-8'))

        else:
            self.send_error(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))


httpd = HTTPServer(('localhost', int(sys.argv[1])), MyHandler)
httpd.serve_forever()
