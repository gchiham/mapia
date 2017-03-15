from openerp import fields, models, exceptions, api, _
import base64
import csv
import cStringIO
from openerp.exceptions import except_orm, Warning, RedirectWarning

class Contractwizard(models.TransientModel):
	_name = "mngfees.coursewizard"
    	
	course_id=fields.Many2one("mngfees.course","Course", required=True)
	section_id = fields.Many2one("mngfees.sections","Section", required=True)

	
	@api.one
	def action_selection_section(self):
		ctx = self._context
		obj_contract= self.env["mngfees.contractsale"].browse(ctx['active_id'])
		obj_section= self.env["mngfees.sections"].browse(ctx['active_id'])
		print "*"*500
		print obj_contract
		print "-"*500
		obj_contract.write({'section_ids': [(0,0,{'course_id': self.course_id.id, 'name': self.section_id.name, 'start_date': self.section_id.start_date, 'end_date': self.section_id.end_date})]})
		

