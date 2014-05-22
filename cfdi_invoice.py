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
#http://chart.apis.google.com/chart?chs=200x200&cht=qr&chl=?re=XAXX010101000%26rr=XAXX010101000%26tt=1234567890.123456%26id=ad662d33-6934-459c-a128-BDf0393f0f44
#http://zxing.org/w/chart?cht=qr&chs=350x350&chld=H&choe=UTF-8&chl=%3Fre%3DXAXX010101000%26rr%3DXAXX010101000%26tt%3D1234567890.123456%26id%3Dad662d33-6934-459c-a128-BDf0393f0f44
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
from SOAPpy import SOAPProxy

ERROR = ""
app_xsltproc = tools.find_in_path("xsltproc")

#class cfdi_account_retenciones(osv):
#    _name = "cfdi.account.retenciones"
#    _columns = {
#        'name' : fields.selection("Retención"),
#        'importe': fields.float("Importe"),
#    }
#    
#cfdi_account_retenciones()

class cfdi_account_invoice(osv.osv):

    def conv_ascii(self, text):
        old_chars = ['á', 'é', 'í', 'ó', 'ú', 'à', 'è', 'ì', 'ò', 'ù', 'ä', 'ë', 'ï', 'ö', 'ü', 'â', 'ê', 'î', \
        'ô', 'û', 'Á', 'É', 'Í', 'Ú', 'Ó', 'À', 'È', 'Ì', 'Ò', 'Ù', 'Ä', 'Ë', 'Ï', 'Ö', 'Ü', 'Â', 'Ê', 'Î', \
        'Ô', 'Û', 'ñ', 'Ñ', 'ç', 'Ç', 'ª', 'º', '°', ' ', 'Ã'
        ]
        new_chars = ['a', 'e', 'i', 'o', 'u', 'a', 'e', 'i', 'o', 'u', 'a', 'e', 'i', 'o', 'u', 'a', 'e', 'i', \
        'o', 'u', 'A', 'E', 'I', 'U', 'O', 'A', 'E', 'I', 'O', 'U', 'A', 'E', 'I', 'O', 'U', 'A', 'E', 'I', \
        'O', 'U', 'n', 'N', 'c', 'C', 'a', 'o', 'o', ' ', 'A'
        ]
        for old, new in zip(old_chars, new_chars):
            try:
                text = text.replace(unicode(old,'UTF-8'), new)
            except:
                try:
                    text = text.replace(old, new)
                except:
                    raise osv.except_osv(('Error !'), 'No se pudo re-codificar la cadena [%s] en la letra [%s]'%(text, old) )
        return text

    def timbrar(self, cr, uid, ids, partner_id, context={}):
        #raise osv.except_osv("AVISO","El sistema se encuentra en mantenimiento, el servicio de timbrado estará  disponible el 22 de Febrero a partir de las 12:00 hrs.")
        global ERROR
        invoice = self.browse(cr,uid,ids)
        inv = invoice[0]
        xml = self.genera_xml(cr,uid,ids,partner_id)
        xml = self.conv_ascii(xml.toxml(encoding='utf-8'))
        #raise osv.except_osv(("ERROR!"),("Se encontraron los siguientes errores:\n%s")%(xml))
        a = SOAPProxy("https://ws2.bovedacomprobante.net/ws/service.asmx")
        user = inv.id_cfdi_rnet.pac_usuario
        pw = inv.id_cfdi_rnet.pac_password
        if not user or not pw:
            ERROR = ERROR + "No estan configurados los datos del PAC\n"
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
            cfdi_base64 = xml_respuesta.getElementsByTagName("Cfdi")[0].firstChild.data #Para guardar como adjunto
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
            return False
        
    def agregarEspacios(self, cadena, caracteres):
        data = ""
        for i in range(len(cadena)):
            data = data + cadena[i]
            if i%(caracteres-1) == 0:
                if i>(caracteres-5):
                    data = data + ' '
        return data
    
    def cancelar(self, cr, uid, ids, partner_id):
        return True

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
        tipoComprobante = "ingreso"
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
        cadena_original = ""
        try:
            f = open(xml_file, 'wb' )
            f.write(self.conv_ascii(doc.toxml()))
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
        except:
            ERROR = ERROR + "No se pudo generar la cadena original.\n"
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
        
    _inherit = 'account.invoice'
    _columns = {
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('timbrada','Timbrada'),
            ('paid','Paid'),
            ('cancel','Cancelled')
            ],'State', select=True, readonly=True,
            help=' * The \'Draft\' state is used when a user is encoding a new and unconfirmed Invoice. \
            \n* The \'Pro-forma\' when invoice is in Pro-forma state,invoice does not have an invoice number. \
            \n* The \'Open\' state is used when user create invoice,a invoice number is generated.Its in open state till user does not pay invoice. \
            \n* The \'Paid\' state is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
            \n* The \'Cancelled\' state is used when user cancel invoice.'),
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
        #'retenciones': fields.many2many(),
        #'total_retenciones':
    }
    
    _defaults = {
        'cfdi_cuatro_digitos' : '0000',
    }
cfdi_account_invoice()