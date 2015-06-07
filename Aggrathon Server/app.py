from flask import Flask, render_template
app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app



#Static methods for showing pages
def show_page(title="", html="", page="", sidebar=True):
    template = "page_base.html"
    if(sidebar):
        template = "page_sidebar.html"
    #Only standard "Featured content" sidebar (no custom sidebars through this method
    if(title == ""):
        if(page == ""):
            return render_template(template, content=html)
        else:
            return render_template(template, content=html, page = page)
    else:
        if(page == ""):
            return render_template(template, title = title, content=html)
        else:
            return render_template(template, title = title, content=html, page = page)



#Include all routes
from routes import *

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
