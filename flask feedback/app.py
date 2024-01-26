from flask import Flask, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Change this to your actual database URI
db = SQLAlchemy(app)

# Import the User and Feedback models from models.py
from models import User, Feedback

# WTForms Feedback Form
class FeedbackForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    content = TextAreaField('Content', validators=[InputRequired()])
    submit = SubmitField('Submit Feedback')

# Routes
@app.route('/users/<username>')
def user_profile(username):
    # Check if the user is logged in
    if 'username' in session:
        # Ensure the logged-in user matches the requested username
        if session['username'] == username:
            user = User.query.filter_by(username=username).first()
            if user:
                feedback = Feedback.query.filter_by(user_id=user.id).all()
                return render_template('user_profile.html', user=user, feedback=feedback)
            else:
                flash('User not found', 'danger')
        else:
            flash('You are not authorized to view this page', 'danger')
    else:
        flash('Please log in to view your profile', 'danger')
    return redirect(url_for('login'))

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    # Check if the user is logged in
    if 'username' in session:
        # Ensure the logged-in user matches the requested username
        if session['username'] == username:
            user = User.query.filter_by(username=username).first()
            if user:
                # Delete all feedback associated with the user
                Feedback.query.filter_by(user_id=user.id).delete()
                
                # Delete the user
                db.session.delete(user)
                db.session.commit()

                # Clear the session
                session.pop('username', None)

                flash('Your account has been deleted.', 'info')
                return redirect(url_for('login'))
            else:
                flash('User not found', 'danger')
        else:
            flash('You are not authorized to delete this account', 'danger')
    else:
        flash('Please log in to delete your account', 'danger')
    return redirect(url_for('login'))

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    # Check if the user is logged in
    if 'username' in session:
        # Ensure the logged-in user matches the requested username
        if session['username'] == username:
            user = User.query.filter_by(username=username).first()
            if user:
                form = FeedbackForm()
                if form.validate_on_submit():
                    new_feedback = Feedback(
                        title=form.title.data,
                        content=form.content.data,
                        user_id=user.id
                    )
                    db.session.add(new_feedback)
                    db.session.commit()

                    flash('Feedback added successfully!', 'success')
                    return redirect(url_for('user_profile', username=username))
                return render_template('add_feedback.html', form=form)
            else:
                flash('User not found', 'danger')
        else:
            flash('You are not authorized to add feedback for this user', 'danger')
    else:
        flash('Please log in to add feedback', 'danger')
    return redirect(url_for('login'))

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    # Check if the user is logged in
    if 'username' in session:
        feedback = Feedback.query.get(feedback_id)
        if feedback:
            # Ensure the logged-in user matches the user who wrote the feedback
            if session['username'] == feedback.user.username:
                form = FeedbackForm(obj=feedback)
                if form.validate_on_submit():
                    feedback.title = form.title.data
                    feedback.content = form.content.data
                    db.session.commit()

                    flash('Feedback updated successfully!', 'success')
                    return redirect(url_for('user_profile', username=feedback.user.username))
                return render_template('update_feedback.html', form=form, feedback=feedback)
            else:
                flash('You are not authorized to update this feedback', 'danger')
        else:
            flash('Feedback not found', 'danger')
    else:
        flash('Please log in to update feedback', 'danger')
    return redirect(url_for('login'))

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    # Check if the user is logged in
    if 'username' in session:
        feedback = Feedback.query.get(feedback_id)
        if feedback:
            # Ensure the logged-in user matches the user who wrote the feedback
            if session['username'] == feedback.user.username:
                db.session.delete(feedback)
                db.session.commit()

                flash('Feedback deleted successfully!', 'info')
                return redirect(url_for('user_profile', username=feedback.user.username))
            else:
                flash('You are not authorized to delete this feedback', 'danger')
        else:
            flash('Feedback not found', 'danger')
    else:
        flash('Please log in to delete feedback', 'danger')
    return redirect(url_for('login'))

# Other routes remain unchanged

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
