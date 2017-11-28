# -*- coding: utf-8 -*-
#setirImportWizardPM.py

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

class setirImportWizardInvoice ( models.TransientModel):
	_name			= "setir.import.wizard.invoice"
	_inherit		= "setir.import.wizard"
	_description	= u"Importación factuarción"


class setirPMtt ( models.TransientModel):
	_name			= "setir.pm.tt"
	#_inherit		= "setir.pm"
	_description	= "Medio de pago import temportal"
	#_order			= 'idCustomer desc, dtSignUp desc'
	
	b2Import		= fields.Boolean	(	string			= "Importar")
	eImportAction	= fields.Selection	(	string			= u"Acción",
											selection		= IMPORT_ACTION)
	nID2Update		= fields.Integer	(	string			= "ID2U")
	idWizardPM		= fields.Many2one 	(	string			= "Wizard",
											comodel_name	= "setir.import.wizard.pm")
	strInfo			= fields.Text		(	string			= "Información de importación")

	
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
	
	idProduct		= fields.Many2one	(	string			= "Producto",
											comodel_name	= "product.product")
	strPMType		= fields.Char		(	string			= "Tipo",
											related			= "idProduct.categ_id.name")

	idAssocPackTmpl	= fields.Many2one	(
											string			= "Pack peaje asociado",
											comodel_name	= "sale.quote.template"
										)
	strPAN			= fields.Char		(	string			= "PAN")
	name			= fields.Char		(	string			= u"OBU ID")
	strSecondaryPAN	= fields.Char		(	string			= "PAN Secundario")

	strPN			= fields.Char		(	string			= u"Matrícula asociada")
	idCountry		= fields.Many2one	(	string			= u"País",
											comodel_name	= "res.country"
										)
	strSN			= fields.Char		(	string			= "SN")
	strSecondarySN	= fields.Char		(	string			= "SN Secundario")

	dtSignUp		= fields.Datetime	(	string			= u"Fecha alta")
	dtCreation		= fields.Datetime	(	string			= u"Fecha creación")
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
	idsPMState			=	fields.Many2one	(
											string			= "Estado MP",
											comodel_name	= "setir.import.base",
											domain			= "[('eImportType','=','estado')]"
											)
	strPMState			=	fields.Char		(
											string = "state",
											related = "idsPMState.name"
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


class setirImportWizardPM ( models.TransientModel):
	_name			= "setir.import.wizard.pm"
	_inherit		= "setir.import.wizard"
	_description	= u"Importación medios de pago"

	#name			= fields.Char
	#strFile2Import	= fields.Char
	#strData		= fields.Text

	idsPM2Import	= fields.One2many	(
										string			= "MP a importar",
										comodel_name	= "setir.pm.tt",
										inverse_name	= "idWizardPM"
										)

	@api.multi
	def checkFile (self):

		import_id		= self.env.context.get ('active_ids', True)[0]
		currentImport	= self.env["setir.import"].search([('id','=', import_id)])

		if not currentImport.idProvider:
			strERR	= "Es necesario seleccionar un proveedor"
			_logger.error ( strERR)
			raise exceptions.ValidationError ( strERR)
		
		if not currentImport.eMonth:
			strERR	= "Es necesario seleccionar un mes"
			_logger.error ( strERR)
			raise exceptions.ValidationError ( strERR)

		strPathBase		= self.env["ir.config_parameter"].search([("key","=", PATH_ROOT)])[0].value
		strPathProvider = self.env["res.partner"].search([("id","=", currentImport.idProvider.id)])[0].name
		strPathYear		= "{}".format(date.today().year) 
		strPathMonth	= str (currentImport.eMonth)
		strPathPM		= self.env["ir.config_parameter"].search([("key","=", PATH_PM)])[0].value

		strPath			= strPathBase + "/" + strPathProvider + "/" + strPathYear + "." + strPathMonth + "/" + strPathPM   

		if ( not os.path.exists (strPath)):
			strERR	= "Rutra no existe [" + strPath + "]"
			_logger.error ( strERR)
			raise exceptions.ValidationError ( strERR)
		
		l = os.listdir ( strPath)
		if l == 0:
			strERR	= "Ruta existe, no hay archivos"
			_logger.error ( strERR)
			raise exceptions.ValidationError ( strERR)

		strFile = ""
		for r in l:
			if r.endswith (".csv"):
				if len (strFile) > 0:
					strERR	= u"Más de un archivo csv - debe haber solo uno en la carpeta"
					_logger.error ( strERR)
					raise exceptions.ValidationError ( strERR)
				else:
					strFile = r

		self.strFile2Import = strPath + "/" + strFile 
	
		return {'type': "ir.actions.do_nothing",}
	
	def formatINFO (self, strError, strAction, strTodo):
		return u"INF: {}, ACT: {}, TODO: {}".format( strError, strAction, strTodo)

	@api.multi
	def saveImport (self):
		self.checkFile()
		
		import_id		= self.env.context.get ('active_ids', True)[0]
		currentImport	= self.env["setir.import"].search([('id','=', import_id)])[0]
		
		#lista única de los clientes
		customer_ids		= []
		for record in self.idsPM2Import:
			if  not dict ( customer_ids).get ( record.idCustomer.id):
				customer_ids.append ( ( record.idCustomer.id, record.idCustomer.name))

		for customer in customer_ids:
			#lista única de proveedores por clinete 
			provider_ids	= []
			for record in self.idsPM2Import.search([	('idCustomer',	'=', customer[0]),
														('b2Import',	'=', True)]):
				if  not dict ( provider_ids).get ( record.idProvider.id):
					provider_ids.append ( ( record.idProvider.id, record.idProvider.name))

			for provider in provider_ids:
				#lista unica de peoductos por cliente y proveedor
				product_ids	= []
				for record in self.idsPM2Import.search([	('idCustomer',		'=', customer[0]),
															('b2Import',		'=', True),
															('idProvider',		'=', provider[0])]):
					if  not dict ( product_ids).get ( record.idProduct.id):
						product_ids.append ( ( record.idProduct.id, record.idProduct.name))

				for product in product_ids:
					for record in self.idsPM2Import.search([	('idCustomer',		'=', customer[0]),
																('b2Import',		'=', True),
																('idProvider',		'=', provider[0]),
																('idProduct',		'=', product[0])]):

						vals2Create	= {}

						vals2Create["name"]				= record.name
						vals2Create["strPAN"]			= record.strPAN
						vals2Create["strSecondaryPAN"]	= record.strSecondaryPAN
						vals2Create["strPN"]			= record.strPN
						vals2Create["idCountry"]		= record.idCountry.id
						vals2Create["strSN"]			= record.strSN
						vals2Create["strSecondarySN"]	= record.strSecondarySN
						vals2Create["dtSignUp"]			= record.dtSignUp
						vals2Create["dtCreation"]		= record.dtCreation
						vals2Create["dateExpiration"]	= record.dateExpiration	
						vals2Create["dtUnsubscribe"]	= record.dtUnsubscribe
						vals2Create["idsPMState"]		= record.idsPMState.id

						#estados de gestión PM
						idsPMManagement					= self.env['setir.pm.management'].search([('name', '=', ESTADO_GESTION_RECIBIDO)])[0].id
						vals2Create['idsPMManagement']	= idsPMManagement

						if record.eImportAction == IMPORT_ACTION_CREATE:
							vals2Create["idOperation"]		= record.idOperation.id
							vals2Create["idCustomer"]		= record.idCustomer.id
							vals2Create["idProvider"]		= record.idProvider.id
							vals2Create["idProduct"]		= record.idProduct.id
							vals2Create["idAssocPackTmpl"]	= record.idAssocPackTmpl.id
							vals2Create["eRegisterState"]	= record.eRegisterState
							
							pmNew		= self.env["setir.pm"].create ( vals2Create)
						else:
							id2Update	= record.nID2Update
							pmNew		= self.env["setir.pm"].search ([('id', '=', id2Update)]).update ( vals2Create)
						
						pmNew.addPMStateHistory ( vals2Create["idsPMState"])
						pmNew.addPMManagementHistory (vals2Create['idsPMManagement'], ACTOR_PROVEEDOR, ACTOR_CLIENTE)
						
					nProductImported	= self.env["setir.pm"].search_count([	('idCustomer',	'=', customer[0]),
																				('idProvider',	'=', provider[0]),
																				('idProduct',	'=', product[0])])
					
					operation			= self.env["setir.operation"].search ([('idCustomer', '=', customer[0])])[0]
					operationLine 		= operation.idsLinePM.search ([('idProvider', '=', provider[0]), ('idProduct', '=', product[0])])[0]
					nProductContracted	= int ( operationLine.fQtyContracted)

					if  nProductImported != nProductContracted: 
						operationLine.fQtyContracted = nProductImported 
						strINFO	=	self.formatINFO (	u"CLIENTE:[{}], PROVEEDOR:[{}], OBU OPERACIÓN:[{}] no coincode con OBU IMPORTADO:[{}]",
														u"actualizada la cantidad OBU en la operación",
														u"comprobar la operación").format( customer[1], provider[1], nProductContracted, nProductImported)
						_logger.debug ( strINFO)
						self.strData += "============================" + os.linesep + strINFO + os.linesep
				#FOR por producto
			#FOR por proveedor
		#for por cliente

		# add history
		historyVals						= {}

		historyVals["idImport"] 		= currentImport.id
		historyVals["dtImport"]			= fields.Datetime.now()
		historyVals["strFileImported"]	= self.strFile2Import
		historyVals["strImportInfo"]	= self.strData
		
		self.env["setir.import.history"].create ( historyVals)
		
		currentImport.dtLastImport		= historyVals["dtImport"]
		
		self.bSaveImport				= False

		return {'type': "ir.actions.do_nothing",}
	
	@api.multi
	def importFile (self):
		self.checkFile()

		self.bSaveImport	= False
				
		import_id			= self.env.context.get ('active_ids', True)[0]
		currentImport		= self.env["setir.import"].search([('id','=', import_id)])[0]
		
		pm2Update			= self.env["setir.pm.tt"]
		pm2Update.search([]).unlink()
		
		incidents			= []

		#obtener el mapa de campos
		importMap = self.env["setir.import.map"].search ([("idProvider", "=", currentImport.idProvider.id), ("eImportType", "=", IMPORT_TYPE_MP)])
		if not importMap:
			
			strINFO	=	self.formatINFO (	u"Mapa de importación de medios de pago no existe para PROVEEDOR[{}]",
											u"importación interrumpida",
											u"crear el mapa").format( currentImport.idProvider.name)
			_logger.error ( strINFO)
			raise exceptions.ValidationError ( strINFO)

		mapFieldREG_EDI=[]
		for record in importMap.idsMapLine:
			mapFieldREG_EDI.append ((record.idFieldBase.name, record.idFieldProvider.name))

		productMap		= self.env["setir.product.import.map"].search([	('idProvider', '=', currentImport.idProvider.id),
																		('eImportType', '=', IMPORT_PRODUCT_CATEGORY_MP)])

		if not productMap:
			strINFO	=	self.formatINFO (	u"No exise el mapa de productos relacionados, proveedor:[{}]",
											u"importación interrumpida",
											u"crear el mapa de productos relacionados").format( currentImport.idProvider.name)
			_logger.error ( strINFO)
			raise exceptions.ValidationError ( strINFO)

		mapProductsEDI_REG	= []
		for record in productMap.idsMapLine:
			mapProductsEDI_REG.append ( ( record.idFieldProvider.name, record.idFieldBase.id))

		#esto es el propio mapa de campos del archivo
		sizeMap		= len (mapFieldREG_EDI)
		strHeader	= "[BASE][PROVEEDOR]" + os.linesep
		_logger.debug ( strHeader)
		#imprimir campos con sus correspondencias (a quitar en futuro)
		for i in range ( sizeMap):
			strHeader	+= "[" + mapFieldREG_EDI[i][0] + "] " + "[" + mapFieldREG_EDI[i][1] + "] " + os.linesep
			_logger.debug ( strHeader)

		#COMIENZO TRABAJO CON ARCHIVO A IMPORTAR
		#"utf-8-sig" - sig es necesario para quitar BOM (caracteres sepeciales que se ponen a principio)
		with codecs.open ( self.strFile2Import, mode="r", encoding="utf-8-sig") as csvfile:
			dial			= csv.Sniffer().sniff(csvfile.read(1024))
			csvfile.seek(0)
			reader			= csv.DictReader(csvfile, delimiter=";", quoting=csv.QUOTE_NONE, dialect=dial)
			
			strAllRows		= ""
			#iterar por filas del archivo
			for row in reader:
				archVals				= {}
				archVals["idWizardPM"]	= self.id
				archVals["idProvider"]	= currentImport.idProvider.id
				archVals["b2Import"]	= True

				strCustomer				= ""
				strNIF					= "sin NIF"
				strCODE					= "sin CODE"
				# 1. encontrar CLIENTE
				# si en el mapa esta presene el NIF, buscamos por el NIF  
				customerNIF		= dict(mapFieldREG_EDI).get (FIELD_NIF_CLIENTE)
				if customerNIF:
					strNIF		= row[customerNIF.encode('utf-8')]
					if self.env["res.partner"].search ([('vat', '=', strNIF)]):
						archVals["idCustomer"]	= self.env["res.partner"].search ([('vat', '=', strNIF), ('customer', '=', True)])[0].id
						strCustomer				= self.env["res.partner"].search ([('vat', '=', strNIF), ('customer', '=', True)])[0].name
				# si en el mapa esta presente el código de cliente, buscamops tambien el código
				customerCODE	= dict(mapFieldREG_EDI).get (FIELD_CODIGO_CLIENTE_PROVEEDOR)
				if customerCODE:
					strCODE		= row[customerCODE.encode('utf-8')]
					# si por el NIF no se encontró el cliente, intentamos buscar por el código ciente  
					if not strCustomer:
						if self.env["setir.customer.provider.code"].search ([('strProviderCode', '=', strCODE)]):
							archVals["idCustomer"]	= self.env["setir.customer.provider.code"].search ([('strProviderCode', '=', strCODE),
																										('idProvider', '=', currentImport.idProvider.id)])[0].idCustomer.id
							strCustomer				= self.env["setir.customer.provider.code"].search ([('strProviderCode', '=', strCODE),
																										('idProvider', '=', currentImport.idProvider.id)])[0].idCustomer.name

				if not strCustomer:
					#cliente en la fila actual no esta registrado en la BBDD 
					#recordadmos la info y vamos a la siguiente fila del archivo
					strINFO	=	self.formatINFO (	u"cliente del MP no registrado nombre:[{}] nif:[{}] código proveedor:[{}]",
													u"linea de archivo no importada",
													u"dar de alta al cliente en el sistema").format( strCustomer, strNIF, strCODE)
					incidents.append ( ( strINFO))
					_logger.debug ( strINFO)
					archVals["b2Import"]	= False
					archVals["strInfo"]		= strINFO
					pm2Update.create ( archVals)
					continue

				operation = self.env["setir.operation"].search ([('idCustomer', '=', archVals["idCustomer"])])
				
				if not operation:
					strINFO	=	self.formatINFO (	u"Operación no existe, cliente:[{}] nif:[{}] código cliente:[{}]",
													u"linea de archivo no importada",
													u"crear operación para el cliente").format( strCustomer, strNIF, strCODE)
					incidents.append ( ( strINFO))
					_logger.debug ( strINFO)
					archVals["b2Import"]	= False
					archVals["strInfo"]		= strINFO
					archVals["idOperation"] = -1
					pm2Update.create ( archVals)
					continue
				else:
					archVals["idOperation"] = operation[0].id

				X_PM_ID				= 0
				X_PM_PRODUCT_ID		= 1
				X_PM_PRODUCT_NAME	= 2
				X_PM_PROVIDER_ID	= 3
				X_PM_STATE_ID		= 4
				# 2. encontrar todos los MP REGISTRADOS de este cliente
				registeredPM	= []
				for record in self.env["setir.pm"].search ([('idCustomer', '=', archVals["idCustomer"])]):
					registeredPM.append ((record.name, (	record.id,
															record.idProduct.id,
															record.idProduct.name,
															record.idProvider.id,
															record.idsPMState.id)))
					
				#obtener el estado del MP del archivo
				strNewStateProvider	= "" 
				strNewStateBase		= ""
				
				if row.get (dict(mapFieldREG_EDI).get ( FIELD_ESTADO_MEDIO_PAGO).encode('utf-8')):
					strNewStateProvider	= row[dict(mapFieldREG_EDI).get ( FIELD_ESTADO_MEDIO_PAGO).encode('utf-8')]
				mapStates = self.env['setir.import.map'].search([	('eImportType','=', IMPORT_TYPE_ESTADO),
																	('idProvider', '=', archVals["idProvider"])])
				if not mapStates:
					strINFO	=	self.formatINFO (	u"Mapa de estados no existe, proveedor:[{}] estado:[{}]",
													u"importación interrumpida",
													u"crear el mapa de estados").format( currentImport.idProvider.name, strNewStateProvider)
					incidents.append ( ( strINFO))
					_logger.error ( strINFO)
					raise exceptions.ValidationError ( strINFO)
				
				for stateCorrespondence in self.env['setir.import.line'].search([('idImportMap','=', mapStates[0].id)]):
					if stateCorrespondence.idFieldProvider.name == strNewStateProvider:
						#encontrada la correspondencia del estado proveedor en el archivo EDI 
						strNewStateBase	= stateCorrespondence.idFieldBase.name
						archVals["idsPMState"] = self.env['setir.import.base'].search([	('eImportType','=', IMPORT_TYPE_ESTADO),
																						('name', '=', strNewStateBase)])[0].id
						break

				if len ( strNewStateBase) == 0:
					strINFO	=	self.formatINFO (	u"Estado no registrado en el mapa, proveedor:[{}] estado:[{}] mapa:[{}]",
													u"importación iterrumpida",
													u"añadir el estado en el mapa").format( currentImport.idProvider.name, strNewStateProvider, mapStates[0].name)
					incidents.append ( ( strINFO))
					_logger.error ( strINFO)
					raise exceptions.ValidationError ( strINFO)

				#3. encontrar PRODUCTO RELACIONADO
				if not row.get (dict(mapFieldREG_EDI).get (FIELD_RELATED_PRODUCT).encode('utf-8')):
					strINFO	=	self.formatINFO (	u"No esta mapeado el campo 'producto_relacionado' en el mapa:[{}]",
													u"importación interrumpida",
													u"revisar y mapear el campo 'producto_relacionado'").format( importMap.name)
					_logger.error ( strINFO)
					raise exceptions.ValidationError ( strINFO)
				
				strEDI_RelatedPorduct	= row[dict(mapFieldREG_EDI).get (FIELD_RELATED_PRODUCT).encode('utf-8')]

				
				if not dict(mapProductsEDI_REG).get ( strEDI_RelatedPorduct):
					strINFO	=	self.formatINFO (	u"El producto relacionado no esta mapeado, el producto EDI:[{}]",
													u"importación interrumpida",
													u"mapear el producto relacionado").format( strEDI_RelatedPorduct)
					_logger.error ( strINFO)
					raise exceptions.ValidationError ( strINFO)

				archVals["idProduct"]		= dict(mapProductsEDI_REG).get ( strEDI_RelatedPorduct)
				
				strProduct	= self.env["product.product"].search([('id', '=', archVals["idProduct"])])[0].name

				#comprobamos si el producto estña registrado en la operación 
				operationLine 		= operation.idsLinePM.search ([('idProvider', '=', archVals["idProvider"]), ('idProduct', '=', archVals["idProduct"])])
				if not operationLine:
					strINFO	=	self.formatINFO (	u"Producto no registrado en la operación:[{}], cliente:[{}], producto:[{}], proveedor:[{}]",
													u"medio de pago no importado",
													u"comprobar la operación").format (	operation.name,
																						strCustomer,
																						strProduct,
																						currentImport.idProvider.name)
					_logger.error ( strINFO)
					incidents.append ( ( strINFO))
					archVals["b2Import"]	= False
					archVals["strInfo"]		= strINFO
					pm2Update.create ( archVals)
					continue

				#encontrar FIELD_PM_ID
				archVals["name"]	= row[dict(mapFieldREG_EDI).get (FIELD_PM_ID).encode('utf-8')]

				#encontrar PAN
				archVals["strPAN"]	= row[dict(mapFieldREG_EDI).get (FIELD_PAN).encode('utf-8')]

				#ver si es un MP nuevo o ya registrado.
				if not dict ( registeredPM).get (archVals["name"]):
					#PM encontrado no esta registado => ALTA
					archVals["eImportAction"]	= IMPORT_ACTION_CREATE
					archVals["eRegisterState"]	= REGISTER_STATE_ALTA

					strINFO						=	self.formatINFO (	u"nuevo PM no registrado, cliente:[{}]  ID:[{}] pan:[{}]",
																		u"dar de alta MP nuevo",
																		u"nada").format( strCustomer, archVals["name"], archVals["strPAN"])
					incidents.append ( ( strINFO))
					_logger.debug ( strINFO)
					archVals["strInfo"]		= strINFO
				else:
					#PM esta registrado  => comprobar el ESTADO del medio de pago 
					#en los registrados solo se hace la actualización de ESPERA a ACTIVO, el resto de actualziaciones no se hacen 
					strRegisteredState	= self.env['setir.import.base'].search([('id','=',dict( registeredPM)[archVals["name"]][X_PM_STATE_ID])])[0].name
					if strRegisteredState != strNewStateBase:
						if strRegisteredState == PM_STATE_ESPERA and strNewStateBase == PM_STATE_ACTIVO:
							strINFO	=	self.formatINFO (	u"cambio de estado permitido, cliente:[{}] ID:[{}] producto :[{}] estadoOLD:[{}] estadoNEW:[{}]",
															u"actualizar Medio de pago",
															u"no es necesario hacer nada").format( strCustomer, archVals["name"],
																								dict( registeredPM)[archVals["name"]][X_PM_PRODUCT_NAME],
																								strRegisteredState, strNewStateBase)
							incidents.append ( ( strINFO))
							_logger.debug ( strINFO)
							archVals["nID2Update"]		= dict( registeredPM)[archVals["name"]][X_PM_ID]
							archVals["eImportAction"]	= IMPORT_ACTION_UPDATE
							archVals["strInfo"]			= strINFO
						else:
							strINFO	=	self.formatINFO (	u"cambio inesperado de estado, cliente:[{}] ID:[{}] producto :[{}] estadoOLD:[{}] estadoNEW:[{}]",
															u"linea de archivo no importada",
															u"comprobar el estado").format( strCustomer, archVals["name"],
																							dict( registeredPM)[archVals["name"]][X_PM_PRODUCT_NAME],
																							strRegisteredState, strNewStateBase)
							incidents.append ( ( strINFO))
							_logger.debug ( strINFO)
							archVals["b2Import"]	= False
							archVals["strInfo"]		= strINFO
							pm2Update.create ( archVals)
							continue
					else:
						strINFO	=	self.formatINFO (	u"no hay cambio inesperado , cliente:[{}] ID:[{}] producto :[{}] estadoOLD:[{}] estadoNEW:[{}]",
														u"linea de archivo no importada",
														u"no hay que hacer nada").format( strCustomer, archVals["name"],
																						dict( registeredPM)[archVals["name"]][X_PM_PRODUCT_NAME],
																						strRegisteredState, strNewStateBase)
						incidents.append ( ( strINFO))
						_logger.debug ( strINFO)
						archVals["b2Import"]	= False
						archVals["strInfo"]		= strINFO
						pm2Update.create ( archVals)
						continue
					

				#campos ya extradidos: idCustomer, strPAN
				self.bSaveImport	= True
				strFormatoFecha		= FORMATO_FECHA_ESTANDAR
				formatoFecha		= self.env['setir.import.map'].search([	('eImportType','=', IMPORT_TYPE_FORMATO_FECHA),
																			('idProvider', '=', archVals["idProvider"]),
																			('name', '=', IMPORT_TYPE_FORMATO_FECHA)
																			])
				
				if not formatoFecha:
					strINFO	=	self.formatINFO (	u"formato de fecha no defenido, proveedor:[{}]",
													u"aplicado el formato fecha estándar:[" + FORMATO_FECHA_ESTANDAR + "]",
													u"definir el formato de fecha para el proveedor").format( currentImport.idProvider.name)
					incidents.append ( ( strINFO))
					_logger.debug ( strINFO)
				else:
					strFormatoFecha	= formatoFecha[0].name 

				# setir.operation.line					
				for linePM in operation.idsLinePM:
					if linePM.idProvider.id == archVals["idProvider"] and linePM.idProduct.id == archVals["idProduct"]: 
						archVals["idAssocPackTmpl"]	= linePM.idAssocPackTmpl.id
						break

				if dict(mapFieldREG_EDI).get ( FIELD_PAN_SECUNDARIO):
					if row.get (dict(mapFieldREG_EDI).get ( FIELD_PAN_SECUNDARIO).encode('utf-8')):
						archVals["strSecondaryPAN"]	= row[dict(mapFieldREG_EDI).get ( FIELD_PAN_SECUNDARIO).encode('utf-8')]
					
				if dict(mapFieldREG_EDI).get ( FIELD_MATRICULA_ASOCIADA):
					if row.get (dict(mapFieldREG_EDI).get ( FIELD_MATRICULA_ASOCIADA).encode('utf-8')):
						archVals["strPN"]	= row[dict(mapFieldREG_EDI).get ( FIELD_MATRICULA_ASOCIADA).encode('utf-8')]
				
				if dict(mapFieldREG_EDI).get ( FIELD_PAIS_DE_MATRICULA):
					if row.get ( dict(mapFieldREG_EDI).get ( FIELD_PAIS_DE_MATRICULA).encode('utf-8')):
						strCountry	= row[dict(mapFieldREG_EDI).get ( FIELD_PAIS_DE_MATRICULA).encode('utf-8')]
						if len (strCountry) == 2:
							#es codigo pais
							strCampo	= "code"
						else:
							strCampo	= "name"
						
						country = self.env['res.country'].search([(strCampo, '=', strCountry)]) 
						if not country:
							strINFO	=	self.formatINFO (	u"País no encontrado, cliente:[{}] pan:[{}] pais:[{}]",
															u"linea de archivo no importada",
															u"revisar el archivo y el código de país").format( strCustomer, archVals["strPAN"], strCountry)
							incidents.append ( ( strINFO))
							_logger.debug ( strINFO)
							#archVals["b2Import"]	= False
							archVals["strInfo"]		= strINFO
							#continue
						
						archVals["idCountry"] = country[0].id

				if dict(mapFieldREG_EDI).get ( FIELD_NUMERO_SERIE) != None:
					if row.get (dict(mapFieldREG_EDI).get ( FIELD_NUMERO_SERIE).encode('utf-8')) != None:
						archVals["strSN"]	= row[dict(mapFieldREG_EDI).get ( FIELD_NUMERO_SERIE).encode('utf-8')]

				if dict(mapFieldREG_EDI).get ( FIELD_NUMERO_SERIE_SECUNDARIO) != None:
					if row.get (dict(mapFieldREG_EDI).get ( FIELD_NUMERO_SERIE_SECUNDARIO).encode('utf-8')) != None:
						archVals["strSecondarySN"]	= row[dict(mapFieldREG_EDI).get ( FIELD_NUMERO_SERIE_SECUNDARIO).encode('utf-8')]

				#FECHAS
				dtSignUp	= None
				if dict(mapFieldREG_EDI).get ( FIELD_FECHA_ALTA) != None:
					if row.get (dict(mapFieldREG_EDI).get ( FIELD_FECHA_ALTA).encode('utf-8')) != None:
						dtSignUp 	= archVals["dtSignUp"]	= datetime.strptime ( row[dict(mapFieldREG_EDI).get ( FIELD_FECHA_ALTA).encode('utf-8')],
																			strFormatoFecha)

				if dict(mapFieldREG_EDI).get ( FIELD_FECHA_CREACION) != None:
					if row.get (dict(mapFieldREG_EDI).get ( FIELD_FECHA_CREACION).encode('utf-8')) != None:
						archVals["dtCreation"]	= datetime.strptime ( row[dict(mapFieldREG_EDI).get ( FIELD_FECHA_CREACION).encode('utf-8')],
																			strFormatoFecha)
						if dtSignUp == None:
							archVals["dtSignUp"] = archVals["dtCreation"]  

				if dict(mapFieldREG_EDI).get ( FIELD_FECHA_EXPIRACION) != None:
					if row.get (dict(mapFieldREG_EDI).get ( FIELD_FECHA_EXPIRACION).encode('utf-8')) != None:
						archVals["dateExpiration"]	= datetime.strptime ( row[dict(mapFieldREG_EDI).get ( FIELD_FECHA_EXPIRACION).encode('utf-8')],
																			strFormatoFecha)

				if dict(mapFieldREG_EDI).get ( FIELD_FECHA_BAJA) != None:
					if row.get (dict(mapFieldREG_EDI).get ( FIELD_FECHA_BAJA).encode('utf-8')) != None:
						archVals["dtUnsubscribe"]	= datetime.strptime ( row[dict(mapFieldREG_EDI).get ( FIELD_FECHA_BAJA).encode('utf-8')],
																			strFormatoFecha)
					
				pm2Update.create ( archVals)

				#recorrer todos los campos de la fila
				strRow	= ""
				#for i  in range ( len (archVals)):
				#	strRow	+= "[" + str ( archVals.items()[i][0]) + "]"
					
				#strAllRows += "=[" + strCustomer + "]=" +  strRow +  os.linesep

				#strRow	= ""
				for i  in range ( len (archVals)):
					strRow	+= "[" + str ( archVals.items()[i][1]) + "]"
					
				strAllRows += "=[" + strCustomer + "]=" +  strRow +  os.linesep

		strInc			= ""
		sizeIncidents 	= len (incidents)
		for i in range (sizeIncidents):
			strInc	+= "[" + incidents[i] + "]" + os.linesep

		strAllRows += "=================" + os.linesep + strInc + os.linesep 
		self.strData = strAllRows
		
		return {'type': "ir.actions.do_nothing",}

class setirUnsubscribeWizardPM ( models.TransientModel):
	_name				= "setir.unsubscribe.wizard.pm"
	_description		= u"Baja medios de pago"

	name				= fields.Char		(	string			= "ids")
	idUnsubscribeReason	= fields.Many2one	(	string			= "Causa de baja",
												comodel_name	= "setir.pm.unsubscribe.reason")

	idsPM2Unsubscribe	= fields.Many2many	(	string			= "Medios d pago",
												comodel_name	= "setir.pm",
												readonly		= True)

	strEmailBody		= fields.Text		(	string			= "Texto email")
	
	@api.multi
	def create (self, vals):
		ids2Unsubscribe	= self.env.context.get ('active_ids', False)

		records2Unsubscribe	= self.env["setir.pm"].search ([('id', 'in', ids2Unsubscribe)])#,
															#('eRegisterState', '!=', REGISTER_STATE_BAJA)])
		
		if not records2Unsubscribe:
			raise exceptions.ValidationError ( "No hay registros para dar de baja")

		vals["name"]		+= "[" + str (ids2Unsubscribe) + "]"
		result				= super ( setirUnsubscribeWizardPM, self).create ( vals)
		

		for record in records2Unsubscribe:
				result.idsPM2Unsubscribe	= [(4, record.id, False)]

		return result

	@api.multi
	def unsubscribePM (self):
		if not self.idUnsubscribeReason:
			raise exceptions.ValidationError ( "Es necesario seleccionar una causa de baja")
		
		idsPM2unsubscribe	= self.env.context.get ('active_ids', False)
		
		stateBAJA			= self.env['setir.import.base'].search([('eImportType','=', IMPORT_TYPE_ESTADO),
																	('name', '=', dict (PM_STATE)[PM_STATE_BAJA])])

		#for pm_id in idsPM2unsubscribe:
		vals	= {}
		vals["dtUnsubscribe"]		= fields.Datetime.now()
		vals["eRegisterState"]		= REGISTER_STATE_BAJA
		vals["idsPMState"]			= stateBAJA.id
		vals["idUnsubscribeReason"]	= self.idUnsubscribeReason.id 

		self.env["setir.pm"].search([('id','in', idsPM2unsubscribe)]).write (vals)
		self.env["setir.pm"].search([('id','in', idsPM2unsubscribe)]).addPMStateHistory ( stateBAJA.id)

		return {'type': "ir.actions.do_nothing",}

	def sendUnsubscribeMail (self):
		return {'type': "ir.actions.do_nothing",}

	def printUnsubscribeReport (self):
		return {'type': "ir.actions.do_nothing",}
