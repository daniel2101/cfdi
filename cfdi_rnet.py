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
import time
import release
import tempfile
import base64
from tools.translate import _
import tools
import os

class cfdi_forma_pago(osv.osv):
    _name="cfdi.forma.pago"
    _columns={
        'name': fields.char("Forma de Pago", size=100, required=True, help="Ponga la forma de pago: \nEj. Pago en una sola exibición"),
        'descripcion': fields.text("Descripción"),
    }
cfdi_forma_pago()

class cfdi_metodo_pago(osv.osv):
    _name="cfdi.metodo.pago"
    _columns={
        'name': fields.char("Metodo de Pago", size=100, required=True, help="Ej. Tarjeta de Credito, Efectivo, Deposito, etc."),
        'descripcion': fields.text("Descripción"),
    }
cfdi_metodo_pago()

class cfdi_tipo_comprobante(osv.osv):
    _name="cfdi.tipo.comprobante"
    _columns={
        'name': fields.char("Tipo de Comprobante", required=True, size=100),
        'descripcion': fields.text("Descripción"),
    }
cfdi_tipo_comprobante()

class cfdi_regimen_fiscal(osv.osv):
    _name="cfdi.regimen.fiscal"
    _columns={
        'name': fields.char("Regimen Fiscal", size=100, required=True, help="Regimen fiscal al que pertenece el partner."),
        'descripcion': fields.text("Descripción"),
    }
cfdi_regimen_fiscal()

class cfdi_rnet(osv.osv):
    _name = "cfdi.rnet"
    _columns = {
        'name': fields.char('Nombre', size=100, required=True, help="Pon un nombre al certificado, para que más facil lo identifiques."),
        #CFDI
            # Certificados
        'certificado': fields.binary('Certificado', filters='*.cer,*.certificate,*.cert', required=True),
        'certificado_key': fields.binary('Certificado Key', filters='*.key', required=True),
        'certificado_password': fields.char('Contraseña del Certificado', size=64, invisible=False, required=True),
        'certificado_pem': fields.binary('Certificado PEM', filters='*.pem,*.cer,*.certificate,*.cert'),
        'certificado_key_pem': fields.binary('Certificado Key PEM', filters='*.pem,*.key'),
        'fecha_inicio': fields.date('Fecha de Inicio'),
        'fecha_fin': fields.date('Fecha de Fin'),
        'numero_serie': fields.char('Número de Serie', size=64),
        'rfc': fields.binary('Cedula de Identificacion Fiscal', filters="*.jpg,*.png,*.jpeg", help="Logo de la Cedula de Identificacion Fiscal"),
            # Datos del PAC
        'pac_usuario': fields.char('Usuario', size=20),
        'pac_password': fields.char('Contraseña', size=20),
        'pac_api_key': fields.char('Key', size=200),
        'wsdl': fields.char('WSDL', size=200),
        #'timbrar': fields.function(),
        #'cancelar': fields.function(),
    }

    defaults = {
        'fecha_inicio': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    
    
    def get_certificate_info(self, cr, uid, ids, context=None):
        certificate = self.browse(cr, uid, ids, context=context)[0]
        cer_der_b64str = certificate.certificado
        key_der_b64str = certificate.certificado_key
        password = certificate.certificado_password
        data = self.onchange_certificate_info(cr, uid, ids, cer_der_b64str, key_der_b64str, password, context=context)
        if data['warning']:
            raise osv.except_osv(data['warning']['title'], data['warning']['message'] )
        return self.write(cr, uid, ids, data['value'], context)
        
    def onchange_certificate_info(self, cr, uid, ids, cer_der_b64str, key_der_b64str, password, context=None):
        certificate_lib = self.pool.get('facturae.certificate.library')
        value = {}
        warning = {}
        certificate_file_pem = False
        certificate_key_file_pem = False
        invoice_obj = self.pool.get('account.invoice')
        if cer_der_b64str and key_der_b64str and password:
            
            fname_cer_der = certificate_lib.b64str_to_tempfile(cer_der_b64str, file_suffix='.der.cer', file_prefix='openerp__' + (False or '') + '__ssl__', )
            fname_key_der = certificate_lib.b64str_to_tempfile(key_der_b64str, file_suffix='.der.key', file_prefix='openerp__' + (False or '') + '__ssl__', )
            fname_password = certificate_lib.b64str_to_tempfile(base64.encodestring(password), file_suffix='der.txt', file_prefix='openerp__' + (False or '') + '__ssl__', ) 
            fname_tmp = certificate_lib.b64str_to_tempfile('', file_suffix='tmp.txt', file_prefix='openerp__' + (False or '') + '__ssl__', )
            
            cer_pem = certificate_lib._transform_der_to_pem(fname_cer_der, fname_tmp, type_der='cer')
            cer_pem_b64 = base64.encodestring( cer_pem )
            
            key_pem = certificate_lib._transform_der_to_pem(fname_key_der, fname_tmp, fname_password, type_der='key')
            key_pem_b64 = base64.encodestring( key_pem )
            date_fmt_return='%Y-%m-%d'
            serial = False
            try:
                serial = certificate_lib._get_param_serial(fname_cer_der, fname_tmp, type='DER')
                value.update({
                    'numero_serie': serial,
                })
            except:
                pass
            date_start = False
            date_end = False
            try:
                dates = certificate_lib._get_param_dates(fname_cer_der, fname_tmp, date_fmt_return=date_fmt_return, type='DER')
                date_start = dates.get('startdate', False)
                date_end = dates.get('enddate', False)
                value.update({
                    'fecha_inicio': date_start,
                    'fecha_fin': date_end,
                })
            
            except:
                pass
            os.unlink( fname_cer_der )
            os.unlink( fname_key_der )
            os.unlink( fname_password )
            os.unlink( fname_tmp ) 
            
            if not key_pem_b64 or not cer_pem_b64:
                warning = {
                   'title': _('Error'),
                   'message': _('El certificado, la llave (key) o la contraseña no son correctos.\nVerifique los datos.\nRecuerde utilizar mayusculas y minusculas de forma adecuada.')
                }
                value.update({
                    'certificado_pem': False,
                    'certificado_key_pem': False,
                })
            else:
                value.update({
                    'certificado_pem': cer_pem_b64,
                    'certificado_key_pem': key_pem_b64,
                })
        return {'value': value, 'warning': warning}
cfdi_rnet()
    
