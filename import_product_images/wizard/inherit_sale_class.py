
import base64
import csv
from odoo import api, fields, models,_
import re
from odoo import exceptions, http
from tempfile import TemporaryFile
from odoo.exceptions import UserError
import io
import urllib.request as req
import logging


_logger = logging.getLogger(__name__)


class Custom_Sale(models.TransientModel):
    _name = 'import.product.product'

    upload_file = fields.Binary(string='File URL')

    def import_apartments(self):

        csv_datas = self.upload_file
        fileobj = TemporaryFile('wb+')
        csv_datas = base64.decodebytes(csv_datas)
        fileobj.write(csv_datas)
        fileobj.seek(0)
        str_csv_data = fileobj.read().decode('utf-8')
        lis = csv.reader(io.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        DATE_FORMAT = '%m/%d/%Y'
        error_list = []
        header_list = []
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header_list.append(value)
                else:
                    _logger.info('-----row number %s', key)
                    internal_reference = value[0].strip() or False
                    pdf_url = value[1].strip() or False
                    _logger.info('-----inside else-------- %s', internal_reference,pdf_url)
                    # name = value[1].strip() or False
                    # # uom = value[2].strip() or False
                    # # uom_value = value[3].strip() or False
                    # public_price = value[2].strip() or False
                    # cost = value[3].strip() or False
                    # product_type = value[4].strip() or False
                    # product_category = value[5].strip() or False
                    # description = value[6].strip() or False

                    # project_obj = self.env['product.product'].search([('name', '=', project)])
                    #
                    # apartment_obj = self.env['product.product'].search([('name', '=', apartment_no)])

                    # if project_obj.id == apartment_obj.project_no.id:
                    #     print('Apartment already Exists with Project.')
                    # elif not apartment_obj:
                        # url = 'http://www.hrecos.org//images/Data/forweb/HRTVBSH.Metadata.pdf'
                    matched_id = self.env['product.template'].search([('default_code', '=', internal_reference)])
                    if "http://" in pdf_url or "https://" in pdf_url and matched_id:
                        try:
                            if pdf_url.__contains__('drive.google.com'):
                                pdf_url = re.sub("/file/d/", "/uc?export=download&id=", pdf_url)
                                pdf_url = re.sub("/view\?usp=sharing", "", pdf_url)
                            request = req.Request(pdf_url, headers={'User-Agent': "odoo"})
                            binary = req.urlopen(request)
                            pdf = base64.b64encode(binary.read())
                            _logger.info('-----inside try-------- %s')
                        except Exception as e:
                            raise UserError(e)
                        # project = self.env['project.product'].search([('id', '=', 522)])
                        # project.write({'document': pdf})
                        apartment_vals = {
                            # 'default_code': internal_reference,
                            # 'name': name,
                            # # 'attribute_line_ids/attribute_id': uom,
                            # # 'attribute_line_ids/value_ids': uom_value,
                            # 'lst_price': public_price,
                            # 'standard_price': cost,
                            # # 'type': product_type.id,
                            # # 'categ_id': product_category.id,
                            # 'description': description,
                            'image_1920': pdf or False,
                        }
                    elif matched_id:
                        with open(pdf_url, 'rb') as image:
                            pdf = base64.b64encode(image.read())
                        apartment_vals = {
                            # 'default_code': internal_reference,
                            # 'name': name,
                            # 'attribute_line_ids/attribute_id': uom,
                            # 'attribute_line_ids/value_ids': uom_value,
                            # 'lst_price': public_price,
                            # 'standard_price': cost,
                            # 'type': product_type.id,
                            # 'categ_i d': product_category.id,
                            # 'description': description,
                            'image_1920': pdf or False,

                        }

                        new_apartment_id = matched_id.sudo().write(apartment_vals)

                    else:
                        raise UserError(_('Internal reference  % s is not available in the system', internal_reference))

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)
                error_list.append(value)
                if 'not enough arguments for format string' in e.args:
                    raise UserError(_('Internal reference %s is not available in the system', value[0].strip()))
                else:
                    raise UserError(
                        _('Please provide correct URL for product  or check your image size.!'))


