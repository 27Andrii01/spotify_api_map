from flask import Flask, render_template, request
import main_task3

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        artist_name = request.form.get('artist')
        token = main_task3.get_token()
        header = main_task3.get_auth_header(token)
        arist_id = main_task3.search_for_artist(token, artist_name)['id']
        songs = main_task3.get_songs_by_artist(token, arist_id)
        gam = main_task3.get_available_markets(token, songs[0]['id'])
        country_name = main_task3.get_country_name(gam)
        main_task3.get_cordinate_map(country_name)
        return render_template('map_spotify.html')
    else:
        return render_template('web.html')
