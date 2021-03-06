# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (moylop260@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
############################################################################
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

from osv import osv
from osv import fields
import tools

import os
import sys
import time
import tempfile
import base64

depends_app_path = os.path.join( tools.config["addons_path"], u'l10n_mx_facturae', u'depends_app')
openssl_path = os.path.abspath( tools.ustr( os.path.join( depends_app_path,  u'openssl_win')  ) )
xsltproc_path = os.path.abspath( tools.ustr( os.path.join( depends_app_path,  u'xsltproc_win')  ) )

def exec_command_pipe(*args):
    #Agregue esta funcion, ya que con la nueva funcion original, de tools no funciona
#TODO: Hacer separacion de argumentos, no por espacio, sino tambien por " ", como tipo csv, pero separator espace & delimiter "
    cmd = ' '.join(args)
    if os.name == "nt":
        cmd = cmd.replace('"', '')#provisionalmente, porque no funcionaba en win32
    return os.popen2(cmd, 'b')

if os.name == "nt":
    app_xsltproc = 'xsltproc.exe'
    app_openssl = 'openssl.exe'
else:
    app_xsltproc = 'xsltproc'
    app_openssl = 'openssl'

app_openssl_fullpath = os.path.join( openssl_path, app_openssl )
if not os.path.isfile( app_openssl_fullpath ):
    app_openssl_fullpath = tools.find_in_path( app_openssl )

app_xsltproc_fullpath = os.path.join( xsltproc_path, app_xsltproc )
if not os.path.isfile( app_xsltproc_fullpath ):
    app_xsltproc_fullpath = tools.find_in_path( app_xsltproc )
            

#TODO: Validar que esta instalado openssl & xsltproc
class facturae_certificate_library(osv.osv):
    _name = 'facturae.certificate.library'
    _auto = False
    #Agregar find subpath
    
    def b64str_to_tempfile(self, b64_str="", file_suffix="", file_prefix=""):
        (fileno, fname) = tempfile.mkstemp(file_suffix, file_prefix)
        f = open( fname, 'wb' )
        f.write( base64.decodestring( b64_str ) )
        f.close()
        os.close( fileno )
        return fname
    
    def _read_file_attempts(self, file_obj, max_attempt=12, seconds_delay=0.5):
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
        return fdata
    
    def _transform_der_to_pem(self, fname_der, fname_out, fname_password_der=None, type_der='cer'):
        """"
        @type_der cer or key
        """
        cmd = ''
        result = ''
        if type_der == 'cer':
            cmd = '"%s" x509 -inform DER -outform PEM -in "%s" -pubkey -out "%s"'%( 
                app_openssl_fullpath, fname_der, fname_out )
        elif type_der == 'key':
            cmd = '"%s" pkcs8 -inform DER -outform PEM -in "%s" -passin file:%s -out "%s"'%( 
                app_openssl_fullpath, fname_der, fname_password_der, fname_out )
        if cmd:
            args = tuple( cmd.split(' ') )
            #input, output = tools.exec_command_pipe(*args)
            input, output = exec_command_pipe(*args)
            result = self._read_file_attempts(open(fname_out, "r"))
            input.close()
            output.close()
        return result
    
    def _get_param_serial(self, fname, fname_out=None, type='DER'):
        result = self._get_params(fname, params=['serial'], fname_out=fname_out, type=type)
        result = result and result.replace('serial=', '').replace('33', 'B').replace('3', '').replace('B', '3').replace(' ', '').replace('\r', '').replace('\n', '').replace('\r\n', '') or ''
        return result

    def _get_param_dates(self, fname, fname_out=None, date_fmt_return='%Y-%m-%d %H:%M:%S', type='DER'):
        result_dict = self._get_params_dict(fname, params=['dates'], fname_out=fname_out, type=type)
        translate_key = {
            'notAfter': 'enddate',
            'notBefore': 'startdate',
        }
        result2 = {}
        if result_dict:
            date_fmt_src = "%b %d %H:%M:%S %Y GMT"
            for key in result_dict.keys():
                date = result_dict[key]
                date_obj = time.strptime(date, date_fmt_src)
                date_fmt = time.strftime(date_fmt_return, date_obj)
                result2[ translate_key[key] ] = date_fmt
        return result2
    
    def _get_params_dict(self, fname, params=None, fname_out=None, type='DER'):
        result = self._get_params(fname, params, fname_out, type)
        result = result.replace('\r\n', '\n').replace('\r', '\n')#.replace('\n', '\n)
        result = result.rstrip('\n').lstrip('\n').rstrip(' ').lstrip(' ')
        result_list = result.split('\n')
        params_dict = {}
        for result_item in result_list:
            if result_item:
                key,value = result_item.split('=')
                params_dict[key] = value
        return params_dict

    def _get_params(self, fname, params=None, fname_out=None, type='DER'):
        """
        @params: list [noout serial startdate enddate subject issuer dates]
        @type: str DER or PEM
        """
        cmd_params = ' -'.join(params)
        cmd_params = cmd_params and '-' + cmd_params or ''
        cmd = '"%s" x509 -inform "%s" -in "%s" -noout "%s" -out "%s"'%( 
            app_openssl_fullpath, type, fname, cmd_params, fname_out )
        args = tuple( cmd.split(' '))
        input, output = exec_command_pipe(*args)
        result = self._read_file_attempts(output)
        input.close()
        output.close()
        return result
facturae_certificate_library()
