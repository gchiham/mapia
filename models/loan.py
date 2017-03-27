# -*- encoding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class Loanmapia(models.Model):
    _name = "mapia.management.loan"
    _inherit = ['mail.thread']

    # Valores numericos
    total_interes = fields.Float("Total de interes", readonly=True, states={'cotizacion': [('readonly', False)]})
    total_monto = fields.Float("Monto Financiado", readonly=True, states={'cotizacion': [('readonly', False)]})
    cuota_seguro = fields.Float("Cuota de seguro", default=0.00)
    cuato_prestamo = fields.Float("Cuota de prestamo", readonly=True, states={'cotizacion': [('readonly', False)]})
    cuota_prestamo_seguro = fields.Float("Cuota con Seguro")
    monto_solicitado = fields.Float("Valor del Terreno", required=True, readonly=True, states={'cotizacion': [('readonly', False)]})
    saldo_pendiente = fields.Float("Saldo pendiente", readonly=True, states={'cotizacion': [('readonly', False)]})
    product_id = fields.Many2many("product.product", string="Terrenos", domain=[('sale_ok', '=', True)])
    proyecto_id = fields.Many2one("product.category", "Proyecto")
    # Gastos de prestamo
    gastos_papeleria = fields.Monetary("Gasto de Papeleria", readonly=True, states={'cotizacion': [('readonly', False)]})
    gasto_timbre = fields.Monetary("Gasto de Timbre", readonly=True, states={'cotizacion': [('readonly', False)]})
    prima = fields.Float("Prima", readonly=True, states={'cotizacion': [('readonly', False)]})
    prestamo_con_seguro = fields.Boolean("Prestamo con seguro")

    notas_desembolso = fields.Text("Notas de desombolso", readonly=True, states={'cotizacion': [('readonly', False)]})
    # Campos generales
    name = fields.Char("Numero de prestamo", required=True, default=lambda self: self.env['ir.sequence'].get('contrato'))
    afiliado_id = fields.Many2one("res.partner", "Cliente", required=True, domain=[('customer', '=', True)])
    fecha_solicitud = fields.Date("Fecha de solicitud", required=True)
    fecha_aprobacion = fields.Date("Fecha de pago", required=True)
    currency_id = fields.Many2one("res.currency", "Moneda", default=lambda self: self.env.user.company_id.currency_id)
    # Parametros
    plazo_pago = fields.Integer("Plazo de pago", required=True)
    periodo_plazo_pago = fields.Selection([('dias', 'Días'), ('meses', 'Meses')], string='Periodo', default='meses', required=True)
    tasa_interes = fields.Float("Tasa de interes", required=True)
    notas = fields.Text("Notas")
    state = fields.Selection([('cotizacion', 'Cotizacion'), ('rechazado', 'Rechazado'), ('progreso', 'En progreso'), ('liquidado', 'Liquidado')], string='Estado de prestamo',  readonly=True, default='cotizacion')
    tipo_prestamo_id = fields.Many2one("mapia.management.loan.type", "Tipo de Prestamo", required=True)
    cuota_ids = fields.One2many("mapia.management.loan.cuota", "prestamo_id", "Cuotas de prestamo")
    doc_ids = fields.One2many("mapia.management.tipo.documento", "prestamo_id", "Documentos de validacion")

    @api.onchange("tipo_prestamo_id")
    def get_tasa_plazo(self):
        self.plazo_pago = self.tipo_prestamo_id.plazo_pago_id.numero_plazo
        self.tasa_interes = self.tipo_prestamo_id.tasa_interes_id.tasa_interes
        # self.periodo_plazo_pago = self.tipo_prestamo_id.tasa_interes_id.capitalizable

    @api.multi
    def action_rechazar(self):
        self.write({'state': 'rechazado'})

    @api.multi
    def action_borrador(self):
        self.write({'state': 'cotizacion'})

    @api.multi
    def action_aprobar(self):
        obj_loan_cuota = self.env["mapia.management.loan.cuota"].search([('prestamo_id', '=', self.id)])
        for cuota in obj_loan_cuota:
            cuota.state = 'novigente'
        self.write({'state': 'progreso'})
        self.saldo_pendiente = self.total_monto

    @api.one
    def get_calculadora_emi(self):
        self.total_interes = 0.0
        for fee in self.cuota_ids:
            self.total_interes += fee.interes
        self.total_monto = (self.monto_solicitado - self.prima) + self.total_interes

        if self.prestamo_con_seguro:
            self.cuota_prestamo_seguro = self.cuato_prestamo + self.cuota_seguro
        # self.cuato_prestamo = self._calcular_cuota(self.monto_solicitado, self.tasa_interes, self.plazo_pago)
        # self.total_interes = self.monto_solicitado * (self.tasa_interes / 100.0)
        # self.total_monto = self.monto_solicitado + self.total_interes

    @api.one
    def get_generar_cuotas(self):
        obj_loan_cuota = self.env["mapia.management.loan.cuota"]
        obj_loan_cuota_unlink = obj_loan_cuota.search([('prestamo_id', '=', self.id)])
        if self.cuota_ids:
            for delete in obj_loan_cuota_unlink:
                delete.unlink()

        plazo = 1
        valor_financiar = 0.0
        cuota_fecha = datetime.now()
        interest = 0.0
        rate_monthly = 0.0
        annuity_factor = 0.0
        saldo_acumulado = 0.0
        capital = 0.0
        numero_cuotas = 0
        if self.tipo_prestamo_id.tasa_interes_id.capitalizable == 'anual':
            if self.tasa_interes > 0:
                rate_monthly = (self.tasa_interes / 12.0) / 100.0
                annuity_factor = (rate_monthly * ((1 + rate_monthly) ** self.plazo_pago)) / (((1 + rate_monthly) ** self.plazo_pago) - 1)
                # self.cuato_prestamo = self.monto_solicitado * annuity_factor

                if self.prima > 0:
                    valor_financiar = self.monto_solicitado - self.prima
                    self.cuato_prestamo = (valor_financiar * annuity_factor)

                if self.prima == 0:
                    valor_financiar = self.monto_solicitado
                    self.cuato_prestamo = (valor_financiar * annuity_factor)

            else:
                if self.prima > 0:
                    valor_financiar = self.monto_solicitado - self.prima
                    self.cuato_prestamo = ((self.monto_solicitado - self.prima) / self.plazo_pago)

                if self.prima == 0:
                    valor_financiar = self.monto_solicitado
                    self.cuato_prestamo = (self.monto_solicitado / self.plazo_pago)

        else:
            raise Warning(_('No se han definido tasas capitalizables mensuales y quincenales'))

        values = {
            'prestamo_id': self.id,
            'afiliado_id': self.afiliado_id.id,
            'monto_cuota': self.cuato_prestamo,
            'state': 'cotizacion',
        }
        cuota_fecha = (datetime.strptime(self.fecha_aprobacion, '%Y-%m-%d'))
        while plazo <= self.plazo_pago:
            #if plazo == 1:
             #   values["fecha_pago"] = cuota_fecha
            #else:
            #    cuota_fecha = cuota_fecha + relativedelta(day=cuota_fecha.day, months=1)
            #    values["fecha_pago"] = cuota_fecha

            if plazo == 1:
                values["fecha_pago"] = cuota_fecha
                interest = valor_financiar * rate_monthly
                capital = self.cuato_prestamo - interest
                values["interes"] = interest
                values["capital"] = capital
                saldo_acumulado = valor_financiar - capital
                values["saldo_prestamo"] = saldo_acumulado
            if plazo > 1:
                interest = saldo_acumulado * rate_monthly
                capital = self.cuato_prestamo - interest
                values["interes"] = interest
                values["capital"] = capital
                saldo_acumulado = saldo_acumulado - capital
                values["saldo_prestamo"] = saldo_acumulado
                cuota_fecha = cuota_fecha + relativedelta(day=cuota_fecha.day, months=1)
                values["fecha_pago"] = cuota_fecha
            values["numero_cuota"] = plazo
            id_cuota = obj_loan_cuota.create(values)
            plazo +=  1
        self.get_calculadora_emi()

    @api.model
    def _calcular_cuota(self, valor_prestamo, interes, plazo_tiempo):
        cuota = (valor_prestamo * (1 + interes / 100.0)) / plazo_tiempo
        return cuota

    @api.model
    def _calcular_capital_cuota(self, valor_prestamo, plazo_tiempo):
        capital = valor_prestamo / plazo_tiempo
        return capital

    @api.model
    def _calcular_interes_cuota(self, valor_prestamo, interes, plazo_tiempo):
        interes = (valor_prestamo * interes / 100.0) / plazo_tiempo
        return interes


class MapiaLoanline(models.Model):
    _name = "mapia.management.loan.cuota"

    prestamo_id = fields.Many2one("mapia.management.loan", "Numero de prestamo")
    afiliado_id = fields.Many2one("res.partner", "Cliente", required=True)
    numero_cuota = fields.Integer("# de cuota", readonly=True)
    fecha_pago = fields.Date("Fecha de Pago")
    monto_cuota = fields.Float("Monto de Cuota")
    capital = fields.Float("Capital")
    interes = fields.Float("Interes")
    mora = fields.Float("Mora de cuota")
    saldo_prestamo = fields.Float("Saldo Pendiente")
    state = fields.Selection(
        [('cotizacion', 'Cotizacion'), ('cancelada', 'Cancelada'), ('novigente', 'No vigente'), ('vigente', 'Vigente'),('morosa', 'Morosa'),('pagada', 'Pagada')], string='Estado de cuota',readonly=True, default='cotizacion')
    description = fields.Text("Notas Generales")
    #cuota_vigente = fields.Boolean("Cuota vigenete", compute=getstatuscuota)

    @api.multi
    def validarcuota(self):
        self.write({'state': 'pagada'})

    @api.multi
    def cuotaborrador(self):
        self.write({'state': 'cotizacion'})

    @api.multi
    def getvigente(self):
        self.write({'state': 'vigente'})