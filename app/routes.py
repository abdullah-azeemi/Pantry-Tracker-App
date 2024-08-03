from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.forms import LoginForm, SignupForm
from app.models import get_user_by_email, create_user
from app.ai_assistant import AI_Assistant

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        if user and check_password_hash(user['password'], form.password.data):
            session['user_id'] = str(user['_id'])  # Convert ObjectId to string
            return redirect(url_for('pantry'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if get_user_by_email(form.email.data):
            flash('Email address already registered', 'danger')
        else:
            password_hash = generate_password_hash(form.password.data)
            create_user(form.email.data, password_hash)
            flash('You have successfully registered! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/pantry')
def pantry():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_pantry = db.pantry.find_one({'user_id': session['user_id']})
    items = user_pantry['items'] if user_pantry else []
    return render_template('pantry.html', items=items)

@app.route('/suggestions')
def suggestions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_pantry = db.pantry.find_one({'user_id': session['user_id']})
    items = user_pantry['items'] if user_pantry else []
    ai_assistant = AI_Assistant()
    recipes = ai_assistant.generate_ai_response(items)
    return render_template('suggestions.html', recipes=[recipes])

@app.route('/add_item', methods=['POST'])
def add_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    item_name = request.form.get('item_name')
    item_quantity = int(request.form.get('item_quantity', 1))

    if item_name:
        user_pantry = db.pantry.find_one({'user_id': session['user_id']})

        if user_pantry:
            existing_item = next((item for item in user_pantry['items'] if item['name'] == item_name), None)
            if existing_item:
                db.pantry.update_one(
                    {'user_id': session['user_id'], 'items.name': item_name},
                    {'$inc': {'items.$.quantity': item_quantity}}
                )
            else:
                db.pantry.update_one(
                    {'user_id': session['user_id']},
                    {'$push': {'items': {'name': item_name, 'quantity': item_quantity}}},
                    upsert=True
                )
        else:
            db.pantry.insert_one({
                'user_id': session['user_id'],
                'items': [{'name': item_name, 'quantity': item_quantity}]
            })
        
        flash('Item added to pantry', 'success')
    return redirect(url_for('pantry'))


@app.route('/remove_item', methods=['POST'])
def remove_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    item_name = request.form.get('item_name')
    item_quantity = int(request.form.get('item_quantity', 1))  
    if item_name:
        user_pantry = db.pantry.find_one({'user_id': session['user_id']})
        if user_pantry:
            existing_item = next((item for item in user_pantry['items'] if item['name'] == item_name), None)
            if existing_item:
                new_quantity = existing_item['quantity'] - item_quantity
                if new_quantity > 0:
                    db.pantry.update_one(
                        {'user_id': session['user_id'], 'items.name': item_name},
                        {'$set': {'items.$.quantity': new_quantity}}
                    )
                else:
                    db.pantry.update_one(
                        {'user_id': session['user_id']},
                        {'$pull': {'items': {'name': item_name}}}
                    )
                flash('Item updated in pantry', 'success')
            else:
                flash('Item not found in pantry', 'warning')
        else:
            flash('Pantry not found', 'warning')
    
    return redirect(url_for('pantry'))
