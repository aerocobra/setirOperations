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
from setirDefinitions import *

class setirProduct ( models.Model):
	_inherit			= "product.template"
	
	idsRelatedServices	=	fields.Many2many	(	string			= "Servicios asociados",
													comodel_name	= "product.template",
													relation		= "rel_pm_service",
													column1			= "pm_id",
													column2			= "service_id")

class setirPartnerOperation ( models.Model):
	_inherit		= "res.partner"

	idInvoicingType				= fields.Many2one	(	string			= u"Tipo facturación",
														comodel_name	= "setir.invoicing.type")
	strInvoicngTypeDescription	= fields.Char		(	string			= u"Descripción",
														related			= "idInvoicingType.strDescription")
	idsProviderCode				= fields.One2many	(	string			= u"Código proveedor",
														comodel_name	= "setir.customer.provider.code",
														inverse_name	= "idCustomer"
													)
	
	#dict (DEF_ADDRESS_TYPE)["invoice"])])
	@api.one	
	def getAddress (self, strAddressType):
		recordset = self.child_ids.search([('type', '=', strAddressType)])
		if recordset:
			record	= recordset[0]
		else:
			record	= self
		
		address = {}
		
		

#codigos que dan los proveedores a los clientes    
class setirPartnerCustomerCodes ( models.Model):
	_name			= "setir.customer.provider.code"
	
	idCustomer		= fields.Many2one	(	string			= "Cliente",
											comodel_name	= "res.partner",
											domain			= "[('is_company', '=', True), ('customer', '=', True)]"
										)
	strCustomer		= fields.Char		(	related			= "idCustomer.name")
	
	idProvider		= fields.Many2one	(	string			= "Proveedor",
											comodel_name	= "res.partner",
											domain			= "[('is_company', '=', True), ('supplier', '=', True)]"
										)
	strProvider		= fields.Char		(	related			= "idProvider.name")
	
	strProviderCode	= fields.Char		(	string	 		= u"Código proveedor")

class setirInvocingType ( models.Model):
	_name	= "setir.invoicing.type"

	name			= fields.Char (			string		= u"Tipo Facturación")
	strDescription	= fields.Char (			string		= u"Descripción")

	eConsumos		= fields.Selection (	string		= "Consumos", 
											selection	= INVOICING_TYPE)
	eCoste			= fields.Selection (	string		= "Coste",
											selection	= INVOICING_TYPE)
	eBeneficio		= fields.Selection (	string		= "Beneficio",
											selection	= INVOICING_TYPE)

class setirSaleOrderOperation ( models.Model):
	_inherit		= "sale.order"

	@api.one
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
			#operation.fillOrdersProviders()
			
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
			vals['idAssocPackTmpl']	= self.template_id.id
			
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
			elif operationLine.strCategory in ["obu", "tarjeta", "activacion"]:
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

	idAssocPackTmpl	= fields.Many2one	(
											string			= "Pack peaje asociado",
											comodel_name	= "sale.quote.template"
										)
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
	_order			= 'name desc, idCustomer desc'

	name			= fields.Char ( string	= u"Operación",
									default	= lambda self: _('New'))

	idCustomer			= fields.Many2one	(
											string			= "Cliente",
											comodel_name	= "res.partner",
											inverse			= "fillOrdersProviders"
										)

	fRiskApproved		= fields.Float ( 	string			= 'Riesgo aprobado')
	
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

	bActive				= fields.Boolean ( string = u"Operación activa")

	dateSignUp			= fields.Date ( 	string = "Fecha Alta")
	dateUnsubscribe		= fields.Date ( 	string = "Fecha Baja")
	idUnsubscribeReason	= fields.Many2one	(
											string			= u"Razón de baja",
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

	strComment			= fields.Text 		( 	string = 'Notas internas')
	
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
	idsLineTax			= fields.Many2many (	string			= "Impuestos",
												comodel_name	= "setir.operation.line",
												relation		= "rel_operation_tax",
												column1			= "operation_id",
												column2			= "line_id",
												domain			= "[('idOperation','=', id),('strCategory', '=', 'impuesto')]"
											)
	idsLineFuel			= fields.Many2many (	string			= "Combustible",
												comodel_name	= "setir.operation.line",
												relation		= "rel_operation_fuel",
												column1			= "operation_id",
												column2			= "line_id",
												domain			= "[('idOperation','=', id),('strCategory', '=', 'combustible')]"
											)
	idsLineOther			= fields.Many2many (	string			= "Otros",
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

	@api.multi
	def createPM (self):
		for operationLine in self.idsLinePM:
			if operationLine.strCategory == PM_TYPE_OBU or operationLine.strCategory == PM_TYPE_TARJETA:
				for i in range ( int (operationLine.fQtyContracted)):
					self.registerPM ( operationLine.idProvider.id, operationLine.idProduct.id, operationLine.idAssocPackTmpl.id)
			
	#cree registros vacios de los PM vendidios 
	@api.one
	def registerPM (self, idProvider, idProduct, idAssocPackTmpl):
		vals = {}
		vals['idOperation']				= self.id
		vals['idCustomer']				= self.idCustomer.id
		vals['idProvider']				= idProvider
		vals['idProduct']				= idProduct
		vals['idAssocPackTmpl']			= idAssocPackTmpl
		#name
		#strPAN 
		#strSecondaryPAN
		#strPN
		#idCountry
		#strSN
		#strSecondarySN
		vals['dtSignUp']				= fields.Datetime.now()
		#dateExpiration	
		#dtUnsubscribe
		vals['eRegisterState']			= REGISTER_STATE_ALTA
		
		#estado del propio PM
		idsPMState 						= self.env['setir.import.base'].search([('eImportType', '=', IMPORT_TYPE_ESTADO),
																				('name', '=', dict (PM_STATE)[PM_STATE_ESPERA])])[0].id	
		vals['idsPMState']				= idsPMState

		#estados de gestión PM
		idsPMManagement					= self.env['setir.pm.management'].search([('name', '=', ESTADO_GESTION_SOLICITADO)])[0].id
		vals['idsPMManagement']			= idsPMManagement

		pm								= self.env['setir.pm'].create ( vals)
		
		pm.addPMStateHistory ( idsPMState)
		pm.addPMManagementHistory (idsPMManagement, ACTOR_SETIR, ACTOR_SETIR)
