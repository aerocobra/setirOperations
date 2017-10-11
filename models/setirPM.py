# -*- coding: utf-8 -*-
#setirPM.py
import openerp.addons.decimal_precision as dp
from openerp import api, fields, models, _
from openerp import tools
from pygments.lexer import _inherit
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import exceptions
from setirDefinitions import *

class setirPM ( models.Model):
	_name			= "setir.pm"
	_inherit		= ['mail.thread', 'ir.needaction_mixin']
	_description	= "Medio de pago"
	_order			= 'idCustomer desc, dtSignUp desc'

	idOperation		= fields.Many2one	(
											string			= u"Operación",
											comodel_name	= "setir.operation"
										)

	idCustomer		= fields.Many2one	(
											string			= "Cliente",
											comodel_name	= "res.partner",
											domain			= "[('customer', '=', True)]"
										)
	idProvider		= fields.Many2one	(
											string			= "Proveedor",
											comodel_name	= "res.partner",
											domain			= "[('supplier', '=', True)]"
										)
	
	idProductPM		= fields.Many2one	(
											string			= "Medio de pago",
											comodel_name	= "product.product"
										)

	idAssocPackTmpl	= fields.Many2one	(
											string			= "Pack peaje asociado",
											comodel_name	= "sale.quote.template"
										)
	ePMType			= fields.Selection	(
											string		= "Tipo",
											selection	= PM_TYPE
										)
	strPAN			= fields.Char		(	string			= "PAN")
	name			= fields.Char		(
											string			= "name",
											related			= "strPAN"
										)
	strSecondaryPAN	= fields.Char		(	string			= "PAN Secundario")

	strPN			= fields.Char		(	string			= u"Matrícula asociada")
	idCountry		= fields.Many2one	(	string			= u"País",
											comodel_name	= "res.country"
										)
	strSN			= fields.Char		(	string			= "SN")
	strSecondarySN	= fields.Char		(	string			= "SN Secundario")

	dtSignUp		= fields.Datetime	(	string			= u"Fecha alta")
	dateExpiration	= fields.Date		(	string			= u"Fecha expiración")	
	dtUnsubscribe	= fields.Datetime	(	string			= u"Fecha baja")

	#estdos de registro PM
	eRegisterState	= fields.Selection	(	string		= "Estado registro",
											selection	= REGISTER_STATE
										)
	idUnsubscribeReason	= fields.Many2one	(
											string			= "Causa de baja",
											comodel_name	= "setir.pm.unsubscribe.reason"
											)
	
	#estados de propio PM
	idsPMSate			=	fields.Many2one	(
											string			= "Estado medio de pago",
											comodel_name	= "setir.pm.state"
											)
	strPMState			=	fields.Char		(
											string = "state",
											related = "idsPMSate.name"
											)
	idBlockReason		= fields.Many2one	(
											string			= "Causa de bloqueo",
											comodel_name	= "setir.pm.block.reason"
											)

	idsPMStateHistory	= fields.One2many	(	
												comodel_name	= "setir.pm.state.history",
												inverse_name	= "idPM",
												string			= "Historial estados PM"
											)
	
	#estados de gestión PM
	idsPMManagement		= fields.Many2one		(
												string			= u"Estado gestión",
												comodel_name	= "setir.pm.management"
												)
	idsPMManagementHist	= fields.One2many	(
												comodel_name	= "setir.pm.management.history", 
												inverse_name	= "idPM",
												string			= "Historial gestiones medio de pago"
											)

	@api.one
	def addPMStateHistory (self, idState):
		vals = {}
		vals['idPM']	= self.id
		vals['idState']	= idState
		dtCurrent		= fields.Datetime.now()
		vals['dtState']	= dtCurrent	

		self.env["setir.pm.state.history"].create ( vals)

		return dtCurrent

	@api.one
	def addPMManagementHistory (self, idMangement, strSender, strReceiver):
		vals = {}
		vals['idPM']			= self.id
		vals['idManagement']	= idMangement
		vals['dtManagement']	= fields.Datetime.now()
		vals['eSender']			= dict(ACTORS)[strSender]
		vals['eReceiver']		= dict(ACTORS)[strReceiver]

		self.env["setir.pm.management.history"].create ( vals)

class setirPMState ( models.Model):
	_name = "setir.pm.state"

	name			= fields.Char	( string = "Estado")
	strDescription  = fields.Char	( string = u"Descripción")

class setirPMStateHistory ( models.Model):
	_name = "setir.pm.state.history"
	_order = 'dtState desc'

	idPM	= fields.Many2one	(	string			= "pm",
									comodel_name	= "setir.pm")
	idState	= fields.Many2one	(	string			= "Estado",
									comodel_name	= "setir.pm.state")
	dtState	= fields.Datetime	(	string	= "Fecha")	

class setirPMUnsubscribeReason ( models.Model):
	_name	= "setir.pm.unsubscribe.reason"

	name	= fields.Char ( string = u"Razón baja")

class setirPMBlockReason ( models.Model):
	_name	= "setir.pm.block.reason"

	name	= fields.Char ( string = u"Razón bloqueo")

class setirPMManagement ( models.Model):
	_name = "setir.pm.management"

	name		= fields.Char		( string = u"Gestión")

class setirPMManagementHistory ( models.Model):
	_name	= "setir.pm.management.history"
	_order	= 'dtManagement desc'

	idPM	= fields.Many2one	(	string			= "pm",
									comodel_name	= "setir.pm")

	idManagement	= fields.Many2one	(	string			= u"Gestión",
											comodel_name	= "setir.pm.management")
	dtManagement	= fields.Datetime	 (	string			= "Fecha")	

	eSender		= fields.Selection	(
									string		= "Remitente",
									selection	= ACTORS
									)
	eReceiver	= fields.Selection	(
									string		= "Destinatario",
									selection	= ACTORS
									)
