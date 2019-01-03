from fpdf import FPDF
title = "ETHANOWELL"
data = [
    ['First name','Last name','Age','City'],
    ['Jules','Smith',34,'San Juan'],
    ['Mary','Ramos',45,'Orlando'],
    ['Carlson','Banks',19,'Los Angeles']
]

class PDF(FPDF):
    def header(self):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Background color
        self.set_fill_color(139,195,74)
        # Text color
        self.set_text_color(255,255,255)
        # Title
        self.cell(0, 6, title, 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def report_title(self, label):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Background color
        self.set_fill_color(199,225,134)
        # Text color
        self.set_text_color(255,255,255)
        # Title
        self.cell(0, 6, label, 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def table(data,pdf, self):
        # Text height
        th = 10.0
        # Printing the table
        for row in data:
            # Printing each element
            for datum in row:
                pdf.cell(col_width, th, str(datum), border=1)
            pdf.ln(th)



pdf = PDF()
pdf.add_page()
pdf.set_title(title)
pdf.set_font('Arial','',10.0) 
pdf.report_title("Sample Report")
pdf.table(data, pdf)
pdf.output('tuto3.pdf', 'F')