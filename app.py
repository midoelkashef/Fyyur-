#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.dialects.postgresql import ARRAY
from flask_migrate import Migrate
from datetime import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:mido2210@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String()))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True)
    artist_id = db.Column(
        db.Integer, db.ForeignKey('Artist.id'), nullable=True)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    venue_locations = Venue.query.distinct(
        'city', 'state').order_by('state').all()
    for location in venue_locations:
        location.venues = Venue.query.filter_by(
            city=location.city, state=location.state)

    return render_template('pages/venues.html', areas=venue_locations)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')

    info = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))

    counts = 0

    for i in info:
        data = []
        data.append(i.name)
        counts = counts + len(data)

    response = {
        "count": counts,
        "data": info,
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()
    past_shows = []
    upcoming_shows = []
    show_time = datetime.today()

    for show in shows:

        venu_info = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        }

        if show_time < show.start_time:
            upcoming_shows.append(venu_info)
        else:
            past_shows.append(venu_info)

    data = {
        "id": venue.id,
        "name": venue.name,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "image_link": venue.image_link,
        "website": venue.website,
        "genres": venue.genres,
        "facebook_link": venue.facebook_link,
        "seeking_description": venue.seeking_description,
        "past_shows": past_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    error = False

    try:
        add_new_venue = Venue(

            name=request.form.get('name'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            address=request.form.get('address'),
            phone=request.form.get('phone'),
            genres=request.form.getlist('genres'),
            facebook_link=request.form.get('facebook_link')

        )

        db.session.add(add_new_venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' +
              add_new_venue.name + ' could not be listed.')

    else:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    error = False
    try:
        delete_venue = Venue.query.get(venue_id)
        db.session.delete(delete_venue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    artists = Artist.query.order_by(Artist.name).all()
    data = []

    for artist in artists:
        data.append({
            'id': artist.id,
            'name': artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')

    info = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))

    counts = 0

    for i in info:
        data = []
        data.append(i.name)
        counts = counts + len(data)

    response = {
        "count": counts,
        "data": info,
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id).all()
    past_shows = []
    upcoming_shows = []
    show_time = datetime.today()

    for show in shows:

        artist_info = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(show.start_time)
        }

        if show_time < show.start_time:
            upcoming_shows.append(artist_info)
        else:
            past_shows.append(artist_info)

    data = {
        "id": artist.id,
        "name": artist.name,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "image_link": artist.image_link,
        "website": artist.website,
        "genres": artist.genres,
        "facebook_link": artist.facebook_link,
        "seeking_description": artist.seeking_description,
        "past_shows": past_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artists = Artist.query.get(artist_id)

    artist_info = {

        "id": artists.id,
        "name": artists.name,
        "genres": artists.genres,
        "city": artists.city,
        "state": artists.state,
        "phone": artists.phone,
        "website": artists.website,
        "facebook_link": artists.facebook_link,
        "seeking_venue": artists.seeking_venue,
        "seeking_description": artists.seeking_description,
        "image_link": artists.image_link

    }

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist_info)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    error = False

    try:
        artist = Artist.query.filter_by(id=artist_id).first()

        artist.id = request.form.get('id')
        artist.name = request.form.get('name')
        artist.genres = request.form.getlist('genres')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.website = request.form.get('website')
        artist.facebook_link = request.form.get('facebook_link')
        artist.seeking_venue = request.form.get('seeking_venue')
        artist.seeking_description = request.form.get('seeking_description')
        artist.image_link = request.form.get('image_link')

        db.session.add(artist)
        db.session.commit()

    except:
        error = True
        db.session.rollback()

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = Venue.query.get(venue_id)

    venue_info = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue_info)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    error = False

    try:
        venue = Venue.query.filter_by(id=venue_id).first()

        venue.id = request.form.get('id')
        venue.name = request.form.get('name')
        venue.genres = request.form.getlist('genres')
        venue.address = request.form.get('address')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.phone = request.form.get('phone')
        venue.website = request.form.get('website')
        venue.facebook_link = request.form.get('facebook_link')
        venue.seeking_talent = request.form.get('seeking_talent')
        venue.seeking_description = request.form.get('seeking_description')
        venue.image_link = request.form.get('image_link')

        db.session.add(artist)
        db.session.commit()

    except:
        error = True
        db.session.rollback()

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    error = False

    try:
        add_new_artist = Artist(

            name=request.form.get('name'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone'),
            genres=request.form.getlist('genres'),
            facebook_link=request.form.get('facebook_link')

        )

        db.session.add(add_new_artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True

    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' +
              add_new_artist.name + ' could not be listed.')

    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    shows = Show.query.all()
    data = []

    for show in shows:
        data.append({
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': str(show.start_time)
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    error = False

    try:
        new_show = Show(

            artist_id=request.form.get('artist_id'),
            venue_id=request.form.get('venue_id'),
            start_time=request.form.get('start_time')

        )

        db.session.add(new_show)
        db.session.commit()

    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if not error:
        # on successful db insert, flash success
        flash('Show was successfully listed!')

    else:
        flash('An error occurred. Show could not be listed.')

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
