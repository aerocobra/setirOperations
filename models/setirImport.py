# -*- coding: utf-8 -*-
#setirOperation.py
import openerp.addons.decimal_precision as dp
from openerp import api, fields, models, _
from openerp import tools
from pygments.lexer import _inherit
from datetime import datetime, timedelta, date
from openerp import SUPERUSER_ID
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import exceptions
from setirDefinitions import *
import base64
import os
import csv
import codecs
import sys  
import logging

_logger = logging.getLogger(__name__)

reload(sys)  
sys.setdefaultencoding('utf8')

#campos base necesarios
#los campos de distintos proveedores deben ser mapeados a estos
class setirImportBase ( models.Model):
	_name			= "setir.import.base"
	_description	= u"Campos base setir"
	_order			= 'eImportType asc, name asc'

	eImportType		=	fields.Selection	(	string		= u"Tipo de dato",
												selection	= IMPORT_TYPE)
	name			=	fields.Char			(	string		= "Nombre campo")
	strDescription	=	fields.Char			(	string		= u"Descripción")

class setirImportProvider ( models.Model):
	_name			= "setir.import.provider"
	_inherit		= "setir.import.base"
	_description	= u"Campos proveedor"
	_order			= 'idProvider asc, eImportType asc, name asc'

	idProvider		=	fields.Many2one	(	string			= "Proveedor",
											comodel_name	= "res.partner",
											domain			= "[('supplier','=', True), ('is_company', '=', True)]")
	strProvider		=	fields.Char		(	related			= "idProvider.name")

class setirProductImportLine ( models.Model):
	_name			= "setir.product.import.line"
	_description	= u"Correpondenca productos"

	idImportMap		= fields.Many2one	(	comodel_name	= "setir.product.import.map")
	strProvider		= fields.Char		(	related			= "idImportMap.idProvider.name")
	strImportType	= fields.Selection	(	related			= "idImportMap.eImportType")

	idFieldProvider	= fields.Many2one	(	string			= "Nombre proveedor",
											comodel_name	= "setir.import.provider",
											domain			= "[('strProvider', '=', strProvider), ('eImportType', '=', 'strImportType')]")

	idFieldBase		= fields.Many2one	(	string			= "Nombre registrado",
											comodel_name	= "product.product")
	strCategory		= fields.Char		(	string			= "Categoria producto",
											related			= "idFieldBase.categ_id.name")

class setirProductImportMap ( models.Model):
	_name			= "setir.product.import.map"
	_inherit		= ['mail.thread', 'ir.needaction_mixin']
	_description	= u"Mapa correpondenca productos"
	_order			= 'name asc, idProvider asc'

	_sql_constraints	= [('map_unique', 'unique(idProvider, eImportType)', 'Mapa ya existe!')]

	name			=	fields.Char			(	string			= "Mapa de correspondencia productos",
												readonly		= True,
												default			= lambda self: _('New')
											)
	idProvider		=	fields.Many2one		(	string			= "Proveedor",
												comodel_name	= "res.partner",
												domain			= "[('supplier','=', True), ('is_company', '=', True)]",
												inverse			= "set_name",
												required		= True)
	strProvider		=	fields.Char			(	related			= "idProvider.name")

	eImportType		=	fields.Selection	(	string			= u"Categoría producto",
												selection		= IMPORT_PRODUCT_CATEGORY,
												inverse			= "set_name",
												required		= True)


	idsMapLine		=	fields.One2many		(	comodel_name	= "setir.product.import.line",
												inverse_name	= "idImportMap",
												string			= u"Líneas mapeo")

	@api.onchange ('idProvider', 'eImportType')
	@api.one
	def set_name (self):
		if self.strProvider:
			self.name =  "[" + str ( self.strProvider) + "]-[" + str (dict(self._fields['eImportType'].selection).get(self.eImportType)) +"]"

	@api.one
	def	setProviderFields ( self):
		#solo rellenar si la lista esta vacia
		if self.idsMapLine:
			return
		strTT = ""
		for rec in self.env["setir.import.provider"].search ( [('strProvider', '=', self.strProvider),
															('eImportType', '=', self.eImportType)]):
			vals = {}
			vals["idImportMap"]		=	self.id
			vals["idFieldProvider"]	=	rec.id
			strTT += "[" +str (self.id) + "],[" + str (rec.id) + "]"
			self.env["setir.product.import.line"].create ( vals)

	@api.one
	def clearNonCorrespondence (self):
		self.env["setir.product.import.line"].search ([('idImportMap', '=', self.id), ('idFieldBase', '=', False)]).unlink()

class setirImportMap ( models.Model):
	_name			= "setir.import.map"
	_inherit		= ['mail.thread', 'ir.needaction_mixin']
	_description	= u"Mapa correpondenca campos"
	_order			= 'name asc, idProvider asc'

	_sql_constraints	= [('map_unique', 'unique(idProvider, eImportType)', 'Mapa ya existe!')]

	name			=	fields.Char			(	string			= "Mapa de correspondencia",
												readonly		= True,
												default			= lambda self: _('New')
											)
	idProvider		=	fields.Many2one		(	string			= "Proveedor",
												comodel_name	= "res.partner",
												domain			= "[('supplier','=', True), ('is_company', '=', True)]",
												inverse			= "set_name",
												required		= True)
	strProvider		=	fields.Char			(	related			= "idProvider.name")
	eImportType		=	fields.Selection	(	string			= u"Tipo importación",
												selection		= IMPORT_TYPE,
												inverse			= "set_name",
												required		= True)

	idsMapLine		=	fields.One2many		(
												comodel_name	= "setir.import.line",
												inverse_name	= "idImportMap",
												string			= u"Líneas mapeo"
											)

	@api.one
	def	setProviderFields ( self):
		#solo rellenar si la lista esta vacia
		if self.idsMapLine:
			return
		strTT = ""
		for rec in self.env["setir.import.provider"].search ( [('strProvider', '=', self.strProvider), ('eImportType', '=', self.eImportType)]):
			vals = {}
			vals["idImportMap"]		=	self.id
			vals["idFieldProvider"]	=	rec.id
			strTT += "[" +str (self.id) + "],[" + str (rec.id) + "]"
			self.env["setir.import.line"].create ( vals)

	@api.one
	def clearNonCorrespondence (self):
		self.env["setir.import.line"].search ([('idImportMap', '=', self.id), ('idFieldBase', '=', False)]).unlink()

	@api.onchange ('idProvider', 'eImportType')
	@api.one
	def set_name (self):
		if self.strProvider != False and self.eImportType != False:
			#self.name =  "[" + str ( self.strProvider) + "]-[" + str (self.eImportType[self.eImportType]) +"]"
			self.name =  "[" + str ( self.strProvider) + "]-[" + str (dict(self._fields['eImportType'].selection).get(self.eImportType)) +"]"

class setirImportLine ( models.Model):
	_name			= "setir.import.line"
	_description	= u"Correpondenca campos"

	idImportMap		= fields.Many2one	(	comodel_name	= "setir.import.map")
	strProvider		= fields.Char		(	related			= "idImportMap.idProvider.name")
	strImportType	= fields.Selection	(	related			= "idImportMap.eImportType")

	idFieldProvider	= fields.Many2one	(	string			= "Campo proveedor",
											comodel_name	= "setir.import.provider",
											domain			= "[('strProvider', '=', strProvider), ('eImportType', '=', strImportType)]")
	idFieldBase		= fields.Many2one	(	string			= "Campo base",
											comodel_name	= "setir.import.base",
											domain			= "[('eImportType', '=', strImportType)]")

class setirImportHistory ( models.Model):
	_name				= "setir.import.history"
	_order				= "dtImport desc"

	idImport			= fields.Many2one	(	string			= u"Importación relacionada",
												comodel_name	= "setir.import")
	dtImport			= fields.Datetime	(	string			= u"Fecha importación")
	strFileImported		= fields.Char 		(	string			= "Archivo importado")
	strImportInfo		= fields.Text		(	string			= u"Información resultados")

class setirPM2Import ( models.Model):
	_name			= "setir.pm.2import"
	_inherit		= "setir.pm"
	_description	= "Medio de pago import temp"
	#_order			= 'idCustomer desc, dtSignUp desc'
	
	b2Import		= fields.Boolean	(	string			= "Importar")
	eImportAction	= fields.Selection	(	string			= u"Acción",
											selection		= IMPORT_ACTION)
	nID2Update		= fields.Integer	(	string			= "ID2U")
	idWizardPM		= fields.Many2one 	(	string			= "Wizard",
											comodel_name	= "setir.import")
	#strInfo			= fields.Text		(	string			= u"Información de importación")


class setirImport ( models.Model):
	_name				= "setir.import"
	_inherit			= ['mail.thread', 'ir.needaction_mixin']
	_description		= u"Importación"
	_order				= "dtLastImport desc"

	name				= fields.Char		(	string			= u"Importación",
												default			= lambda self: _('New'))
	eImportType			= fields.Selection	(	string			= u"Tipo de importación",
												selection		= IMPORT_PROCES_TYPE,
												required		= True)
	idProvider			= fields.Many2one	(	string			= "Proveedor",
												comodel_name	= "res.partner",
												domain			= "[('supplier','=', True), ('is_company', '=', True)]",
												required		= True)
	eYear				= fields.Selection	(	string			= u"Año de importación",
												selection		= YEARS,
												required		= True)
	eMonth				= fields.Selection	(	string			= u"Mes de importación",
												selection		= MONTHS,
												required		= True)
	bDirs				= fields.Boolean	(	string			= "Carpetas importación",
												default			= True)
	
	dtLastImport		= fields.Datetime	(	string			= u"Fecha última importación",
												readonly		= True)
	idsImportHistory	= fields.One2many	(	comodel_name	= "setir.import.history",
												inverse_name	= "idImport",
												string			= "Historial Importaciones")

	@api.model
	def create (self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('setir.import.sequence') or _('New')

		vals["eYear"]	= "{}".format(date.today().year)
		vals["eMonth"]	= "{}".format(date.today().month)
		vals["bDirs"]	= False 

		result			= super ( setirImport, self).create(vals)

		return result
	
	@api.multi
	def checkDirs (self):
		strPathBase		= self.env["ir.config_parameter"].search([("key","=", PATH_ROOT)])[0].value
		strPathProvider = self.env["res.partner"].search([("id","=", self.idProvider.id)])[0].ref
		strPathYear		= str ( self.eYear) 
		strPathMonth	= str ( self.eMonth)

		strPath			= strPathBase + "/" + strPathProvider + "/" + strPathYear + "/" + strPathMonth   

		if ( not os.path.exists (strPath)):
			strERR	= "Ruta NO existe [" + strPath + "], crear"
			_logger.error ( strERR)
			self.message_post ( strERR)
			self.bDirs	= False
			return False
		else:
			strERR	= "Ruta EXISTE [" + strPath + "]"
			self.message_post ( strERR)
			self.bDirs	= True
			return True
	
	@api.multi
	def makeDirs (self):
		strPathBase			= self.env["ir.config_parameter"].search([("key","=", PATH_ROOT)])[0].value
		strPathInvoicing	= self.env["ir.config_parameter"].search([("key","=", PATH_INVOICING)])[0].value
		strPathInvoices		= self.env["ir.config_parameter"].search([("key","=", PATH_INVOICES)])[0].value
		strPathConsumptions	= self.env["ir.config_parameter"].search([("key","=", PATH_CONSUPTIONS)])[0].value
		strPathPM			= self.env["ir.config_parameter"].search([("key","=", PATH_PM)])[0].value

		strPathProvider		= self.env["res.partner"].search([("id","=", self.idProvider.id)])[0].ref
		strPathYear			= str ( self.eYear) 

		strYear				= strPathBase + "/" + strPathProvider + "/" + strPathYear + "/"
		os.makedirs ( strYear)
		os.chmod ( strYear, 0o777)

		for i in range (12):
			strMonth	= strYear + "{:02d}".format ( ( i +1 ))
			os.makedirs ( strMonth)
			os.chmod ( strMonth, 0o777)
			
			strDir		= strMonth + "/" + strPathInvoicing
			os.makedirs ( strDir)
			os.chmod ( strDir, 0o777)
			
			strDir		= strMonth + "/" + strPathInvoices
			os.makedirs ( strDir)
			os.chmod ( strDir, 0o777)

			strDir		= strMonth + "/" + strPathConsumptions
			os.makedirs ( strDir)
			os.chmod ( strDir, 0o777)

			strDir		= strMonth + "/" + strPathPM
			os.makedirs ( strDir)
			os.chmod ( strDir, 0o777)
		
		self.bDirs	= True

class setirImportWizard ( models.TransientModel):
	_name			= "setir.import.wizard"
	_description	= u"Wizard de importación"

	name			= fields.Char		(	string	= u"Wizard importación")
	strFile2Import	= fields.Char		(	string	= "Archivo a importar", default = "")
	strData		 	= fields.Text		(	string	= "Datos leidos")
	bSaveImport		= fields.Boolean	(	default	= False)

