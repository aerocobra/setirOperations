# -*- coding: utf-8 -*-
#setirDefinitions.py

INVOICING_TYPE_FACTURA				= "factura"
INVOICING_TYPE_SUPLIDO				= "suplido"
INVOICING_TYPE_RAPEL				= "rapel"
INVOICING_TYPE  					=   [
										(INVOICING_TYPE_FACTURA,	"factura"),
										(INVOICING_TYPE_SUPLIDO,	"suplido"),
										(INVOICING_TYPE_RAPEL,		"rapel"),
										]

#categorias productos setir a dar de alata como categorias internas
CATEGORIA_MEDIO_DE_PAGO				= "medio de pago"
CATEGORIA_OBU						= "obu"
CATEGORIA_TARJETA					= "tarjeta"
CAEGORIA_ACTIVACION					= "activacion"
CATEGORIA_PEAJE						= "peaje"
CATEGORIA_RAPEL						= "rapel"
CATEGORIA_COMBUSTIBLE				= "combustible"
CATEGORIA_IMPUESTO					= "impuesto"

PM_TYPE_OBU							= "obu"
PM_TYPE_TARJETA						= "tarjeta"
PM_TYPE         					=   [
					                    (PM_TYPE_OBU,		"obu"),
					                    (PM_TYPE_TARJETA,	"tarjeta")
					                    ]

REGISTER_STATE_ALTA					= "alta"
REGISTER_STATE_BAJA					= "baja"
REGISTER_STATE  					=   [
										(REGISTER_STATE_ALTA, "Alta"),
										(REGISTER_STATE_BAJA, "Baja")
										]

PM_STATE_ESPERA						= "espera"
PM_STATE_ACTIVO						= "activo"
PM_STATE_BLOQUEADO					= "bloqueado"
PM_STATE_BAJA						= "baja"
PM_STATE							=	[
										(PM_STATE_ESPERA, "Espera"),
										(PM_STATE_ACTIVO, "Activo"),
										(PM_STATE_BLOQUEADO, "Bloqueado"),
										(PM_STATE_BAJA, "Baja")
										]

GESTION_BLOQUEO						= "bloqueo" 
GESTION_DESBLOQUEO					= "desbloqueo"
GESTION_BAJA						= "baja"
GESTION_ENVIO						= "envio"
GESTION_RECEPCION					= "recepcion"
GESTIONES							=	[
										(GESTION_BLOQUEO,		"Bloqueo"), 
										(GESTION_DESBLOQUEO,	"Desbloqueo"),
										(GESTION_BAJA,			"Baja"),
										(GESTION_ENVIO, 		u"Envío"),
										(GESTION_RECEPCION, 	u"Recepción"),
										]

IMPORT_TYPE_FACTURACION				= "facturacion"
IMPORT_TYPE_FACTURA					= "factura"
IMPORT_TYPE_CONSUMO					= "consumo"
IMPORT_TYPE_MP						= "medio_pago"
IMPORT_TYPE_ESTADO					= "estado"
IMPORT_TYPE_TOKEN_MP				= "token_mp"
IMPORT_TYPE_FORMATO_FECHA			= "formato_fecha"

IMPORT_PRODUCT_CATEGORY_MP			= "producto_mp"
IMPORT_PRODUCT_CATEGORY_SERVICIO	= "producto_service"

IMPORT_TYPE  						=   [
										(IMPORT_TYPE_FACTURACION,			u"Facturación"),
										(IMPORT_TYPE_FACTURA,				"Factura"),
										(IMPORT_TYPE_CONSUMO,				"Consumo"),
										(IMPORT_TYPE_MP,					"Medio de pago"),
										(IMPORT_TYPE_ESTADO,				"Estado"),
										(IMPORT_TYPE_TOKEN_MP,				"Token de medio de pago"),
										(IMPORT_TYPE_FORMATO_FECHA,			"Formato de la fecha"),
										(IMPORT_PRODUCT_CATEGORY_MP,		u"Categoría medio de pago"),
										(IMPORT_PRODUCT_CATEGORY_SERVICIO,	u"Categoría servicio")
										]

IMPORT_PRODUCT_CATEGORY				=	[
										(IMPORT_PRODUCT_CATEGORY_MP,		u"Categoría medio de pago"),
										(IMPORT_PRODUCT_CATEGORY_SERVICIO,	u"Categoría servicio")
										]

FORMATO_FECHA_ESTANDAR			= u"%d/%m/%Y"

IMPORT_PROCESS_TYPE_FACTURACION	= "process_facturacion"
IMPORT_PROCESS_TYPE_MP			= "process_medio_pago"
IMPORT_PROCES_TYPE				=	[
									(IMPORT_PROCESS_TYPE_FACTURACION,	"Facturacion"),
									(IMPORT_PROCESS_TYPE_MP,			"Medio de pago")
									]

PATH_ROOT			= "path_root"
PATH_INVOICING		= "path_invoicing"
PATH_INVOICES		= "path_invoices"
PATH_CONSUPTIONS	= "path_consumtions"
PATH_PM				= "path_payment_media"
DEF_PATHS  			=   [
						(PATH_ROOT,"path_root"),
						(PATH_INVOICING,"path_invoicing"),
						(PATH_INVOICES,"path_invoices"),
						(PATH_CONSUPTIONS,"path_consumtions"),
						(PATH_PM,"path_payment_media")
						]

YEARS			  	=   [
						("2016", "2016"),
						("2017", "2017"),
						("2018", "2018"),
						("2019", "2019"),
						("2020", "2020"),
						]

MONTHS			  	=   [
						("01", "Enero"),
						("02", "Febrero"),
						("03", "Marzo"),
						("04", "Abril"),
						("05", "Mayo"),
						("06", "Junio"),
						("07", "Julio"),
						("08", "Agosto"),
						("09", "Septiembre"),
						("10", "Octubre"),
						("11", "Noviembre"),
						("12", "Diciembre")
						]

#campos base de importación de medios de pago
FIELD_PM_ID							= "id_medio_pago"
FIELD_NOMBRE_CLINETE				= "nombre_cliente"
FIELD_NIF_CLIENTE					= "nif_cliente"
FIELD_BASE_CODIGO_CLIENTE_SETIR		= "codigo_cliente_setir"
FIELD_CODIGO_CLIENTE_PROVEEDOR		= "codigo_cliente_proveedor"
FIELD_NOMBRE_PROVEEDOR				= "nombre_proveedor"
FIELD_CODIGO_PROVEEDOR_SETIR		= "codigo_proveedor_setir"
FIELD_CODIGO_PROVEEDOR_PROVEEDOR	= "codigo_proveedor_proveedor"
FIELD_PRODUCT						= "product"
FIELD_RELATED_PRODUCT				= "producto_relacionado"
FIELD_PAN							= "pan"
FIELD_PAN_SECUNDARIO				= "pan_secundario"
FIELD_MATRICULA_ASOCIADA			= "matricula_asociada"
FIELD_PAIS_DE_MATRICULA				= "pais_de_matricula"
FIELD_NUMERO_SERIE					= "numero_serie"
FIELD_NUMERO_SERIE_SECUNDARIO		= "numero_serie_secundario"
FIELD_FECHA_ALTA					= "fecha_alta"
FIELD_FECHA_CREACION				= "fecha_creacion"
FIELD_FECHA_EXPIRACION				= "fecha_expiracion"
FIELD_FECHA_BAJA					= "fecha_baja"
FIELD_ESTADO_REGISTRO				= "estado_registro"
FIELD_ESTADO_MEDIO_PAGO				= "estado_medio_pago"

FIELD_TIPO							= "tipo"
FIELD_TOKEN_MP_OBU					= "token_mp_obu"
FIELD_TOKEN_MP_TARJETA				= "token_mp_tarjeta"


FIELD_BASE							=	[
										(FIELD_PM_ID,						"id_medio_pago"),
										(FIELD_NOMBRE_CLINETE,				"nombre_cliente"),
										(FIELD_NIF_CLIENTE,					"nif_cliente"),
										(FIELD_BASE_CODIGO_CLIENTE_SETIR,	"codigo_cliente_setir"),
										(FIELD_CODIGO_CLIENTE_PROVEEDOR,	"codigo_cliente_proveedor"),
										(FIELD_NOMBRE_PROVEEDOR,			"nombre_proveedor"),
										(FIELD_CODIGO_PROVEEDOR_SETIR,		"codigo_proveedor_setir"),
										(FIELD_CODIGO_PROVEEDOR_PROVEEDOR,	"codigo_proveedor_proveedor"),
										(FIELD_RELATED_PRODUCT,				"producto_relacionado"),
										(FIELD_PAN,							"pan"),
										(FIELD_PAN_SECUNDARIO,				"pan_secundario"),
										(FIELD_MATRICULA_ASOCIADA,			"matricula_asociada"),
										(FIELD_PAIS_DE_MATRICULA,			"pais_de_matricula"),
										(FIELD_NUMERO_SERIE,				"numero_serie"),
										(FIELD_NUMERO_SERIE_SECUNDARIO,		"numero_serie_secundario"),
										(FIELD_FECHA_ALTA,					"fecha_alta"),
										(FIELD_FECHA_CREACION,				"fecha_creacion"),
										(FIELD_FECHA_EXPIRACION,			"fecha_expiracion"),
										(FIELD_FECHA_BAJA,					"fecha_baja"),
										(FIELD_ESTADO_REGISTRO,				"estado_registro"),
										(FIELD_ESTADO_MEDIO_PAGO,			"estado_medio_de_pago"),
										
										(FIELD_TIPO, "tipo"),
										(FIELD_TOKEN_MP_OBU, "token_mp_obu"),
										(FIELD_TOKEN_MP_TARJETA, "token_mp_tarjeta"),
										]

IMPORT_ACTION_CREATE		= "create"
IMPORT_ACTION_UPDATE		= "update"
IMPORT_ACTION	=	[
					(IMPORT_ACTION_CREATE, "Alta"),
					(IMPORT_ACTION_UPDATE, "Actualizar"),
					]

#tipos de direcciones definidos en odoo
ADDRESS_CONTACT				= "contact"
ADDRESS_INVOICE				= "invoice"
ADDRESS_DELIVERY			= "delivery"
ADDRESS_OTHER				= "other"

DEF_ADDRESS_TYPE			=	[
								(ADDRESS_CONTACT, "Contacto"),
								(ADDRESS_INVOICE, u"Facturación"),
								(ADDRESS_DELIVERY, u"Envío"),
								(ADDRESS_OTHER, "Otra"),
								]

CONTACT_NAME_ENVIO			= "envio"
CONTACT_NAME_ENVIO_OBU		= "envio-obu"
CONTACT_NAME_ENVIO_TARJETA	= "envio-tarjeta"
CONTACT_NAME_FACTURACION	= "facturacion"
CONTACT_NAME_OPERACIONES	= "operaciones"

ACTOR_CLIENTE				= "cliente"
ACTOR_PROVEEDOR				= "proveedor"
ACTOR_SETIR					= "setir"
ACTORS          			=   [
								(ACTOR_CLIENTE,		"cliente"),
								(ACTOR_PROVEEDOR,	"proveedor"),
								(ACTOR_SETIR,		"setir")
								]

#estados por defecto, es posible añadir más manualmente 
ESTADO_GESTION_SOLICITADO	= "Solicitado"
ESTADO_GESTION_ENVIADO		= "Enviado"
ESTADO_GESTION_RECIBIDO		= "Recibido"
ESTADO_GESTION_INSTALADO	= "Instalado"
ESTADO_GESTION_PERDIDO		= "Perdido"
ESTADO_GESTION_DEFECTUOSO	= "Defectuoso"
