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

class res_partner(osv.osv):
    
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

    _inherit = "res.partner"
    
    _columns = {
        'cfdi_forma_pago': fields.many2one('cfdi.forma.pago',"Forma de Pago Preferida"),
        'cfdi_metodo_pago': fields.many2one('cfdi.metodo.pago', "Metodo de Pago Preferido"),
    }
    
    _defaults = {
        'vat': "XAXX010101000",
        'cfdi_forma_pago': get_forma_pago,
        'cfdi_metodo_pago': get_metodo_pago,
    }
    
res_partner()
