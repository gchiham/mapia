# -*- encoding: utf-8 -*-
from openerp import models, fields, api


class MapiaLoanType(models.Model):
    _name = "mapia.management.loan.type"
    _inherit = ['mail.thread']

    name = fields.Char("Tipo de Prestamo", required=True)
    active = fields.Boolean(string="Prestamo Activo", default=True)
    description = fields.Text("Notas Generales")
    monto_maximo = fields.Float("Monto Maximo", help="Monto maximo para el prestamo", required=True)
    plazo_pago_id = fields.Many2one("mapia.management.loan.plazo", "Plazo de tiempo", required=True)
    tasa_interes_id = fields.Many2one("mapia.management.loan.interes", "Tasa de Interes", required=True)


class LoanPlazo(models.Model):
    _name = "mapia.management.loan.plazo"

    name = fields.Char("Nombre de Plazo")
    numero_plazo = fields.Integer("Numero de plazos", required=True)
    active = fields.Boolean(string="Activo", default=True)
    tipo_plazo = fields.Selection([('quincenal', 'Quincenas'), ('mensual', 'Meses'), ('diario', 'Diario')], string='Periodos', default='mensual')

    @api.model
    def create(self, vals):
        plazo = vals.get("numero_plazo")
        tipo = vals.get("tipo_plazo")
        description = ""
        if tipo == 'quincenal':
            description = "Quincenas"
        if tipo == "mensual":
            description = "Meses"

        vals["name"] = str(plazo) + " " + description
        return super(LoanPlazo, self).create(vals)


class LoanInteres(models.Model):
    _name = "mapia.management.loan.interes"

    name = fields.Char("Nombre de Tasa")
    tasa_interes = fields.Float("Tasa de interes (%)", required=True)
    capitalizable = fields.Selection([('quincenal', 'Quincenal'), ('mensual', 'Mensual'), ('anual', 'Anual')], string='Capitalizable', default='mensual')
    active = fields.Boolean(string="Activo", default=True)

    @api.model
    def create(self, vals):
        capitalizable = vals.get("capitalizable")
        tasa = vals.get("tasa_interes")
        vals["name"] = str(tasa) + "%" + " " + capitalizable
        return super(LoanInteres, self).create(vals)

