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
	_order			= 'eImportType desc, name desc'

	eImportType		=	fields.Selection	(	string		= u"Tipo de dato",
												selection	= IMPORT_TYPE)
	name			=	fields.Char			(	string		= "Nombre campo")
	strDescription	=	fields.Char			(	string		= u"Descripción")

class setirImportProvider ( models.Model):
	_name			= "setir.import.provider"
	_inherit		= "setir.import.base"
	_description	= u"Campos proveedor"
	_order			= 'idProvider desc, eImportType desc, name desc'

	idProvider		=	fields.Many2one	(	string			= "Proveedor",
											comodel_name	= "res.partner",
											domain			= "[('supplier','=', True), ('is_company', '=', True)]")
	strProvider		=	fields.Char		(	related			= "idProvider.name")

class setirImportMap ( models.Model):
	_name			= "setir.import.map"
	_inherit		= ['mail.thread', 'ir.needaction_mixin']
	_description	= u"Mapa correpondenca campos"
	_order			= 'name desc, idProvider desc'

	_sql_constraints = [('map_unique', 'unique(idProvider, eImportType)', 'Mapa ya existe!')]

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
											domain			= "[('strProvider', '=', strProvider), ('eImportType', '=', strImportType)]"
										)
	idFieldBase		= fields.Many2one	(	string			= "Campo base",
											comodel_name	= "setir.import.base",
											domain			= "[('eImportType', '=', strImportType)]"
											)

class setirImportHistory ( models.Model):
	_name				= "setir.import.history"
	_order				= "dtImport desc"

	idImport			= fields.Many2one	(	string			= u"Importación relacionada",
												comodel_name	= "setir.import")
	dtImport			= fields.Datetime	(	string			= u"Fecha importación")
	strFileImported		= fields.Char 		(	string			= "Archivo importado")
	strImportInfo		= fields.Text		(	string			= u"Información resultados")

class setirImport ( models.Model):
	_name				= "setir.import"
	_inherit			= ["mail.thread", "ir.needaction_mixin"]
	_description		= u"Importación"
	_order				= "dtLastImport desc"

	name				=	fields.Char		(	string			= u"Importación",
												default			= lambda self: _('New'))
	eImportType			=	fields.Selection(	string			= u"Tipo de importación",
												selection		= IMPORT_PROCES_TYPE,
												required		= True)
	idProvider			= fields.Many2one	(	string			= "Proveedor",
												comodel_name	= "res.partner",
												domain			= "[('supplier','=', True), ('is_company', '=', True)]",
												required		= True)
	eMonth				= fields.Selection	(	string			= u"Mes de importación",
												selection		= MONTHS,
												required		= True)
	dtLastImport		= fields.Datetime	(	string			= u"Fecha última importación",
												readonly		= True)
	idsImportHistory	= fields.One2many	(	comodel_name	= "setir.import.history",
												inverse_name	= "idImport",
												string			= "Historial Importaciones")

	@api.model
	def create (self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('setir.import.sequence') or _('New')

		result = super ( setirImport, self).create(vals)

		return result
	
class setirImportWizard ( models.TransientModel):
	_name			= "setir.import.wizard"
	_description	= u"Wizard de importación"

	name			= fields.Char		(	string	= u"Wizard importación")
	strFile2Import	= fields.Char		(	string	= "Archivo a importar", default = "")
	strData		 	= fields.Text		(	string	= "Datos leidos")
	bSaveImport		= fields.Boolean	(	default	= False)

