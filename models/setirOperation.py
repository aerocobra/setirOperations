# -*- coding: utf-8 -*-
#setirOperation.py
import openerp.addons.decimal_precision as dp
from openerp import api, fields, models, _
from openerp import tools
from pygments.lexer import _inherit
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp.exceptions import UserError
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import exceptions

class setirSaleOrderOperation ( models.Model):
	_inherit		= 'sale.order'

	@api.multi
	def action_done(self):
		super(setirSaleOrderOperation, self).action_done()
		
		#comprobar si ya hay una operación creada y activa
		activeOperation = self.env['setir.operation'].search([("idCustomer", "=", self.partner_id.id), ("bActive","=", True)])
		
		if activeOperation:
			#operacion activa existe - añadir lineas de operación
			a = 1
		else:
			vals = {}
			vals['idCustomer']		= self.partner_id.id
			vals['fRiskApproved']	= self.opportunity_id.x_fLeadRiskApproved
			vals['idResonsible']	= self.x_idOperationUser.id
			vals['bActive']			= True
			vals['dateSignUp']		= fields.Datetime.now()
			
			oper = self.env["setir.operation"].create ( vals)
			oper.fillProviders()

class setirOperationLine ( models.Model):
	_name			= "setir.operation"
	_description	= u"Línea de operación"

class setirOperation ( models.Model):
	_name			= "setir.operation"
	_inherit		= ['mail.thread', 'ir.needaction_mixin']
	_description	= u"Operación"
	_order = 'name desc, idCustomer desc'

	name			= fields.Char ( string	= u"Operación",
									default	= lambda self: _('New'))

	idCustomer			= fields.Many2one	(
											string			= "Cliente",
											comodel_name	= "res.partner",
											inverse			= "fillProviders"
										)

	fRiskApproved		= fields.Float ( string = 'Riesgo aprobado')
	idResonsible		= fields.Many2one (
											string			= "Responsable",
											comodel_name	= "res.users" 
											)

	bActive				= fields.Boolean ( string = "Operación activa")

	dateSignUp			= fields.Date ( string = "Fecha Alta")
	dateUnsubscribe		= fields.Date ( string = "Fecha Baja")
	idUnsubscribeReason	= fields.Many2one	(
											string			= "Razón de baja",
											comodel_name	= "setir.pm.unsubscribe.reason"
											)

	idsOrder			= fields.Many2many (
											comodel_name	= "sale.order",
											relation		= "rel_operation_sale_order",
											column1			= "operation_id",
											column2			= "order_id",
											string			= "Pedidos de venta"
											)

	idsProvider			= fields.Many2many (
												comodel_name	= "res.partner",
												relation		= "rel_operation_partner",
												column1			= "operation_id",
												column2			= "partner_id",
												string			= "Proveedores"
											)

	strComment			= fields.Text ( string = 'Notas internas')

	@api.onchange ('idCustomer')
	def fillProviders ( self):
		listOrders		= []
		listProviders	= []
		
		orders			= self.idCustomer.sale_order_ids
		
		for order in orders:
			if order.state == "done":
				listOrders.append ( order.id)
				provider_id 	= int (order.x_eProvider)
				if provider_id and provider_id not in listProviders:
					listProviders.append ( provider_id)

		self.idsOrder		= [(6, False, listOrders)]
		self.idsProvider	= [(6, False, listProviders)]
		
		res = {}
		res.update({'idsOrder': [('id', 'in', listOrders)]})
		res.update({'idsProvider': [('id', 'in', listProviders)]})

		return {'domain': res}

	@api.model
	def create (self, vals):
		if vals.get('name', _('New')) == _('New'):
			vals['name'] = self.env['ir.sequence'].next_by_code('setir.operation.name.sequence') or _('New')

		result = super(setirOperation, self).create(vals)

		return result



class setirPMState ( models.Model):
	_name = "setir.pm.state"

	name            = fields.Char ( string = "Estado")
	strDescription  = fields.Char ( string = u"Descripción")

class setirPMUnsubscribeReason ( models.Model):
	_name = "setir.pm.unsubscribe.reason"

	name            = fields.Char ( string = "Razón")

class setirPMBlockReason ( models.Model):
	_name = "setir.pm.block.reason"

	name            = fields.Char ( string = "Razón")

class setirPMStateHistory ( models.Model):
	_name = "setir.pm.state.history"
	
	idState	= fields.Many2one ( string			= "Estado",
								comodel_name	= "setir.pm.state")
	dtState	= fields.Datetime (	string	= "Fecha")	

class setirPMManagement ( models.Model):
	_name = "setir.pm.management"

	name    = fields.Char ( string = "Gestión")
