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
{
    "name" : "Creacion de Factura Electronica para Mexico (CFDi)",
    "version" : "1.4",
    "author" : "rNet Soluciones",
    "category" : "Accounting & Finance",
    "depends": ["sale", "account", "account_voucher", "base_vat_mx","l10n_mx_invoice_amount_to_text","l10n_mx_partner_address","partner_bank_last_digits"],
    "website": "http://rnet.mx",
    "description" : """FACTURACIÓN ELÉCTRONICA CFDi, SEGÚN LA LEGISLACIÓN MEXICANA 2013.
  
  Pogramas requeridos:
  xsltproc
        sudo apt-get install xsltproc

  openssl
        sudo apt-get install openssl
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["view.xml",
                    "cfdi_company_view.xml",
                    "cfdi_invoice_view.xml",
                    "cfdi_partner_view.xml",
                    "security/event_security.xml",
                    "security/ir.model.access.csv",
                    "required/l10n_mx_facturae_lib/security/ir.model.access.csv",
                    "cfdi_data.xml"
                    ],
    "installable" : True,
    'auto_install': False,
    'application': True,
}
