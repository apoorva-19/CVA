from fpdf import FPDF
title = "ETHANOWELL"

# header = ['First name','Last name','Age','City']
# data = [
#     ['Jules','Smith',34,'San Juan'],
#     ['Mary','Ramos',45,'Orlando'],
#     ['Carlson','Banks',19,'Los Angeles']
# ]

# duration = ['01-01-2019', '05-01-2019']
# gen_by = ['Shamsunder Dhoot', 'CH13A000023']

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
        self.cell(0, 6, label, 0, 1, 'C', 1)
        # Line break
        self.ln(4)
    
    def report_desc(self, duration, gen_by):
        '''
            Duration is an array in which the first value is the start date and the 
            second value is the end date

            Gen by is the array that contains the details of the report generator. 
            The first value is the name of the generator
            The second value is the id of the generator
            
        '''
        # Arial 12
        self.set_font('Arial', '', 12)
        # Text Color
        self.set_text_color(0,0,0)
        # Date
        self.cell(0, 6, "From: "+duration[0]+"  To: "+duration[1])
        self.ln(12)
        # Generated by
        self.cell(0,6, "Generated by: "+gen_by[0],0,1,'L')
        self.cell(0,6, "Id: "+gen_by[1])
        self.ln(12)

    def table(pdf, header, data):
        # Text Color
        pdf.set_text_color(0,0,0)
        # Text height
        th = 10.0
        # Column Width
        col_width = pdf.w / 6.5
        # For bold header
        pdf.set_font('Arial', 'B', 10)
        # Printing header
        for head in header:
            pdf.cell(col_width, th, str(head), border=1)
        pdf.ln(th)
        pdf.set_font('Arial', '', 10)
        # Printing the table
        for row in data:
            # Printing each element
            for datum in row:
                pdf.cell(col_width, th, str(datum), border=1)
            pdf.ln(th)



# pdf = PDF()
# pdf.add_page()
# pdf.set_title(title)
# pdf.set_font('Arial','',10.0) 
# pdf.report_title("Sample Report")
# pdf.report_desc(duration,gen_by)
# pdf.table()
# pdf.output('tuto3.pdf', 'F')