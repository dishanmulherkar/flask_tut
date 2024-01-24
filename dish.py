from flask import Flask 

app = Flask(__name__)
 
@app.route('/about')
def about():
    return "dishan is good guy "

@app.route('/about')
def about():
    return "dishan is good guy "

@app.route('/about')
def about():
    return "dishan is good guy "



if __name__ == '__main__':

    app.run(debug=True)