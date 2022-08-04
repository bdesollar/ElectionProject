from flask import Flask, render_template, request, url_for, redirect
import flask
app = Flask(__name__)

@app.route("/") #Adding /<name> adds to the url. This can also be done using app.add_url_rule('/',  'hello', home) *notice syntax*
def home():
    return render_template('homenav.html')

@app.route("/login", methods=['GET','POST'])
def login():
    error = None #Start off with no error
    if request.method == 'POST': 
        if request.form['username'] != 'admin' or request.form['password'] != 'admin': #FIXED TEST for words admin. These can most likely be channged to fit 
            error = 'Invalid Input Try again'
        else:
            return redirect(url_for('welcome'))
    return render_template('users/login.html', error=error)

#Very similar layout as Login. Just different function
@app.route("/register", methods=['GET','POST'])
def register():
    error = None #Start off with no error
    if request.method == 'POST': 
        if request.form['username'] != 'admin' or request.form['password'] != 'admin': #Tester variables, These can be used to 
            error = 'Invalid Input Try again'
        else:
            return redirect(url_for('/'))
    return render_template('users/admin_register.html', error=error)


@app.route("/welcome")
def welcome():
    return render_template('welcome.html')

@app.route("/about")
def about():
    return render_template('about.html')



if __name__ == '__main__':
    app.run(debug = True) #If debugger is set true the server will reload itself if the code changes