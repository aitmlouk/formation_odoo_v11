from odoo import models, fields, api,_
from odoo.exceptions import UserError, AccessError, ValidationError



class Registration(models.Model):
    _name = 'registration.registration'
    _description = 'egistration.registration'
    _inherit = ['mail.thread']

    @api.multi
    def print_report(self):
        return self.env.ref('formation.report_registration').report_action(self)
    @api.one
    def action_new(self):
        self.state = 'new'
        return True
    
    @api.one
    def action_done(self):
        self.state = 'done'
        return True   

    @api.one
    def action_cancel(self):
        self.state = 'cancel'
        return True   
    
        
    @api.model
    @api.depends('code')
    def create(self, vals):
        if ('code' not in vals) or (vals.get('code')=='/'):
            vals['code'] = self.env['ir.sequence'].get('registration.registration')
        return super(Registration, self).create(vals) 
    
    @api.multi
    def write(self, vals):
        vals['name'] = 'value by write method'
        return super(Registration, self).write(vals)
    
    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        default.update({'name': 'copy(name)','code': 'copy -001'})
        return super(Registration, self).copy(default)


    @api.multi
    def unlink(self):
        for record in self:
            if record.state in 'done,cancel':
                raise UserError(_('You cannot delete records in done state.'))
        res = super(Registration, self).unlink()
        return res

    @api.one
    @api.depends('claim_ids')
    def _compute_claims(self):
        self.nbr = len(self.claim_ids)
        
            
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', default='/', readonly=True)
    start_date = fields.Date('Date début',help="Date",track_visibility='onchange')
    end_date = fields.Date('Date fin',help="Date")
    description=fields.Text(string='description', required=False, readonly=False)
    cycle_id = fields.Many2one('cycle.cycle', string='Cycle', track_visibility='onchange') 
    year_id = fields.Many2one('year.year', string='Année univ', track_visibility='onchange')
    claim_ids = fields.One2many('claim.claim', 'reg_id', string='Reclamation')
    student_id = fields.Many2one('res.partner', string='Etudiant',domain="[('student_ok', '=',True)]", track_visibility='onchange')
    state=fields.Selection([('new', 'Nouveau'), ('done', 'Validé'), ('cancel', 'Annulé')], string= 'Status', default='new',track_visibility='onchange')
    
    nbr = fields.Integer(compute='_compute_claims', string='#reclamation')


class Claim(models.Model):
    _name = 'claim.claim'
    _description = 'Reclamation'
    
    
    @api.one
    @api.depends('amount','hours_nbr')
    def _total_compute(self):
        if self.hours_nbr:
            self.total = self.amount * self.hours_nbr
        else :
            self.sum = self.amount + self.amount
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', default=lambda x: x.env['ir.sequence'].get('claim.claim'))
    start_date = fields.Date('Date début',help="Date")
    end_date = fields.Date('Date fin',help="Date")
    description=fields.Text(string='description', required=False, readonly=False)
    reg_id = fields.Many2one('registration.registration', string='Inscription')
    user_id = fields.Many2one('res.users',string='Responsable')
    state=fields.Selection([('new', 'Nouvelle'), ('done', 'Validé'), ('cancel', 'Annulée')], string= 'Status')
    priority=fields.Selection([('1', 'base'), ('2', 'normal'), ('3', 'hight')], string= 'Priorité')
    
    amount = fields.Float(string='Montant')
    hours_nbr = fields.Integer(string='#heurs')
    sum = fields.Float(string='Somme')
    total = fields.Float(compute='_total_compute',string='Total')
    
 
 
 
    
class Year(models.Model):
    _name = 'year.year'
    _description = 'year.year'
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', required=False, readonly=False)
    start_date = fields.Date('Date début',help="Date")
    end_date = fields.Date('Date fin',help="Date")
    description=fields.Text(string='description', required=False, readonly=False)
    session_ids = fields.One2many('session.session','year_id',string='Session')
    
    
class Session(models.Model):
    _name = 'session.session'
    _description = ''
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', required=False, readonly=False)
    start_date = fields.Date('Date début',help="Date")
    end_date = fields.Date('Date fin',help="Date")
    description=fields.Text(string='description', required=False, readonly=False)
    year_id = fields.Many2one('year.year', string='Année univ')
    

class Cycle(models.Model):
    _name = 'cycle.cycle'
    _description = 'cycle.cycle'
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', required=False, readonly=False)
    description=fields.Text(string='description', required=False, readonly=False)
    level_ids = fields.One2many('level.level','cycle_id', string='Niveau') 
 
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.name + ' -- ' + record.code))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result   
    
class Level(models.Model):
    _name = 'level.level'
    _description = 'level.level'
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', required=False, readonly=False)
    description=fields.Text(string='description', required=False, readonly=False)
    section_ids = fields.One2many('section.section','level_id', string='Section') 
    cycle_id =fields.Many2one('cycle.cycle', string='Cycle')
        
class Section(models.Model):
    _name = 'section.section'
    _description = 'section.section'
 
    name=fields.Char(string='Nom', required=False, readonly=False)
    code=fields.Char(string='Code', required=False, readonly=False)
    description=fields.Text(string='description', required=False, readonly=False)
    module_ids = fields.One2many('module.module','section_id', string='Module') 
    level_id = fields.Many2one('level.level', string='Niveau')


class Module(models.Model):
    _name = 'module.module' 
    _description = 'modules' 
    
    name = fields.Char(string='Nom', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    section_id = fields.Many2one('section.section',string='Section')
 
class Partner(models.Model):
    _inherit = 'res.partner' 
    
    student_ok = fields.Boolean(string='Est un étudiant')
    birthday = fields.Date(string='Date de naissance')
    age = fields.Integer(string='Age')
    reg_ids = fields.One2many('registration.registration','student_id', string='Inscription')
    

class Prof(models.Model):
    _inherit = 'hr.employee' 
    _name = 'teacher.teacher'
    
    age = fields.Integer(string='Age')
    cin = fields.Char(string='CIN')
 
    
    
    
 

    
    
    
