from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'twoj_tajny_klucz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@db/wydatki'
db = SQLAlchemy(app)

# Model danych dla użytkownika
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Model danych dla wydatków
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Konfiguracja Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Strona główna
@app.route('/')
def index():
    return render_template('index.html')

# Rejestracja użytkownika
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return 'Użytkownik o tej nazwie już istnieje!'

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Nieprawidłowa nazwa użytkownika lub hasło!', 'error')  # Dodaj komunikat o błędzie
    return render_template('login.html')


# Wylogowanie użytkownika
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Strona panelu użytkownika
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

# Dodawanie wydatku
@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        expense = Expense(
            name=request.form['name'], 
            amount=request.form['amount'],
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        return render_template('expense_added.html')  # Renderuj nowy widok po dodaniu wydatku
    return render_template('add_expense.html')

# Kontroler do edycji wydatku
@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get(expense_id)
    
    if not expense or expense.user_id != current_user.id:
        return redirect(url_for('view_expenses'))
    
    if request.method == 'POST':
        expense.name = request.form['name']
        expense.amount = float(request.form['amount'])
        db.session.commit()
        flash('Wydatek został zaktualizowany!', 'success')
        return redirect(url_for('view_expenses'))
    
    return render_template('edit_expense.html', expense=expense)

# Usuwanie wydatku
@app.route('/delete_expense/<int:expense_id>')
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
    return redirect(url_for('view_expenses'))

# Dodaj link do edycji w widoku view_expenses.html
@app.route('/view_expenses')
@login_required
def view_expenses():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    return render_template('view_expenses.html', expenses=expenses)


# Utworzenie tabel
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=False)
