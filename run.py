from dash_project.app import app

if __name__ == '__main__':
    app.run_server(debug=False)
    app.config.suppress_callback_exceptions = True

