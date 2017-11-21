# -*- coding: utf-8 -*-
#setirDefinitions.py

INVOICING_TYPE_FACTURA	= "factura"
INVOICING_TYPE_SUPLIDO	= "suplido"
INVOICING_TYPE_RAPEL	= "rapel"
INVOICING_TYPE  =   [
					(INVOICING_TYPE_FACTURA,	"factura"),
					(INVOICING_TYPE_SUPLIDO,	"suplido"),
					(INVOICING_TYPE_RAPEL,		"rapel"),
					]

PM_TYPE_OBU		= "obu"
PM_TYPE_TARJETA	= "tarjeta"
PM_TYPE         =   [
                    (PM_TYPE_OBU,		"obu"),
                    (PM_TYPE_TARJETA,	"tarjeta")
                    ]

REGISTER_STATE_ALTA				= "alta"
REGISTER_STATE_BAJA				= "baja"
REGISTER_STATE  	=   [
						(REGISTER_STATE_ALTA, "Alta"),
						(REGISTER_STATE_BAJA, "Baja")
						]

PM_STATE_ESPERA		= "espera"
PM_STATE_ACTIVO		= "activo"
PM_STATE_BLOQUEADO	= "bloqueado"
PM_STATE_BAJA		= "baja"
PM_STATE			=	[
						(PM_STATE_ESPERA, "Espera"),
						(PM_STATE_ACTIVO, "Activado"),
						(PM_STATE_BLOQUEADO, "Bloqueado"),
						(PM_STATE_BAJA, "Baja")
						]

IMPORT_TYPE_FACTURACION		= "facturacion"
IMPORT_TYPE_FACTURA			= "factura"
IMPORT_TYPE_CONSUMO			= "consumo"
IMPORT_TYPE_MP				= "medio_pago"
IMPORT_TYPE_ESTADO			= "estado"
IMPORT_TYPE_TOKEN_MP		= "token_mp"
IMPORT_TYPE_FORMATO_FECHA	= "formato_fecha"

IMPORT_TYPE  			=   [
							(IMPORT_TYPE_FACTURACION, u"Facturación"),
							(IMPORT_TYPE_FACTURA, "Factura"),
							(IMPORT_TYPE_CONSUMO, "Consumo"),
							(IMPORT_TYPE_MP, "Medio de pago"),
							(IMPORT_TYPE_ESTADO, "Estado"),
							(IMPORT_TYPE_TOKEN_MP, "Token de medio de pago"),
							(IMPORT_TYPE_FORMATO_FECHA, "Formato de la fecha")
							]

FORMATO_FECHA_ESTANDAR		= u"%d/%m/%Y"

IMPORT_PROCESS_TYPE_FACTURACION	= "facturacion"
IMPORT_PROCESS_TYPE_MP			= "medio_pago"
IMPORT_PROCES_TYPE				=	[
									("facturacion", "Facturacion"),
									("medio_pago", "Medios de pago")
									]

PATH_ROOT			= "path_root"
PATH_INVOICING		= "path_invoicing"
PATH_INVOICE		= "path_invoice"
PATH_CONSUPTION		= "path_consumtion"
PATH_PM				= "path_payment_media"
DEF_PATHS  		=   [
					(PATH_ROOT,"path_root"),
					(PATH_INVOICING,"path_invoicing"),
					(PATH_INVOICE,"path_invoice"),
					(PATH_CONSUPTION,"path_consumtion"),
					(PATH_PM,"path_payment_media")
					]

MONTHS		  	=   [
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
FIELD_NOMBRE_CLINETE				= "nombre_cliente"
FIELD_NIF_CLIENTE					= "nif_cliente"
FIELD_BASE_CODIGO_CLIENTE_SETIR		= "codigo_cliente_setir"
FIELD_CODIGO_CLIENTE_PROVEEDOR		= "codigo_cliente_proveedor"
FIELD_NOMBRE_PROVEEDOR				= "nombre_proveedor"
FIELD_CODIGO_PROVEEDOR_SETIR		= "codigo_proveedor_setir"
FIELD_CODIGO_PROVEEDOR_PROVEEDOR	= "codigo_proveedor_proveedor"
FIELD_TIPO							= "tipo"
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
FIELD_TOKEN_MP_OBU					= "token_mp_obu"
FIELD_TOKEN_MP_TARJETA				= "token_mp_tarjeta"
FIELD_BASE							=	[
										(FIELD_NOMBRE_CLINETE, "nombre_cliente"),
										(FIELD_NIF_CLIENTE, "nif_cliente"),
										(FIELD_BASE_CODIGO_CLIENTE_SETIR, "codigo_cliente_setir"),
										(FIELD_CODIGO_CLIENTE_PROVEEDOR, "codigo_cliente_proveedor"),
										(FIELD_NOMBRE_PROVEEDOR, "nombre_proveedor"),
										(FIELD_CODIGO_PROVEEDOR_SETIR, "codigo_proveedor_setir"),
										(FIELD_CODIGO_PROVEEDOR_PROVEEDOR, "codigo_proveedor_proveedor"),
										(FIELD_TIPO, "tipo"),
										(FIELD_PAN, "pan"),
										(FIELD_PAN_SECUNDARIO, "pan_secundario"),
										(FIELD_MATRICULA_ASOCIADA, "matricula_asociada"),
										(FIELD_PAIS_DE_MATRICULA, "pais_de_matricula"),
										(FIELD_NUMERO_SERIE, "numero_serie"),
										(FIELD_NUMERO_SERIE_SECUNDARIO, "numero_serie_secundario"),
										(FIELD_FECHA_ALTA, "fecha_alta"),
										(FIELD_FECHA_CREACION, "fecha_creacion"),
										(FIELD_FECHA_EXPIRACION, "fecha_expiracion"),
										(FIELD_FECHA_BAJA, "fecha_baja"),
										(FIELD_ESTADO_REGISTRO, "estado_registro"),
										(FIELD_ESTADO_MEDIO_PAGO, "estado_medio_de_pago"),
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
CONTACT_NAME_ENVIO_TTA		= "envio-tta"
CONTACT_NAME_FACTURACION	= "facturacion"
CONTACT_NAME_OPERACIONES	= "operaciones"

ACTOR_CLIENTE				= "cliente"
ACTOR_PROVEEDOR				= "proveedor"
ACTOR_SETIR					= "setir"
ACTORS          			=   [
								(ACTOR_CLIENTE, "cliente"),
								(ACTOR_PROVEEDOR, "proveedor"),
								(ACTOR_SETIR, "setir")
								]

#estados por defecto, es posible añadir más manualmente 
ESTADO_GESTION_SOLICITADO	= "Solicitado"
ESTADO_GESTION_ENVIADO		= "Enviado"
ESTADO_GESTION_RECIBIDO		= "Recibido"
ESTADO_GESTION_INSTALADO	= "Instalado"
ESTADO_GESTION_PERDIDO		= "Perdido"
ESTADO_GESTION_DEFECTUOSO	= "Defectuoso"
