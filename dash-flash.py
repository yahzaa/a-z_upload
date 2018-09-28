from dash import Dash
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go


from werkzeug.wsgi import DispatcherMiddleware
from flask import  Flask, render_template, redirect, url_for, request, session, g
from werkzeug.serving import run_simple
import requests
#import athleteDash

server = Flask(__name__)
dash1 = Dash(__name__, server = server, url_base_pathname='/dashboard/' )

def print_button():
    printButton = html.A(['Print PDF'],className="button no-print print",style={'position': "absolute", 'top': '-40', 'right': '0'})
    return printButton

# includes page/full view
def get_logo():
    logo = html.Div([

        html.Div([
            html.Img(src='http://logonoid.com/images/vanguard-logo.png', height='40', width='160')
        ], className="ten columns padded"),

        html.Div([
            dcc.Link('Full View   ', href='/full-view')
        ], className="two columns page-view no-print")

    ], className="row gs-header")
    return logo


def get_header():
    header = html.Div([

        html.Div([
            html.H5(
                'Vanguard 500 Index Fund Investor Shares')
        ], className="twelve columns padded")

    ], className="row gs-header gs-text-header")
    return header


def get_menu():
    menu = html.Div([

        dcc.Link('Overview   ', href='/overview', className="tab first"),

        # dcc.Link('Price Performance   ', href='/price-performance', className="tab"),

        # dcc.Link('Portfolio & Management   ', href='/portfolio-management', className="tab"),

        # dcc.Link('Fees & Minimums   ', href='/fees', className="tab"),

        # dcc.Link('Distributions   ', href='/distributions', className="tab"),

        # dcc.Link('News & Reviews   ', href='/news-and-reviews', className="tab")

    ], className="row ")
    return menu


overview = html.Div([  # page 1

        print_button(),

        html.Div([

            # Header
            get_logo(),
            get_header(),
            html.Br([]),
            get_menu(),

            html.Div([
              dcc.Upload(
                id='upload-data',
                children=html.Div([
                  'Drag and Drop File or ',
                  html.A('Select Files')
                  ]),
                style={
                'width':'100%',
                'height':'60px',
                'lineHeight':'60px',
                'borderWidth':'1px',
                'borderStyle':'dashed',
                'borderRadius':'5px',
                'textAlign':'center',
                'margin':'10px',
                },
                #allow multiple files to be uploaded here 
                multiple=True
                ),
                html.Div(id='output-data-upload'),
                #html.Div(dt.DataTable(rows=[{}]), style={'display':'none'})
              ], className='row'),
        ], className="subpage")

    ], className="page")


noPage = html.Div([  # 404

    html.P(["404 Page not found"]),
    html.H3('hello we are here'),
    get_header(),
    get_menu(),

    ], className="no-page")



# Describe the layout, or the UI, of the app
dash1.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Upload(id='upload-data'),
    html.Div(id='output-data-upload'),
    html.Div(id='page-content'),
])

  
# Update page
@dash1.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dashboard/' or pathname == '/overview':
        return overview
    elif pathname == '/price-performance':
        return pricePerformance
    elif pathname == '/portfolio-management':
        return portfolioManagement
    elif pathname == '/fees':
        return feesMins
    elif pathname == '/distributions':
        return distributions
    elif pathname == '/news-and-reviews':
        return newsReviews
    elif pathname == '/full-view':
        return overview,pricePerformance,portfolioManagement,feesMins,distributions,newsReviews
    else:
        return noPage

from parser import parser_csv

#upload data 
@dash1.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data','last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
  if list_of_contents is not None:
    children = [
        parser_csv.parse_contents(c,n,d) for c, n, d in
        zip(list_of_contents, list_of_names, list_of_dates)]
    upload_data = children
    print(children)

    return children
#dash_app2 = Dash(__name__, server = server, url_base_pathname='/reports/')
#dash_app1.layout = html.Div([html.H1('Hi there, I am app1 for dashboards')])
#dash_app2.layout = html.Div([html.H1('Hi there, I am app2 for reports')])

@server.route('/')
@server.route('/login', methods=['POST','GET'])
def login():
	return render_template('login.html')


@server.route('/loginTwo', methods=['POST', 'GET'])
def loginTwo():
	error = None
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		payload_login = dict(username=username,password=password)
		token = requests.post("https://a-zapi.herokuapp.com/login/",data=payload_login)
		if token.status_code != 200:
			return "error " + str(token.status_code)
		else: 
			#session['access_token'] = token.json()['token']
			return redirect(url_for('/dashboard/'))
	return render_template('login.html')

@server.route('/dashboard')
def render_dashboard():
    return flask.redirect('/dash1')

# @server.route('/reports')
# def render_reports():
#     return flask.redirect('/dash2')
external_css = ["https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
                "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "https://codepen.io/bcd/pen/KQrXdb.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
                "https://codepen.io/chriddyp/pen/bWLwgP.css",]

for css in external_css:
    dash1.css.append_css({"external_url": css})

external_js = ["https://code.jquery.com/jquery-3.2.1.min.js",
               "https://codepen.io/bcd/pen/YaXojL.js"]

for js in external_js:
    dash1.scripts.append_script({"external_url": js})

app = DispatcherMiddleware(server, {
    '/dash1': dash1.server,
    #'/dash2': dash_app2.server
})

run_simple('0.0.0.0', 8080, app, use_reloader=True, use_debugger=True)