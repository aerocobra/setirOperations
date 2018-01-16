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
from itertools import groupby

class setirPM ( models.Model):
	_name				= "setir.pm"
	_inherit			= ['mail.thread', 'ir.needaction_mixin']
	_description		= "Medio de pago"
	_order				= 'idProvider,idCustomer,dtSignUp'

	name				= fields.Char		(	string			= u"OBU ID")

	nPMCount			= fields.Integer	(	string			= "Count")

	idOperation			= fields.Many2one	(	string			= u"Operación",
												comodel_name	= "setir.operation")

	idCustomer			= fields.Many2one	(	string			= "Cliente",
												comodel_name	= "res.partner",
												domain			= "[('customer', '=', True)]")

	strCustomer			= fields.Char		(	string			= "Cliente",
												related			= "idCustomer.name")

	idProvider			= fields.Many2one	(	string			= "Proveedor",
												comodel_name	= "res.partner",
												domain			= "[('supplier', '=', True)]")

	strProvider			= fields.Char		(	string			= "Proveedor",
												related			= "idProvider.name")
	
	idProduct			= fields.Many2one	(	string			= "Producto",
												comodel_name	= "product.product")
	strPMType			= fields.Char		(	string			= "Tipo",
												related			= "idProduct.categ_id.name",
												store			= True)

	idAssocPackTmpl		= fields.Many2one	(	string			= "Pack peaje asociado",
												comodel_name	= "sale.quote.template")
	
	strPAN				= fields.Char		(	string			= "PAN")
	strSecondaryPAN		= fields.Char		(	string			= "PAN Secundario")

	strPN				= fields.Char		(	string			= u"Matrícula asociada")
	idCountry			= fields.Many2one	(	string			= u"País",
												comodel_name	= "res.country")
	
	strSN				= fields.Char		(	string			= "SN")
	strSecondarySN		= fields.Char		(	string			= "SN Secundario")

	dtSignUp			= fields.Datetime	(	string			= u"Fecha alta")
	dtCreation			= fields.Datetime	(	string			= u"Fecha creación")
	dateExpiration		= fields.Date		(	string			= u"Fecha expiración")	
	dtUnsubscribe		= fields.Datetime	(	string			= u"Fecha baja")

	#estdos de registro PM
	eRegisterState		= fields.Selection	(	string			= "Estado registro",
												selection		= REGISTER_STATE,
												readonly		= True)
	
	idUnsubscribeReason	= fields.Many2one	(	string			= "Causa de baja",
												comodel_name	= "setir.pm.unsubscribe.reason",
												readonly		= True)
	bReplace			= fields.Boolean	(	string			= u"Sustitución",
												default			= False)
	
	#estados de propio PM
	idsPMState			= fields.Many2one	(	string			= "Estado medio de pago",
												comodel_name	= "setir.import.base",
												domain			= "[('eImportType','=','estado')]")
	strPMState			= fields.Char		(	string = "state",
												related = "idsPMState.name")
	
	idBlockReason		= fields.Many2one	(	string			= "Causa de bloqueo",
												comodel_name	= "setir.pm.block.reason")

	idsPMStateHistory	= fields.One2many	(	comodel_name	= "setir.pm.state.history",
												inverse_name	= "idPM",
												string			= "Historial estados PM",
												readonly		= True)
	
	#estados de gestión PM
	idsPMManagement		= fields.Many2one	(	string			= u"Estado gestión",
												comodel_name	= "setir.pm.management")
	
	idsPMManagementHist	= fields.One2many	(	comodel_name	= "setir.pm.management.history", 
												inverse_name	= "idPM",
												string			= "Historial gestiones medio de pago",
												readonly		= True)


	@api.model
	def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
		return super(setirPM, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=False)

	@api.one
	def addPMManagementHistory (self, idMangement, eSender, eReceiver):
		vals = {}
		vals['idPM']			= self.id
		vals['idManagement']	= idMangement
		vals['dtManagement']	= fields.Datetime.now()
		vals['eSender']			= eSender #dict(ACTORS)[strSender]
		vals['eReceiver']		= eReceiver #dict(ACTORS)[strReceiver]

		self.env["setir.pm.management.history"].create ( vals)

	def requestPM (self):
		strIDS = str ( self.env.context.get ("active_ids", False))
		raise exceptions.ValidationError ( "solicitar:" + strIDS)

	def sendPM (self):
		strIDS = str ( self.env.context.get ("active_ids", False))
		raise exceptions.ValidationError ( "enviar:" + strIDS)

	def receivePM (self):
		strIDS = str ( self.env.context.get ("active_ids", False))
		raise exceptions.ValidationError ( "recibir:" + strIDS)

	def managePM (self):
		ids2D	= self.env.context.get ("active_ids", False) 
		strIDS	= str ( ids2D)
		
		wizard = self.env['setir.unsubscribe.wizard.pm'].with_context(active_ids=ids2D).create({'name': strIDS})
		
		ctx	= {'active_ids': ids2D}
		
		
		return {
            'name': u'Gestión de los medios de pago',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env['ir.ui.view'].search([('name','=','setirPMUnlinkForm')])[0].id,
			'src_model': 'setir.pm',
            'res_model': 'setir.unsubscribe.wizard.pm',
            'res_id': wizard.id,
            'type': 'ir.actions.act_window',
			'target': "new",
			'context': ctx
        }

	@api.one
	def addPMStateHistory (self, idState):
		vals = {}
		vals['idPM']	= self.id
		vals['idState']	= idState
		dtCurrent		= fields.Datetime.now()
		vals['dtState']	= dtCurrent	

		self.env["setir.pm.state.history"].create ( vals)

		return dtCurrent

class setirPMStateHistory ( models.Model):
	_name = "setir.pm.state.history"
	_order = 'dtState desc'

	idPM	= fields.Many2one	(	string			= "pm",
									comodel_name	= "setir.pm")
	
	idState	=	fields.Many2one	(
									string			= "Estado medio de pago",
									comodel_name	= "setir.import.base",
									domain			= "[('eImportType','=','estado')]"
								)
	
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
