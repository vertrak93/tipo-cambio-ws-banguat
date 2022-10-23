import xml.etree.cElementTree as et
import requests
import os

catalogos = []
valores_validos = []
titulos_conversion = []
tipo_conversion = []

class Catalogo:
    def __init__(self, nombre, valor) -> None:
        self.nombre = nombre
        self.valor = valor

valor_referencia = []

def pausa():
    pausa = input("Presione enter para continuar...")

#imprime catalogo de monedas en xml
def printXML(xml):

    tree = et.fromstring(xml)

    namespaces ={
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'a' : 'http://www.banguat.gob.gt/variables/ws/'
    }

    ignoreTxt = '''{http://www.banguat.gob.gt/variables/ws/}'''

    for el in tree.findall(
    './soap:Body'
    '/a:VariablesDisponiblesResponse'
    '/a:VariablesDisponiblesResult'
    '/a:Variables'
    '/a:Variable',
    namespaces=namespaces
    ):
        print ('---------------------------')
        for ch in list(el):
            print('{:>15}: {:<30}'.format(ch.tag[len(ignoreTxt):], ch.text))

#convierte xml de catalogo de monedas al tipo "Catalogo"
def request_to_Catalogo(xml):
    tree = et.fromstring(xml)

    namespaces ={
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'a' : 'http://www.banguat.gob.gt/variables/ws/'
    }

    ignoreTxt = '''{http://www.banguat.gob.gt/variables/ws/}'''

    for el in tree.findall(
    './soap:Body'
    '/a:VariablesDisponiblesResponse'
    '/a:VariablesDisponiblesResult'
    '/a:Variables'
    '/a:Variable',
    namespaces=namespaces
    ):
        nombre = ''
        valor = ''
        
        for ch in list(el):
            #print('{:>15}: {:<30}'.format(ch.tag[len(ignoreTxt):], ch.text))
            if(valor ==''):
                valor = ch.text
                valores_validos.append(valor)
            else:
                nombre = ch.text
                titulos_conversion.append(nombre)

        res = Catalogo(nombre,valor)
        catalogos.append(res)    

#convierte el request xml a ValorReferencia
def request_to_referencia(xml):
    tree = et.fromstring(xml)

    namespaces ={
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'a' : 'http://www.banguat.gob.gt/variables/ws/'
    }

    ignoreTxt = '''{http://www.banguat.gob.gt/variables/ws/}'''

    for el in tree.findall(
    './soap:Body'
    '/a:VariablesResponse'
    '/a:VariablesResult'
    '/a:CambioDolar'
    '/a:VarDolar',
    namespaces=namespaces
    ):  
        x = 0
        tmp = float(0)
        for ch in list(el):
            
            if x == 0: 
                x=1 
            else:
                tmp =  float(ch.text)

    valor_referencia.append(tmp)

#convierte el request xml a float
def request_to_cambioDia(xml):
    tree = et.fromstring(xml)

    namespaces ={
        'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
        'a' : 'http://www.banguat.gob.gt/variables/ws/'
    }

    ignoreTxt = '''{http://www.banguat.gob.gt/variables/ws/}'''
    tmp = float(0)
    for el in tree.findall(
    './soap:Body'
    '/a:VariablesResponse'
    '/a:VariablesResult'
    '/a:CambioDia'
    '/a:Var',
    namespaces=namespaces
    ):  
        contador = 0
        for ch in list(el):
            if contador == 2: 
                tmp =  float(ch.text) 
                break
            contador += 1
    return tmp

#request http que obtiene valor de referncia del dolar
def getValorReferencia():
    valor_referencia.clear()
    header = {
        'Content-Type':'text/xml;charset=utf-8',
        'Content-Length':'length',
        'SOAPAction': '"http://www.banguat.gob.gt/variables/ws/Variables"'
        }
    body = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <Variables xmlns="http://www.banguat.gob.gt/variables/ws/">
      <variable>2</variable>
    </Variables>
  </soap:Body>
</soap:Envelope>"""
    r = requests.post("https://www.banguat.gob.gt/variables/ws/TipoCambio.asmx?op=Variables", headers=header, data=body)
    request_to_referencia(r.text)
    print(valor_referencia)

#request http que obtiene listado de catalogos del tipo de cambio 
def getVariables():
    catalogos.clear()
    valores_validos.clear()
    titulos_conversion.clear()
    header = {
        'Content-Type':'text/xml;charset=utf-8',
        'Content-Length':'length',
        'SOAPAction': '"http://www.banguat.gob.gt/variables/ws/VariablesDisponibles"'
        }
    body = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <VariablesDisponibles xmlns="http://www.banguat.gob.gt/variables/ws/" />
  </soap:Body>
</soap:Envelope>"""
    r = requests.post("https://www.banguat.gob.gt/variables/ws/TipoCambio.asmx?op=VariablesDisponibles", headers=header, data=body)
    request_to_Catalogo(r.text)

#request http que ontiene el cambio al día de la opcion seleccionada
def getCambioDia(variable):
    header = {
        'Content-Type':'text/xml;charset=utf-8',
        'Content-Length':'length',
        'SOAPAction': '"http://www.banguat.gob.gt/variables/ws/Variables"'
        }
    body = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <Variables xmlns="http://www.banguat.gob.gt/variables/ws/">
      <variable>"""+ variable +"""</variable>
    </Variables>
  </soap:Body>
</soap:Envelope>"""
    r = requests.post("https://www.banguat.gob.gt/variables/ws/TipoCambio.asmx?op=Variables", headers=header, data=body)
    return request_to_cambioDia(r.text)

#imprime menu de conversion
def printMenuConversion(opcion_seleccioanada):
    texto = ''
    if opcion_seleccioanada == '1':
        texto = "de Quetzales a..."
        tipo_conversion.append('Quetzales')
    elif opcion_seleccioanada == '2':
        texto = 'de Dólares EE.UU a..'
        tipo_conversion.append('Dólares EE.UU')

    os.system("clear")
    print("******** PROGRAMA CONVERSOR DE MONEDAS ********")
    print("Menu de conversiones de " + texto + ": ")
    for catalogo in catalogos:
        if opcion_seleccioanada == '1' and catalogo.valor == '1':
            continue
    
        if(opcion_seleccioanada == '2' and catalogo.valor == '2'):
            continue

        print(catalogo.valor + ": " + catalogo.nombre)

    print("0. Regresar ")
    opcion_seleccionada = input("Ingrese el tipo de conversión a realizar: ")
    seleccionMenuConversion(opcion_seleccionada)

#seleccion de opcion del menu de converciones
def seleccionMenuConversion(opcion_seleccionada):
    if (opcion_seleccionada == '1' and tipo_conversion[0] == '1') or (opcion_seleccionada == '2' and tipo_conversion[0] == '2'):
        os.system("clear")
        print("Seleccione una opción valida")
        pausa()
        printMenuConversion(opcion_seleccionada)
        
    if opcion_seleccionada=='0':
       printMenuPrincipal()
    elif opcion_seleccionada in valores_validos:
        res = getCambioDia(opcion_seleccionada)
        conversion(res, opcion_seleccionada)
    else:
        os.system("clear")
        print("Seleccione una opción valida")
        pausa()
        printMenuConversion(opcion_seleccionada)

#imprime menu procipal del programa
def printMenuPrincipal():
    tipo_conversion.clear()
    os.system("clear")
    print("******** PROGRAMA CONVERSOR DE MONEDAS ********")

    print("Menu de opciones: ")
    print("1. Conversión de Quetzales a... ")
    print("2. Conversión de Dolares a... ")
    print("0. Salir del programa")
    opcion_seleccioanada = input("Ingrese una Opción: ")
    seleccionMenuPrincipal(opcion_seleccioanada)

#seleccion de opcion del menu principal
def seleccionMenuPrincipal(opcion_seleccioanada):
    tipo_conversion.append(opcion_seleccioanada)
    if(opcion_seleccioanada=='1' or opcion_seleccioanada == '2'):
        getValorReferencia()
        printMenuConversion(opcion_seleccioanada)
    elif(opcion_seleccioanada == '0'):
        os.system("clear")
        print("Adios!")
        pausa()
        exit()
    else:
        os.system("clear")
        print("Seleccione una opción valida")
        pausa()
        printMenuPrincipal()

def conversion(tipoCambioRef, opcion_seleccionada):
    os.system("clear")
    index = valores_validos.index(opcion_seleccionada)
    print("***** Conversión de " + tipo_conversion[1] + " a " + titulos_conversion[index] + " *******")
    valor = input("Ingrese cantidad a convertir: ")
    resultado = 0.0

    if tipo_conversion[0] == '1':
        if opcion_seleccionada == '2':
            resultado = float(valor) / valor_referencia[0] 
        else:
            resultado = (float(valor) / valor_referencia[0]) * tipoCambioRef

    elif tipo_conversion[0] == '2':

        if opcion_seleccionada == '1':
            resultado = valor_referencia[0] * float(valor)
        else:
            resultado = tipoCambioRef * float(valor)

    print("La conversión es: " + str(round(resultado,2)))
    pausa()
    printMenuConversion(opcion_seleccionada)

#init program
def run():
    getVariables()
    printMenuPrincipal()

if __name__ == "__main__":
    run()