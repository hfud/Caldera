from lxml import etree as ET 
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, PageBreak, Image
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate

class Story:
    _header_logo_path = None

    def __init__(self):
        self.story_arr = []

    def append(self, data):
        self.story_arr.append(data)
        self.story_arr.append(Spacer(1, 12))

    def append_text(self, text, style, space):
        self.story_arr.append(Paragraph(text, style))
        self.story_arr.append(Spacer(1, space))

    def get_description(self, desc):
        return self._descriptions(desc)

    def page_break(self):
        self.story_arr.append(PageBreak())

    @staticmethod
    def set_header_logo_path(header_logo_path):
        Story._header_logo_path = header_logo_path

    @staticmethod
    def header_footer_first(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Header
        caldera_logo = "./plugins/debrief/static/img/caldera.png"
        im = Image(caldera_logo, 1.5 * inch, 1 * inch)
        im.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - im.drawHeight / 2)

        if Story._header_logo_path:
            Story.draw_header_logo(canvas, doc, Story._header_logo_path)

        canvas.setStrokeColor(colors.maroon)
        canvas.setLineWidth(4)
        canvas.line(doc.leftMargin + im.drawWidth + 5,
                    doc.height + doc.topMargin,
                    doc.width + doc.leftMargin,
                    doc.height + doc.topMargin)

        # Footer
        page_num = canvas.getPageNumber()
        text = "Page %s" % page_num
        canvas.drawRightString(doc.width + doc.rightMargin * 1.5, doc.bottomMargin / 2, text)

        # Release the canvas
        canvas.restoreState()

    @staticmethod
    def header_footer_rest(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()

        # Header
        if Story._header_logo_path:
            Story.draw_header_logo(canvas, doc, Story._header_logo_path)

        canvas.setFillColor(colors.maroon)
        canvas.setFont('Helvetica-Bold', 18)
        canvas.drawString(doc.leftMargin, doc.height + doc.topMargin * 1.25, 'OPERATIONS DEBRIEF')
        canvas.setStrokeColor(colors.maroon)
        canvas.setLineWidth(4)
        canvas.line(doc.leftMargin,
                    doc.height + doc.topMargin * 1.25 - 5,
                    doc.width + doc.leftMargin,
                    doc.height + doc.topMargin * 1.25 - 5)

        # Footer
        canvas.setFillColor(colors.black)
        canvas.setFont('Helvetica', 10)
        page_num = canvas.getPageNumber()
        text = "Page %s" % page_num
        canvas.drawRightString(doc.width + doc.rightMargin * 1.5, doc.bottomMargin / 2, text)

        # Release the canvas
        canvas.restoreState()

    @staticmethod
    def draw_header_logo(canvas, doc, logo_path):
        im = Image(logo_path, 2.5 * inch, 0.75 * inch)
        im.drawOn(canvas, doc.width + doc.leftMargin + doc.rightMargin - im.drawWidth - 10,
                  doc.height + doc.topMargin + doc.bottomMargin - im.drawHeight - 10)

    @staticmethod
    def adjust_icon_svgs(path):
        parser = ET.XMLParser(resolve_entities=False)
        svg = ET.parse(path, parser)
        for icon_svg in svg.getroot().iter("{http://www.w3.org/2000/svg}svg"):
            if icon_svg.get('id') == 'copy-svg':
                continue
            viewbox = [int(float(val)) for val in icon_svg.get('viewBox').split()]
            aspect = viewbox[2] / viewbox[3]
            icon_svg.set('width', str(round(float(icon_svg.get('height')) * aspect)))
            if not icon_svg.get('id') or 'legend' not in icon_svg.get('id'):
                icon_svg.set('x', '-' + str(int(icon_svg.get('width')) / 2))
        svg.write(open(path, 'wb'))

    @staticmethod
    def get_table_object(val):
        table_style = ParagraphStyle(name='Table', fontSize=8, wordWrap='CJK')
        max_chars = 1000
        max_height = 600

        if isinstance(val, str):
            val = val.replace('\n', '<br/>')
            if len(val) > max_chars:
                val = val[:max_chars] + '<br/><b>(truncated)</b>'
            para = Paragraph(val, table_style)

        elif isinstance(val, list):
            list_string = '<br/>'.join(val)
            if len(list_string) > max_chars:
                list_string = list_string[:max_chars] + '<br/><b>(truncated)</b>'
            para = Paragraph(list_string, table_style)

        elif isinstance(val, dict):
            dict_string = ''
            for k, v in val.items():
                dict_string += f'<font color=grey>{k}</font><br/>'
                for item in v:
                    dict_string += f'&nbsp;&nbsp;&nbsp;{item}<br/>'
            if len(dict_string) > max_chars:
                dict_string = dict_string[:max_chars] + '<br/><b>(truncated)</b>'
            para = Paragraph(dict_string, table_style)

        else:
            para = Paragraph('<b>[Unsupported Type]</b>', table_style)

        temp_doc = SimpleDocTemplate(BytesIO())
        w, h = para.wrap(temp_doc.width, temp_doc.height)
        if h > max_height:
            return Paragraph('<b>[Content too long - omitted]</b>', table_style)
        return para