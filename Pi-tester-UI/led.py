import os
import web
from web import form
import csv

#Defining the index page
urls = ('/', 'index',
        '/graph/(.*)', 'graph',
        '/circle', 'circle' )
render = web.template.render('templates') #index.html is stored in '/templates' folder
app = web.application(urls, globals())

title = "Pi UI test"
test_form = web.form.Form(
    web.form.Textbox('', class_='textfield', id='textfield'),
    )

filepath = "/Users/0120140192/Desktop/Pi-tester-UI/results/"    #Defining the path for saved results
    
# define the task of index page
class index:
    # rendering the HTML page
    def GET(self):
        return render.index(title)

class graph:
    def GET(self, path):
        global filepath
        with open( filepath+path, 'rb') as f:
            reader = csv.reader(f)
            graphdata = map(tuple, reader)
        x_values = map(int, [row[0] for row in graphdata])
        y_values = map(int, [row[1] for row in graphdata])
        return render.graph(title, x_values, y_values)
    
class circle:
    def GET(self):
        global filepath
        form = test_form()
        file_list=os.listdir(filepath)
        return render.circle(form, title, "modify", file_list)

    def POST(self):
        form = test_form()
        form.validates()
        s = form.value['textfield']
        return s
    
# run
if __name__ == '__main__':
    app.run()

