# -*- coding: utf-8 -*-
#setirManagementWizardPM.py

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

class setirUnsubscribeWizardPM ( models.TransientModel):
	_name				= "setir.unsubscribe.wizard.pm"
	_description		= u"Baja medios de pago"
	_inherit			= ['mail.thread']

	name				= fields.Char		(	string			= "ids")
	eManagement			= fields.Selection	(	string			= u"Gestión",
												selection		= GESTIONES)
	strPMType			= fields.Char		(	string			= "Tipo a gestionar")
	idUnsubscribeReason	= fields.Many2one	(	string			= "Causa de baja",
												comodel_name	= "setir.pm.unsubscribe.reason")
	idBlockReason		= fields.Many2one	(	string			= "Causa de bloqueo",
												comodel_name	= "setir.pm.block.reason")

	eSender				= fields.Selection	(	string			= "Remitente",
												selection		= ACTORS)
	eReceiver			= fields.Selection	(	string			= "Destinatario",
												selection		= ACTORS)

	idsPM2Manage		= fields.Many2many	(	string			= "Medios de pago",
												comodel_name	= "setir.pm")
	
	idCustomer			= fields.Many2one	(	string			= "Cliente",
												comodel_name	= "res.partner",
												domain			= "[('customer', '=', True)]")
	idProvider			= fields.Many2one	(	string			= "Proveedor",
												comodel_name	= "res.partner",
												domain			= "[('supplier', '=', True)]")
	idCustomerCode		= fields.Many2one	(	string			= u"Código cliente",
												comodel_name	= "setir.customer.provider.code",
												domain			= "[('idCustomer', '=', idCustomer),('idProvider', '=', idProvider)]"
												)
	
	
	
	strMailDestination	= fields.Char		(	string			= "Correo destinatario")
	idUser				= fields.Many2one	(	string			= "Responsable operaciones",
												comodel_name	= "res.users")
	user_id				= fields.Many2one	(	string			= "Responsable operaciones",
												comodel_name	= "res.users")

	strEmailBody		= fields.Text		(	string			= "Texto email")
	
	@api.multi
	def create (self, vals):
		ids2Unsubscribe	= self.env.context.get ('active_ids', False)

		records2Unsubscribe	= self.env["setir.pm"].search ([('id', 'in', ids2Unsubscribe)])#,
															#('eRegisterState', '!=', REGISTER_STATE_BAJA)])
		
		if not records2Unsubscribe:
			raise exceptions.ValidationError ( "No hay registros para dar de baja")


		vals["name"]		= "[" + str (ids2Unsubscribe) + "]"
		vals["idCustomer"]	= records2Unsubscribe[0].idCustomer.id
		vals["idProvider"]	= records2Unsubscribe[0].idProvider.id
		vals["user_id"]		= records2Unsubscribe[0].idOperation.idResonsibleToll.id
		vals["strPMType"]	= records2Unsubscribe[0].strPMType

		customerCode = self.env["setir.customer.provider.code"].search([('idCustomer', '=', vals["idCustomer"]),('idProvider', '=', vals["idProvider"])])
		if customerCode: 
			vals["idCustomerCode"] = customerCode.id
		
		strMailDestination	= records2Unsubscribe[0].idProvider.email
		
		strContactType	= "no_type" 
		if vals["strPMType"] == PM_TYPE_OBU:
			strContactType	= CONTACT_NAME_ENVIO_OBU
		elif  vals["strPMType"] == PM_TYPE_TARJETA:
			strContactType	= CONTACT_NAME_ENVIO_TARJETA

		contact = self.env["res.partner"].search ([('parent_id', '=', vals["idProvider"]), ('type', '=', ADDRESS_DELIVERY), ('name', '=', strContactType)])
		if contact:
			strMailDestination = contact[0].email
		else:  
			contact = self.env["res.partner"].search ([('parent_id', '=', vals["idProvider"]), ('type', '=', ADDRESS_DELIVERY), ('name', '=', CONTACT_NAME_ENVIO)])
			if contact:
				strMailDestination = contact[0].email
			else:
				contact = self.env["res.partner"].search ([('parent_id', '=', vals["idProvider"]), ('type', '=', ADDRESS_DELIVERY)])
				if contact:
					strMailDestination = contact[0].email
		
		vals["strMailDestination"]	= strMailDestination

		result				= super ( setirUnsubscribeWizardPM, self).create ( vals)

		for record in records2Unsubscribe:
				result.idsPM2Manage	= [(4, record.id, False)]

		return result

	@api.multi
	def unsubscribePM (self):
		if not self.idUnsubscribeReason:
			raise exceptions.ValidationError ( "Es necesario seleccionar una causa de baja")
		
		idsPM2manage	= self.env.context.get ('active_ids', False)

		#values = self.env["setir.pm.tt"].distinct_field_get(field='strCustomer', value='')
		#if len(set(values)) > 1:
		#	raise exceptions.ValidationError ( u"Ha seleccionado más de un CLINTE")
		
		stateBAJA		= self.env['setir.import.base'].search([('eImportType','=', IMPORT_TYPE_ESTADO),
																('name', '=', dict (PM_STATE)[PM_STATE_BAJA])])

		#for pm_id in idsPM2unsubscribe:
		vals	= {}
		vals["dtUnsubscribe"]		= fields.Datetime.now()
		vals["eRegisterState"]		= REGISTER_STATE_BAJA
		vals["idsPMState"]			= stateBAJA.id
		vals["idUnsubscribeReason"]	= self.idUnsubscribeReason.id 

		self.env["setir.pm"].search([('id','in', idsPM2manage)]).write (vals)
		self.env["setir.pm"].search([('id','in', idsPM2manage)]).addPMStateHistory ( stateBAJA.id)

		strPMs	= ""
		for rec in self.env["setir.pm"].search([('id', 'in', idsPM2manage)]):
			strPMs += rec.name + ", "
		rec.idOperation.message_post ( "Baja PM["+ strPMs + "]")

		return {'type': "ir.actions.do_nothing",}

	@api.multi
	def lockPM (self):
		if not self.idBlockReason:
			raise exceptions.ValidationError ( "Es necesario seleccionar una causa de bloqueo")
		
		idsPM2manage	= self.env.context.get ('active_ids', False)

		
		stateBLOQUEADO	= self.env['setir.import.base'].search([('eImportType','=', IMPORT_TYPE_ESTADO),
																('name', '=', dict (PM_STATE)[PM_STATE_BLOQUEADO])])

		#for pm_id in idsPM2unsubscribe:
		vals	= {}
		#vals["dtUnsubscribe"]		= fields.Datetime.now()
		#vals["eRegisterState"]		= REGISTER_STATE_BAJA
		vals["idsPMState"]			= stateBLOQUEADO.id
		vals["idBlockReason"]		= self.idBlockReason.id 

		self.env["setir.pm"].search([('id','in', idsPM2manage)]).write (vals)
		self.env["setir.pm"].search([('id','in', idsPM2manage)]).addPMStateHistory ( stateBLOQUEADO.id)

		strPMs	= ""
		for rec in self.env["setir.pm"].search([('id', 'in', idsPM2manage)]):
			strPMs += rec.name + ", "
		rec.idOperation.message_post ( "Desbloqueo PM["+ strPMs + "]")

		return {'type': "ir.actions.do_nothing",}

	@api.multi
	def unlockPM (self):
		
		idsPM2manage	= self.env.context.get ('active_ids', False)
	
		stateACTIVO		= self.env['setir.import.base'].search([('eImportType','=', IMPORT_TYPE_ESTADO),
																('name', '=', dict (PM_STATE)[PM_STATE_ACTIVO])])

		#for pm_id in idsPM2unsubscribe:
		vals	= {}
		#vals["dtUnsubscribe"]		= fields.Datetime.now()
		#vals["eRegisterState"]		= REGISTER_STATE_BAJA
		vals["idsPMState"]			= stateACTIVO.id
		#vals["idBlockReason"]		= self.idUnsubscribeReason.id 

		self.env["setir.pm"].search([('id','in', idsPM2manage)]).write (vals)
		self.env["setir.pm"].search([('id','in', idsPM2manage)]).addPMStateHistory ( stateACTIVO.id)

		strPMs	= ""
		for rec in self.env["setir.pm"].search([('id', 'in', idsPM2manage)]):
			strPMs += rec.name + ", "
		rec.idOperation.message_post ( "Desbloqueo PM["+ strPMs + "]")

		return {'type': "ir.actions.do_nothing",}

	@api.multi
	def sendPM (self):
		
		idsPM2manage	= self.env.context.get ('active_ids', False)
	
		stateENVIADO		= self.env['setir.pm.management'].search([('name', '=', ESTADO_GESTION_ENVIADO)])

		#for pm_id in idsPM2unsubscribe:
		vals	= {}
		#vals["dtUnsubscribe"]		= fields.Datetime.now()
		#vals["eRegisterState"]		= REGISTER_STATE_BAJA
		#vals["idsPMState"]			= stateACTIVO.id
		#vals["idBlockReason"]		= self.idUnsubscribeReason.id 
		vals["idsPMManagement"]		= stateENVIADO.id

		self.env["setir.pm"].search([('id','in', idsPM2manage)]).write (vals)
		self.env["setir.pm"].search([('id','in', idsPM2manage)]).addPMManagementHistory (stateENVIADO.id, self.eSender, self.eReceiver)

		strPMs	= ""
		for rec in self.env["setir.pm"].search([('id', 'in', idsPM2manage)]):
			strPMs += rec.name + ", "
		rec.idOperation.message_post ( "Envio PM["+ strPMs + "]")

		return {'type': "ir.actions.do_nothing",}

	@api.multi
	def receivePM (self):
		
		idsPM2manage	= self.env.context.get ('active_ids', False)
	
		stateRECIBIDO	= self.env['setir.pm.management'].search([('name', '=', ESTADO_GESTION_RECIBIDO)])

		#for pm_id in idsPM2unsubscribe:
		vals	= {}
		#vals["dtUnsubscribe"]		= fields.Datetime.now()
		#vals["eRegisterState"]		= REGISTER_STATE_BAJA
		#vals["idsPMState"]			= stateACTIVO.id
		#vals["idBlockReason"]		= self.idUnsubscribeReason.id 
		vals["idsPMManagement"]		= stateRECIBIDO.id

		self.env["setir.pm"].search([('id','in', idsPM2manage)]).write (vals)
		self.env["setir.pm"].search([('id','in', idsPM2manage)]).addPMManagementHistory ( stateRECIBIDO.id, self.eSender, self.eReceiver)

		strPMs	= ""
		for rec in self.env["setir.pm"].search([('id', 'in', idsPM2manage)]):
			strPMs += rec.name + ", "
		rec.idOperation.message_post ( "Recepción PM["+ strPMs + "]")

		return {'type': "ir.actions.do_nothing",}

	@api.multi
	def sendManagementMail ( self):
		
		strEmailTemplate	= u"Gestión indefinida"
		if self.eManagement == GESTION_BAJA:
			strEmailTemplate	= "unlink_pm_email_template"
		elif self.eManagement == GESTION_BLOQUEO: 
			strEmailTemplate	= "lock_pm_email_template"
		elif self.eManagement == GESTION_DESBLOQUEO:
			strEmailTemplate	= "unlock_pm_email_template"
		else:
			raise exceptions.ValidationError ( strEmailTemplate)

		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		
		try:
			template_id = ir_model_data.get_object_reference( "setirOperations", strEmailTemplate)[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False

		ctx = dict()
		
		idsPM2manage	= self.env.context.get ('active_ids', False)
		rec = self.env["setir.pm"].search([('id', 'in', idsPM2manage)])[0]

		ctx.update({
			'default_model': 'setir.unsubscribe.wizard.pm',
			'default_res_id': self.ids[0],
			#'default_res_id': rec.idOperation.id,
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			#'default_composition_mode': 'mass_mail',
			#'default_message_type': 'comment',
			'default_notify': False,
			'default_notification': False,
			'default_subtype_id': False,
		})
	
		return {
			#return {'type': "ir.actions.do_nothing",}
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}

	@api.multi
	def printUnsubscribeReport (self):
		return {'type': "ir.actions.do_nothing",}
