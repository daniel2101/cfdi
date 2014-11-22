# -*- encoding: utf-8 -*-
###########################################################################
#    
#    Desarrollado por rNet Soluciones
#    Jefe de Proyecto: Linf. Ulises Tlatoani Vidal Rieder
#    Desarrollador: Ing. Salvador Daniel Pelayo Gòmez
#    Desarrollador: Carlos David Padilla Bobadilla
#
############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import urllib
import base64 as B64
from xml.dom import minidom
import time
from datetime import datetime
from pytz import timezone
import tempfile
import os
import lxml.etree as ET
import tools
import subprocess as SB
import shlex as SH
import hashlib
from SOAPpy import SOAPProxy

ERROR = ""
app_xsltproc = tools.find_in_path("xsltproc")

class cfdi_account_invoice(osv.osv):

    def check_timbres(self, cr, uid, ids, partner_id, context={}):
        invoice = self.browse(cr,uid,ids)
        inv = invoice[0]
        timbres_c = inv.id_cfdi_rnet.timbres_comprados
        timbres_u = inv.id_cfdi_rnet.timbres_usados
        aviso = "El Número de timbres comprados es: %s\nEl Número de timbres usados es: %s\nUsted tiene: %s timbres disponibles.\n" % (timbres_c, timbres_u, timbres_c - timbres_u)
        raise osv.except_osv("Aviso!", aviso)
<<<<<<< HEAD
        
    def soporte_tecnico(self, cr, uid, ids, partner_id, context={}):
        invoice = self.browse(cr,uid,ids)
        inv = invoice[0]
<<<<<<< HEAD
        raise osv.except_osv("Contacto!", "Si tiene algún problema con el sistema por favor contactenos al correo: atencion@rnet.mx\nTelefonos: 01800 015 7477 | (443) 209 0726 y 340 0599\nVisite nuestra página: www.rnet.mx")
=======
        raise osv.except_osv("Contacto!", "Si tiene algún problema con el sistema por favor contactenos al correo: atencio@rnet.mx\nTelefonos: 01800 015 7477 | (443) 209 0726 y 340 0599\nVisite nuestra página: www.rnet.mx")
=======
>>>>>>> origin/master
>>>>>>> parent of eca01e2... Versión 1.4

    def timbrar(self, cr, uid, ids, partner_id, context={}):
        global ERROR
        invoice = self.browse(cr,uid,ids)
        inv = invoice[0]
        timbres = inv.id_cfdi_rnet.timbres_comprados - inv.id_cfdi_rnet.timbres_usados
        if timbres < 1:
            aviso = ("Timbres comprados: %s, Timbres usados: %s\n%s") % (inv.id_cfdi_rnet.timbres_comprados, inv.id_cfdi_rnet.timbres_usados, inv.id_cfdi_rnet.aviso)
            raise osv.except_osv("AVISO",aviso)
        user = inv.id_cfdi_rnet.pac_usuario
        pw = inv.id_cfdi_rnet.pac_password
        if not user or not pw:
            raise osv.except_osv("AVISO","No se encuentran configurados los datos del PAC, no es posible timbrar!")
        xml = self.genera_xml(cr,uid,ids,partner_id)
        xml = xml.toxml(encoding='utf-8')
<<<<<<< HEAD
        a = SOAPProxy("https://generacfdi.com.mx/rvltimbrado/service1.asmx")
=======
        a = SOAPProxy("https://ws2.bovedacomprobante.net/ws/service.asmx")
>>>>>>> origin/master
        if ERROR not in ("", "--"):
            error = ERROR
            ERROR = "--"
            raise osv.except_osv(("ERROR!"),("Se encontraron los siguientes errores:\n%s")%(error))
        env = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Header><AuthSoapHd xmlns="http://tempuri.org/"><strUserName>'+user.encode('utf-8')+'</strUserName><strPassword>'+pw.encode('utf-8')+'</strPassword></AuthSoapHd></soap:Header><soap:Body><GetTicket xmlns="http://tempuri.org/"><base64Cfd>'+B64.encodestring(xml)+'</base64Cfd></GetTicket></soap:Body></soap:Envelope>'
        ns = None
        sa = "http://tempuri.org/GetTicket" #soap action
        r, a.namespace = a.transport.call(a.proxy, env, ns, sa, encoding = 'utf-8', http_proxy = a.http_proxy, config = a.config)
        xml_respuesta = minidom.parseString(r)
        estado = xml_respuesta.getElementsByTagName("state")[0].firstChild.data
        descripcion = xml_respuesta.getElementsByTagName("Descripcion")[0].firstChild.data
        if estado not in ["0"]:
            ERROR = ERROR + "Estado: "+estado.encode('utf-8')+" Descripción: "+descripcion.encode('utf-8')
            error = ERROR
            ERROR = "--"
            raise osv.except_osv(("ERROR AL TIMBRAR"),("Se encontraron los siguientes errores al realizar el timbrado:\n%s\n")%(error))
        else:
            try:
                cfdi_base64 = xml_respuesta.getElementsByTagName("Cfdi")[0].firstChild.data #Para guardar como adjunto
            except:
                ERROR = ERROR + "Estado: "+estado.encode('utf-8')+" Descripción: "+descripcion.encode('utf-8')
                error = ERROR
                ERROR = "--"
                raise osv.except_osv(("ERROR AL TIMBRAR"),("Se encontraron los siguientes errores al realizar el timbrado:\n%s\n")%(error))
            data_attach = {
                    'name': inv.number+'.xml',
                    'datas': cfdi_base64,
                    'datas_fname': inv.number+'.xml',
                    'description': 'Factura-E XML',
                    'res_model': self._name,
                    'res_id': inv.id,
            }
            self.pool.get('ir.attachment').create(cr, uid, data_attach, context=context)
            cfdi_xml = minidom.parseString(B64.decodestring(cfdi_base64))
            fecha = cfdi_xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('fecha')
            xml_timbre = cfdi_xml.getElementsByTagName("tfd:TimbreFiscalDigital")[0]
            version = xml_timbre.getAttribute('version')
            UUID = xml_timbre.getAttribute('UUID')
            selloCFDI = xml_timbre.getAttribute('selloCFD')
            fechaTimbrado = xml_timbre.getAttribute('FechaTimbrado')
            selloSAT = xml_timbre.getAttribute('selloSAT')
            noCertificadoSAT = xml_timbre.getAttribute('noCertificadoSAT')
            cfdi_lugarExpedicion = cfdi_xml.getElementsByTagName('cfdi:Comprobante')[0].getAttribute('LugarExpedicion')
            cfdi_cadena_original = '||%s|%s|%s|%s|%s||'%(version,UUID,fechaTimbrado,selloCFDI,noCertificadoSAT)
            re = xml_respuesta.getElementsByTagName("RfcEmisor")[0].firstChild.data
            rr = xml_respuesta.getElementsByTagName("RfcReceptor")[0].firstChild.data
            total_operacion = xml_respuesta.getElementsByTagName("MontoOperacion")[0].firstChild.data.split(".")
            entero = total_operacion[0]
            decimal = total_operacion[1]
            for i in range(10-len(entero)):
                entero = '0' + entero
            for i in range(6-len(decimal)):
                decimal = decimal + '0'
            tt = entero+'.'+decimal
            selloCFDI = self.agregarEspacios(selloCFDI, 62)
            selloSAT = self.agregarEspacios(selloSAT, 62)
            cfdi_cadena_original = self.agregarEspacios(cfdi_cadena_original, 62)
            mensaje = '?re=%s&rr=%s&tt=%s&id=%s' % (re,rr,tt,UUID)
            cbb = self.obtener_cbb(mensaje)
            data = {
                'cfdi_fecha': fecha,
                'selloCFDI': selloCFDI,
                'fechaTimbrado': fechaTimbrado,
                'UUID': UUID,
                'selloSAT': selloSAT,
                'noCertificadoSAT': noCertificadoSAT,
                'cfdi_cadena_original': cfdi_cadena_original,
                'state': 'timbrada',
                'cbb': cbb,
                'cfdi_lugarExpedicion': cfdi_lugarExpedicion,
                }
            self.write(cr, uid, ids, data, context)
            vals = {
                'timbres_usados': inv.id_cfdi_rnet.timbres_usados +1,
            }
            return inv.id_cfdi_rnet.write(vals)
        
    def agregarEspacios(self, cadena, caracteres):
        data = ""
        for i in range(len(cadena)):
            data = data + cadena[i]
            if i%(caracteres-1) == 0:
                if i>(caracteres-5):
                    data = data + ' '
        return data
    
    def cancelar(self, cr, uid, ids, partner_id):
        invoice = self.browse(cr,uid,ids)[0]
        # 1.- XML DE CANCELACION
        mexico = timezone('America/Mexico_City')
        sa_time = datetime.now(mexico)
        fecha = sa_time.strftime('%Y-%m-%dT%H:%M:%S')
        xml_cancelacion = '<Cancelacion xmlns="http://cancelacfd.sat.gob.mx" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Fecha="%s" RfcEmisor="%s"><Folios><UUID>%s</UUID></Folios></Cancelacion>' % (fecha, invoice.company_id.partner_id.vat, invoice.UUID.upper())
        # 2.- SHA1
        m = hashlib.sha1()
        m.update(xml_cancelacion)
        # 3.- Codificar base64 hash
        DigestValue = B64.encodestring(m.digest())
        # 4.- XML SignedInfo
        xml_signedInfo = '<SignedInfo xmlns="http://www.w3.org/2000/09/xmldsig#" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></CanonicalizationMethod><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></SignatureMethod><Reference URI=""><Transforms><Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></Transform></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></DigestMethod><DigestValue>%s</DigestValue></Reference></SignedInfo>' % DigestValue
        # 5.- Firmar con Private Key en SHA1
        (filepem, pem_file) = tempfile.mkstemp(".pem","key")
        (filesalida, signedInfo_file) = tempfile.mkstemp(".xml","signed")
        pem = "%s" % (B64.decodestring(invoice.id_cfdi_rnet.certificado_key_pem),)
        f = open(pem_file, 'wb' )
        f.write(pem)
        f.close()
        os.close(filepem)
        f2 = open(signedInfo_file, 'wb')
        f2.write(xml_signedInfo.replace("\n",""))
        f2.close()
        os.close(filesalida)
        cmd = 'openssl dgst -sha1 -sign %s %s' % (pem_file, signedInfo_file)
        args = SH.split(cmd)
        a = SB.check_output(args)
        firma = B64.encodestring(a)
        # 6.- Extraer datos del certificado
        certificate_lib = self.pool.get('facturae.certificate.library')
        certificado = invoice.id_cfdi_rnet.certificado_pem
        fname_cer_der = certificate_lib.b64str_to_tempfile(certificado, file_suffix='.der.cer', file_prefix='openerp__' + (False or '') + '__ssl__', )
        serial = "%s" % int(certificate_lib._get_params(fname_cer_der, params=['serial'], type="PEM").replace("serial=","").replace(" ",""),16)
        name = certificate_lib._get_params(fname_cer_der, params=['issuer'], type="PEM").replace("issuer= ","")
        # 7.- Crear XML Final
        signature = '<Signature xmlns="http://www.w3.org/2000/09/xmldsig#">'+xml_signedInfo+'<SignatureValue>'+firma+'</SignatureValue>'
        keyInfo = '<KeyInfo><X509Data><X509IssuerSerial><X509IssuerName>'+name+'</X509IssuerName><X509SerialNumber>'+serial+'</X509SerialNumber></X509IssuerSerial><X509Certificate>'+B64.decodestring(certificado).replace("-----BEGIN CERTIFICATE-----","").replace("-----END CERTIFICATE-----","")+'</X509Certificate></X509Data></KeyInfo></Signature>'
        xml_final = '<?xml version="1.0" encoding="UTF-8"?>'+xml_cancelacion.replace("</Cancelacion>", "")+signature+keyInfo+"</Cancelacion>"
        xml_final = self.cambiar_caracteres(xml_final.replace("\n",""))
        # 8.- Solicitar cancelacion al PAC
        user = invoice.id_cfdi_rnet.pac_usuario
        pw = invoice.id_cfdi_rnet.pac_password
        if not user or not pw:
            raise osv.except_osv("AVISO","No se encuentran configurados los datos del PAC, no es posible cancelar!")
<<<<<<< HEAD
        a = SOAPProxy("https://generacfdi.com.mx/rvltimbrado/service1.asmx")
        env = '<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Header><AuthSoapHd xmlns="http://tempuri.org/"><strUserName>'+user+'</strUserName><strPassword>'+pw+'</strPassword></AuthSoapHd></soap:Header><soap:Body><CancelTicket xmlns="http://tempuri.org/"><base64Cfd>'+B64.encodestring(xml_final)+'</base64Cfd></CancelTicket></soap:Body></soap:Envelope>'
        ns = None
        sa = "http://tempuri.org/CancelTicket" #soap action
=======
        a = SOAPProxy("https://ws2.bovedacomprobante.net/ws/service.asmx")
        env = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Header><AuthSoapHd xmlns="http://tempuri.org/"><strUserName>'+user+'</strUserName><strPassword>'+pw+'</strPassword></AuthSoapHd></soap:Header><soap:Body><CancelTicketExtended xmlns="http://tempuri.org/"><base64Cfd>'+B64.encodestring(xml_final)+'</base64Cfd></CancelTicketExtended></soap:Body></soap:Envelope>'
        ns = None
        sa = "http://tempuri.org/CancelTicketExtended" #soap action
>>>>>>> origin/master
        r, a.namespace = a.transport.call(a.proxy, env, ns, sa, encoding = 'utf-8', http_proxy = a.http_proxy, config = a.config)
        xml_respuesta = minidom.parseString(r)
        # 9.- Validar la respuesta del PAC
        estado = xml_respuesta.getElementsByTagName("state")[0].firstChild.data
<<<<<<< HEAD
        if estado not in ("201", "202"):
            descripcion = xml_respuesta.getElementsByTagName("Descripcion")[0].firstChild.data
            raise osv.except_osv("Aviso", "Estado: %s\nDescripción: %s\n" % (estado, descripcion))
=======
        descripcion = xml_respuesta.getElementsByTagName("Descripcion")[0].firstChild.data
        if estado not in ("201"):
            raise osv.except_osv("Aviso", descripcion)
>>>>>>> origin/master
        # 10.- Cambiar estado a cancelado y escribir xml de cancelacion
        data_attach = {
                    'name': 'Cancelada_'+invoice.number+'.xml',
                    'datas': B64.encodestring(xml_final),
                    'datas_fname': 'Cancelada_'+invoice.number+'.xml',
                    'description': 'Factura-E Cancelada XML',
                    'res_model': self._name,
                    'res_id': invoice.id,
        }
        self.pool.get('ir.attachment').create(cr, uid, data_attach, context=context)
        data_attach = {
                    'name': 'Cancelada_PAC_'+invoice.number+'.xml',
                    'datas': B64.encodestring(r),
                    'datas_fname': 'Cancelada_PAC_'+invoice.number+'.xml',
                    'description': 'Factura-E Cancelada PAC XML',
                    'res_model': self._name,
                    'res_id': invoice.id,
        }
        self.pool.get('ir.attachment').create(cr, uid, data_attach, context=context)
        data = {
            'fechaCancelacion': xml_respuesta.getElementsByTagName("Fecha")[0].firstChild.data,
            'state': 'cancelada',
        }
        vals = {
                'timbres_usados': invoice.id_cfdi_rnet.timbres_usados +1,
        }
        invoice.id_cfdi_rnet.write(vals)
        return self.write(cr, uid, ids, data, context)
        
    def cambiar_caracteres(self, string):
        string = string.encode('utf8')
        resultado = string.replace("\\xc3\\x81", "Á").replace("\\xc3\\x89", "É").replace("\\xc3\\x8d", "Í").replace("\\xc3\\x93", "Ó").replace("\\xc3\\x9a", "Ú").replace("\\xc3\\xa1", "á").replace("\\xc3\\xa9","é").replace("\\xc3\\xad","í").replace("\\xc3\\xb3","ó").replace("\\xc3\\xba","ú").replace("\\xc3\\x91", "Ñ").replace("\\xc3\\xb1","ñ")
        resultado = resultado.replace("\\xC3\\x81", "Á").replace("\\xC3\\x89", "É").replace("\\xC3\\x8D", "Í").replace("\\xC3\\x93", "Ó").replace("\\xC3\\x9A", "Ú").replace("\\xC3\\xA1", "á").replace("\\xC3\\xA9","é").replace("\\xC3\\xAD","í").replace("\\xC3\\xB3","ó").replace("\\xC3\\xBA","ú").replace("\\xC3\\x91", "Ñ").replace("\\xC3\\xB1","ñ")
        return resultado

    def genera_xml(self, cr, uid, ids, partner_id):
        global ERROR
        doc = minidom.Document()
        comprobante = doc.createElement("cfdi:Comprobante")
        invoice = self.browse(cr,uid,ids)
        inv = invoice[0]
        #comprobante
        subTotal = "%.4f" % (inv.amount_untaxed)
        total = "%.4f" % (inv.amount_total)
        moneda = inv.currency_id.name
        certificado = "%s" % (B64.decodestring(inv.id_cfdi_rnet.certificado_pem),)
        certificado = certificado.replace("-----BEGIN CERTIFICATE-----","").replace("-----END CERTIFICATE-----","")
        certificado = certificado.replace("\n","").replace(" ","")
        no_certificado = inv.id_cfdi_rnet.numero_serie
        tipoComprobante = inv.tipoComprobante
        formaDePago =  inv.cfdi_forma_pago.name
        metodoDePago = inv.cfdi_metodo_pago.name
        sello="" #sello
        mexico = timezone('America/Mexico_City')
        sa_time = datetime.now(mexico)
        fecha = sa_time.strftime('%Y-%m-%dT%H:%M:%S')
        numero_factura = inv.number.split("-")
        NumCtaPago = inv.cfdi_cuatro_digitos
        sf = True
        try:
            serie = numero_factura[0]
            folio = numero_factura[1]
        except:
            sf = False
        LugarExpedicion = ("%s, %s") % (inv.company_id.city,inv.company_id.state_id.name)
        comprobante.setAttribute('xmlns:cfdi','http://www.sat.gob.mx/cfd/3')
        comprobante.setAttribute('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
        comprobante.setAttribute('xsi:schemaLocation','http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd')
        comprobante.setAttribute('version','3.2')
        if sf:
            comprobante.setAttribute('serie',serie)
            comprobante.setAttribute('folio',folio)
        if moneda not in (''):
            comprobante.setAttribute('Moneda',moneda)
        comprobante.setAttribute('formaDePago',formaDePago)
        comprobante.setAttribute('metodoDePago', metodoDePago)
        comprobante.setAttribute('tipoDeComprobante',tipoComprobante)
        comprobante.setAttribute('subTotal',subTotal)
        comprobante.setAttribute('total', total)
        comprobante.setAttribute('noCertificado', no_certificado)
        comprobante.setAttribute('certificado', certificado)
        comprobante.setAttribute('sello','')
        comprobante.setAttribute('fecha',fecha)
        comprobante.setAttribute('LugarExpedicion', LugarExpedicion)
        if NumCtaPago and NumCtaPago not in (''):
            comprobante.setAttribute('NumCtaPago',NumCtaPago)
        doc.appendChild(comprobante)
        #fin comprobante
        #emisor
        emisor = doc.createElement("cfdi:Emisor")
        emisor_rfc = inv.company_id.partner_id.vat
        emisor_nombre = inv.company_id.partner_id.name
        emisor.setAttribute('rfc', emisor_rfc)
        emisor.setAttribute('nombre', emisor_nombre)
            #DomicilioFiscal
        emisor_df = doc.createElement("cfdi:DomicilioFiscal")
        emisor_address = self.pool.get('res.partner.address').browse(cr,uid,inv.company_id.partner_id.id)
        emisor_calle = emisor_address.street
        emisor_noExterior = emisor_address.street3
        emisor_noInterior = emisor_address.street4
        emisor_colonia = emisor_address.street2
        emisor_localidad = emisor_address.city2
        emisor_municipio = emisor_address.city
        emisor_estado = emisor_address.state_id.name
        emisor_pais = emisor_address.country_id.name
        emisor_cp = emisor_address.zip
        emisor_df.setAttribute('calle', emisor_calle)
        emisor_df.setAttribute('noExterior', emisor_noExterior)
        if emisor_noInterior:
            emisor_df.setAttribute('noInterior', emisor_noInterior)
        emisor_df.setAttribute('colonia', emisor_colonia)
        if emisor_localidad and emisor_localidad not in (""):
            emisor_df.setAttribute('localidad', emisor_localidad)
        emisor_df.setAttribute('municipio', emisor_municipio)
        emisor_df.setAttribute('estado', emisor_estado)
        emisor_df.setAttribute('pais', emisor_pais)
        emisor_df.setAttribute('codigoPostal', emisor_cp)
        emisor.appendChild(emisor_df)
            #RegimenFiscal
        emisor_rf = doc.createElement("cfdi:RegimenFiscal")
        regimen = inv.cfdi_regimen_fiscal.name or inv.company_id.regimen_fiscal.name
        emisor_rf.setAttribute('Regimen', regimen)
        emisor.appendChild(emisor_rf)
        comprobante.appendChild(emisor)
        #fin emisor
        #receptor
        receptor = doc.createElement("cfdi:Receptor")
        receptor_rfc = inv.address_invoice_id.partner_id.vat
        receptor_nombre = inv.address_invoice_id.partner_id.name
        receptor.setAttribute('rfc',receptor_rfc)
        receptor.setAttribute('nombre',receptor_nombre)
            #Domicilio
        receptor_domicilio = doc.createElement("cfdi:Domicilio")
        receptor_calle = inv.address_invoice_id.street
        receptor_noExterior = inv.address_invoice_id.street3
        receptor_noInterior = inv.address_invoice_id.street4
        receptor_colonia = inv.address_invoice_id.street2
        receptor_localidad = inv.address_invoice_id.city2
        receptor_municipio = inv.address_invoice_id.city
        receptor_estado = inv.address_invoice_id.state_id.name
        receptor_pais = inv.address_invoice_id.country_id.name
        receptor_cp = inv.address_invoice_id.zip
        receptor_domicilio.setAttribute('calle',receptor_calle)
        receptor_domicilio.setAttribute('noExterior',receptor_noExterior)
        if receptor_noInterior:
            receptor_domicilio.setAttribute('noInterior',receptor_noInterior)
        receptor_domicilio.setAttribute('colonia',receptor_colonia)
        if receptor_localidad and receptor_localidad not in (""):
            receptor_domicilio.setAttribute('localidad',receptor_localidad)
        receptor_domicilio.setAttribute('municipio',receptor_municipio)
        receptor_domicilio.setAttribute('estado',receptor_estado)
        receptor_domicilio.setAttribute('pais',receptor_pais)
        receptor_domicilio.setAttribute('codigoPostal',receptor_cp)
        receptor.appendChild(receptor_domicilio)
        comprobante.appendChild(receptor)
        #fin receptor
        #Conceptos
        conceptos = doc.createElement("cfdi:Conceptos")
        for concepto in inv.invoice_line:
            concepto_xml = doc.createElement("cfdi:Concepto")
            importe = "%.4f" % concepto.price_subtotal
            valorUnitario = "%.4f" % concepto.price_unit
            descripcion = concepto.name
            noIdentificacion = concepto.product_id.default_code or ''
            unidad = concepto.uos_id.name or 'No Aplica'
            cantidad = "%.4f" % concepto.quantity
            concepto_xml.setAttribute('cantidad',cantidad)
            concepto_xml.setAttribute('unidad', unidad)
            if noIdentificacion not in (''):
                concepto_xml.setAttribute('noIdentificacion',noIdentificacion)
            concepto_xml.setAttribute('descripcion',descripcion)
            concepto_xml.setAttribute('valorUnitario',valorUnitario)
            concepto_xml.setAttribute('importe', importe)
            conceptos.appendChild(concepto_xml)
        comprobante.appendChild(conceptos)
        #fin Conceptos
        #impuestos
        impuestos_xml = doc.createElement("cfdi:Impuestos")
            #traslados
        traslados = doc.createElement("cfdi:Traslados")
            #retenciones
        retenciones = doc.createElement("cfdi:Retenciones")
        total_retenciones = 0
        total_impuestos = 0
        for impuestos in inv.tax_line:
            if "RETENCION" in impuestos.name:
                retencion_xml = doc.createElement("cfdi:Retencion")
                retencion = impuestos.name.replace("RETENCION_","").replace("RETENCION ","")
                total_retenciones = total_retenciones + abs(impuestos.amount)
                importe = "%.4f" % abs(impuestos.amount)
                retencion_xml.setAttribute('impuesto',retencion)
                retencion_xml.setAttribute('importe',importe)
                retenciones.appendChild(retencion_xml)
            else:
                traslado_xml = doc.createElement("cfdi:Traslado")
                if "TASA 0" in impuestos.name:
                    impuesto = impuestos.name.replace(" TASA 0","")
                else: 
                    impuesto = impuestos.name
                base = impuestos.base
                total_impuestos = total_impuestos + impuestos.amount
                importe = "%.4f" % impuestos.amount
                tasa = "%.2f" % (impuestos.tax_amount/impuestos.base_amount*100)
                traslado_xml.setAttribute('impuesto', impuesto)
                traslado_xml.setAttribute('tasa', tasa)
                traslado_xml.setAttribute('importe', importe)
                traslados.appendChild(traslado_xml)
        total_retenciones = "%.4f" % total_retenciones
        total_impuestos = "%.4f" % total_impuestos
        impuestos_xml.setAttribute("totalImpuestosRetenidos", total_retenciones)
        impuestos_xml.setAttribute("totalImpuestosTrasladados", total_impuestos)
        if total_retenciones not in ('0.0000'):
            impuestos_xml.appendChild(retenciones)
        impuestos_xml.appendChild(traslados)
        comprobante.appendChild(impuestos_xml)
        try:
            (filexml, xml_file) = tempfile.mkstemp(".xml","factura")
            (filepem, pem_file) = tempfile.mkstemp(".pem","key")
            (filesalida, salida) = tempfile.mkstemp(".xml","salida")
        except:
            ERROR = ERROR + "No se pudieron cargar los archivos para generar la cadena original.\n"
            error = ERROR
            ERROR = "--"
            raise osv.except_osv("ERROR",error)
        cadena_original = ""
        f = open(xml_file, 'wb' )
        f.write(doc.toxml(encoding='utf-8'))
        f.close()
        os.close(filexml)
        pem = "%s" % (B64.decodestring(inv.id_cfdi_rnet.certificado_key_pem),)
        f = open(pem_file, 'wb' )
        f.write(pem)
        f.close()
        os.close(filepem)
        cmd = 'xsltproc -o %s %s %s' % (salida, "/opt/openerp/server/openerp/addons/cfdi_rnet/cadena_original_3.2.xslt", xml_file)
        args = SH.split(cmd)
        a = SB.call(args)
        cadena_original = self.leer_archivo(open(salida,"r"))
        f = open(salida, 'wb')
        f.write(cadena_original.replace("  "," "))
        f.close()
        os.close(filesalida)
        if cadena_original in (""):
            ERROR = ERROR + "No se pudo generar la cadena original_IF.\n"
        sello=""
        cmd = 'openssl dgst -sha1 -sign %s %s' % (pem_file, salida)
        args = SH.split(cmd)
        a = SB.check_output(args)
        sello = B64.encodestring(a)
        comprobante.setAttribute('sello', sello.replace("\n",""))
        return doc
        
    def leer_archivo(self, file_obj):
        seconds_delay=0.5
        max_attempt=12
        fdata = False
        cont = 1
        while True:
            time.sleep( seconds_delay )
            try:
                fdata = file_obj.read()
            except:
                pass
            if fdata or max_attempt < cont:
                break
            cont += 1
        return fdata.replace("\n","").replace("    ","").replace("||  ","||")
        
    def obtener_cbb(self, mensaje):
        global ERROR
        url = "http://chart.apis.google.com/chart?chs=200x200&cht=qr&chld=H&choe=UTF-8&chl="
        if not mensaje:
            ERROR = ERROR + "No se encontro la información para crear el CBB\n"
            return False
        mensaje = mensaje.replace("%","%25").replace(" ","%20").replace("&","%26")
        try:
            imagen = urllib.urlopen(url+mensaje).read()
            data = B64.encodestring(imagen)
        except:
            ERROR = ERROR + "No se pudo descargar la imagen CBB\n"
            return False
        return data

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,date_invoice=False, payment_term=False, partner_bank_id=False,company_id=False):
        res1 = {}
        invoice_addr_id = False
        contact_addr_id = False
        partner_payment_term = False
        acc_id = False
        bank_id = False
        fiscal_position = False

        opt = [('uid', str(uid))]
        if partner_id:

            opt.insert(0, ('id', partner_id))
            res = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact', 'invoice'])
            contact_addr_id = res['contact']
            invoice_addr_id = res['invoice']
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if company_id:
                if p.property_account_receivable.company_id.id != company_id and p.property_account_payable.company_id.id != company_id:
                    property_obj = self.pool.get('ir.property')
                    rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = property_obj.read(cr,uid,rec_pro_id,['name','value_reference','res_id'])
                    pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
                    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not rec_res_id and not pay_res_id:
                        raise osv.except_osv(_('Configuration Error !'),
                            _('Can not find a chart of accounts for this company, you should create one.'))
                    account_obj = self.pool.get('account.account')
                    rec_obj_acc = account_obj.browse(cr, uid, [rec_res_id])
                    pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
                    p.property_account_receivable = rec_obj_acc[0]
                    p.property_account_payable = pay_obj_acc[0]

            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
            else:
                acc_id = p.property_account_payable.id
            fiscal_position = p.property_account_position and p.property_account_position.id or False
            partner_payment_term = p.property_payment_term and p.property_payment_term.id or False
            if p.bank_ids:
                bank_id = p.bank_ids[0].id

        result = {'value': {
            'address_contact_id': contact_addr_id,
            'address_invoice_id': invoice_addr_id,
            'account_id': acc_id,
            'payment_term': partner_payment_term,
            'fiscal_position': fiscal_position
            }
        }

        if type in ('in_invoice', 'in_refund'):
            result['value']['partner_bank_id'] = bank_id

        if payment_term != partner_payment_term:
            if partner_payment_term:
                to_update = self.onchange_payment_term_date_invoice(
                    cr, uid, ids, partner_payment_term, date_invoice)
                result['value'].update(to_update['value'])
            else:
                result['value']['date_due'] = False

        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(cr, uid, ids, bank_id)
            result['value'].update(to_update['value'])
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        compania = self.pool.get('res.company').browse(cr,uid,company_id)
        res1['id_cfdi_rnet'] = compania['cfdi'].id
        res1['cfdi_regimen_fiscal'] = compania['regimen_fiscal'].id
        res1['cfdi_forma_pago'] = partner['cfdi_forma_pago'].id
        res1['cfdi_metodo_pago'] = partner['cfdi_metodo_pago'].id
        cuentas = partner['bank_ids']
        digitos = ''
        if cuentas:
            digitos = cuentas[0].last_acc_number
        res1['cfdi_cuatro_digitos'] = digitos or '0000'
        result['value'].update(res1)
        return result
        
    def get_cfdi(self, cr, uid, ids, context=None):
        id_cmp = self.pool.get('res.company').search(cr,uid,[])
        compania = self.pool.get('res.company').browse(cr,uid,id_cmp[0])
        return compania['cfdi'].id

    def get_regimen_fiscal(self, cr, uid, ids, context=None):
        id_cmp = self.pool.get('res.company').search(cr, uid, [])
        compania = self.pool.get('res.company').browse(cr, uid, id_cmp[0])
        return compania['regimen_fiscal'].id
        
    def get_forma_pago(self, cr, uid, ids, context=None):
        fp = self.pool.get("cfdi.forma.pago").search(cr, uid, [('name','=', 'UNA SOLA EXHIBICIÓN')])
        if len(fp)>0:
            return fp[0]
        return False
        
    def get_metodo_pago(self, cr, uid, ids, context=None):
        mp = self.pool.get("cfdi.metodo.pago").search(cr, uid, [('name','=', 'NO IDENTIFICADO')])
        if len(mp)>0:
            return mp[0]
        return False
<<<<<<< HEAD
        
    #Funcion para obtener valores del XML
    
    def obtener_validacion(self, cr, uid, ids, context=None):
        for id in ids:
            try:
                self.validar_linea(cr, uid, id, context)
            except:
                ""
        return True
        
    def validar_linea(self, cr, uid, id, context=None):
        #Generar XML
        adjuntos = self.pool.get('ir.attachment')
        id_adjunto = adjuntos.search(cr, uid, [('res_model', '=', 'account.invoice'), ('res_id', '=', id), ('name','like', '%.xml')])
        archivo = B64.decodestring(adjuntos.browse(cr, uid, id_adjunto)[0].datas)
        xml = minidom.parseString(archivo)
        #Obtener Valores
        comprobante = xml.getElementsByTagName("cfdi:Comprobante")[0]
        if comprobante.getAttribute("serie") in "":
            folio = comprobante.getAttribute("folio")
        else:
            folio = comprobante.getAttribute("serie") + "-" + comprobante.getAttribute("folio")
        total = comprobante.getAttribute("total").split(".")
        entero = total[0]
        decimal = total[1]
        for i in range(10-len(entero)):
            entero = '0' + entero
        for i in range(6-len(decimal)):
            decimal = decimal + '0'
        total = entero+'.'+decimal
        rfcEmisor = xml.getElementsByTagName("cfdi:Emisor")[0].getAttribute("rfc")
        rfcReceptor = xml.getElementsByTagName("cfdi:Receptor")[0].getAttribute("rfc")
        UUID = xml.getElementsByTagName("tfd:TimbreFiscalDigital")[0].getAttribute("UUID")
        consulta = '?re=%s&amp;rr=%s&amp;tt=%s&amp;id=%s' % (rfcEmisor,rfcReceptor,total,UUID)
        #Consulta al servico del SAT
        a = SOAPProxy("https://consultaqr.facturaelectronica.sat.gob.mx/ConsultaCFDIService.svc")
        env = '<?xml version="1.0" encoding="utf-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/"><soapenv:Header/><soapenv:Body><tem:Consulta><tem:expresionImpresa>'+consulta+'</tem:expresionImpresa></tem:Consulta></soapenv:Body></soapenv:Envelope>'
        ns = None
        sa = "http://tempuri.org/IConsultaCFDIService/Consulta" #soap action
        r, a.namespace = a.transport.call(a.proxy, env, ns, sa, encoding = 'utf-8', http_proxy = a.http_proxy, config = a.config)
        xml_respuesta = minidom.parseString(r)
        estatus = xml_respuesta.getElementsByTagName("a:Estado")[0].firstChild.data
        codigoEstatus = xml_respuesta.getElementsByTagName("a:CodigoEstatus")[0].firstChild.data
        #Escribir valores
        mexico = timezone('America/Mexico_City')
        sa_time = datetime.now(mexico)
        fecha = sa_time.strftime('%Y-%m-%d %H:%M:%S')
        vals = {
            'fechaValidacion': fecha,
            'estatus': estatus,
            'codigoEstatus': codigoEstatus,
            'reference': folio,
        }
        return self.write(cr, uid, [id], vals, context)
=======
>>>>>>> origin/master
             
    _inherit = 'account.invoice'
    _columns = {
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('timbrada','Timbrada'),
            ('cancelada', 'Cancelada SAT'),
            ('paid','Paid'),
            ('cancel','Cancelled')
            ],'State', select=True, readonly=True,
            help=' * The \'Draft\' state is used when a user is encoding a new and unconfirmed Invoice. \
            \n* The \'Pro-forma\' when invoice is in Pro-forma state,invoice does not have an invoice number. \
            \n* The \'Open\' state is used when user create invoice,a invoice number is generated.Its in open state till user does not pay invoice. \
            \n* The \'Paid\' state is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
            \n* The \'Cancelled\' state is used when user cancel invoice.'),
        'tipoComprobante': fields.selection([
            ('ingreso','Ingreso'),
            ('egreso','Egreso')
            ], "Tipo de Comprobante", required=True),
        #No de serie del Certificado del CSD
        'id_cfdi_rnet': fields.many2one('cfdi.rnet', "DATOS CFDI"),
        'cfdi_forma_pago': fields.many2one('cfdi.forma.pago',"Forma de Pago"),
        'cfdi_metodo_pago': fields.many2one('cfdi.metodo.pago', "Metodo de Pago"),
        'cfdi_regimen_fiscal': fields.many2one('cfdi.regimen.fiscal', "Regimen Fiscal"),
        'cfdi_cuatro_digitos': fields.char("Ultimos 4 digitos", size=4),
        'cfdi_cadena_original': fields.text("Cadena Original"), #Del complemento de Certificacion
        'cfdi_fecha': fields.char("Fecha de Generación",size=30),
        'cfdi_lugarExpedicion' : fields.text("Lugar de Expedición"),
        #Sello digital CFDI
        'selloCFDI': fields.text("Sello CFDI"),
        'fechaTimbrado': fields.char("Fecha de Timbrado",size=30),
        #Folio Fiscal
        'UUID': fields.text("UUID"), #Folio Fiscal
        #No de serie del Certificado del SAT
        'noCertificadoSAT': fields.text("Certificado SAT"),
        'selloSAT': fields.text("Sello SAT"),
        'cbb': fields.binary("Codigo de Barras"),
        #Fecha de Cancelacion
        'fechaCancelacion': fields.char("Fecha de Cancelacion", size=30),
<<<<<<< HEAD
        #Validar Archivos XML y Facturas ante el SAT, para Compras
        'fechaValidacion': fields.datetime("Fecha de Validación", readonly=True),
        'estatus': fields.char("Estatus de Factura", size=100, readonly=True),
        'codigoEstatus': fields.text("Codigo de Estatus", readonly=True),
=======
>>>>>>> origin/master
    }
    
    _defaults = {
        'tipoComprobante': 'ingreso',
        'cfdi_cuatro_digitos' : '0000',
        'id_cfdi_rnet': get_cfdi,
        'cfdi_forma_pago': get_forma_pago,
        'cfdi_metodo_pago': get_metodo_pago,
        'cfdi_regimen_fiscal': get_regimen_fiscal
    }
cfdi_account_invoice()
