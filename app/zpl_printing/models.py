import zpl
import re


class ZPLLabel(zpl.Label):

    def append_code(self, code):
        try:
            self.code += code
        except UnicodeEncodeError:
            self.code = self.code.decode().encode('utf-8')
            self.code += code

    def unicode(self):
        self.append_code("^CI28")

    def write_unicode_text(self, text, char_height=None, char_width=None, font='0', orientation='N',
                           line_width=None, max_line=1, line_spaces=0, justification='L', hanging_indent=0):
        if char_height and char_width and font and orientation:
            assert orientation in 'NRIB', "invalid orientation"
            if re.match(r'^[A-Z0-9]$', font):
                self.code += "^A%c%c,%i,%i" % (font, orientation, char_height * self.dpmm,
                                               char_width * self.dpmm)
            elif re.match(r'[REBA]?:[A-Z0-9\_]+\.(FNT|TTF|TTE)', font):
                self.code += "^A@%c,%i,%i,%s" % (orientation, char_height * self.dpmm,
                                                 char_width * self.dpmm, font)
            else:
                raise ValueError("Invalid font.")
        if line_width is not None:
            assert justification in "LCRJ", "invalid justification"
            self.code += "^FB%i,%i,%i,%c,%i" % (line_width * self.dpmm, max_line, line_spaces,
                                                justification, hanging_indent)
        self.code += "^CI17^F8^FD"
        self.append_code(text)

    def write_barcode(self, height, barcode_type, oritentation='N', check_digit='N',
                      print_interpretation_line='Y', print_interpretation_line_above='N'):
        # guard for only currently allowed bar codes
        assert barcode_type in ['2', '3', 'U', 'C'], "invalid barcode type"

        if barcode_type == '2':
            barcode_zpl = '^B%s%s,%i,%s,%s,%s' % (barcode_type, oritentation, height,
                                                  print_interpretation_line,
                                                  print_interpretation_line_above,
                                                  check_digit)
        elif barcode_type == '3':
            barcode_zpl = '^B%s%s,%s,%i,%s,%s' % (barcode_type, oritentation,
                                                  check_digit, height,
                                                  print_interpretation_line,
                                                  print_interpretation_line_above)
        elif barcode_type == 'U':
            barcode_zpl = '^B%s%s,%s,%s,%s,%s' % (barcode_type, oritentation, height,
                                                  print_interpretation_line,
                                                  print_interpretation_line_above,
                                                  check_digit)
        elif barcode_type == 'C':
            barcode_zpl = '^B%s,%s,%s,%s,%s' % (barcode_type, height,
                                                  print_interpretation_line,
                                                  print_interpretation_line_above,
                                                  check_digit)
        elif barcode_type == 'Q':
            barcode_zpl = '^BQN,2,8,Q,7'

        self.code += barcode_zpl

    def print_qr(self, model=2, magnification_factor=8):
        self.append_code("^BQN,%i,%i,Q,7" % (model, magnification_factor))
