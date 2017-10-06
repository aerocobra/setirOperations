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

class setirPartnerOperation ( models.Model):
	_inherit		= "res.partner"

	idInvoicingType				= fields.Many2one (	string			= u"Tipo facturación",
													comodel_name	= "setir.invoicing.type")
	strInvoicngTypeDescription	= fields.Char (		string			= u"Descripción",
													related			= "idInvoicingType.strDescription")

class setirInvocingType ( models.Model):
	_name	= "setir.invoicing.type"

	name			= fields.Char (			string		= u"Tipo Facturación")
	strDescription	= fields.Char (			string		= u"Descripción")

	VALS = [('F', 'Factura'), ('S', 'Suplido')]

	eConsumos		= fields.Selection (	string		= "Consumos", 
											selection	= VALS)
	eCoste			= fields.Selection (	string		= "Coste",
											selection	= VALS)
	eBeneficio		= fields.Selection (	string		= "Beneficio",
											selection	= VALS)

class setirSaleOrderOperation ( models.Model):
	_inherit		= "sale.order"

	@api.multi
	def action_done(self):
		super(setirSaleOrderOperation, self).action_done()
		
		#comprobar si ya hay una operación creada y activa
		operation = self.env['setir.operation'].search([("idCustomer", "=", self.partner_id.id), ("bActive","=", True)])
		
		if operation:
			#operacion activa existe - solo añadir lineas de operación
			vals = {}
			#actualizar riesgo
			vals['fRiskApproved']	= self.opportunity_id.x_fLeadRiskApproved
		else:
			vals = {}
			vals['idCustomer']		= self.partner_id.id
			vals['fRiskApproved']	= self.opportunity_id.x_fLeadRiskApproved
			vals['bActive']			= True
			vals['dateSignUp']		= fields.Datetime.now()

			operation = self.env["setir.operation"].create ( vals)
			operation.fillOrdersProviders()

		listToll	= []
		listPM		= []
		listTax		= []
		listFuel	= []
		listOther	= []

		#formar nuevas lineas de operación
		for orderLine in self.order_line:
			vals = {}
			vals['bActive']			= True
			vals['idOperation']		= operation.id
			vals['idProvider']		= self.x_eProvider
			vals['idProduct']		= orderLine.product_id.id
			vals['strPackTemplate']	= self.template_id.name
			vals['idProductUOM']	= orderLine.product_uom.id
			vals['fQtyContracted']	= orderLine.product_uom_qty
			vals['fPriceUnit']		= orderLine.price_unit
			vals['fCostUnit']		= orderLine.x_fPriceProvider
			
			#strProviderName = dict(self._fields['self.x_eProvider'].selection).get(self.type)
			
			#encontrar el nombre de producto en proveedor 
			#supplierInfo = orderLine.product_id.product_tmpl_id.seller_ids.browse ([self.x_eProvider])
			supplierInfo = self.env["product.supplierinfo"].search ([
																	'&',
																	('product_tmpl_id', '=', orderLine.product_id.product_tmpl_id.id),
																	('name', '=', int ( self.x_eProvider))
																	])

			
			if supplierInfo:
				vals['strSupplierProductName'] = supplierInfo.product_name
			else:
				vals['strSupplierProductName'] = "ERR: proveedor no definido" 
			
			operationLine	= self.env["setir.operation.line"].create ( vals)

			#NOTE: strCategory ' is related field
			if operationLine.strCategory == "peaje":
				listToll.append ( operationLine.id)
			elif operationLine.strCategory == "medio de pago":
				listPM.append ( operationLine.id)
			elif operationLine.strCategory == "impuesto":
				listTax.append ( operationLine.id)
			elif operationLine.strCategory == "combustible":
				listFuel.append ( operationLine.id)
			else:
				listOther.append ( operationLine.id)

		#los productos del pedido a traspoasar a la operacion pueden ser solo de una categoria
		#por eso solo una de las listas será llena
		#en casos excepcionales la lsiats listOthersç puede ser llena tambien
		if len (listToll) > 0:
			operation.idResponsibleToll	= self.x_idOperationUser.id
		elif len (listTax) > 0:
			operation.idResponsibleTax	= self.x_idOperationUser.id


		#componer listas de las pestañas en funcion de la categorio de producto
		for id in listToll:
			operation.idsLineToll		= [(4, id, False)]

		for id in listPM:
			operation.idsLinePM			= [(4, id, False)]

		for id in listTax:
			operation.idsLineTax		= [(4, id, False)]

		for id in listFuel:
			operation.idsLineFuel		= [(4, id, False)]

		for id in listOther:
			operation.idsLineOther		= [(4, id, False)]


class setirOperationLine ( models.Model):
	_name			= "setir.operation.line"
	_description	= u"Línea de operación"

	bActive			= fields.Boolean (	string			= "Activa")
		
	idOperation		= fields.Many2one (	string			= u"Operación",
										comodel_name	= "setir.operation")
	
	idProvider		= fields.Many2one (	string			= "Proveedor",
										comodel_name	= "res.partner")
	idProduct		= fields.Many2one (	string			= "Producto",
										comodel_name	= "product.product")
	
	strCategory		= fields.Char (		string			= u"Categoría",
										related			= "idProduct.categ_id.name")

	strPackTemplate			= fields.Char (	string		= "Pack")
	strSupplierProductName	= fields.Char (	string		= "NPP")

	idProductUOM	= fields.Many2one ( string			= "UOM",
										comodel_name	= "product.uom")
	fQtyContracted	= fields.Float (	string			= "Cantidad contratada")
	fPriceUnit		= fields.Float (	string			= "Precio unidad")
	fCostUnit		= fields.Float (	string			= "Coste unidad")
	

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
											inverse			= "fillOrdersProviders"
										)

	fRiskApproved		= fields.Float ( string = 'Riesgo aprobado')
	
	idResonsibleGen		= fields.Many2one (
											string			= "Responsable General",
											comodel_name	= "res.users" 
											)
	idResonsibleToll	= fields.Many2one (
											string			= "Responsable Peaje",
											comodel_name	= "res.users" 
											)
	idResonsibleTax		= fields.Many2one (
											string			= "Responsable Impuestos",
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
	
	idsLineToll			= fields.Many2many (	string			= "Peajes",
												comodel_name	= "setir.operation.line", 
												relation		= "rel_operation_toll",
												column1			= "operation_id",
												column2			= "line_id",
												domain			= "[('idOperation','=', id),('strCategory', '=', 'peaje')]"
											)

	idsLinePM			= fields.Many2many (	string			= "Medios de pago",
												comodel_name	= "setir.operation.line",
												relation		= "rel_operation_pm",
												column1			= "operation_id",
												column2			= "line_id",
												domain			= "[('idOperation','=', id),('strCategory', '=', 'medio de pago')]"
											)
	idsLineTax			= fields.Many2many (	string			= "Medios de pago",
												comodel_name	= "setir.operation.line",
												relation		= "rel_operation_tax",
												column1			= "operation_id",
												column2			= "line_id",
												domain			= "[('idOperation','=', id),('strCategory', '=', 'impuesto')]"
											)
	idsLineFuel			= fields.Many2many (	string			= "Medios de pago",
												comodel_name	= "setir.operation.line",
												relation		= "rel_operation_fuel",
												column1			= "operation_id",
												column2			= "line_id",
												domain			= "[('idOperation','=', id),('strCategory', '=', 'combustible')]"
											)
	idsLineOther			= fields.Many2many (	string			= "Medios de pago",
												comodel_name	= "setir.operation.line",
												relation		= "rel_operation_other",
												column1			= "operation_id",
												column2			= "line_id",
												domain			= "[('idOperation','=', id),('strCategory', 'not in',\
																	 ['peaje','medio de pago','impuesto', 'combustible'])]"
											)

	@api.onchange ('idCustomer')
	def fillOrdersProviders ( self):
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

class setirPM ( models.Model):
	_name = "setir.pm"

	idOperation		= fields.Many2one	(
											string			= u"Operación",
											comodel_name	= "setir.operation"
										)

	idCustomer		= fields.Many2one	(
											string			= "Cliente",
											comodel_name	= "res.partner",
											domain			= "[('id', '=', idOperation.idCustomer)]"
										)
	idProvider		= fields.Many2one	(
											string			= "Proveedor",
											comodel_name	= "res.partner",
											domain			= "[('id', 'in', idOperation.idsProvider)]"
										)
	
	idProductPM		= fields.Many2one	(
											string			= "Medio de pago",
											comodel_name	= "product.product"
										)

	idAssociatedTollProduct	= fields.Many2one	(
											string			= "Producto peaje asociado",
											comodel_name	= "product.product"
										)
	ePMType			= fields.Selection	(
										string		= "Tipo",
										selection	= [('obu','obu'),
														('tarjeta', 'tarjeta')]
										)
	strPAN			= fields.Char		(	string			= "PAN")
	strSN			= fields.Char		(	string			= "SN")
	strPN			= fields.Char		(	string			= u"Matrícula asociada")

	dateSignUp		= fields.Date		(	string			= u"Fecha alta")
	dateExpiration	= fields.Date		(	string			= u"Fecha expiración")	
	dateUnsubscribe	= fields.Date		(	string			= u"Fecha baja")

	#estdos de registro PM
	eRegisterState	= fields.Selection	(	string		= "Estado registro",
											selection	= [('alta', 'alta'),
															('baja', 'baja')]	
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
	dtLastPMState		= fields.Datetime	( string		= "Fecha estado")
	idBlockReason		= fields.Many2one	(
											string			= "Causa de bloqueo",
											comodel_name	= "setir.pm.block.reason"
											)
	idsPMStateHistory	=	fields.Many2many	(
												string			= "Historial estados medio de pago",
												comodel_name	= "setir.pm.state.history", 
												relation		= "rel_pm_state_history",
												column1			= "pm_id",
												column2			= "history_id"
												)
	#estados de gestión PM
	idsPMManagenet		= fields.Many2one		(
												string			= u"Estado gestión",
												comodel_name	= "setir.pm.management"
												)
	dtLastPMManagement	= fields.Datetime		( string		= "Fecha estado")

	VALS = [
			('cliente', 'cliente'),
			('proveedor', 'proveedor'),
			('setir', 'setir')
			] 

	eLastSender			= fields.Selection	(
												string		= "Remitente",
												selection	= VALS
											)
	eLastReceiver		= fields.Selection	(
												string		= "Destinatario",
												selection	= VALS
											)
	idsPMManagementHist	= fields.Many2one		(
												string			= "Historial gestiones medio de pago",
												comodel_name	= "setir.pm.management.history", 
												relation		= "rel_pm_management_history",
												column1			= "pm_id",
												column2			= "history_id"
												)

class setirPMState ( models.Model):
	_name = "setir.pm.state"

	name            = fields.Char	( string = "Estado")
	strDescription  = fields.Char	( string = u"Descripción")

class setirPMStateHistory ( models.Model):
	_name = "setir.pm.state.history"
	
	idState	= fields.Many2one ( string			= "Estado",
								comodel_name	= "setir.pm.state")
	dtState	= fields.Datetime (	string	= "Fecha")	

class setirPMUnsubscribeReason ( models.Model):
	_name = "setir.pm.unsubscribe.reason"

	name            = fields.Char ( string = "Razón baja")

class setirPMBlockReason ( models.Model):
	_name = "setir.pm.block.reason"

	name            = fields.Char ( string = "Razón bloqueo")


class setirPMManagement ( models.Model):
	_name = "setir.pm.management"

	name		= fields.Char		( string = "Gestión")

class setirPMManagementHistory ( models.Model):
	_name = "setir.pm.management.history"

	idManagement	= fields.Many2one ( string			= "Gestión",
										comodel_name	= "setir.pm.management")
	dtManagemen	= fields.Datetime 	(	string	= "Fecha")	

	VALS = [
			('cliente', 'cliente'),
			('proveedor', 'proveedor'),
			('setir', 'setir')
			] 

	eSender		= fields.Selection	(
									string		= "Remitente",
									selection	= VALS
									)
	eReceiver	= fields.Selection	(
									string		= "Destinatario",
									selection	= VALS
									)
