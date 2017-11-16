<?xml version="1.0" encoding="utf-8"?>
<openerp>
	<data>
		<report id="setirSaleTimespanReport_action"
			string="Tiempos ejecución"
			model="sale.order"
			report_type="qweb-pdf"
            file="setirSale.setirSaleTimespanReport"
			name="setirSale.setirSaleTimespanReport"
		/>
		<template id="setirSaleTimespanReport">
			<t t-call="report.html_container">
				<t t-call="report.internal_layout">
					<div class="page">
						<p><strong>Tiempos medios de los procesos de venta y formalización</strong><br></br><br></br></p>
						<table class="table table-condensed">
							<thead>
								<tr>
									<th class="text-right">Oferta</th>
									<th class="text-right">Pedido de Venta</th>
									<th class="text-right">Asignación</th>
									<th class="text-right">Realización</th>
									<th class="text-right">COMERCIAL</th>
									<th class="text-right">OPERACIONES</th>
								</tr>
							</thead>
							<tbody class="sale_tbody">
								<t t-set="nOfertaDias" t-value="0"/>
								<t t-set="nOfertaRegistros" t-value="0"/>
								<t t-set="nPedidoDias" t-value="0"/>
								<t t-set="nPedidoRegistros" t-value="0"/>
								<t t-set="nRevisionDias" t-value="0"/>
								<t t-set="nRevisionRegistros" t-value="0"/>
								<t t-set="nFormalizacionDias" t-value="0"/>
								<t t-set="nFormalizacionRegistros" t-value="0"/>

								<t t-set="nComercial" t-value="0"/>
								<t t-set="nComercialRegistros" t-value="0"/>
								<t t-set="nOperaciones" t-value="0"/>

								<t t-set="nTotalRegistros" t-value="0"/>
								<t t-foreach="docs" t-as="doc">
									<!-- t t-set="doc" t-value="doc.with_context({'lang':doc.partner_id.lang})"/ -->
									<t t-set="nTotalRegistros" t-value="nTotalRegistros + 1"/>
									<t t-if="doc.opportunity_id.create_date"> 
										<t t-set="nOfertaDias" t-value="nOfertaDias + (datetime.datetime.strptime(doc.date_order, '%Y-%m-%d %H:%M:%S').date() - datetime.datetime.strptime(doc.opportunity_id.create_date, '%Y-%m-%d %H:%M:%S').date()).days"/>
										<t t-set="nOfertaRegistros" t-value="nOfertaRegistros + 1"/>
									</t>
									<t t-if="doc.x_dtPOconfirm">
										<t t-set="nPedidoDias" t-value="nPedidoDias + (datetime.datetime.strptime(doc.x_dtPOconfirm, '%Y-%m-%d %H:%M:%S').date() - datetime.datetime.strptime(doc.date_order, '%Y-%m-%d %H:%M:%S').date()).days"/>
										<t t-set="nPedidoRegistros" t-value="nPedidoRegistros + 1"/>
										<t t-if="doc.opportunity_id.create_date">
											<t t-set="nComercial" t-value="nComercial + (datetime.datetime.strptime(doc.x_dtPOconfirm, '%Y-%m-%d %H:%M:%S').date() - datetime.datetime.strptime(doc.opportunity_id.create_date, '%Y-%m-%d %H:%M:%S').date()).days"/>
											<t t-set="nComercialRegistros" t-value="nComercialRegistros + 1"/>
										</t>
										<t t-if="doc.x_dtPOformalize">
											<t t-set="nRevisionDias" t-value="nRevisionDias + (datetime.datetime.strptime(doc.x_dtPOformalize, '%Y-%m-%d %H:%M:%S').date() - datetime.datetime.strptime(doc.x_dtPOconfirm, '%Y-%m-%d %H:%M:%S').date()).days"/>
											<t t-set="nRevisionRegistros" t-value="nRevisionRegistros + 1"/>

											<t t-if="doc.x_dtPOdone">
												<t t-set="nFormalizacionDias" t-value="nFormalizacionDias + (datetime.datetime.strptime(doc.x_dtPOdone, '%Y-%m-%d %H:%M:%S').date() - datetime.datetime.strptime(doc.x_dtPOformalize, '%Y-%m-%d %H:%M:%S').date()).days"/>
												<t t-set="nFormalizacionRegistros" t-value="nFormalizacionRegistros + 1"/>
												<t t-set="nOperaciones" t-value="nOperaciones + (datetime.datetime.strptime(doc.x_dtPOdone, '%Y-%m-%d %H:%M:%S').date() - datetime.datetime.strptime(doc.x_dtPOconfirm, '%Y-%m-%d %H:%M:%S').date()).days"/>
											</t>
										</t>
									</t>
								</t>
								<tr>
									<t t-if="nOfertaRegistros > 0">
										<t t-set="nOfertaDias" t-value="nOfertaDias / nOfertaRegistros"/>
									</t>
									<t t-if="nPedidoRegistros > 0">
										<t t-set="nPedidoDias" t-value="nPedidoDias / nPedidoRegistros"/>
									</t>
									<t t-if="nRevisionRegistros > 0">
										<t t-set="nRevisionDias" t-value="nRevisionDias / nRevisionRegistros"/>
									</t>
									<t t-if="nFormalizacionRegistros > 0">
										<t t-set="nFormalizacionDias" t-value="nFormalizacionDias / nFormalizacionRegistros"/>
										<t t-set="nComercial" t-value="nComercial / nFormalizacionRegistros"/>
										<t t-set="nOperaciones" t-value="nOperaciones / nFormalizacionRegistros"/>
									</t>
									<td class="text-right">
										<span style="color:green" t-esc="nOfertaDias"/> / <span t-esc="nOfertaRegistros"/>
									</td>
									<td class="text-right">
										<span style="color:green" t-esc="nPedidoDias"/> / <span t-esc="nPedidoRegistros"/>
									</td>
									<td class="text-right">
										<span style="color:green" t-esc="nRevisionDias"/> / <span t-esc="nRevisionRegistros"/>
									</td>
									<td class="text-right">
										<span style="color:green" t-esc="nFormalizacionDias"/> / <span t-esc="nFormalizacionRegistros"/>
									</td>
									<td class="text-right">
										<span style="color:green" t-esc="nComercial"/> / <span t-esc="nComercialRegistros"/>
									</td>
									<td class="text-right">
										<span style="color:green" t-esc="nOperaciones"/> / <span t-esc="nFormalizacionRegistros"/>
									</td>
								</tr>
							</tbody>
						</table>
						<strong>
							<p>
							Total registros:
							<span style="color:blue" t-esc="nTotalRegistros"/>
							</p>
						</strong>
						<p>Leyenda:</p>
						<pre>

						Hitos para el cáculo de intervalos (creación):

						<strong>[oportunidad] - [oferta] - [pedido de venta (PV)] - [asignación de PV (para formalizar)] - [PV realizado]</strong>
						
						</pre>
						<p>Cálculos de los intervalos:</p>
						<table>
							<tbody>
								<tr>
									 <td>Oferta</td>
									 <td>:= [oportunidad] - [oferta]</td>
								</tr>
								<tr>
									 <td>Pedido de Venta</td>
									 <td>:= [oferta] - [pedido de venta (PV)]</td>
								</tr>
								<tr>
									 <td>Asignación</td>
									 <td>:= [pedido de venta (PV)] - [asignación de PV]</td>
								</tr>
								<tr>
									 <td>Realización</td>
									 <td>:= [asignación de PV] - [PV realizado]</td>
								</tr>
								<tr>
									 <td>COMERCIAL</td>
									 <td>:= [oportunidad] - [pedido de venta (PV)]</td>
								</tr>
								<tr>
									 <td>OPERACIONES</td>
									 <td>:= [pedido de venta (PV)] - [PV realizado]</td>
								</tr>
								<tr>
								</tr>
								<tr>
									 <td>Presentación del intervalo</td>
									 <td>:= dias / registros con datos</td>
								</tr>
								<tr>
									 <td>Total registros</td>
									 <td>:= Total registros en el estudio</td>
								</tr>
							</tbody>
						</table>
					</div>
				</t>
			</t>
		</template>
	</data>
</openerp>