from flask import Flask, render_template, request, redirect, url_for, send_file,jsonify
import sqlite3

app = Flask(__name__)

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Connect to the report database
def get_report_connection():
    conn = sqlite3.connect('report1.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if they don't exist
def create_tables():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        phone TEXT NOT NULL,
                        password TEXT NOT NULL)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS cars (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        type TEXT,
                        fuel TEXT,
                        seats INTEGER,
                        price_day INTEGER,
                        price_unlimited INTEGER,
                        free_kms INTEGER,
                        extra_km_charge REAL,
                        image_url TEXT)''')
    conn.commit()
    conn.close()

# Create report table for storing bookings in report1.db
def create_report_table():
    conn = get_report_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS bookings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        car_id INTEGER NOT NULL,
                        car_name TEXT NOT NULL,
                        plan TEXT NOT NULL,
                        quantity INTEGER DEFAULT 1,
                        FOREIGN KEY(car_id) REFERENCES cars(id)
                    )''')
    conn.commit()
    conn.close()

# Add sample car data with corrected image URLs
def add_sample_cars():
    conn = get_db_connection()
    existing_cars = conn.execute('SELECT * FROM cars').fetchall()
    
    if not existing_cars:
        sample_cars = [
            ("XUV 700", "SUV", "Petrol", 6, 7000, 12000, 500, 7, "xuv.png"),
            ("Tata Safari", "SUV", "Diesel", 7, 7000, 12000, 500, 7, "safari.png"),
            ("Virtus", "Sedan", "Petrol", 5, 7000, 12000, 500, 7, "virtus.png"),
            ("Tiago EV", "Hatchback", "EV", 5, 7000, 12000, 500, 7, "tiago.png")
        ]
        
        conn.executemany('''INSERT INTO cars (name, type, fuel, seats, price_day, price_unlimited, free_kms, extra_km_charge, image_url) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_cars)
        conn.commit()
    
    conn.close()

# Initialize databases
create_tables()
create_report_table()
add_sample_cars()


@app.route('/')
def home():
    return render_template('dbms1.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and user['password'] == password:
            conn.close()
            return redirect(url_for('car'))
        else:
            conn.close()
            alert = "Incorrect password" if user else "Username does not exist"
            return render_template('logindbms1.html', alert=alert)

    return render_template('logindbms1.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        re_password = request.form['re_password']

        if password != re_password:
            return render_template('signupdbms1.html', alert="Passwords do not match")

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)', (username, email, phone, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            existing_email = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            conn.close()
            if existing_user:
                return render_template('signupdbms1.html', alert="Username already exists")
            elif existing_email:
                return render_template('signupdbms1.html', alert="Email already exists")

    return render_template('signupdbms1.html')

@app.route('/car')
def car():
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM cars').fetchall()
    conn.close()
    return render_template('car.html', cars=cars)

@app.route('/book/<int:car_id>', methods=['POST'])
def book_car(car_id):
    username = request.form['username']
    plan = request.form['plan']

    # Retrieve car name from the car ID
    conn = get_db_connection()
    car = conn.execute('SELECT name FROM cars WHERE id = ?', (car_id,)).fetchone()
    car_name = car['name'] if car else "Unknown Car"
    conn.close()

    # Check if the user has already booked this car with the same plan
    conn = get_report_connection()
    booking = conn.execute('SELECT * FROM bookings WHERE username = ? AND car_id = ? AND plan = ?', (username, car_id, plan)).fetchone()

    if booking:
        # If booking exists, increase the quantity
        conn.execute('UPDATE bookings SET quantity = quantity + 1 WHERE username = ? AND car_id = ? AND plan = ?', (username, car_id, plan))
    else:
        # If no booking exists, create a new one
        conn.execute('INSERT INTO bookings (username, car_id, car_name, plan, quantity) VALUES (?, ?, ?, ?, ?)', (username, car_id, car_name, plan, 1))

    conn.commit()
    conn.close()

    # Redirect to the thank you page
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thankyou.html')

@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin_username = "admin"
        admin_password = "adminpass"

        if username == admin_username and password == admin_password:
            return redirect(url_for('admin_car'))
        else:
            return render_template('adminlogin.html', alert="Incorrect admin credentials")

    return render_template('adminlogin.html')

@app.route('/admincar')
def admin_car():
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM cars').fetchall()
    conn.close()
    return render_template('admincar.html', cars=cars)

@app.route('/generate_report')
def generate_report():
    conn = get_report_connection()
    bookings = conn.execute('SELECT * FROM bookings').fetchall()
    conn.close()

    # Create a report file
    report_file_path = 'booking_report.txt'
    with open(report_file_path, 'w') as report_file:
        for booking in bookings:
            report_file.write(f"USER: {booking['username']}\n")
            report_file.write(f"CAR RENTED: {booking['car_name']}\n")
            report_file.write(f"PLAN: {booking['plan']}\n")
            report_file.write(f"NUMBER OF CARS: {booking['quantity']}\n")
            report_file.write("\n")

    # Send the file to the user
    return send_file(report_file_path, as_attachment=True)

@app.route('/add_car', methods=['POST'])
def add_car():
    name = request.form['name']
    type = request.form['type']
    fuel = request.form['fuel']
    seats = request.form['seats']
    price_day = request.form['price_day']
    price_unlimited = request.form['price_unlimited']
    free_kms = request.form['free_kms']
    extra_km_charge = request.form['extra_km_charge']
    image_url = request.form['image_url']

    conn = get_db_connection()
    conn.execute('INSERT INTO cars (name, type, fuel, seats, price_day, price_unlimited, free_kms, extra_km_charge, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 (name, type, fuel, seats, price_day, price_unlimited, free_kms, extra_km_charge, image_url))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_car'))

@app.route('/delete_car/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM cars WHERE id = ?', (car_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_car'))

@app.route('/update_car/<int:car_id>', methods=['GET', 'POST'])
def update_car(car_id):
    conn = get_db_connection()
    car = conn.execute('SELECT * FROM cars WHERE id = ?', (car_id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        fuel = request.form['fuel']
        seats = request.form['seats']
        price_day = request.form['price_day']
        price_unlimited = request.form['price_unlimited']
        free_kms = request.form['free_kms']
        extra_km_charge = request.form['extra_km_charge']
        image_url = request.form['image_url']

        conn.execute('''UPDATE cars SET name = ?, type = ?, fuel = ?, seats = ?, price_day = ?, price_unlimited = ?, free_kms = ?, extra_km_charge = ?, image_url = ?
                        WHERE id = ?''', (name, type, fuel, seats, price_day, price_unlimited, free_kms, extra_km_charge, image_url, car_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_car'))
    
    conn.close()
    return render_template('updatecar.html', car=car)
@app.route('/search_car')
def search_car():
    query = request.args.get('query', '')
    conn = get_db_connection()
    cars = conn.execute('SELECT * FROM cars WHERE name LIKE ?', ('%' + query + '%',)).fetchall()
    conn.close()
    return render_template('car.html', cars=cars)


if __name__ == '__main__':
    app.run(debug=True)
