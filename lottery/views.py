# IMPORTS
import logging

from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from app import db, requires_roles
from models import Draw, decrypt
from sqlalchemy.orm import make_transient


# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# VIEWS
# view lottery page
@lottery_blueprint.route('/lottery')
#there has to be an account logged in to view the lottery page
@login_required
#the view lottery page can only be viewed when the user account is logged in
@requires_roles('user')
def lottery():
    return render_template('lottery/lottery.html')


@lottery_blueprint.route('/add_draw', methods=['POST'])
def add_draw():
    submitted_draw = ''
    for i in range(6):
        submitted_draw += request.form.get('no' + str(i + 1)) + ' '
    submitted_draw.strip()

    # create a new draw with the form data.
    #changed user_id=1 to =current_user.id meaning when a new draw is created its user_id will correspond to the id of the current user signed in
    new_draw = Draw(user_id=current_user.id, numbers=submitted_draw, master_draw=False, lottery_round=0)  # TODO: update user_id [user_id=1 is a placeholder]


    # add the new draw to the database
    db.session.add(new_draw)
    db.session.commit()

    # re-render lottery.page
    flash('Draw %s submitted.' % submitted_draw)
    return lottery()


# view all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
@login_required
@requires_roles('user')
def view_draws():
    # get all draws that have not been played [played=0]
    #playable_draws = Draw.query.filter_by(been_played= False).all()  # TODO: filter playable draws for current user

    #shows the playable draws that belong to current user signed in
    playable_draws = Draw.query.filter_by(user_id= current_user.id, been_played=False).all()

    # if playable draws exist
    if len(playable_draws) != 0:
        user_id = current_user.id
        i = 0
        # decrypts the numbers before showing them when the view playable draws is clicked
        for draw in playable_draws:
            make_transient(draw)
            draw.numbers = decrypt(draw.numbers, current_user.postkey)
            i += 1

        # re-render lottery page with playable draws
        return render_template('lottery/lottery.html', playable_draws=playable_draws)
    else:
        flash('No playable draws.')
        return lottery()


# view lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
@login_required
@requires_roles('user')
def check_draws():
    # get played draws
    played_draws = Draw.query.filter_by(user_id= current_user.id, been_played=True).all()  # TODO: filter played draws for current user

    # if played draws exist
    if len(played_draws) != 0:
        return render_template('lottery/lottery.html', results=played_draws, played=True)

    # if no played draws exist [all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
@login_required
@requires_roles('user')
def play_again():
    Draw.query.filter_by(been_played=True, master_draw=False).delete(synchronize_session=False)
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()


